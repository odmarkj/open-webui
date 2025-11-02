"""
title: n8n Workflow Agent
description: AI agent that can search n8n nodes, templates, create workflows, and execute them using tool calling
requirements: openai,requests
author: Assistant
version: 1.0.0
"""

from pydantic import BaseModel, Field
from typing import Optional, Callable, Any
import json
import asyncio

# Import shared libraries
from lib.n8n import N8nClient, get_n8n_tools
from lib.tool_calling import VLLMToolCallingClient, ToolExecutor, format_tool_call_summary


class Pipe:
    """
    n8n Workflow Agent Pipe

    This Pipe creates a custom AI model in Open WebUI that can interact with
    n8n API using tool calling. It demonstrates:

    - Registering a custom model in the UI
    - Setting up Pydantic-based tool schemas
    - Calling a local vLLM model with tool support
    - Executing tools (n8n API calls)
    - Managing multi-turn tool calling loops

    The agent can:
    - Search for available n8n nodes
    - Find workflow templates
    - Create new workflows
    - Execute workflows

    This serves as a template for building complex AI agents that perform
    multi-step operations through tool calling.
    """

    class Valves(BaseModel):
        """Configuration for the n8n Workflow Agent."""

        # vLLM Configuration
        vllm_base_url: str = Field(
            default="http://localhost:8000/v1",
            description="Base URL for vLLM API (OpenAI-compatible endpoint)"
        )
        vllm_model: str = Field(
            default="hermes-3-llama-3.1-8b",
            description="Model name/ID in vLLM"
        )
        vllm_api_key: str = Field(
            default="EMPTY",
            description="API key for vLLM (use 'EMPTY' for local instances)"
        )

        # n8n Configuration
        n8n_base_url: str = Field(
            default="http://localhost:5678",
            description="Base URL for n8n instance"
        )
        n8n_api_key: str = Field(
            default="",
            description="n8n API key (optional, leave empty if not using auth)"
        )

        # Agent Configuration
        max_tool_iterations: int = Field(
            default=5,
            description="Maximum number of tool calling iterations",
            ge=1,
            le=10
        )
        temperature: float = Field(
            default=0.7,
            description="LLM temperature for responses",
            ge=0.0,
            le=2.0
        )
        max_tokens: int = Field(
            default=2000,
            description="Maximum tokens to generate",
            ge=100,
            le=8000
        )
        show_tool_calls: bool = Field(
            default=True,
            description="Show tool call details in responses"
        )

    def __init__(self):
        """Initialize the n8n Workflow Agent."""
        self.name = "n8n Workflow Agent"
        self.valves = self.Valves()

        # These will be initialized in pipe() method
        self.vllm_client: Optional[VLLMToolCallingClient] = None
        self.n8n_client: Optional[N8nClient] = None
        self.tool_executor: Optional[ToolExecutor] = None

    def _initialize_clients(self):
        """Initialize vLLM and n8n clients with current valve settings."""

        # Initialize vLLM client
        self.vllm_client = VLLMToolCallingClient(
            base_url=self.valves.vllm_base_url,
            model=self.valves.vllm_model,
            api_key=self.valves.vllm_api_key,
            max_iterations=self.valves.max_tool_iterations
        )

        # Initialize n8n client
        api_key = self.valves.n8n_api_key if self.valves.n8n_api_key else None
        self.n8n_client = N8nClient(
            base_url=self.valves.n8n_base_url,
            api_key=api_key
        )

        # Initialize tool executor and register n8n tools
        self.tool_executor = ToolExecutor()
        self._register_tools()

    def _register_tools(self):
        """Register n8n API tools with the executor."""

        # Tool: search_nodes
        def search_nodes(query: str, limit: int = 10):
            """Search for n8n nodes."""
            nodes = self.n8n_client.search_nodes(query, limit)
            return {
                "nodes": nodes,
                "count": len(nodes),
                "query": query
            }

        # Tool: search_templates
        def search_templates(query: str, limit: int = 5):
            """Search for workflow templates."""
            templates = self.n8n_client.search_templates(query, limit)
            return {
                "templates": templates,
                "count": len(templates),
                "query": query
            }

        # Tool: create_workflow
        def create_workflow(name: str, nodes: list, description: str = None):
            """Create a new workflow."""
            result = self.n8n_client.create_workflow(name, nodes, description)
            if result:
                return {
                    "success": True,
                    "workflow_id": result.get('id'),
                    "name": result.get('name'),
                    "message": f"Workflow '{name}' created successfully"
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to create workflow"
                }

        # Tool: execute_workflow
        def execute_workflow(workflow_id: str, input_data: dict = None):
            """Execute a workflow."""
            result = self.n8n_client.execute_workflow(workflow_id, input_data)
            if result:
                return {
                    "success": True,
                    "execution_id": result.get('executionId'),
                    "status": result.get('status'),
                    "message": "Workflow executed successfully"
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to execute workflow"
                }

        # Register all tools
        self.tool_executor.register_tool("search_nodes", search_nodes)
        self.tool_executor.register_tool("search_templates", search_templates)
        self.tool_executor.register_tool("create_workflow", create_workflow)
        self.tool_executor.register_tool("execute_workflow", execute_workflow)

    async def pipe(
        self,
        body: dict,
        __user__: dict,
        __event_emitter__: Optional[Callable[[dict], Any]] = None
    ) -> str:
        """
        Process user messages with tool calling support.

        This is the main entry point called by Open WebUI.

        Args:
            body: Request body containing messages and other parameters
            __user__: User information dictionary
            __event_emitter__: Optional event emitter for status updates

        Returns:
            str: Response from the agent
        """

        # ============================================================================
        # EVENT EMITTER EXAMPLE 1: Initial Status Update
        # ============================================================================
        # Shows a processing status that's not done yet
        if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": "Initializing n8n Workflow Agent...",
                        "done": False
                    },
                }
            )

        # Initialize clients if not already done
        if self.vllm_client is None:
            self._initialize_clients()

            # ========================================================================
            # EVENT EMITTER EXAMPLE 2: Completion Status Update
            # ========================================================================
            # Shows a status that's completed (done: True)
            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": "Clients initialized successfully",
                            "done": True
                        },
                    }
                )

        # Extract messages from body
        messages = body.get("messages", [])

        if not messages:
            return "No messages provided."

        # ============================================================================
        # EVENT EMITTER EXAMPLE 3: Progress Status
        # ============================================================================
        # Shows ongoing work
        if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": "Preparing conversation with AI model...",
                        "done": False
                    },
                }
            )

        # Add system message if not present
        if not messages or messages[0].get("role") != "system":
            system_message = {
                "role": "system",
                "content": (
                    "You are an n8n workflow automation assistant. You can help users "
                    "search for n8n nodes, find workflow templates, create workflows, "
                    "and execute them. Use the available tools to accomplish tasks. "
                    "Always explain what you're doing and provide clear results."
                )
            }
            messages = [system_message] + messages

        # Get n8n tool definitions
        tools = get_n8n_tools()

        try:
            # ========================================================================
            # EVENT EMITTER EXAMPLE 4: Message Update (Streaming Text)
            # ========================================================================
            # Shows a partial message being built
            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "message",
                        "data": {
                            "content": "🤖 Processing your request with tool calling..."
                        },
                    }
                )

            # ========================================================================
            # EVENT EMITTER EXAMPLE 5: Citation (Source References)
            # ========================================================================
            # Shows sources or references being used
            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "citation",
                        "data": {
                            "document": [f"n8n API: {self.valves.n8n_base_url}"],
                            "metadata": [{"source": "n8n_instance"}],
                            "source": {"name": "n8n API"}
                        },
                    }
                )

            # ========================================================================
            # EVENT EMITTER EXAMPLE 6: Status with Tool Information
            # ========================================================================
            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": f"Calling vLLM model with {len(tools)} available tools...",
                            "done": False
                        },
                    }
                )

            # Call vLLM with tool support
            result = self.vllm_client.chat_with_tools(
                messages=messages,
                tools=tools,
                tool_executor=self.tool_executor,
                temperature=self.valves.temperature,
                max_tokens=self.valves.max_tokens
            )

            # ========================================================================
            # EVENT EMITTER EXAMPLE 7: Tool Call Notification
            # ========================================================================
            # Notify about tool calls that were made
            if __event_emitter__ and result.get("tool_calls"):
                tool_count = len(result["tool_calls"])
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": f"Executed {tool_count} tool call(s) successfully",
                            "done": True
                        },
                    }
                )

                # Add citation for each tool call
                for tool_call in result["tool_calls"]:
                    await __event_emitter__(
                        {
                            "type": "citation",
                            "data": {
                                "document": [f"Tool: {tool_call['name']}"],
                                "metadata": [{"tool": tool_call['name'], "args": tool_call['arguments']}],
                                "source": {"name": f"n8n API - {tool_call['name']}"}
                            },
                        }
                    )

            # Format response
            response = result.get("content", "")

            # Optionally append tool call summary
            if self.valves.show_tool_calls and result.get("tool_calls"):
                tool_summary = format_tool_call_summary(result["tool_calls"])
                response += f"\n\n---\n**Debug Info:**\n{tool_summary}\n"
                response += f"Iterations: {result.get('iterations', 0)}\n"
                response += f"Finish: {result.get('finish_reason', 'unknown')}"

            # ========================================================================
            # EVENT EMITTER EXAMPLE 8: Final Completion Status
            # ========================================================================
            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": "Response generated successfully",
                            "done": True
                        },
                    }
                )

            return response

        except Exception as e:
            error_msg = f"Error in n8n Workflow Agent: {str(e)}"
            print(error_msg)  # Log to console

            # ========================================================================
            # EVENT EMITTER EXAMPLE 9: Error Status
            # ========================================================================
            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": f"Error: {str(e)}",
                            "done": True
                        },
                    }
                )

            return f"❌ {error_msg}\n\nPlease check:\n" \
                   f"- vLLM is running at {self.valves.vllm_base_url}\n" \
                   f"- n8n is running at {self.valves.n8n_base_url}\n" \
                   f"- Model '{self.valves.vllm_model}' is loaded in vLLM\n" \
                   f"- Configuration in Valves is correct"
