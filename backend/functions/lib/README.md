# Shared Library Modules

This directory contains reusable Python modules that can be imported by your functions.

## Purpose

The `lib/` directory allows you to:
- Share code between multiple functions
- Organize common utilities and classes
- Maintain DRY (Don't Repeat Yourself) principles
- Build more maintainable function code

## How to Use

### 1. Create Your Module

Create a `.py` file in this directory:

```bash
cd backend/functions/lib
touch my_module.py
```

### 2. Define Your Classes/Functions

```python
# lib/my_module.py

class MyHelper:
    def __init__(self):
        self.name = "Helper"

    def process(self, data):
        return f"Processed: {data}"

def my_utility_function(value):
    return value.upper()
```

### 3. Import in Your Functions

```python
# backend/functions/my_pipe.py
"""
title: My Pipe
description: Uses shared lib modules
"""

from lib.my_module import MyHelper, my_utility_function

class Pipe:
    def __init__(self):
        self.helper = MyHelper()

    def pipe(self, body: dict, __user__: dict) -> str:
        result = self.helper.process("data")
        return my_utility_function(result)
```

## Import Patterns

### Basic Import
```python
from lib.score import Score
from lib.utils import format_response
```

### Import Specific Items
```python
from lib.utils import (
    extract_user_message,
    format_response,
    MessageBuilder
)
```

### Import Entire Module
```python
import lib.score as scoring

scorer = scoring.Score()
```

### Relative Imports (within lib/)
If you have `lib/helpers/tools.py`:
```python
# In lib/helpers/tools.py
from ..utils import format_response  # Import from parent lib/
```

## Example Modules Included

### `score.py`
Scoring and rating functionality:
```python
from lib.score import Score

scorer = Score(max_score=100)
scorer.add_score("quality", 85)
rating = scorer.get_rating()  # Returns "B"
```

### `utils.py`
Common utility functions:
```python
from lib.utils import (
    extract_user_message,
    format_response,
    MessageBuilder
)

# Extract message
msg = extract_user_message(body)

# Build messages
builder = MessageBuilder()
builder.add_system("You are helpful")
builder.add_user("Hello")
messages = builder.build()

# Format response
response = format_response("Result", metadata={"score": 95})
```

## Best Practices

### 1. Keep Modules Focused
Each module should have a clear, single purpose:
- ✅ `lib/scoring.py` - Scoring functionality
- ✅ `lib/validators.py` - Input validation
- ✅ `lib/formatters.py` - Output formatting
- ❌ `lib/everything.py` - Kitchen sink module

### 2. Document Your Code
```python
"""
Module for handling API requests.

This module provides utilities for making HTTP requests
to external APIs with error handling and retry logic.
"""

def make_request(url: str, timeout: int = 30) -> dict:
    """
    Make an HTTP GET request.

    Args:
        url: The URL to request
        timeout: Request timeout in seconds

    Returns:
        dict: Response data

    Raises:
        RequestException: If request fails
    """
    pass
```

### 3. Use Type Hints
```python
from typing import Dict, List, Optional

def process_data(
    items: List[str],
    config: Dict[str, any],
    user: Optional[str] = None
) -> List[Dict[str, any]]:
    pass
```

### 4. Handle Dependencies
If your lib module needs external packages:

**Option 1**: Add to `requirements.txt`:
```txt
# backend/functions/requirements.txt
requests==2.31.0
```

**Option 2**: Document in module docstring:
```python
"""
API utilities module.

Requirements:
    - requests>=2.31.0
    - aiohttp>=3.9.0
"""
```

### 5. Avoid Circular Imports
```python
# ❌ BAD: lib/a.py imports lib/b.py, lib/b.py imports lib/a.py

# ✅ GOOD: Move shared code to lib/common.py
# lib/a.py imports lib/common.py
# lib/b.py imports lib/common.py
```

## Directory Structure

You can organize lib/ into subdirectories:

```
lib/
├── __init__.py
├── README.md
├── score.py              # Top-level module
├── utils.py              # Top-level module
├── api/                  # Subdirectory
│   ├── __init__.py
│   ├── openai.py
│   └── anthropic.py
└── helpers/              # Subdirectory
    ├── __init__.py
    ├── text.py
    └── validation.py
```

Import from subdirectories:
```python
from lib.api.openai import OpenAIClient
from lib.helpers.text import clean_text
```

## Testing Your Modules

You can test lib modules independently:

```python
# test_score.py (in lib/ or elsewhere)
from lib.score import Score

def test_score():
    scorer = Score(max_score=100)
    scorer.add_score("test", 85)
    assert scorer.get_rating(85) == "B"

if __name__ == "__main__":
    test_score()
    print("Tests passed!")
```

## Version Control

The `lib/` directory is tracked in git, so:
- ✅ Commit your shared modules
- ✅ Document changes in commit messages
- ✅ Use meaningful module names
- ✅ Keep backward compatibility when possible

## Troubleshooting

### Import Error: ModuleNotFoundError
```
ModuleNotFoundError: No module named 'lib'
```

**Solution**: Make sure you're importing in a function file, not running the module directly. The `lib/` directory is added to sys.path when functions are loaded.

### Import Error: Cannot Import Name
```
ImportError: cannot import name 'MyClass' from 'lib.mymodule'
```

**Solutions**:
1. Check the class/function name is spelled correctly
2. Ensure the module file exists: `backend/functions/lib/mymodule.py`
3. Verify the class/function is defined in that module
4. Check for syntax errors in the module

### Module Changes Not Reflected
**Solution**: Restart Open WebUI. Module changes require a restart to take effect.

## Examples

See `examples/score_example_pipe.py` for a complete example of using lib modules.

## Additional Resources

- [Python Modules Documentation](https://docs.python.org/3/tutorial/modules.html)
- [Organizing Python Code](https://docs.python-guide.org/writing/structure/)
- Main Functions Guide: [../FUNCTION_GUIDE.md](../FUNCTION_GUIDE.md)
