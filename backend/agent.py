from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from mcp_server import MCPTools


try:
    
    import google.genai as genai
except ImportError:
    genai = None

try:
    from groq import Groq
except ImportError:
    Groq = None


class AgentState(TypedDict):
    query: str
    messages: List
    steps: List[str]
    final_answer: str
    iteration: int
    max_iterations: int
    search_results: List
    analysis: str
    needs_more_info: bool


class EnhancedResearchAgent:
    def __init__(self, llm_type: str = None, api_key: str = None):
        self.mcp_tools = MCPTools()
        self.llm_type = llm_type.lower() if llm_type else None
        self.llm = None

        # Initialize Gemini
        if self.llm_type == "gemini" and genai:
            self.llm = genai.Client(api_key=api_key)

        # Initialize Groq
        elif self.llm_type == "groq" and Groq:
            self.llm = Groq(api_key=api_key)

        

        self.graph = self._create_graph()

    def _create_graph(self):
        workflow = StateGraph(AgentState)
        workflow.add_node("understand_query", self.understand_query)
        workflow.add_node("plan_search", self.plan_search)
        workflow.add_node("search_web", self.search_web)
        workflow.add_node("analyze_with_llm", self.analyze_with_llm)
        workflow.add_node("generate_answer", self.generate_answer)

        workflow.set_entry_point("understand_query")
        workflow.add_edge("understand_query", "plan_search")
        workflow.add_edge("plan_search", "search_web")
        workflow.add_edge("search_web", "analyze_with_llm")
        workflow.add_conditional_edges(
            "analyze_with_llm",
            self.should_continue,
            {"continue": "search_web", "finish": "generate_answer"}
        )
        workflow.add_edge("generate_answer", END)
        return workflow.compile()

    def understand_query(self, state: AgentState) -> AgentState:
        state["steps"].append(f"🧠 Understanding query: {state['query']}")
        state["messages"].append(HumanMessage(content=state["query"]))
        return state

    def plan_search(self, state: AgentState) -> AgentState:
        state["steps"].append("📋 Planning search strategy...")
        q_lower = state["query"].lower()
        if any(word in q_lower for word in ["latest", "recent", "current"]):
            state["steps"].append("🔍 Identified: Recent/trending information needed")
        elif any(word in q_lower for word in ["how", "what"]):
            state["steps"].append("🔍 Identified: Explanatory information needed")
        elif "vs" in q_lower or "compare" in q_lower:
            state["steps"].append("🔍 Identified: Comparative analysis needed")
        return state

    def search_web(self, state: AgentState) -> AgentState:
        query = state["query"]
        iteration = state.get("iteration", 0)
        if iteration > 0 and state.get("needs_more_info"):
            query = f"{query} detailed information"
            state["steps"].append(f"🔄 Refining search (attempt {iteration + 1}): {query}")
        else:
            state["steps"].append(f"🌐 Searching web for: {query}")

        results = self.mcp_tools.search(query)
        state["search_results"] = results
        state["messages"].append(AIMessage(content=f"Found {len(results)} results"))
        return state

    def analyze_with_llm(self, state: AgentState) -> AgentState:
        state["steps"].append("🤔 Analyzing search results...")
        results = state["search_results"]
        results_preview = "\n".join(
            f"{i+1}. {r['title']}: {r['snippet']}"
            for i, r in enumerate(results[:5])
        )

        if self.llm:
            prompt = (
                f"You are an expert researcher. Given the following query and these search results, "
                f"answer the query accurately using both your knowledge and the results.\n\n"
                f"Query: {state['query']}\n\n"
                f"Search Results:\n{results_preview}\n\n"
                f"If the search results are insufficient, you can rely on your knowledge."
            )

            try:
                if self.llm_type == "gemini":
                    response = self.llm.models.generate_content(
                        model="gemini-2.5-flash",  # or any Gemini model you want
                        contents=prompt
                    )
                    analysis = response.text
                elif self.llm_type == "groq":
                    resp = self.llm.predict(prompt)
                    # Groq response format might differ — adjust if needed
                    analysis = resp.get("text", "")
                else:
                    analysis = results_preview
            except Exception as e:
                analysis = f"LLM analysis failed: {e}"

            state["analysis"] = analysis
            state["needs_more_info"] = False
        else:
            # No LLM: fallback summarization
            state["analysis"] = "\n\n".join(
                f"**{r['title']}**\n{r['snippet']}"
                for r in results[:3]
            ) or "No results found."
            state["needs_more_info"] = False

        state["iteration"] = state.get("iteration", 0) + 1
        return state

    def should_continue(self, state: AgentState) -> str:
        if state["iteration"] >= state["max_iterations"]:
            state["steps"].append("⏸️ Reached max iterations")
            return "finish"
        if state.get("needs_more_info") and state["iteration"] < state["max_iterations"]:
            state["steps"].append("🔄 Need more information, searching again...")
            return "continue"
        return "finish"

    def generate_answer(self, state: AgentState) -> AgentState:
        state["steps"].append("✍️ Generating final answer...")
        analysis = state["analysis"]
        query = state["query"]

        if self.llm:
            prompt = (
                f"Create a clear, structured, and informative answer for the query below.\n\n"
                f"Query: {query}\n\n"
                f"Research / Analysis:\n{analysis}"
            )

            try:
                if self.llm_type == "gemini":
                    resp = self.llm.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt
                    )
                    final_answer = resp.text
                elif self.llm_type == "groq":
                    resp = self.llm.predict(prompt)
                    final_answer = resp.get("text", "")
                else:
                    final_answer = analysis
            except Exception as e:
                final_answer = f"(LLM error) {e}\n\n{analysis}"
        else:
            final_answer = (
                f"# Research Results for: {query}\n\n"
                f"## Summary\n"
                f"{analysis}\n\n"
                f"---\n"
                f"*Note: This is a summary of search results. For more detailed information, check original sources.*"
            )

        state["final_answer"] = final_answer
        state["steps"].append("✅ Answer generated successfully!")
        return state

    async def run(self, query: str, max_iterations: int = 5) -> dict:
        initial: AgentState = {
            "query": query,
            "messages": [],
            "steps": [],
            "final_answer": "",
            "iteration": 0,
            "max_iterations": max_iterations,
            "search_results": [],
            "analysis": "",
            "needs_more_info": False
        }
        result = await self.graph.ainvoke(initial)
        return {
            "final_answer": result.get("final_answer", ""),
            "steps": result.get("steps", []),
            "sources": result.get("search_results", [])
        }

