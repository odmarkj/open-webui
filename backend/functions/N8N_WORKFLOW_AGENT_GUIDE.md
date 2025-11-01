# n8n Workflow Agent Guide

This guide explains how to use and customize the **n8n Workflow Agent** - a complete example of building an AI agent with tool calling capabilities in Open WebUI.

## Overview

The n8n Workflow Agent demonstrates:

✅ **Model Registration** - Appears as a selectable model in Open WebUI
✅ **Tool Calling** - Uses vLLM with OpenAI-compatible function calling
✅ **Pydantic Schemas** - Type-safe tool definitions and validation
✅ **Multi-Step Operations** - Handles complex workflows with multiple tool calls
✅ **API Integration** - Connects to n8n API for workflow automation

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Open WebUI                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  n8n Workflow Agent (Pipe Function)                   │  │
│  │                                                         │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │  VLLMToolCallingClient                          │  │  │
│  │  │  - Manages conversation loop                    │  │  │
│  │  │  - Calls vLLM with tools                        │  │  │
│  │  │  - Parses tool calls                            │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  │                                                         │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │  ToolExecutor                                   │  │  │
│  │  │  - Registers tools                              │  │  │
│  │  │  - Executes tool functions                      │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  │                                                         │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │  N8nClient                                      │  │  │
│  │  │  - search_nodes()                               │  │  │
│  │  │  - search_templates()                           │  │  │
│  │  │  - create_workflow()                            │  │  │
│  │  │  - execute_workflow()                           │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴──────────┐
                    │                    │
            ┌───────▼───────┐    ┌──────▼──────┐
            │  vLLM Server  │    │  n8n Server │
            │  (localhost:  │    │  (localhost:│
            │   8000)       │    │   5678)     │
            └───────────────┘    └─────────────┘
```

## Setup

### Prerequisites

1. **vLLM Server** with a tool-calling capable model (e.g., Hermes-3)
2. **n8n Instance** with API access
3. **Open WebUI** with this function installed

### Step 1: Install vLLM

```bash
# Install vLLM
pip install vllm

# Download a tool-calling capable model (e.g., Hermes-3-Llama-3.1-8B)
# This will be done automatically on first run
```

### Step 2: Start vLLM Server

```bash
# Start vLLM with Hermes-3 model
vllm serve NousResearch/Hermes-3-Llama-3.1-8B \
    --host 0.0.0.0 \
    --port 8000 \
    --enable-auto-tool-choice \
    --tool-call-parser hermes

# Or use a GGUF model with llama.cpp
# See vLLM documentation for more options
```

**Verify it's running:**
```bash
curl http://localhost:8000/v1/models
```

### Step 3: Setup n8n

```bash
# Using Docker
docker run -it --rm \
    -p 5678:5678 \
    -v ~/.n8n:/home/node/.n8n \
    docker.n8n.io/n8nio/n8n

# Or install locally
npm install -g n8n
n8n start
```

**Access n8n:** http://localhost:5678

**Get API Key (Optional):**
1. Go to n8n Settings → API
2. Generate an API key
3. Add it to the Valves configuration

### Step 4: Deploy Function

Copy the example to your functions directory:

```bash
cd backend/functions
cp examples/n8n_workflow_agent.py ./my_n8n_agent.py
```

Restart Open WebUI - the model will appear in your model selector!

### Step 5: Configure Valves

In Open WebUI:
1. Select the "n8n Workflow Agent" model
2. Click the settings icon
3. Configure the Valves:

```
vllm_base_url: http://localhost:8000/v1
vllm_model: NousResearch/Hermes-3-Llama-3.1-8B
n8n_base_url: http://localhost:5678
n8n_api_key: [your-api-key-or-leave-empty]
```

## Usage

### Example 1: Search for Nodes

```
You: What HTTP nodes are available in n8n?

Agent: Let me search for HTTP nodes in n8n.

[Calls: search_nodes(query="http", limit=10)]

I found 5 HTTP-related nodes:
1. HTTP Request - Makes HTTP requests to APIs
2. Webhook - Receives HTTP webhooks
3. HTTP Request Tool - Advanced HTTP client
...
```

### Example 2: Create a Workflow

```
You: Create a workflow that fetches data from an API and sends it to Slack

Agent: I'll help you create that workflow. Let me first search for the necessary nodes.

[Calls: search_nodes(query="http")]
[Calls: search_nodes(query="slack")]
[Calls: create_workflow(name="API to Slack", nodes=["HTTP Request", "Slack"])]

I've created a workflow called "API to Slack" with the following nodes:
- HTTP Request (for fetching API data)
- Slack (for sending messages)

