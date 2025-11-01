"""
Utilities for filesystem-based function management.

This module provides functionality to scan a directory for function files
and sync them with the database, enabling IDE-based function development.
"""

import logging
import re
from pathlib import Path
from typing import Optional, Dict, List

from open_webui.env import FUNCTIONS_DIR, SRC_LOG_LEVELS
from open_webui.utils.plugin import extract_frontmatter, replace_imports

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MAIN"])


def extract_function_type(content: str) -> Optional[str]:
    """
    Determine the function type by checking which class is defined.

    Args:
        content: Python source code as string

    Returns:
        "pipe", "filter", "action", or None if no valid class found
    """
    # Look for class definitions
    class_pattern = re.compile(r'^\s*class\s+(\w+)\s*[:\(]', re.MULTILINE)
    matches = class_pattern.findall(content)

    for class_name in matches:
        if class_name == "Pipe":
            return "pipe"
        elif class_name == "Filter":
            return "filter"
        elif class_name == "Action":
            return "action"

    return None


def validate_function_id(function_id: str) -> bool:
    """
    Validate that a function ID contains only allowed characters.

    Function IDs must contain only alphanumeric characters and underscores.

    Args:
        function_id: The ID to validate

    Returns:
        True if valid, False otherwise
    """
    return bool(re.match(r'^[a-zA-Z0-9_]+$', function_id))


def scan_functions_dir() -> List[Dict]:
    """
    Scan FUNCTIONS_DIR for .py files and extract function metadata.

    Returns:
        List of dictionaries containing function data:
        {
            "id": str,           # Filename without .py extension
            "path": Path,        # Full path to the file
            "content": str,      # Python source code
            "type": str,         # "pipe", "filter", or "action"
            "meta": dict,        # Extracted frontmatter
        }
    """
    if not FUNCTIONS_DIR:
        log.debug("FUNCTIONS_DIR not configured, skipping filesystem scan")
        return []

    if not FUNCTIONS_DIR.exists():
        log.warning(f"FUNCTIONS_DIR does not exist: {FUNCTIONS_DIR}")
        return []

    if not FUNCTIONS_DIR.is_dir():
        log.error(f"FUNCTIONS_DIR is not a directory: {FUNCTIONS_DIR}")
        return []

    functions = []

    # Scan for .py files
    for file_path in FUNCTIONS_DIR.glob("*.py"):
        try:
            # Extract function ID from filename
            function_id = file_path.stem

            # Validate function ID
            if not validate_function_id(function_id):
                log.warning(
                    f"Skipping {file_path.name}: ID must contain only "
                    f"alphanumeric characters and underscores"
                )
                continue

            # Read file content
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Process imports
            content = replace_imports(content)

            # Extract frontmatter
            frontmatter = extract_frontmatter(content)

            # Determine function type
            function_type = extract_function_type(content)
            if not function_type:
                log.warning(
                    f"Skipping {file_path.name}: No Pipe, Filter, or Action "
                    f"class found"
                )
                continue

            # Build metadata
            meta = {
                "description": frontmatter.get("description", ""),
                "manifest": frontmatter,
            }

            # Extract name from frontmatter or use ID
            name = frontmatter.get("title", frontmatter.get("name", function_id))

            functions.append({
                "id": function_id,
                "path": file_path,
                "content": content,
                "type": function_type,
                "meta": meta,
                "name": name,
                "frontmatter": frontmatter,
            })

            log.info(f"Discovered function: {function_id} ({function_type}) from {file_path.name}")

        except Exception as e:
            log.error(f"Error reading function file {file_path}: {e}")
            continue

    log.info(f"Scanned {FUNCTIONS_DIR}: found {len(functions)} valid function(s)")
    return functions
