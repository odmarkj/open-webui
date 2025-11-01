# Filesystem-Based Function Management

This feature enables you to manage Open WebUI functions through your filesystem and IDE, rather than only through the web interface.

## Overview

When configured, Open WebUI will automatically:
- Scan a directory for function files (`.py` files)
- Load them into the database on startup
- Update functions when file content changes
- Enable IDE-based development with version control

## Configuration

Set the `FUNCTIONS_DIR` environment variable to point to your functions directory:

```bash
export FUNCTIONS_DIR=/path/to/your/functions
```

Or in your `.env` file:

```env
FUNCTIONS_DIR=/path/to/your/functions
```

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

### 1. Create a Functions Directory

```bash
mkdir -p /path/to/functions
```

### 2. Set Environment Variable

```bash
export FUNCTIONS_DIR=/path/to/functions
```

### 3. Create Function Files

```bash
cd /path/to/functions
touch my_pipe.py
```

Edit `my_pipe.py` with your favorite IDE/editor.

### 4. Restart Open WebUI

Functions are loaded on startup:

```bash
# You'll see logs like:
# INFO: Syncing functions from filesystem...
# INFO: Discovered function: my_pipe (pipe) from my_pipe.py
# INFO: Created new function from filesystem: my_pipe
# INFO: Filesystem sync: 1 created, 0 updated, 0 unchanged
```

### 5. Iterate and Develop

- Edit function files in your IDE
- Use version control (git)
- Restart the application to sync changes
- Changes are automatically detected and updated

## How It Works

### On Startup:
1. Open WebUI scans `FUNCTIONS_DIR` for `.py` files
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

1. **Version Control**: Keep your functions directory in git
   ```bash
   cd /path/to/functions
   git init
   git add .
   git commit -m "Initial functions"
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
- **Missing FUNCTIONS_DIR**: Ensure environment variable is set

### Dependencies Not Installing

- Check the `requirements` field format (comma-separated)
- Ensure pip can access the packages
- Check logs for installation errors

### Changes Not Reflecting

- Restart the application (sync runs at startup)
- Check file permissions
- Verify the file is in FUNCTIONS_DIR

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

3. **Move to FUNCTIONS_DIR**:
   ```bash
   mv *.py $FUNCTIONS_DIR/
   ```

4. **Restart**: Open WebUI will sync them

## Examples

See example function files in the `examples/functions/` directory:
- `echo_pipe.py` - Simple echo pipe
- `sentiment_filter.py` - Sentiment analysis filter
- `logger_action.py` - Message logging action
- `api_pipe.py` - External API integration

## API Compatibility

Filesystem-managed functions work identically to web-managed functions:
- Same execution environment
- Same API access
- Same user permissions
- Same valve configuration

The only difference is where the source code is stored and how it's updated.