Workflow ID: 12345
```

### Example 3: Multi-Step Operation

```
You: Find a template for sending emails, then create a similar workflow

Agent: Let me search for email templates first.

[Calls: search_templates(query="email")]

I found a template called "Daily Email Report". Let me create a similar workflow for you.

[Calls: search_nodes(query="email")]
[Calls: create_workflow(name="My Email Workflow", nodes=["Schedule", "Email Send"])]

I've created a workflow based on the template...
```

## Customization

### Adding New Tools

**1. Define the Pydantic Model**

In `lib/n8n.py`:

```python
class GetWorkflowParams(BaseModel):
    """Parameters for getting workflow details."""
    workflow_id: str = Field(
        description="ID of the workflow to retrieve"
    )
```

**2. Add Tool Definition**

In `lib/n8n.py` → `get_n8n_tools()`:

```python
{
    "type": "function",
    "function": {
        "name": "get_workflow",
        "description": "Get details of a specific workflow",
        "parameters": GetWorkflowParams.model_json_schema()
    }
}
```

**3. Implement the Tool Function**

In your Pipe's `_register_tools()` method:

```python
def get_workflow(workflow_id: str):
    """Get workflow details."""
    result = self.n8n_client.get_workflow(workflow_id)
    return {"workflow": result}

self.tool_executor.register_tool("get_workflow", get_workflow)
```

**4. Add n8n API Method**

In `lib/n8n.py` → `N8nClient`:

```python
def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
    """Get workflow by ID."""
    try:
        response = self.session.get(
            f"{self.base_url}/api/v1/workflows/{workflow_id}",
            timeout=10
        )
        response.raise_for_status()
        return response.json().get('data')
    except requests.exceptions.RequestException as e:
        log.error(f"Error getting workflow: {e}")
        return None
```

### Using Different Models

The agent works with any OpenAI-compatible model that supports tool calling:

**Hermes-3 (Recommended):**
```python
vllm_model: "NousResearch/Hermes-3-Llama-3.1-8B"
```

**Llama 3.1:**
```python
vllm_model: "meta-llama/Llama-3.1-8B-Instruct"
```

**Mistral:**
```python
vllm_model: "mistralai/Mistral-7B-Instruct-v0.3"
```

### Adjusting Behavior

**More Detailed Responses:**
```python
max_tokens: 4000
temperature: 0.8
```

**Stricter/Deterministic:**
```python
temperature: 0.1
max_tokens: 1000
```

**More Tool Calls:**
```python
max_tool_iterations: 10
```

## Advanced Patterns

### Sequential Workflow Creation

```python
# In your Pipe, add a complex tool that chains operations:

def create_full_workflow(name: str, trigger_type: str, actions: list):
    """Create a complete workflow with trigger and actions."""

    # 1. Search for trigger node
    trigger_nodes = self.n8n_client.search_nodes(trigger_type)

    # 2. Search for action nodes
    action_node_names = []
    for action in actions:
        nodes = self.n8n_client.search_nodes(action)
        if nodes:
            action_node_names.append(nodes[0]['name'])

    # 3. Create workflow
    all_nodes = [trigger_nodes[0]['name']] + action_node_names
    result = self.n8n_client.create_workflow(name, all_nodes)

    # 4. Execute it
    if result:
        exec_result = self.n8n_client.execute_workflow(result['id'])
        return {"workflow": result, "execution": exec_result}

    return {"error": "Failed to create workflow"}
```

### Error Recovery

```python
def search_nodes_with_retry(query: str, limit: int = 10):
    """Search with fallback logic."""
    results = self.n8n_client.search_nodes(query, limit)

    if not results:
        # Try alternative query
        alternative = query.replace("_", " ")
        results = self.n8n_client.search_nodes(alternative, limit)

    return {"nodes": results, "query": query}
```

### State Management

```python
class Pipe:
    def __init__(self):
        self.name = "n8n Agent"
        self.valves = self.Valves()

        # Maintain state across calls
        self.created_workflows = []
        self.last_search_results = {}

    def _register_tools(self):
        def create_workflow(name: str, nodes: list, description: str = None):
            result = self.n8n_client.create_workflow(name, nodes, description)
            if result:
                # Store for later reference
                self.created_workflows.append(result['id'])
            return result

        self.tool_executor.register_tool("create_workflow", create_workflow)
```

## Troubleshooting

### Error: "Connection refused" to vLLM

**Solution:**
1. Check vLLM is running: `curl http://localhost:8000/v1/models`
2. Verify the URL in Valves matches your vLLM server
3. Check firewall rules

### Error: "Model not found"

**Solution:**
1. List available models: `curl http://localhost:8000/v1/models`
2. Update `vllm_model` in Valves to match exactly
3. Restart vLLM if you just loaded the model

