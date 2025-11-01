# Function Examples

This directory contains example functions demonstrating filesystem-based function management in Open WebUI.

## Examples

### 1. `echo_pipe.py` - Basic Pipe
A simple pipe that echoes back user messages. Great for understanding the basic pipe structure.

**Features:**
- Basic pipe implementation
- Message handling
- Simple return value

**Usage:**
```bash
cp echo_pipe.py $FUNCTIONS_DIR/
```

### 2. `sentiment_filter.py` - Filter with Dependencies
A filter that analyzes message sentiment using TextBlob.

**Features:**
- Filter inlet/outlet implementation
- External dependency (textblob)
- Message modification
- Error handling

**Usage:**
```bash
cp sentiment_filter.py $FUNCTIONS_DIR/
# Dependencies will be auto-installed on startup
```

### 3. `logger_action.py` - Action Example
An action that logs chat messages to a file.

**Features:**
- Action implementation
- Async operations
- File I/O
- Logging configuration

**Usage:**
```bash
cp logger_action.py $FUNCTIONS_DIR/
# Check ./logs/chat_messages.log for output
```

### 4. `api_pipe.py` - Advanced Pipe with Valves
A pipe that calls external APIs with configurable parameters.

**Features:**
- Valves for global configuration
- UserValves for per-user settings
- HTTP requests
- Comprehensive error handling

**Usage:**
```bash
cp api_pipe.py $FUNCTIONS_DIR/
# Configure API key and URL via admin settings
```

## Quick Start

1. **Set up functions directory:**
   ```bash
   mkdir -p ~/my-functions
   export FUNCTIONS_DIR=~/my-functions
   ```

2. **Copy examples:**
   ```bash
   cp examples/functions/*.py ~/my-functions/
   ```

3. **Restart Open WebUI:**
   ```bash
   # The functions will be automatically loaded
   ```

4. **Check the logs:**
   ```bash
   # You should see:
   # INFO: Discovered function: echo_pipe (pipe) from echo_pipe.py
   # INFO: Discovered function: sentiment_filter (filter) from sentiment_filter.py
   # INFO: Discovered function: logger_action (action) from logger_action.py
   # INFO: Discovered function: api_pipe (pipe) from api_pipe.py
   ```

## Customizing Examples

Feel free to modify these examples to suit your needs:

1. **Change the frontmatter:**
   ```python
   """
   title: My Custom Name
   description: My custom description
   requirements: my,custom,packages
   """
   ```

2. **Add your logic:**
   ```python
   def pipe(self, body: dict, __user__: dict) -> str:
       # Your custom implementation
       return result
   ```

3. **Test locally:**
   ```python
   from echo_pipe import Pipe
   pipe = Pipe()
   result = pipe.pipe({"messages": [{"content": "test"}]}, {})
   print(result)
   ```

4. **Restart to reload:**
   - Modified files are automatically synced on restart

## Tips

- **Start simple**: Begin with `echo_pipe.py` to understand the basics
- **Add complexity**: Move to filters and actions as you learn
- **Use version control**: Keep your functions in git
- **Test thoroughly**: Always test before deploying to production
- **Check logs**: Monitor startup logs for loading errors

## Documentation

See the main [FILESYSTEM_FUNCTIONS.md](../../FILESYSTEM_FUNCTIONS.md) for complete documentation.
