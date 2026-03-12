"""
项目2：多文档知识库问答（带元数据/标签过滤）
支持：多文件、按部门/类型过滤检索
"""
import os
from pathlib import Path

# 建议在本项目用 LangChain 实现，便于熟悉 Document、VectorStore、metadata
def load_docs_from_dir(data_dir: str) -> list[tuple[str, dict]]:
    """
    从目录加载文档，返回 [(文本, metadata), ...]。
    metadata 至少包含 source（文件名）、department（用子目录名表示）。
    """
    data_path = Path(data_dir)
    if not data_path.exists():
        return []

    results = []
    for ext in ["*.pdf", "*.txt"]:
        for f in data_path.rglob(ext):
            try:
                if f.suffix.lower() == ".pdf":
                    from pypdf import PdfReader
                    reader = PdfReader(str(f))
                    text = "".join(p.extract_text() or "" for p in reader.pages)
                else:
                    text = f.read_text(encoding="utf-8", errors="ignore")
                # 用父目录名作为部门，如 data/hr/xxx.pdf -> department=hr
                rel = f.relative_to(data_path)
            except Exception as e:
                print(f"跳过 {f}: {e}")
                continue
            parts = rel.parts
            department = parts[0] if len(parts) > 1 else "default"
            results.append((text.strip(), {"source": str(f.name), "department": department}))
    return results


def _split_text(text: str, chunk_size: int = 400, overlap: int = 50) -> list[str]:
    """按固定长度切块，带重叠。"""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - overlap
    return chunks


def chunks_with_metadata(doc_list: list[tuple[str, dict]], chunk_size: int = 400, overlap: int = 50):
    """切块并保留每块的 metadata。"""
    all_chunks = []
    for text, meta in doc_list:
        if not text:
            continue
        for i, chunk in enumerate(_split_text(text, chunk_size, overlap)):
            all_chunks.append((chunk, {**meta, "chunk_id": i}))
    return all_chunks


# 此处仅作骨架：实际用 LangChain 的 VectorStore（Chroma）存 document+metadata，
# 查询时用 filter 参数。参考 LangChain 文档 "Metadata filtering"。
def main():
    from dotenv import load_dotenv
    load_dotenv()
    data_dir = os.getenv("DATA_DIR", "data")
    docs = load_docs_from_dir(data_dir)
    print(f"加载到 {len(docs)} 个文档")
    if not docs:
        print("请在 data/ 下创建子目录（如 hr/、finance/）并放入 PDF 或 TXT")
        return
    # TODO: 切块 → 向量化 → 存入 Chroma（带 metadatas）→ 实现 query(question, filter_department=...)
    print("请在此接上 LangChain Chroma + metadata 过滤，见 README 步骤。")


if __name__ == "__main__":
    main()
