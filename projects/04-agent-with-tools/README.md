# 项目 4：Agent + 工具调用

**建议学习周**：第 11 周 | **目标**：知识库 + 外部工具（如天气），由模型决定先查库还是先调工具

## 做什么

1. 把「RAG 知识库」封装成一个 Tool：输入问题，返回检索到的答案或摘要。
2. 再写一个简单 Tool，例如「查天气」或「计算器」。
3. 用 LangChain 的 Agent（如 ReAct）把两个 Tool 注册进去，用户问混合问题（如「公司年假几天？珠海明天天气怎么样？」），由 Agent 决定先调哪个、再调哪个，最后综合回答。

## 通俗理解

- **Tool**：一个函数，有名字和描述，Agent 根据描述决定「要不要用、什么时候用」。
- **Agent**：模型会「想一步→选工具→执行→再看结果再想一步」，直到得出最终答案。

## 步骤建议

1. 用 LangChain 的 `@tool` 或 `Tool(name="...", func=..., description="...")` 定义两个工具。
2. 用 `create_react_agent` 或 `initialize_agent` 把工具和 LLM 绑在一起。
3. 用脚本或简单对话循环测试：问「年假几天」应主要用 RAG；问「明天天气」应调天气；问「年假几天且明天天气如何」应两个都调。

## 文件说明

- `agent_demo.py`：定义 RAG Tool、天气 Tool，创建 Agent 并跑一轮对话。
- 天气可用免费 API（如 wttr.in 或心知天气）或 mock。

## 运行示例

```bash
python agent_demo.py
# 或交互式
python agent_demo.py --interactive
```

## 扩展（可选）

- 增加「查数据库」Tool（如查员工考勤统计）。
- 用 Streamlit 做简单聊天界面。
