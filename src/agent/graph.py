"""LangGraph agent with MCP integration."""

from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from .mock_llm import MockLLM, ParseResult
from .tools import (
    calculate_discount,
    format_price,
    format_product_list,
    format_statistics,
)


class AgentState(TypedDict):
    """State for the agent graph."""
    query: str
    parse_result: ParseResult | None
    tool_results: dict[str, Any]
    response: str
    tools_used: list[str]
    error: str | None


class ProductAgent:
    """LangGraph-based agent for product queries."""

    def __init__(self):
        self.llm = MockLLM()
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state graph."""
        graph = StateGraph(AgentState)

        # Add nodes
        graph.add_node("parse_request", self._parse_request)
        graph.add_node("execute_tools", self._execute_tools)
        graph.add_node("format_response", self._format_response)

        # Add edges
        graph.set_entry_point("parse_request")
        graph.add_edge("parse_request", "execute_tools")
        graph.add_edge("execute_tools", "format_response")
        graph.add_edge("format_response", END)

        return graph.compile()

    def _parse_request(self, state: AgentState) -> dict:
        """Parse the user request using mock LLM."""
        try:
            parse_result = self.llm.parse(state["query"])
            return {
                "parse_result": parse_result,
                "tools_used": [tc.tool_name for tc in parse_result.tool_calls]
            }
        except Exception as e:
            return {"error": str(e)}

    def _execute_tools(self, state: AgentState) -> dict:
        """Execute tools synchronously."""
        if state.get("error"):
            return {}

        parse_result = state["parse_result"]
        if not parse_result:
            return {"error": "No parse result"}

        tool_results = {}

        for tool_call in parse_result.tool_calls:
            tool_name = tool_call.tool_name
            arguments = tool_call.arguments

            # Handle custom tools
            if tool_name == "calculate_discount":
                # Need product price from previous get_product call
                product_result = tool_results.get("get_product", {})
                if isinstance(product_result, dict) and "price" in product_result:
                    price = product_result["price"]
                    result = calculate_discount(price, arguments["percent"])
                    result["product_name"] = product_result.get("name", "Unknown")
                else:
                    result = {"error": "Product not found for discount calculation"}
                tool_results[tool_name] = result

            elif tool_name == "format_price":
                result = format_price(arguments["amount"])
                tool_results[tool_name] = result

            else:
                # MCP tools - call synchronously
                result = self._call_mcp_tool(tool_name, arguments)
                tool_results[tool_name] = result

        return {"tool_results": tool_results}

    def _call_mcp_tool(self, tool_name: str, arguments: dict) -> Any:
        """Call MCP tool.

        In this implementation, we directly import and call the MCP server tools.
        In production, this would use the MCP protocol via stdio subprocess.
        """
        from src.mcp_server.server import (
            list_products,
            get_product,
            add_product,
            get_statistics,
        )

        tool_map = {
            "list_products": list_products,
            "get_product": get_product,
            "add_product": add_product,
            "get_statistics": get_statistics,
        }

        if tool_name in tool_map:
            return tool_map[tool_name](**arguments)

        return {"error": f"Unknown tool: {tool_name}"}

    def _format_response(self, state: AgentState) -> dict:
        """Format the final response as structured data."""
        if state.get("error"):
            return {"response": {"error": state["error"]}}

        tool_results = state.get("tool_results", {})

        if not tool_results:
            return {"response": {"error": "Не удалось выполнить запрос"}}

        # Return structured data based on tool type
        response_data = {}

        for tool_name, result in tool_results.items():
            if tool_name == "list_products":
                response_data["products"] = format_product_list(result)
            elif tool_name == "get_product":
                if isinstance(result, dict) and "name" in result:
                    response_data["product"] = result
                else:
                    response_data["error"] = result.get("error", "Продукт не найден")
            elif tool_name == "get_statistics":
                response_data["statistics"] = format_statistics(result)
            elif tool_name == "add_product":
                response_data["added_product"] = result
            elif tool_name == "calculate_discount":
                response_data["discount"] = result
            else:
                response_data[tool_name] = result

        return {"response": response_data}

    def process_query(self, query: str) -> dict:
        """Process a user query.

        Args:
            query: User query string

        Returns:
            Dictionary with response and tools_used
        """
        initial_state: AgentState = {
            "query": query,
            "parse_result": None,
            "tool_results": {},
            "response": "",
            "tools_used": [],
            "error": None
        }

        # Run the graph
        final_state = self.graph.invoke(initial_state)

        return {
            "response": final_state.get("response", ""),
            "tools_used": final_state.get("tools_used", [])
        }


# Singleton instance
_agent: ProductAgent | None = None


def get_agent() -> ProductAgent:
    """Get or create the agent instance."""
    global _agent
    if _agent is None:
        _agent = ProductAgent()
    return _agent
