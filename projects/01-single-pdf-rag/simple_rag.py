"""
项目1：单 PDF 知识库问答（最小 RAG）

【RAG 是什么】
RAG = Retrieval-Augmented Generation（检索增强生成）。
传统大模型容易「幻觉」：不知道的事也会瞎编。RAG 的做法是：先把企业文档、
知识库做成「可检索的向量」，用户提问时先检索出最相关的几段原文，再把这
几段 + 问题一起喂给大模型，并明确要求「只根据资料回答」，从而减少瞎编。

【本脚本整体流程】
  1. PDF → 全文文本（load_pdf_text）
  2. 全文 → 切成多段「块」（split_into_chunks），每块单独做向量、存库
  3. 用户提问 → 把问题也变成向量 → 在库里找最相似的几块（build_index / query）
  4. 把这几块拼成「资料」+ 问题 → 调用大模型生成回答（query_llm）
"""
# ---------- 标准库导入（按字母序便于查找）----------
import os
# os：读写环境变量（如 API Key）、路径等；这里主要用 os.getenv("XXX_API_KEY") 从 .env 或系统环境取配置。
import argparse
# argparse：解析命令行参数（--pdf、--query、--top-k、--rebuild），不用手写 sys.argv 解析，且自动生成 --help。
import hashlib
# hashlib：生成文本的哈希值；用于「占位向量」时把任意字符串变成确定性的数字序列，保证同一文本多次调用维度一致。
import warnings
# warnings：发出警告而不中断程序（如 Embedding 失败时提示用占位向量），便于调试和兼容无 API 环境。
from pathlib import Path
# pathlib.Path：面向对象的路径操作，如 Path(".chroma_db").exists()、Path(args.pdf)，跨平台且可读性好。

# ---------- 常量（集中配置，方便修改与复用）----------
CHROMA_DIR = ".chroma_db"
# Chroma 持久化目录名。数据会存到当前工作目录下的 .chroma_db（内含 chroma.sqlite3 等），重启进程后可复用，无需每次重算向量。
COLLECTION_NAME = "pdf_rag"
# Chroma 的「集合」名称。一个集合相当于一张表，存当前 PDF 的所有块（id + embedding + 原文）；不同知识库可用不同集合名区分。
PLACEHOLDER_DIM = 1536
# 占位向量的维度。1536 与 OpenAI text-embedding-3-small、通义 text-embedding-v2 等常见模型一致，避免与 Chroma 建索引时的维度冲突。


def _embedding_to_list(emb) -> list[float]:
    """
    将 API 返回的 embedding（可能为 numpy 或 list）统一转为 list。
    知识：Chroma 的 add/query 接口通常接受 list[float]；部分 SDK 返回 numpy.ndarray，
    若直接传给 Chroma 或做「if emb:」判断时，numpy 数组可能触发歧义（例如 bool(empty_array) 为 False 但 len>0）。
    统一转 list 可避免这类错误；返回类型标注 list[float] 便于类型检查与文档。
    """
    if hasattr(emb, "tolist"):
        # numpy 数组有 tolist() 方法，转为 Python 原生 list，Chroma 和后续逻辑都兼容。
        return emb.tolist()
    # 已是 list 则直接返回，否则用 list(emb) 拷贝一份（如从 API 返回的 list 转成可修改的 list，这里主要为了类型统一）。
    return list(emb) if not isinstance(emb, list) else emb
"""
if isinstance(emb, list):
    return emb
return list(emb)
"""

