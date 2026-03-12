# 项目 1：单 PDF 知识库问答

**建议学习周**：第 6 周 | **目标**：从零实现最小 RAG  

> 想系统了解 ChromaDB 是什么、能做什么、和别的向量库怎么选，可看 **[ChromaDB向量数据库介绍与选型对比](../../docs/ChromaDB向量数据库介绍与选型对比.md)**。

## 做什么

1. 读入一个 PDF，按块切分文本。
2. 把每块文本用「嵌入 API」转成向量，存进向量库（如 Chroma）。
3. 用户提问时：把问题转成向量 → 在库里检索最相关的几块 → 把这几块 + 问题一起发给大模型 → 返回答案。

## 通俗理解

- **切块**：长文档拆成 300～500 字的小段，方便按「段」检索。
- **向量**：把文字变成一串数字，意思相近的段向量离得近。
- **检索**：用「问题」的向量去库里找最相近的几段，这些段就是「资料」。
- **生成**：把「资料 + 问题」交给大模型，让它「只根据资料回答」，减少瞎编。

## 步骤建议

1. 先跑通 `simple_rag.py`（见下方骨架），能对一份示例 PDF 提问。
2. 调切块大小（如 300/500）、重叠（如 50），看回答质量变化。
3. 自测：准备 5 个「问题 + 标准答案」，对比模型输出，算一个简单的准确率。

## 文件说明

- `simple_rag.py`：主流程（加载 PDF → 切块 → 建索引 → 问答）。
- `data/sample.pdf`：放一个你自己准备的 PDF（如公司制度一两页），不要提交大文件。

## 在 Cursor 中 Debug 本脚本

1. **确认环境**：已安装 Python 扩展、依赖已装（`pip install -r requirements.txt`），且已在 `data/` 下放置 PDF（如 `data/sample.pdf`）。
2. **打断点**：在 `simple_rag.py` 里需要停下的行号左侧点击，出现红点即为断点（如 `load_pdf_text`、`split_into_chunks`、`get_embedding`、`main` 内某行）。
3. **启动调试**：
   - 按 **F5** 或 左侧「运行和调试」图标 → 顶部下拉选 **「Debug: simple_rag.py（项目1 单 PDF RAG）」** → 点绿色三角或再按 F5。
   - 若当前打开的是 `simple_rag.py`，也可选 **「Debug: simple_rag.py（仅当前文件）」**，工作目录仍是 `projects/01-single-pdf-rag`，便于读 `data/` 和 `.env`。
4. **运行到断点**：程序会在断点处暂停，可查看变量、单步（F10）、进入函数（F11）、继续（F5）。底部「变量」「监视」「调用堆栈」可查看当前状态。
5. **改参数**：在 `.vscode/launch.json` 里修改对应配置的 `args`（如 `--pdf`、`--query`、`--top-k`），保存后重新 F5 即可用新参数调试。

## 运行示例

```bash
#建议使用 Python 3.10+，创建虚拟环境后按各项目 README 安装依赖。
python -m venv venv
# Windows:
venv\Scripts\activate
# 然后进入具体项目目录安装依赖
cd projects/01-single-pdf-rag
pip install -r requirements.txt
# 在 data/ 下放一个 sample.pdf
python simple_rag.py --pdf data/sample.pdf --query "年假有几天"
```

## 扩展（可选）

- 支持 TXT 文件。
- 把 Top-K 从 3 改成 5，观察答案变化。

