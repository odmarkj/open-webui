# Functions Directory

This directory is for **filesystem-based function management**. Place your function `.py` files here and they will be automatically loaded when Open WebUI starts.

## Quick Start

1. **Create a function file** in this directory:
   ```bash
   cd backend/functions
   touch my_function.py
   ```

2. **Edit the file** with your IDE:
   ```python
   """
   title: My Custom Function
   description: Does something useful
   requirements: requests
   """

   class Pipe:
       def pipe(self, body: dict, __user__: dict) -> str:
           return "Hello from filesystem!"
   ```

3. **Restart Open WebUI** - your function will be automatically loaded!

## Function Types

### Pipe Functions
Act as custom chat models:
```python
class Pipe:
    def pipe(self, body: dict, __user__: dict) -> str:
        # Process and return response
        return "response"
```

### Filter Functions
Intercept and modify messages:
```python
class Filter:
    def inlet(self, body: dict, __user__: dict) -> dict:
        # Modify incoming messages
        return body

    def outlet(self, body: dict, __user__: dict) -> dict:
        # Modify outgoing messages
        return body
```

### Action Functions
Perform side effects:
```python
class Action:
    async def action(self, body: dict, __user__: dict) -> None:
        # Do something (log, notify, etc.)
        pass
```

## File Naming

- Filename (without `.py`) becomes the function ID
- Use only alphanumeric characters and underscores
- Examples: `my_pipe.py`, `sentiment_filter.py`, `logger.py`

## Frontmatter

Add metadata at the top of your file:
```python
"""
title: Display Name
description: What this function does
requirements: package1,package2
"""
```

## Managing Dependencies

### Global Dependencies (requirements.txt)

For packages needed by multiple functions, create a `requirements.txt` file:

```bash
# Copy the example file
cp requirements.txt.example requirements.txt

# Add your dependencies
echo "requests==2.31.0" >> requirements.txt
echo "openai>=1.0.0" >> requirements.txt
```

Packages listed in `requirements.txt` will be automatically installed when Open WebUI starts.

**Example requirements.txt:**
```
requests==2.31.0
openai>=1.0.0
pydantic==2.5.0
```

### Function-Specific Dependencies

Individual functions can also specify dependencies in their frontmatter:
```python
"""
title: My Function
requirements: beautifulsoup4,lxml
"""
```

Both `requirements.txt` (global) and frontmatter requirements (per-function) will be installed.

## Configuration with Valves

Define configurable parameters:
```python
from pydantic import BaseModel

class Pipe:
    class Valves(BaseModel):
        api_key: str = ""
        timeout: int = 30

    def __init__(self):
        self.valves = self.Valves()

    def pipe(self, body: dict, __user__: dict) -> str:
        # Use self.valves.api_key, etc.
        return "response"
```

## Examples

See the `examples/` subdirectory for working examples:
- `echo_pipe.py` - Basic pipe example
- `sentiment_filter.py` - Filter with dependencies
- `logger_action.py` - Action with file operations
- `api_pipe.py` - Advanced pipe with configuration

## How It Works

**On startup:**
1. Open WebUI scans this directory for `.py` files
2. Extracts function type and metadata
3. Creates/updates functions in the database
4. Installs dependencies from `requirements`

**Sync behavior:**
- New files → Created in database
- Modified files → Updated in database
- Unchanged files → Skipped
- Deleted files → Remain in database (delete via UI if needed)

## Development Workflow

1. **Create function** in your IDE
2. **Test locally** if desired
3. **Copy to this directory**
4. **Restart application** to sync
5. **Iterate** - edit files and restart to update

## Tips

✅ Use version control for this directory
✅ Test functions before deploying
✅ Document your functions well
✅ Handle errors gracefully
✅ Pin dependency versions

## Documentation

- **[FUNCTION_GUIDE.md](./FUNCTION_GUIDE.md)** - Complete guide to building functions (Pipe, Filter, Action)
- **[FILESYSTEM_FUNCTIONS.md](../../FILESYSTEM_FUNCTIONS.md)** - Filesystem-based function management documentation
- **[examples/](./examples/)** - Working examples for all function types
