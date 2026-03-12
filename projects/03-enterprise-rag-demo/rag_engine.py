"""
项目3：RAG 引擎封装 — 建索引、检索、调用 LLM。
与项目 1/2 逻辑一致，这里集中封装，便于 app 和评测脚本调用。
"""
import os
from pathlib import Path


def build_index(data_dir: str, persist_dir: str = ".chroma_db"):
    """从 data_dir 加载文档，切块、向量化并持久化到 persist_dir。"""
    # TODO: 复用 01/02 的加载与切块逻辑，使用 Chroma(persist_directory=persist_dir)
    print(f"建索引: {data_dir} -> {persist_dir}")
    return None


def query_rag(question: str, top_k: int = 5) -> tuple[str, list[str]]:
    """检索 + 生成，返回 (answer, sources)。"""
    # TODO: 加载已建好的向量库，检索后拼 context，调 LLM
    return "（请实现检索与 LLM 调用）", []


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--build-index", action="store_true")
    p.add_argument("--data-dir", default="data")
    p.add_argument("--query", default="")
    args = p.parse_args()
    if args.build_index:
        build_index(args.data_dir)
    if args.query:
        ans, src = query_rag(args.query)
        print("Answer:", ans)
        print("Sources:", src)
