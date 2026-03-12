# AI- 职业发展与学习仓库

> 面向企业开发背景（C#/ASP.NET/前端），在 AI 时代往**企业级 AI 应用**方向突破：掌握 RAG、企业知识库与 Agent 落地，形成可展示项目与简历亮点。

---

## 项目简介

本仓库包含：

- **学习计划与分析**：珠海高新区岗位行情、AI 时代核心竞争力方向、按周拆解的学习计划（约 14 周，每周 16 小时）。
- **通俗知识讲解**：大模型 API、提示词、向量与 RAG、Agent 等概念，用通俗话术和例子说明。
- **四个实战小项目**：从单 PDF RAG 到多文档知识库、企业场景 Demo、Agent 工具调用，带 README 与代码骨架，便于按周推进。

适合已有 3～8 年企业系统开发经验、希望向「AI 应用 / 用 AI 改造业务」转型的开发者。

---

## 仓库结构

```
AI-/
├── README.md                 # 本文件
├── LICENSE
├── docs/                     # 文档
│   ├── AI时代职业发展与学习计划.md   # 主文档：分析 + 计划 + 知识讲解 + 项目说明
│   └── 每周笔记.md               # 每周复盘模板
└── projects/                 # 学习用小项目
    ├── README.md             # 项目总览与通用依赖说明
    ├── 01-single-pdf-rag/    # 单 PDF 知识库问答（第 6 周）
    ├── 02-multi-doc-rag/     # 多文档 + 标签过滤（第 9 周）
    ├── 03-enterprise-rag-demo/  # 企业场景 RAG Demo（第 12 周）
    └── 04-agent-with-tools/  # Agent + 工具调用（第 11 周）
```

---

## 快速开始

### 1. 阅读主文档

建议先通读 **[docs/AI时代职业发展与学习计划.md](docs/AI时代职业发展与学习计划.md)**，了解：

- 岗位与方向分析  
- 14 周学习计划（每周 16 小时）  
- RAG / 向量 / Agent 等通俗讲解  
- 各小项目的目标与步骤  

### 2. 环境准备

- **Python**：建议 3.10+  
- **依赖**：各项目目录下有 `requirements.txt`，按需安装：

```bash
python -m venv venv
# Windows
venv\Scripts\activate
cd projects/01-single-pdf-rag
pip install -r requirements.txt
```

- **API Key**：在项目根或各项目下创建 `.env`（勿提交到 Git），例如：

```ini
OPENAI_API_KEY=sk-xxx
# 或国产大模型
DASHSCOPE_API_KEY=xxx
ZHIPU_API_KEY=xxx
```

### 3. 按周做项目

| 周次   | 主题           | 对应项目 / 文档 |
|--------|----------------|------------------|
| 1～3   | 基础与环境     | 主文档「阶段一」 |
| 4～7   | RAG 入门       | 项目 1：`01-single-pdf-rag` |
| 8～10  | 框架与多源     | 项目 2：`02-multi-doc-rag` |
| 11     | Agent 入门     | 项目 4：`04-agent-with-tools` |
| 12～14 | 综合与简历     | 项目 3：`03-enterprise-rag-demo` |

每个项目目录内都有 **README** 说明「做什么、通俗理解、运行示例」，代码中有 `# TODO` 标注，用于接真实 API 与逻辑。

### 4. 每周复盘

使用 **[docs/每周笔记.md](docs/每周笔记.md)** 记录「计划内容、实际完成、卡点、下周重点」，便于调整节奏。

### 5. Git / GitHub 学习

从本地创建项目到提交、推送到 GitHub 的完整步骤见 **[docs/Git与GitHub从零到提交完整流程.md](docs/Git与GitHub从零到提交完整流程.md)**。

---

## 核心方向简述

在 AI 时代、结合珠海高新区行情，本仓库建议的**核心竞争力**方向为：

- **企业级 AI 应用落地**：RAG / 企业知识库优先，再延伸至 Agent、内部 Copilot。  
- **使力点**：在保留现有 C#/前端/企业系统经验的基础上，补 **Python + 大模型 API + RAG 全链路 + 提示词/评测**，并结合 AI 训练师证书与业务理解。

详细分析见主文档第一部分。

---

## 许可证

见 [LICENSE](LICENSE) 文件。
