# Filesystem-Based Function Management

This feature enables you to manage Open WebUI functions through your filesystem and IDE, rather than only through the web interface.

## Overview

Open WebUI automatically scans the `backend/functions/` directory and:
- Loads function files (`.py` files) into the database on startup
- Updates functions when file content changes
- Enables IDE-based development with version control
- Works alongside web-managed functions

**No configuration needed** - just drop your `.py` files in `backend/functions/` and restart!

## Quick Start

1. **Navigate to the functions directory:**
   ```bash
   cd backend/functions
   ```

2. **Create a function file:**
   ```bash
   touch my_pipe.py
   ```

3. **Edit with your IDE** (VS Code, vim, etc.)

4. **Restart Open WebUI** - your function is automatically loaded!

## Function File Structure

Each function should be a separate `.py` file. The filename (without `.py`) becomes the function ID.

### Filename Requirements
- Must contain only alphanumeric characters and underscores
- Examples: `my_function.py`, `calculator_pipe.py`, `sentiment_filter.py`

### File Format

```python
"""
title: My Custom Function
description: Does something useful
requirements: requests,pandas
"""

class Pipe:
    def __init__(self):
        self.name = "My Custom Pipe"

    def pipe(self, body: dict, __user__: dict) -> dict:
        # Your implementation here
        return body
```

## Function Types

### 1. Pipe Functions

Pipes act as custom chat models that process messages:

```python
"""
title: Echo Pipe
description: Simple echo function that returns user messages
"""

class Pipe:
    def __init__(self):
        self.name = "Echo"

    def pipe(self, body: dict, __user__: dict) -> str:
        messages = body.get("messages", [])
        if messages:
            return messages[-1].get("content", "")
        return "No message found"
```

### 2. Filter Functions

Filters intercept and modify messages before/after processing:

```python
"""
title: Uppercase Filter
description: Converts all messages to uppercase
"""

class Filter:
    def __init__(self):
        self.name = "Uppercase Filter"

    def inlet(self, body: dict, __user__: dict) -> dict:
        """Process incoming messages"""
        messages = body.get("messages", [])
        for message in messages:
            if "content" in message:
                message["content"] = message["content"].upper()
        return body

    def outlet(self, body: dict, __user__: dict) -> dict:
        """Process outgoing messages"""
        messages = body.get("messages", [])
        for message in messages:
            if "content" in message:
                message["content"] = message["content"].upper()
        return body
```

### 3. Action Functions

Actions perform operations without modifying the message flow:

```python
"""
title: Logger Action
description: Logs chat messages to a file
requirements: python-dateutil
"""

import logging
from datetime import datetime

class Action:
    def __init__(self):
        self.name = "Logger"
        logging.basicConfig(filename='chat.log', level=logging.INFO)

    async def action(self, body: dict, __user__: dict) -> None:
        """Log the message"""
        messages = body.get("messages", [])
        if messages:
            msg = messages[-1].get("content", "")
            logging.info(f"[{datetime.now()}] {__user__.get('name')}: {msg}")
```

## Frontmatter Fields

Include metadata in triple-quoted docstrings at the start of your file:

| Field | Description | Required |
|-------|-------------|----------|
| `title` | Display name for the function | No |
| `description` | Brief description | No |
| `requirements` | Comma-separated list of pip packages | No |

Custom fields are also supported and stored in the function metadata.

## Managing Dependencies

### Global Dependencies (requirements.txt)

For packages used by multiple functions, create a `requirements.txt` file in `backend/functions/`:

```bash
cd backend/functions
cp requirements.txt.example requirements.txt
```

Edit the file to add your dependencies:

```txt
# backend/functions/requirements.txt
requests==2.31.0
openai>=1.0.0
anthropic==0.8.0
pydantic==2.5.0
beautifulsoup4==4.12.0
```

These packages will be automatically installed when Open WebUI starts, **before** individual function requirements are processed.

### Function-Specific Dependencies

Individual functions can specify their own dependencies in frontmatter:

```python
"""
title: My Function
requirements: textblob,nltk
"""
```

### Dependency Installation Order

1. **Global**: `backend/functions/requirements.txt` installed first
2. **Per-function**: Each function's frontmatter `requirements` installed next

This allows you to:
- Define common dependencies once in `requirements.txt`
- Add function-specific packages in frontmatter
- Avoid duplicate package specifications

## Configuration with Valves

Functions can define configuration parameters using `Valves`:

```python
"""
title: API Caller
description: Calls an external API
requirements: requests
"""

from pydantic import BaseModel
import requests

class Pipe:
    class Valves(BaseModel):
        api_key: str = ""
        api_url: str = "https://api.example.com"
        timeout: int = 30

    def __init__(self):
        self.valves = self.Valves()

    def pipe(self, body: dict, __user__: dict) -> str:
        response = requests.get(
            self.valves.api_url,
            headers={"Authorization": f"Bearer {self.valves.api_key}"},
            timeout=self.valves.timeout
        )
        return response.text
```

Users can also have their own valve overrides with `UserValves`:

