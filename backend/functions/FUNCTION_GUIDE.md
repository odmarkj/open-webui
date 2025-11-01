# Open WebUI Function Development Guide

This guide helps you understand and create functions for Open WebUI. Functions extend Open WebUI's capabilities by adding custom logic, integrations, and behaviors.

## Table of Contents

- [What are Functions?](#what-are-functions)
- [Function Types](#function-types)
- [Getting Started](#getting-started)
- [Pipe Functions](#pipe-functions)
- [Filter Functions](#filter-functions)
- [Action Functions](#action-functions)
- [Configuration with Valves](#configuration-with-valves)
- [Advanced Features](#advanced-features)
- [Best Practices](#best-practices)

---

## What are Functions?

Functions are Python-based plugins that extend Open WebUI's functionality. They run server-side and can:

- Create custom AI models or agents
- Modify chat messages before/after processing
- Add interactive buttons to chat messages
- Integrate with external APIs and services
- Process and transform data in real-time

**Three Types of Functions:**

1. **Pipe** - Custom models/agents that appear as selectable models
2. **Filter** - Hooks that modify data flowing through the system
3. **Action** - Buttons that trigger custom operations on messages

---

## Function Types

### Quick Comparison

| Type | Purpose | Visibility | Use Case |
|------|---------|------------|----------|
| **Pipe** | Custom model/agent | Shows as model in dropdown | RAG, external LLM integration, custom logic |
| **Filter** | Data transformation | Works in background | Content moderation, translation, logging |
| **Action** | Interactive button | Button on messages | Export, analyze, regenerate |

### When to Use Each Type

**Use Pipe when:**
- Creating a custom AI agent
- Integrating external LLM providers (Claude, Gemini, etc.)
- Building RAG systems
- Implementing complex workflows

**Use Filter when:**
- Modifying messages before they reach the model (inlet)
- Processing model responses (outlet)
- Logging or monitoring conversations
- Content filtering or moderation

**Use Action when:**
- Adding interactive features to messages
- Providing one-click operations (translate, summarize, etc.)
- Triggering external workflows
- Collecting user feedback

---

## Getting Started

### File Structure

Create a `.py` file in `backend/functions/`:

```
backend/functions/
├── my_pipe.py         # Your Pipe function
├── my_filter.py       # Your Filter function
└── my_action.py       # Your Action function
```

### Basic Template

Every function needs:

```python
"""
title: Function Title
description: What this function does
requirements: package1,package2
"""

class Pipe:  # or Filter, or Action
    def __init__(self):
        self.name = "My Function"

    # Function-specific methods here
```

### Frontmatter

The docstring at the top defines metadata:

```python
"""
title: My Custom Function
description: Does something useful
requirements: requests,openai
author: Your Name
version: 1.0.0
"""
```

---

## Pipe Functions

Pipes create custom models that appear in the model selector.

### Basic Structure

```python
"""
title: Echo Pipe
description: Simple echo function
"""

class Pipe:
    def __init__(self):
        self.name = "Echo Bot"

    def pipe(
        self,
        body: dict,
        __user__: dict,
    ) -> str:
        """
        Main processing method.

        Args:
            body: Request containing messages, model, etc.
            __user__: User information (id, name, email, role)

        Returns:
            str or dict: Response content
        """
        messages = body.get("messages", [])

        if messages:
            last_message = messages[-1]["content"]
            return f"You said: {last_message}"

        return "No message to echo"
```

### Accessing Request Data

The `body` dictionary contains:

```python
{
    "messages": [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"}
    ],
    "model": "model_id",
    "stream": True/False,
    "temperature": 0.7,
    # ... other parameters
}
```

### External API Integration

```python
"""
title: OpenAI Pipe
description: Calls OpenAI API
requirements: openai
"""

from openai import OpenAI
from pydantic import BaseModel, Field

class Pipe:
    class Valves(BaseModel):
        OPENAI_API_KEY: str = Field(default="", description="OpenAI API Key")
        MODEL: str = Field(default="gpt-4", description="Model to use")

    def __init__(self):
        self.valves = self.Valves()

    def pipe(self, body: dict, __user__: dict) -> str:
        client = OpenAI(api_key=self.valves.OPENAI_API_KEY)

        response = client.chat.completions.create(
            model=self.valves.MODEL,
            messages=body["messages"]
        )

        return response.choices[0].message.content
```

### Streaming Responses

```python
def pipe(self, body: dict, __user__: dict):
    """
    Stream responses for real-time display.
    """
    # Yield chunks of text
    for word in "Hello from streaming pipe".split():
        yield word + " "
```

### Manifold Pipes

Manifolds allow one Pipe to provide multiple models:

```python
"""
title: OpenAI Manifold
description: Access all OpenAI models
requirements: openai
"""

from openai import OpenAI
from pydantic import BaseModel, Field

class Pipe:
    class Valves(BaseModel):
        OPENAI_API_KEY: str = Field(default="")

    def __init__(self):
        self.valves = self.Valves()
        self.name = "OpenAI"

    def pipes(self) -> list[dict]:
        """
        Return list of available models.
        Called when the Pipe is loaded.
        """
        return [
            {"id": "gpt-4", "name": "GPT-4"},
            {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo"},
            {"id": "gpt-4-turbo", "name": "GPT-4 Turbo"},
        ]

    def pipe(self, body: dict, __user__: dict) -> str:
        model_id = body.get("model", "gpt-4")

        client = OpenAI(api_key=self.valves.OPENAI_API_KEY)

        response = client.chat.completions.create(
            model=model_id,
            messages=body["messages"]
        )

        return response.choices[0].message.content
```

---

## Filter Functions

Filters modify data as it flows through the system.

### Basic Structure

```python
"""
title: Content Filter
description: Filters inappropriate content
"""

class Filter:
    def __init__(self):
        self.name = "Content Filter"

    def inlet(self, body: dict, __user__: dict) -> dict:
        """
        Modify user input before it reaches the model.

        Args:
            body: Request body with messages
            __user__: User information

        Returns:
            dict: Modified body
        """
        print(f"Inlet called: {body}")
        return body

    def outlet(self, body: dict, __user__: dict) -> dict:
        """
        Modify model output before it reaches the user.

        Args:
            body: Response body with messages
            __user__: User information

        Returns:
            dict: Modified body
        """
        print(f"Outlet called: {body}")
        return body
```

### Modifying Messages

```python
class Filter:
    def inlet(self, body: dict, __user__: dict) -> dict:
        """Add system message to all requests."""
        messages = body.get("messages", [])

        # Prepend system message
        system_msg = {
            "role": "system",
            "content": "You are a helpful assistant. Be concise."
        }

        body["messages"] = [system_msg] + messages
        return body

    def outlet(self, body: dict, __user__: dict) -> dict:
        """Convert responses to uppercase."""
        messages = body.get("messages", [])

        for message in messages:
            if message.get("role") == "assistant":
                message["content"] = message["content"].upper()

        return body
```

### Real-Time Streaming

```python
class Filter:
    def inlet(self, body: dict, __user__: dict) -> dict:
        """Process incoming request."""
        return body

    async def outlet(self, body: dict, __user__: dict) -> dict:
        """Process final response."""
        return body

    async def stream(self, event: dict, __user__: dict) -> dict:
        """
        Process streamed chunks in real-time.

        Args:
            event: Stream event with chunk data
            __user__: User information

        Returns:
            dict: Modified event
        """
        # Modify streaming chunks
        if "content" in event:
            event["content"] = event["content"].upper()

        return event
```

### Enabling Filters

**Important:** Filters must be enabled globally or assigned to specific models:

1. Navigate to **Workspace → Models**
2. Select a model
3. Assign your filter to that model

Or enable globally in the filter settings.

---

## Action Functions

Actions add interactive buttons to chat messages.

### Basic Structure

```python
"""
title: Translate Action
description: Translates message to another language
requirements: googletrans
"""

from googletrans import Translator

class Action:
    def __init__(self):
        self.name = "Translate"

    async def action(
        self,
        body: dict,
        __user__: dict,
        __event_emitter__=None,
        __event_call__=None,
    ) -> dict:
        """
        Execute action when button is clicked.

        Args:
            body: Message data
            __user__: User information
            __event_emitter__: Function to emit events
            __event_call__: Function to request user input

        Returns:
            dict: Result with message content
        """
        message = body.get("messages", [{}])[-1].get("content", "")

        translator = Translator()
        translated = translator.translate(message, dest='es')

        return {
            "content": translated.text
        }
```

### Using Event Emitter

Send real-time updates to the user:

```python
import asyncio

class Action:
    async def action(
        self,
        body: dict,
        __user__: dict,
        __event_emitter__=None,
        __event_call__=None,
    ):
        # Show status update
        if __event_emitter__:
            await __event_emitter__({
                "type": "status",
                "data": {"description": "Processing...", "done": False}
            })

        # Do work
        await asyncio.sleep(2)

        # Show completion
        if __event_emitter__:
            await __event_emitter__({
                "type": "status",
                "data": {"description": "Done!", "done": True}
            })

        return {"content": "Action completed!"}
```

### Requesting User Input

```python
class Action:
    async def action(
        self,
        body: dict,
        __user__: dict,
        __event_emitter__=None,
        __event_call__=None,
    ):
        if __event_call__:
            # Request confirmation
            response = await __event_call__({
                "type": "confirmation",
                "data": {
                    "title": "Confirm Action",
                    "message": "Are you sure you want to proceed?"
                }
            })

            if response.get("confirmed"):
                return {"content": "Action confirmed!"}
            else:
                return {"content": "Action cancelled."}

        return {"content": "No event call available"}
```

### Event Types

**Status Events** (one-way notifications):
```python
await __event_emitter__({
    "type": "status",
    "data": {"description": "Processing...", "done": False}
})
```

**Message Events** (add to chat):
```python
await __event_emitter__({
    "type": "message",
    "data": {"content": "Here's the result..."}
})
```

**Input Requests** (get user response):
```python
response = await __event_call__({
    "type": "input",
    "data": {
        "title": "Enter Value",
        "message": "Please provide input:",
        "placeholder": "Type here..."
    }
})
user_input = response.get("content", "")
```

**Confirmation Requests**:
```python
response = await __event_call__({
    "type": "confirmation",
    "data": {
        "title": "Confirm",
        "message": "Are you sure?"
    }
})
confirmed = response.get("confirmed", False)
```

---

## Configuration with Valves

Valves provide configurable parameters for your functions.

### Basic Valves

```python
from pydantic import BaseModel, Field

class Pipe:
    class Valves(BaseModel):
        """Admin-configurable settings."""

        api_key: str = Field(
            default="",
            description="API key for external service"
        )

        temperature: float = Field(
            default=0.7,
            ge=0.0,
            le=2.0,
            description="Temperature for response generation"
        )

        max_tokens: int = Field(
            default=1000,
            description="Maximum tokens in response"
        )

    def __init__(self):
        self.valves = self.Valves()

    def pipe(self, body: dict, __user__: dict) -> str:
        # Access valve values
        api_key = self.valves.api_key
        temp = self.valves.temperature

        return f"Using temperature: {temp}"
```

### User-Specific Valves

```python
class Pipe:
    class Valves(BaseModel):
        """Admin settings."""
        api_key: str = Field(default="")

    class UserValves(BaseModel):
        """User-specific settings."""
        preferred_model: str = Field(
            default="gpt-4",
            description="Your preferred model"
        )

        style: str = Field(
            default="concise",
            description="Response style (concise, detailed, creative)"
        )

    def __init__(self):
        self.valves = self.Valves()

    def pipe(self, body: dict, __user__: dict) -> str:
        # Access user-specific valves
        user_valves = __user__.get("valves", {})
        preferred_model = user_valves.get("preferred_model", "gpt-4")
        style = user_valves.get("style", "concise")

        return f"Using {preferred_model} with {style} style"
```

### Valve Field Types

```python
from pydantic import BaseModel, Field

class Valves(BaseModel):
    # String
    api_key: str = Field(default="", description="API Key")

    # Integer with range
    max_retries: int = Field(default=3, ge=1, le=10, description="Max retries")

    # Float with range
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)

    # Boolean
    enable_logging: bool = Field(default=True, description="Enable logging")

    # Enum (dropdown)
    mode: str = Field(
        default="standard",
        enum=["standard", "advanced", "expert"],
        description="Operation mode"
    )

    # List
    allowed_models: list[str] = Field(
        default=["gpt-4", "gpt-3.5-turbo"],
        description="Allowed models"
    )
```

### Security Best Practices

**Never hardcode secrets:**

```python
# ❌ BAD
class Pipe:
    def __init__(self):
        self.api_key = "sk-1234567890"  # DON'T DO THIS!

# ✅ GOOD
class Pipe:
    class Valves(BaseModel):
        api_key: str = Field(default="", description="API Key")

    def __init__(self):
        self.valves = self.Valves()

    def pipe(self, body: dict, __user__: dict) -> str:
        api_key = self.valves.api_key  # Configured via UI
```

---

## Advanced Features

### Lifecycle Hooks

```python
class Pipe:
    def __init__(self):
        """Called when function is loaded."""
        self.name = "My Pipe"
        print("Pipe initialized")

    async def on_startup(self):
        """Called when application starts."""
        print("Application starting...")
        # Initialize connections, load models, etc.

    async def on_shutdown(self):
        """Called when application shuts down."""
        print("Application shutting down...")
        # Close connections, cleanup resources
```

### Error Handling

```python
class Pipe:
    def pipe(self, body: dict, __user__: dict) -> str:
        try:
            # Your logic here
            result = self.process_message(body)
            return result

        except KeyError as e:
            return f"Missing required field: {e}"

        except Exception as e:
            # Log error
            print(f"Error in pipe: {e}")
            return f"An error occurred: {str(e)}"
```

### Async Operations

```python
import asyncio
import aiohttp

class Pipe:
    async def pipe(self, body: dict, __user__: dict) -> str:
        """Async pipe for I/O operations."""

        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.example.com/data") as resp:
                data = await resp.json()
                return str(data)
```

### Context and State

```python
class Pipe:
    def __init__(self):
        # Instance state persists across calls
        self.call_count = 0
        self.cache = {}

    def pipe(self, body: dict, __user__: dict) -> str:
        self.call_count += 1

        # Access user information
        user_id = __user__["id"]
        user_name = __user__["name"]
        user_role = __user__["role"]  # "admin" or "user"

        return f"Call #{self.call_count} by {user_name} ({user_role})"
```

---

## Best Practices

### 1. Structure Your Code

```python
"""
Clear frontmatter with all metadata.
"""

from pydantic import BaseModel, Field
from typing import Optional

class Pipe:
    """Clear class docstring."""

    class Valves(BaseModel):
        """Valves docstring."""
        pass

    def __init__(self):
        """Initialize resources."""
        pass

    def pipe(self, body: dict, __user__: dict) -> str:
        """
        Clear method docstring.

        Args:
            body: Request body
            __user__: User info

        Returns:
            str: Response
        """
        pass
```

### 2. Validate Input

```python
def pipe(self, body: dict, __user__: dict) -> str:
    # Validate required fields
    messages = body.get("messages")
    if not messages:
        return "Error: No messages provided"

    # Validate valve configuration
    if not self.valves.api_key:
        return "Error: API key not configured"

    # Process...
    return result
```

### 3. Handle Errors Gracefully

```python
def pipe(self, body: dict, __user__: dict) -> str:
    try:
        result = self.process(body)
        return result
    except requests.exceptions.Timeout:
        return "Request timed out. Please try again."
    except requests.exceptions.RequestException as e:
        return f"API error: {str(e)}"
    except Exception as e:
        print(f"Unexpected error: {e}")
        return "An unexpected error occurred."
```

### 4. Use Type Hints

```python
from typing import Dict, List, Optional, Union

def pipe(
    self,
    body: Dict[str, any],
    __user__: Dict[str, any]
) -> Union[str, Dict[str, any]]:
    """Type hints improve code clarity."""
    pass
```

### 5. Log Appropriately

```python
import logging

logger = logging.getLogger(__name__)

class Pipe:
    def pipe(self, body: dict, __user__: dict) -> str:
        logger.debug(f"Processing request from {__user__['name']}")

        try:
            result = self.process(body)
            logger.info("Request processed successfully")
            return result
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            raise
```

### 6. Test Your Functions

```python
# test_my_pipe.py
from my_pipe import Pipe

def test_basic_functionality():
    pipe = Pipe()

    body = {
        "messages": [{"role": "user", "content": "Hello"}]
    }
    user = {"id": "test", "name": "Test User", "role": "user"}

    result = pipe.pipe(body, user)

    assert result is not None
    assert isinstance(result, str)
```

### 7. Document Your Functions

```python
"""
title: My Custom Pipe
description: Detailed description of what this does
author: Your Name
version: 1.0.0
requirements: requests,openai
license: MIT
"""

class Pipe:
    """
    A custom pipe that does X, Y, and Z.

    Features:
    - Feature 1
    - Feature 2
    - Feature 3

    Configuration:
    - api_key: Your API key
    - model: Model to use

    Usage:
    1. Configure API key in settings
    2. Select this pipe as your model
    3. Start chatting
    """
    pass
```

---

## Quick Reference

### Function Template Files

See the `examples/` directory for working templates:

- `echo_pipe.py` - Basic Pipe
- `sentiment_filter.py` - Filter with dependencies
- `logger_action.py` - Action with file I/O
- `api_pipe.py` - Advanced Pipe with Valves

### Common Patterns

**External API Call:**
```python
import requests

def pipe(self, body: dict, __user__: dict) -> str:
    response = requests.post(
        self.valves.api_url,
        headers={"Authorization": f"Bearer {self.valves.api_key}"},
        json={"messages": body["messages"]}
    )
    return response.json()["content"]
```

**Message Modification:**
```python
def inlet(self, body: dict, __user__: dict) -> dict:
    for msg in body.get("messages", []):
        if msg["role"] == "user":
            msg["content"] = msg["content"].upper()
    return body
```

**Status Updates:**
```python
async def action(self, body, __user__, __event_emitter__=None, __event_call__=None):
    await __event_emitter__({
        "type": "status",
        "data": {"description": "Working...", "done": False}
    })
    # Do work...
    await __event_emitter__({
        "type": "status",
        "data": {"description": "Done!", "done": True}
    })
```

---

## Additional Resources

- **Official Docs**: https://docs.openwebui.com/features/plugin/functions/
- **Community Functions**: https://openwebui.com/functions
- **GitHub Examples**: https://github.com/open-webui/pipelines/tree/main/examples
- **Discord Community**: Join for help and discussions

---

## Troubleshooting

**Function not appearing:**
- Check filename (alphanumeric + underscores only)
- Verify class name (Pipe, Filter, or Action)
- Check Python syntax errors
- Restart Open WebUI

**Dependencies not installing:**
- Check `requirements` field format (comma-separated)
- Verify package names are correct
- Check logs for pip errors

**Filter not working:**
- Ensure filter is enabled globally OR assigned to model
- Check Workspace → Models → [Select Model] → Assign Filter

**Valves not showing:**
- Verify Valves class is properly defined
- Check Field() definitions
- Restart after changes

---

**Happy Function Building!** 🚀

For more help, check the examples directory or visit the Open WebUI documentation.