### Tool Calls Not Working

**Solution:**
1. Verify your model supports tool calling (Hermes-3, Llama 3.1, etc.)
2. Check vLLM started with `--enable-auto-tool-choice`
3. Look for errors in vLLM logs
4. Try with `temperature: 0.1` for more deterministic behavior

### n8n API Errors

**Solution:**
1. Check n8n is running: `curl http://localhost:5678`
2. Verify API key if using authentication
3. Check n8n API documentation for correct endpoints
4. Review n8n logs for errors

### No Response from Agent

**Solution:**
1. Check Open WebUI logs for errors
2. Verify all imports are working (no `ModuleNotFoundError`)
3. Test with a simple message first
4. Check `show_tool_calls: true` in Valves to see debug info

## Testing

### Manual Testing

1. **Simple Query:**
   ```
   You: Hello
   Agent: [Should respond normally]
   ```

2. **Tool Call:**
   ```
   You: Search for HTTP nodes
   Agent: [Should call search_nodes tool]
   ```

3. **Multi-Step:**
   ```
   You: Find Slack nodes, then create a workflow
   Agent: [Should make multiple tool calls]
   ```

### Automated Testing

Create a test file:

```python
# test_n8n_agent.py
import sys
sys.path.insert(0, '/path/to/backend/functions')

from examples.n8n_workflow_agent import Pipe

def test_agent():
    pipe = Pipe()

    # Configure for testing
    pipe.valves.vllm_base_url = "http://localhost:8000/v1"
    pipe.valves.n8n_base_url = "http://localhost:5678"

    body = {
        "messages": [
            {"role": "user", "content": "Search for HTTP nodes"}
        ]
    }

    response = pipe.pipe(body, {"id": "test", "name": "Test"})
    print(response)
    assert "HTTP" in response

if __name__ == "__main__":
    test_agent()
```

## Next Steps

### Build Your Own Agent

1. **Copy the template:**
   ```bash
   cp examples/n8n_workflow_agent.py my_custom_agent.py
   ```

2. **Modify the tools:**
   - Update `lib/n8n.py` with your API client
   - Define your Pydantic models
   - Add your tool definitions

3. **Register tools:**
   - Implement tool functions in `_register_tools()`
   - Connect to your APIs/services

4. **Test iteratively:**
   - Use Open WebUI to test conversations
   - Refine prompts and tool descriptions
   - Adjust parameters in Valves

### Expand n8n Integration

**More Tools:**
- List all workflows
- Update workflow
- Delete workflow
- Get execution history
- Activate/deactivate workflows

**Advanced Features:**
- Node configuration (set parameters)
- Connection mapping (link nodes together)
- Credential management
- Workflow versioning

### Use Other APIs

The same pattern works for any API:
- **GitHub**: Create repos, manage issues, PRs
- **Jira**: Create tickets, update status
- **Slack**: Send messages, create channels
- **Email**: Send emails, manage inbox
- **Database**: Query, insert, update data

## Resources

- **vLLM Documentation**: https://docs.vllm.ai/
- **n8n API Docs**: https://docs.n8n.io/api/
- **Hermes Models**: https://huggingface.co/NousResearch
- **OpenAI Function Calling**: https://platform.openai.com/docs/guides/function-calling

## Example Output

```
User: I need a workflow that gets weather data and sends it to Slack daily

n8n Workflow Agent:
I'll help you create a weather-to-Slack workflow. Let me start by finding the necessary nodes.

[Searching for weather-related nodes...]

Found:
- OpenWeatherMap (for fetching weather data)
- Schedule Trigger (for daily execution)
- Slack (for sending messages)

[Creating workflow...]

✅ Successfully created workflow "Daily Weather to Slack"!

Workflow ID: wx-12345
Nodes configured:
1. Schedule Trigger - Set to run daily at 8 AM
2. OpenWeatherMap - Fetches weather for your location
3. Slack - Sends formatted weather report

The workflow is ready! You can:
- View it in n8n: http://localhost:5678/workflow/wx-12345
- Activate it to start daily reports
- Customize the message format
- Add more locations

Would you like me to execute it now to test?

---
Debug Info:
Tools Called (3):
  1. search_nodes(query=weather, limit=10)
  2. search_nodes(query=slack, limit=10)
  3. create_workflow(name=Daily Weather to Slack, nodes=['Schedule', 'OpenWeatherMap', 'Slack'])
Iterations: 2
Finish: stop
```

---

**Ready to build your AI agent!** 🚀

This template provides everything you need to create sophisticated AI agents that can interact with external APIs through tool calling. Customize it for your specific use case and iterate through Open WebUI's chat interface.