```python
class Pipe:
    class Valves(BaseModel):
        api_key: str = ""  # Admin sets this

    class UserValves(BaseModel):
        model: str = "gpt-4"  # Each user can choose

    def __init__(self):
        self.valves = self.Valves()

    def pipe(self, body: dict, __user__: dict) -> dict:
        # Access user-specific valves via __user__["valves"]
        user_valves = __user__.get("valves", {})
        model = user_valves.get("model", "gpt-4")
        # Use the model...
        return body
```

## Development Workflow

### 1. Create Your Function

```bash
cd backend/functions
touch my_pipe.py
```

### 2. Edit in Your IDE

Open `backend/functions/my_pipe.py` in VS Code, vim, or any editor:

```python
"""
title: My Custom Pipe
description: Does something cool
"""

class Pipe:
    def pipe(self, body: dict, __user__: dict) -> str:
        return "Hello from my IDE!"
```

### 3. Restart Open WebUI

Functions are automatically loaded on startup:

```bash
# You'll see logs like:
# INFO: Syncing functions from filesystem...
# INFO: Discovered function: my_pipe (pipe) from my_pipe.py
# INFO: Created new function from filesystem: my_pipe
# INFO: Filesystem sync: 1 created, 0 updated, 0 unchanged
```

### 4. Iterate and Develop

- Edit function files in your IDE
- Use version control (git)
- Restart the application to sync changes
- Changes are automatically detected and updated

### 5. Use Examples as Templates

```bash
cd backend/functions
cp examples/echo_pipe.py my_new_function.py
# Edit my_new_function.py
# Restart Open WebUI
```

## How It Works

### On Startup:
1. Open WebUI scans `backend/functions/` for `.py` files
2. Each file is parsed to extract:
   - Function type (Pipe/Filter/Action)
   - Frontmatter metadata
   - Source code
3. New functions are created in the database
4. Existing functions are updated if content changed
5. Dependencies are installed from `requirements` field

### Sync Behavior:
- **New files**: Created in database with `is_active=True`
- **Modified files**: Database content updated
- **Unchanged files**: No database changes
- **Deleted files**: Currently remain in database (can be manually deleted via UI)

### Function Ownership:
- Filesystem functions are owned by a system user (`user_id="system"`)
- They can still be edited via the web UI
- Changes in the UI won't be overwritten unless the filesystem file also changes

## Best Practices

1. **Version Control**: The functions directory is already in your git repo
   ```bash
   cd backend/functions
   git add my_pipe.py
   git commit -m "Add my custom pipe"
   ```

2. **Testing**: Test functions locally before deploying
   ```python
   # test_my_pipe.py
   from my_pipe import Pipe

   pipe = Pipe()
   result = pipe.pipe({"messages": [{"content": "test"}]}, {})
   assert result is not None
   ```

3. **Documentation**: Document your functions in docstrings
   ```python
   def pipe(self, body: dict, __user__: dict) -> str:
       """
       Process chat messages.

       Args:
           body: Request body with messages
           __user__: User information dict

       Returns:
           Response string
       """
   ```

4. **Dependencies**: Pin versions in requirements
   ```python
   """
   requirements: requests==2.31.0,pandas>=2.0.0
   """
   ```

5. **Error Handling**: Always handle errors gracefully
   ```python
   def pipe(self, body: dict, __user__: dict) -> str:
       try:
           # Your logic
           return result
       except Exception as e:
           return f"Error: {str(e)}"
   ```

## Troubleshooting

### Functions Not Loading

Check the logs for errors:
```bash
grep "function" /path/to/logs
```

Common issues:
- **Invalid filename**: Must be alphanumeric + underscores
- **No class found**: Must define Pipe, Filter, or Action class
- **Syntax errors**: Check Python syntax
- **Wrong location**: File must be in `backend/functions/` (not in subdirectories except `examples/`)

### Dependencies Not Installing

- Check the `requirements` field format (comma-separated)
- Ensure pip can access the packages
- Check logs for installation errors

### Changes Not Reflecting

- Restart the application (sync runs at startup)
- Check file permissions
- Verify the file is in `backend/functions/`
- Check that the file doesn't have syntax errors

## Migration from Web UI

To migrate existing web-managed functions to filesystem:

1. **Export functions**: Use the export API
   ```bash
   curl -H "Authorization: Bearer $TOKEN" \
        http://localhost:8080/api/v1/functions/export > functions.json
   ```

2. **Convert to files**: Extract each function's content
   ```python
   import json

   with open('functions.json') as f:
       functions = json.load(f)

   for func in functions:
       with open(f"{func['id']}.py", 'w') as f:
           f.write(func['content'])
   ```

3. **Move to functions directory**:
   ```bash
   mv *.py backend/functions/
   ```

4. **Restart**: Open WebUI will sync them

## Examples

See example function files in the `backend/functions/examples/` directory:
- `echo_pipe.py` - Simple echo pipe
- `sentiment_filter.py` - Sentiment analysis filter
- `logger_action.py` - Message logging action
- `api_pipe.py` - External API integration

To use an example:
```bash
cd backend/functions
cp examples/echo_pipe.py my_custom_pipe.py
# Edit my_custom_pipe.py
# Restart Open WebUI
```

## API Compatibility

Filesystem-managed functions work identically to web-managed functions:
- Same execution environment
- Same API access
- Same user permissions
- Same valve configuration

The only difference is where the source code is stored and how it's updated.
