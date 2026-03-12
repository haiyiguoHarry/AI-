"""
项目3：企业场景 RAG Demo — Web 入口（骨架）
可选：Streamlit 或 FastAPI。这里用 FastAPI 示例，可改为 Streamlit。
"""
import os
from dotenv import load_dotenv
load_dotenv()

# FastAPI 示例
def create_app():
    from fastapi import FastAPI
    from pydantic import BaseModel

    app = FastAPI(title="企业知识库问答 Demo")

    # 实际从 rag_engine 导入：build_index, query
    # from .rag_engine import build_index, query_rag

    class QueryRequest(BaseModel):
        question: str

    @app.post("/query")
    def query(req: QueryRequest):
        # answer, sources = query_rag(req.question)
        # return {"answer": answer, "sources": sources}
        return {"answer": "（请接上 rag_engine 的 query_rag）", "sources": []}

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()

# 运行: uvicorn app:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
