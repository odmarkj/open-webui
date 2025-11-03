# Function Examples

This directory contains example functions demonstrating filesystem-based function management.

## Available Examples

### 1. `echo_pipe.py` - Basic Pipe
A simple pipe that echoes back user messages.

**Features:**
- Basic pipe structure
- Message handling
- Simple return value

**To use:**
```bash
cp echo_pipe.py ../
# Restart Open WebUI
```

### 2. `sentiment_filter.py` - Filter with Dependencies
Analyzes message sentiment using TextBlob.

**Features:**
- Filter inlet/outlet
- External dependency (textblob)
- Message modification
- Error handling

**To use:**
```bash
cp sentiment_filter.py ../
# Dependencies auto-install on restart
```

### 3. `logger_action.py` - Action Example
Logs chat messages to a file.

**Features:**
- Action implementation
- Async operations
- File I/O
- Logging setup

**To use:**
```bash
cp logger_action.py ../
# Check logs/chat_messages.log for output
```

### 4. `api_pipe.py` - Advanced Pipe with Valves
Calls external APIs with configurable parameters.

**Features:**
- Global Valves configuration
- User-specific UserValves
- HTTP requests
- Error handling

**To use:**
```bash
cp api_pipe.py ../
# Configure via admin settings after restart
```

## Quick Start

Copy all examples to use them:
```bash
cp *.py ../
# Restart Open WebUI
```

Or copy individual examples as needed.

## Customization

These examples are templates - feel free to:
- Modify the code for your needs
- Change frontmatter metadata
- Add your own logic
- Combine concepts from multiple examples

## Testing

Test examples before deployment:
```python
# From this directory
from echo_pipe import Pipe

pipe = Pipe()
result = pipe.pipe({"messages": [{"content": "test"}]}, {})
print(result)
```

## More Information

- Parent README: [../README.md](../README.md)
- Full documentation: [../../FILESYSTEM_FUNCTIONS.md](../../FILESYSTEM_FUNCTIONS.md)
