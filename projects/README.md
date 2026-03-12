# 。AI 学习小项目总览

配合主文档 [../docs/AI时代职业发展与学习计划.md](../docs/AI时代职业发展与学习计划.md) 使用，按周完成对应项目。

## 项目列表


| 项目           | 目录                                                  | 建议周次   | 目标                        |
| ------------ | --------------------------------------------------- | ------ | ------------------------- |
| 单 PDF 知识库问答  | [01-single-pdf-rag](./01-single-pdf-rag/)           | 第 6 周  | 最小 RAG：一个 PDF → 检索 → 生成回答 |
| 多文档知识库问答     | [02-multi-doc-rag](./02-multi-doc-rag/)             | 第 9 周  | 多文件 + 标签/过滤               |
| 企业场景 Demo    | [03-enterprise-rag-demo](./03-enterprise-rag-demo/) | 第 12 周 | 制度/FAQ 等场景，可演示            |
| Agent + 工具调用 | [04-agent-with-tools](./04-agent-with-tools/)       | 第 11 周 | 知识库 + 天气等工具               |


## 环境与依赖（通用）

建议使用 Python 3.10+，创建虚拟环境后按各项目 README 安装依赖。

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# 然后进入具体项目目录安装依赖
pip install -r requirements.txt
```

### 常用依赖（各项目会按需使用）

- `requests`：调用大模型 API、嵌入 API
- `pypdf` 或 `pdfplumber`：读 PDF
- `chromadb`：向量库（轻量）
- `langchain`、`langchain-community`：RAG/Agent 框架
- `python-dotenv`：从 `.env` 读 API Key，不要提交到 Git

### API Key 配置

在项目根目录或各项目下创建 `.env`（不要提交），例如：

```ini
# 任选一个或多个
OPENAI_API_KEY=sk-xxx
DASHSCOPE_API_KEY=xxx   # 通义千问
ZHIPU_API_KEY=xxx       # 智谱
#DEEPSEEK_API_KEY=XX #deepseek https://platform.deepseek.com/api_keys 只能对话，不能用
```

各项目代码中通过 `os.getenv("XXX")` 或 `dotenv.load_dotenv()` 读取。