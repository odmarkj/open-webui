"""
Tool Calling Utilities for vLLM Integration

This module provides utilities for function/tool calling with vLLM models,
including OpenAI-compatible API integration and tool execution management.
"""

from typing import List, Dict, Any, Optional, Callable
import json
import logging
from openai import OpenAI

log = logging.getLogger(__name__)


class ToolExecutor:
    """
    Manages tool execution for function calling.

    Example:
        executor = ToolExecutor()
        executor.register_tool("search", my_search_function)
        result = executor.execute_tool("search", {"query": "test"})
    """

    def __init__(self):
        self.tools: Dict[str, Callable] = {}

    def register_tool(self, name: str, func: Callable) -> None:
        """
        Register a tool function.

        Args:
            name: Name of the tool (must match tool definition)
            func: Callable that executes the tool
        """
        self.tools[name] = func
        log.debug(f"Registered tool: {name}")

    def execute_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """
        Execute a registered tool.

        Args:
            name: Tool name
            arguments: Tool arguments as dictionary

        Returns:
            Tool execution result

        Raises:
            ValueError: If tool not found
        """
        if name not in self.tools:
            raise ValueError(f"Tool '{name}' not registered")

        try:
            log.info(f"Executing tool: {name} with args: {arguments}")
            result = self.tools[name](**arguments)
            log.debug(f"Tool {name} result: {result}")
            return result

        except Exception as e:
            log.error(f"Error executing tool {name}: {e}")
            raise


class VLLMToolCallingClient:
    """
    Client for calling vLLM models with tool/function calling support.

    This wraps the OpenAI-compatible API and handles the tool calling loop.

    Example:
        client = VLLMToolCallingClient(
            base_url="http://localhost:8000/v1",
            model="hermes-3-llama-3.1-8b"
        )

        tools = [...]
        result = client.chat_with_tools(
            messages=[{"role": "user", "content": "Search for HTTP nodes"}],
            tools=tools,
            tool_executor=executor
        )
    """

    def __init__(
        self,
        base_url: str,
        model: str,
        api_key: str = "EMPTY",
        max_iterations: int = 5
    ):
        """
        Initialize vLLM client.

        Args:
            base_url: vLLM API base URL (e.g., "http://localhost:8000/v1")
            model: Model name/ID
            api_key: API key (use "EMPTY" for local vLLM)
            max_iterations: Maximum tool calling iterations
        """
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )
        self.model = model
        self.max_iterations = max_iterations

    def chat_with_tools(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]],
        tool_executor: ToolExecutor,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> Dict[str, Any]:
        """
        Chat with tool calling support.

        Handles the full tool calling loop:
        1. Send messages + tools to model
        2. If model calls tools, execute them
        3. Add results back to conversation
        4. Repeat until model responds or max iterations reached

        Args:
            messages: Conversation messages
            tools: Tool definitions (OpenAI format)
            tool_executor: ToolExecutor with registered tools
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Dictionary with final response and metadata:
            {
                "content": str,              # Final response text
                "tool_calls": List[Dict],    # All tool calls made
                "iterations": int,           # Number of iterations
                "finish_reason": str         # How it finished
            }
        """
        conversation = messages.copy()
        all_tool_calls = []
        iteration = 0

        while iteration < self.max_iterations:
            iteration += 1
            log.debug(f"Tool calling iteration {iteration}/{self.max_iterations}")

            try:
                # Call the model with tools
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=conversation,
                    tools=tools,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

                message = response.choices[0].message
                finish_reason = response.choices[0].finish_reason

                # Add assistant message to conversation
                conversation.append({
                    "role": "assistant",
                    "content": message.content or "",
                    "tool_calls": message.tool_calls if message.tool_calls else None
                })

                # Check if model wants to call tools
                if message.tool_calls:
                    log.info(f"Model requested {len(message.tool_calls)} tool call(s)")

                    # Execute each tool call
                    for tool_call in message.tool_calls:
                        function_name = tool_call.function.name
                        function_args = json.loads(tool_call.function.arguments)

                        log.info(f"Calling tool: {function_name}")
                        all_tool_calls.append({
                            "name": function_name,
                            "arguments": function_args
                        })

                        try:
                            # Execute the tool
                            result = tool_executor.execute_tool(
                                function_name,
                                function_args
                            )

                            # Add tool result to conversation
                            conversation.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "name": function_name,
                                "content": json.dumps(result)
                            })

                        except Exception as e:
                            # Add error as tool result
                            log.error(f"Tool execution failed: {e}")
                            conversation.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "name": function_name,
                                "content": json.dumps({"error": str(e)})
                            })

                    # Continue loop to get next model response
                    continue

                else:
                    # Model provided final response
                    return {
                        "content": message.content or "",
                        "tool_calls": all_tool_calls,
                        "iterations": iteration,
                        "finish_reason": finish_reason,
                        "full_conversation": conversation
                    }

            except Exception as e:
                log.error(f"Error in chat_with_tools: {e}")
                return {
                    "content": f"Error: {str(e)}",
                    "tool_calls": all_tool_calls,
                    "iterations": iteration,
                    "finish_reason": "error",
                    "full_conversation": conversation
                }

        # Max iterations reached
        return {
            "content": "Maximum tool calling iterations reached.",
            "tool_calls": all_tool_calls,
            "iterations": iteration,
            "finish_reason": "max_iterations",
            "full_conversation": conversation
        }

    def chat_simple(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """
        Simple chat without tools.

        Args:
            messages: Conversation messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens

        Returns:
            Model response text
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            return response.choices[0].message.content or ""

        except Exception as e:
            log.error(f"Error in chat_simple: {e}")
            return f"Error: {str(e)}"


def format_tool_call_summary(tool_calls: List[Dict[str, Any]]) -> str:
    """
    Format a summary of tool calls for display.

    Args:
        tool_calls: List of tool call dictionaries

    Returns:
        Formatted string summary
    """
    if not tool_calls:
        return "No tools were called."

    lines = [f"Tools Called ({len(tool_calls)}):"]

    for i, call in enumerate(tool_calls, 1):
        name = call.get("name", "unknown")
        args = call.get("arguments", {})
        lines.append(f"  {i}. {name}({', '.join(f'{k}={v}' for k, v in args.items())})")

    return "\n".join(lines)
