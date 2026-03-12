"""
项目4：Agent + 工具调用（骨架）
定义 RAG 工具 + 天气工具，用 LangChain Agent 自动选工具并回答。
"""
import os
from dotenv import load_dotenv
load_dotenv()


def rag_tool(question: str) -> str:
    """Tool 1：查知识库。实际接项目 1/2 的 query_rag。"""
    # return query_rag(question)[0]
    return f"[RAG 占位] 问题: {question}"


def weather_tool(city: str) -> str:
    """Tool 2：查天气。可用 wttr.in 或 mock。"""
    # 示例：requests.get(f"https://wttr.in/{city}?format=%l+%c+%t")
    return f"[天气占位] 城市: {city} 晴 25°C"


def main():
    try:
        from langchain.agents import create_react_agent, AgentExecutor
        from langchain.tools import Tool
        from langchain_openai import ChatOpenAI
    except ImportError:
        print("请安装: pip install langchain langchain-openai")
        return

    llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=os.getenv("OPENAI_API_KEY"), temperature=0)
    tools = [
        Tool(name="KnowledgeBase", func=rag_tool, description="查询公司制度、文档、FAQ。输入：一个问题。"),
        Tool(name="Weather", func=weather_tool, description="查询城市天气。输入：城市名，如珠海。"),
    ]
    # 创建 Agent 并执行
    # agent = create_react_agent(llm, tools, ...)
    # executor = AgentExecutor(agent=agent, tools=tools, ...)
    # result = executor.invoke({"input": "公司年假有几天？珠海明天天气怎么样？"})
    # print(result["output"])
    print("请接上 create_react_agent + AgentExecutor，并替换 rag_tool/weather_tool 为真实实现。")


if __name__ == "__main__":
    main()