def _placeholder_embedding(text: str) -> list[float]:
    """
    无可用 Embedding API 时的占位向量：固定维度、确定性、无真实语义。
    用途：本地无 Key 或 API 失败时仍能跑通「建索引 → 检索 → 问答」流程，便于演示和调试；
    检索效果无意义，仅保证程序不报错。维度与 PLACEHOLDER_DIM 一致，避免 Chroma 报维度不匹配。
    """
    h = hashlib.sha256(text.encode()).hexdigest()
    # 用 SHA256 把文本变成 64 个十六进制字符，再每 2 位转成一个 0~1 的数并减 0.5 到 [-0.5,0.5]，得到 32 个浮点数作为「种子」。
    base = [int(h[i : i + 2], 16) / 255.0 - 0.5 for i in range(0, 32, 2)]
    # 将 base 重复拼接至不少于 PLACEHOLDER_DIM 长度，再截取前 PLACEHOLDER_DIM 个，保证维度固定且同一文本多次调用结果相同。
    return (base * (PLACEHOLDER_DIM // len(base)))[:PLACEHOLDER_DIM]


def load_pdf_text(pdf_path: str) -> str:
    """
    从 PDF 文件中提取全部纯文本。
    为什么需要：向量库和 Embedding 都是针对「文字」做的，所以先把 PDF 里的
    文字按页读出来、拼成一大段字符串，才能继续切块和向量化。
    依赖：pypdf 库（pip install pypdf），按页遍历并用 extract_text() 取文字。
    """
    try:
        # 延迟导入：仅在本函数内用 pypdf，避免未安装时在 import 阶段就报错；且 pypdf 非所有环境必装。
        from pypdf import PdfReader
        # PdfReader 打开文件句柄，可迭代 .pages 得到每一页的对象。
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            # extract_text() 返回该页的纯文本，无文字时可能返回 None，用 or "" 避免 None 拼接。
            text += page.extract_text() or ""
        # strip() 去掉首尾空白，避免开头多一个换行等。
        return text.strip()
    except Exception as e:
        # 用 from e 保留原始异常链，便于排查是文件不存在、权限问题还是 pypdf 解析错误。
        raise RuntimeError(f"读取 PDF 失败: {pdf_path}") from e


def split_into_chunks(text: str, chunk_size: int = 400, overlap: int = 50) -> list[str]:
    """
    把一整段长文本按「块」切开，每块约 chunk_size 个字符，块与块之间有一段「重叠」。

    为什么要切块？
      - 整篇 PDF 可能几万字，不能整篇去做相似度检索：成本高，且检索结果应是「一小段可读的上下文」。
      - 切成多块后，每块单独转成向量存库；用户提问时用问题的向量找「最像的几块」，再拼起来当「资料」。

    参数：chunk_size 每块字符数（太小碎、太大不精准）；overlap 块间重叠字符数，避免句子被截断在边界。

    举例（chunk_size=10, overlap=3）：
      块1: text[0:10] → "员工请假须提前一"；块2: text[7:17] → "须提前一天申请。"（从 10-3=7 开始）
    """
    chunks = []
    start = 0
    while start < len(text):
        # 当前块的范围：左闭右开 [start, start + chunk_size)，与 Python 切片语义一致。
        end = start + chunk_size
        chunk = text[start:end]
        # 只保留非空块（strip 后为空则跳过），避免空白块占用 id 和向量。
        if chunk.strip():
            chunks.append(chunk.strip())
        # 下一块起点 = end - overlap，实现重叠；若 overlap>=chunk_size 会死循环，一般 overlap < chunk_size。
        start = end - overlap
    return chunks


def get_embedding(text: str, api_key: str) -> list[float]:
    """
    把一段文字变成「向量」（一长串浮点数）。通俗理解：意思相近的文字对应向量距离近，
    检索时用问题的向量在库里找距离最近的几块作为「最相关资料」。常见维度 1536（OpenAI/通义）或 1024。
    支持 .env：OPENAI_API_KEY（OpenAI/兼容）、DASHSCOPE_API_KEY（通义）；DeepSeek 无公开 embedding 接口，仅用于对话。
    未配置或调用失败时返回占位向量，保证流程可跑通。
    """
    import os
    from openai import OpenAI
    import dashscope
    from dotenv import load_dotenv
    load_dotenv()
    # 从环境变量读取 Key；优先用专门做 embedding 的，避免用 DeepSeek Key 调不存在的 /v1/embeddings。
    openai_key = os.getenv("OPENAI_API_KEY")
    dashscope_key = os.getenv("DASHSCOPE_API_KEY")

    if openai_key:
        # 可自定义 base_url（如代理或自建兼容接口）、模型名；默认 OpenAI 官方。
        base_url = os.getenv("EMBEDDING_BASE_URL", "https://api.openai.com/v1")
        model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        try:
            client = OpenAI(api_key=openai_key, base_url=base_url)
            # embeddings.create：单次请求可传 string 或 list of string，返回 .data[0].embedding（list/array）。
            completion = client.embeddings.create(model=model, input=text)
            return _embedding_to_list(completion.data[0].embedding)
        except Exception as e:
            warnings.warn(f"Embedding 调用失败，使用占位向量: {e}", UserWarning)
    elif dashscope_key:
        model = os.getenv("EMBEDDING_MODEL", "text-embedding-v2")
        try:
            # 通义多模态 qwen3-vl-embedding 需在百炼控制台开通；默认用文本 embedding（OpenAI 兼容），1536 维。
            if "vl-embedding" in model.lower() or model == "qwen3-vl-embedding":
                input_data = [{"text": text}]
                resp = dashscope.MultiModalEmbedding.call(
                    api_key=dashscope_key,
                    model=model,
                    input=input_data,
                )
                if resp.status_code != 200:
                    raise RuntimeError(f"MultiModalEmbedding 调用失败: {getattr(resp, 'code', '')} {getattr(resp, 'message', resp)}")
                out = getattr(resp, "output", None) or {}
                emb = out.get("embedding")
                if emb is None:
                    embs = out.get("embeddings")
                    emb = embs[0] if embs is not None and len(embs) > 0 else None
                if emb is not None and isinstance(emb, dict):
                    emb = emb.get("embedding")
                if emb is None:
                    raise RuntimeError("MultiModalEmbedding 未返回 embedding")
                return _embedding_to_list(emb)
            else:
                # 通义 OpenAI 兼容的文本 embedding 接口，与 OpenAI 调用方式一致。
                base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
                client = OpenAI(api_key=dashscope_key, base_url=base_url)
                completion = client.embeddings.create(model=model, input=text)
                return _embedding_to_list(completion.data[0].embedding)
        except Exception as e:
            warnings.warn(f"Embedding 调用失败，使用占位向量: {e}", UserWarning)
    elif api_key:
        # 仅有 DeepSeek 等无 embedding 接口的 Key 时，提示用户并退回占位。
        warnings.warn(
            "当前仅有 DEEPSEEK_API_KEY，DeepSeek 暂不提供公开 embedding 接口，使用占位向量。"
            "如需真实语义检索，请在 .env 中配置 OPENAI_API_KEY 或 DASHSCOPE_API_KEY。",
            UserWarning,
        )
    return _placeholder_embedding(text)


def _get_chroma_collection():
    """
    获取持久化 Chroma 集合，与 build_index / load_existing_collection 共用同一目录和集合名。
    知识：Chroma 有两种客户端——Client() 仅内存，重启即丢；PersistentClient(path) 把数据写到本地目录，可复用。
    """
    try:
        import chromadb
        from chromadb.config import Settings
    except ImportError:
        raise ImportError("请安装: pip install chromadb")
    # PersistentClient：数据落盘到 path 目录（默认生成 chroma.sqlite3 等），进程重启后直接加载，无需重新建索引。
    client = chromadb.PersistentClient(
        path=CHROMA_DIR,
        settings=Settings(anonymized_telemetry=False),  # 关闭匿名遥测，避免联网上报。
    )
    # get_or_create_collection：按名称取集合，不存在则创建；metadata 可写描述，便于区分不同知识库。
    return client.get_or_create_collection(COLLECTION_NAME, metadata={"description": "single pdf"})


def build_index(chunks: list[str], api_key: str):
    """
    把切好的文本块向量化后存入 Chroma，便于后续按相似度检索。
    步骤：对每个 chunk 调用 get_embedding → 用 add(ids, embeddings, documents) 批量写入集合；
    用户提问时用问题的向量在同一个 collection 里 query，即可拿到最相似的几块原文。
    """
    coll = _get_chroma_collection()
    # ids：Chroma 要求每条记录有唯一 id（字符串），用于更新/删除或区分块；这里 c_0, c_1, ... 与 chunks 下标一一对应。
    ids = [f"c_{i}" for i in range(len(chunks))]
    # embeddings：对每个块调 get_embedding 得到向量，顺序与 ids、documents 一致；检索时用余弦相似度等找最近邻。
    embeddings = [get_embedding(c, api_key) for c in chunks]
    # add：批量写入；documents 存原文，query 时返回的即是这些文本，供后续拼成 context 给大模型。
    coll.add(ids=ids, embeddings=embeddings, documents=chunks)
    return coll


def load_existing_collection():
    """加载已持久化的 Chroma 集合（不重新读 PDF、不重建索引），与 build_index 共用 CHROMA_DIR 和 COLLECTION_NAME。"""
    return _get_chroma_collection()


def _ensure_embedding_dimension(coll, query_embedding: list[float]) -> None:
    """
    校验当前 query 的 embedding 维度与集合中已有向量一致；不一致时抛出 ValueError 并提示用户删库重建。
    知识：Chroma 建索引时用的是某一维度的向量（如 1536），若之后换模型得到不同维度（如 2560），
    query 会报 InvalidArgumentError，因此先读一条已有记录的 embedding 长度做校验。
    """
    try:
        one = coll.get(limit=1, include=["embeddings"])
        embeddings = one.get("embeddings")
        if embeddings is not None and len(embeddings) > 0:
            expected_dim = len(embeddings[0])
            if len(query_embedding) != expected_dim:
                raise ValueError(
                    f"当前 Embedding 维度为 {len(query_embedding)}，与已建索引维度 {expected_dim} 不一致。"
                    f"请删除本目录下的 {CHROMA_DIR} 文件夹后，执行：python simple_rag.py --pdf <你的PDF> --query \"...\" --rebuild"
                )
    except ValueError:
        raise
    except Exception:
        pass  # 无法读取维度时（如空集合）不拦，交给 Chroma query 时再报错。


def query_llm(context: str, question: str, api_key: str | None = None) -> str:
    """
    RAG 最后一步：把检索到的资料 + 用户问题拼成提示词，调用大模型生成回答。
    设计要点：明确写「只根据资料回答、不要编造」，减少幻觉；context 即上面 query 返回的 Top-K 块拼成的字符串。
    支持 .env：DASHSCOPE_API_KEY（通义）、DEEPSEEK_API_KEY、OPENAI_API_KEY；通义优先 Responses API，解析不到再回退 chat/completions。
    """
    # 三段式提示：资料 + 问题 + 回答要求；大模型会依此生成只基于资料的答案。
    prompt = f"""根据以下资料回答问题。只根据资料回答，不要编造。

资料：
{context}

问题：{question}

回答："""
    import os
    from openai import OpenAI
    from dotenv import load_dotenv
    load_dotenv()

    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    dashscope_key = os.getenv("DASHSCOPE_API_KEY")
    # 若调用方传入了 api_key 且环境变量里没有任何 Key，则把传入的 key 当作 DeepSeek 使用（兼容 main 里统一取的 api_key）。
    if api_key and not (deepseek_key or openai_key or dashscope_key):
        deepseek_key = api_key

    # ---------- 通义百炼：优先 Responses API（新协议），解析不到再回退到 OpenAI 兼容的 chat/completions ----------
    if dashscope_key:
        text_out = None
        try:
            # Responses API 的 base_url 与 chat 不同，见阿里云百炼文档。
            client = OpenAI(
                api_key=dashscope_key,
                base_url="https://dashscope.aliyuncs.com/api/v2/apps/protocols/compatible-mode/v1",
            )
            response = client.responses.create(
                model=os.getenv("CHAT_MODEL", "qwen3.5-plus"),
                input=prompt,
            )
            # 返回结构为 output 列表，每项可能有 content（含 type/output_text 与 text），需遍历取首段文本。
            out = getattr(response, "output", None) or []
            if out:
                first = out[0] if isinstance(out, list) else out
                content = getattr(first, "content", None) if hasattr(first, "content") else (first.get("content", []) if isinstance(first, dict) else [])
                content = content or []
                for item in content:
                    itype = getattr(item, "type", None) or (item.get("type") if isinstance(item, dict) else None)
                    text = getattr(item, "text", None) if hasattr(item, "text") else (item.get("text") if isinstance(item, dict) else None)
                    if itype == "output_text" and text:
                        text_out = (text or "").strip()
                        break
                    if text:
                        text_out = (text or "").strip()
                        break
        except Exception:
            pass
        if text_out:
            return text_out
        # 回退：通义兼容 OpenAI 的 chat/completions（qwen-plus 等），返回结构与 OpenAI 一致，.choices[0].message.content。
        try:
            client = OpenAI(
                api_key=dashscope_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            )
            completion = client.chat.completions.create(
                model=os.getenv("CHAT_MODEL", "qwen-plus"),
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1024,   # 回答最大 token 数，避免过长。
                temperature=0.3,   # 越低越确定、越少发挥，适合「按资料答」。
            )
            text_out = (completion.choices[0].message.content or "").strip()
            if text_out:
                return text_out
        except Exception as e:
            return f"[通义对话 API 调用失败: {e}]\n占位回答：根据资料：{context[:80]}..."
        return "[空回答]（Responses 与 chat 接口均未返回有效文本，请检查 CHAT_MODEL 或控制台权限）"

    # ---------- DeepSeek / OpenAI：统一走 OpenAI 兼容的 chat/completions ----------
    key, base_url, model = None, None, None
    if deepseek_key:
        key, base_url, model = deepseek_key, "https://api.deepseek.com/v1", "deepseek-chat"
    elif openai_key:
        key, base_url, model = openai_key, "https://api.openai.com/v1", os.getenv("CHAT_MODEL", "gpt-4o-mini")

    if key and base_url and model:
        try:
            client = OpenAI(api_key=key, base_url=base_url)
            completion = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1024,
                temperature=0.3,
            )
            return (completion.choices[0].message.content or "").strip() or "[空回答]"
        except Exception as e:
            return f"[对话 API 调用失败: {e}]\n占位回答：根据资料：{context[:80]}..."
    return f"[未配置对话 API Key] 请设置 DEEPSEEK_API_KEY / OPENAI_API_KEY / DASHSCOPE_API_KEY 之一。占位：{context[:80]}..."


def main():
    """
    主流程：读 PDF → 切块 → 建索引（可选）→ 用用户问题检索 → 拼资料调用大模型 → 输出回答。
    不传 --rebuild 且已有 .chroma_db 时会复用索引，跳过读 PDF 与建索引，直接做检索与问答。
    """
    # ---------- 命令行参数 ----------
    parser = argparse.ArgumentParser(description="单 PDF RAG 问答")
    parser.add_argument("--pdf", default="data/sample.pdf", help="PDF 文件路径，相对或绝对均可")
    parser.add_argument("--query", default="请总结文档主要内容", help="要问的问题，将用于检索与拼进提示词")
    parser.add_argument("--top-k", type=int, default=3, help="检索时取相似度最高的前 K 段作为「资料」喂给大模型，越大上下文越长、可能越全但噪声也多")
    parser.add_argument("--rebuild", action="store_true", help="为 True 时强制重新读 PDF、切块、建索引；不传则优先复用已有 CHROMA_DIR 中的集合")
    args = parser.parse_args()

    from dotenv import load_dotenv
    load_dotenv()
    # 从 .env 或环境变量取任一可用 Key，用于 embedding 与对话；优先级 OpenAI > 通义 > DeepSeek（仅对话用）。
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("DASHSCOPE_API_KEY") or os.getenv("DEEPSEEK_API_KEY") or ""

    coll = None
    # 未要求重建 且 持久化目录已存在：尝试加载已有集合，若有数据则复用，跳过耗时的读 PDF 与建索引。
    if not args.rebuild and Path(CHROMA_DIR).exists():
        try:
            coll = load_existing_collection()
            n = coll.count()
            if n > 0:
                print(f"复用已有索引（共 {n} 块），跳过读 PDF 与建索引。")
        except Exception:
            coll = None

    if coll is None or coll.count() == 0:
        # ---------- 第 1 步：从 PDF 取出全文，再按块大小与重叠切分 ----------
        pdf_path = Path(args.pdf)
        if not pdf_path.exists():
            print(f"请先放置 PDF 文件: {pdf_path}")
            return
        print("1. 读取 PDF 并切块...")
        text = load_pdf_text(str(pdf_path))
        chunks = split_into_chunks(text)
        print(f"   得到 {len(chunks)} 块")
        # ---------- 第 2 步：每块转成向量并写入 Chroma（add）----------
        print("2. 构建向量索引...")
        coll = build_index(chunks, api_key)
        n_docs = len(chunks)
    else:
        n_docs = coll.count()

    # ---------- 第 3 步：把用户问题也转成向量，在集合中 query 取最相似的 top_k 块，拼成 context 再调大模型 ----------
    print("3. 检索 + 生成回答...")
    q_embedding = get_embedding(args.query, api_key)
    _ensure_embedding_dimension(coll, q_embedding)
    # query：按向量相似度返回 n_results 条，results["documents"] 为二维列表，第一维为 query 条数（这里只有 1），故取 [0]。
    results = coll.query(query_embeddings=[q_embedding], n_results=min(args.top_k, n_docs))
    docs = results["documents"][0] if results.get("documents") else []
    context = "\n\n".join(docs)
    answer = query_llm(context, args.query, api_key)
    print("\n--- 检索到的资料（前 200 字）---")
    print(context[:200])
    print("\n--- 回答 ---")
    print(answer)


# 只有「直接运行本文件」时（如 python simple_rag.py --pdf xx.pdf --query "年假几天"）才执行 main；
# 被 import 时不会执行，便于作为模块复用函数。
if __name__ == "__main__":
    main()
