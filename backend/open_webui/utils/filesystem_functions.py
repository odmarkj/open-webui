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
    if not FUNCTIONS_DIR.exists():
        log.debug(f"Functions directory does not exist: {FUNCTIONS_DIR}")
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


def sync_functions_from_filesystem(system_user_id: str = "system") -> Dict[str, any]:
    """
    Sync functions from FUNCTIONS_DIR to the database.

    This function:
    1. Scans FUNCTIONS_DIR for function files
    2. Creates new functions in the database
    3. Updates existing functions if content has changed
    4. Marks functions from filesystem as active

    Args:
        system_user_id: User ID to assign as owner of filesystem functions
                       (default: "system")

    Returns:
        Dictionary with sync results:
        {
            "scanned": int,     # Number of files scanned
            "created": int,     # Number of functions created
            "updated": int,     # Number of functions updated
            "unchanged": int,   # Number of functions unchanged
            "errors": list,     # List of errors encountered
        }
    """
    # Import here to avoid circular dependency
    from open_webui.models.functions import Functions, FunctionForm, FunctionMeta

    # Scan filesystem for functions
    discovered_functions = scan_functions_dir()

    results = {
        "scanned": len(discovered_functions),
        "created": 0,
        "updated": 0,
        "unchanged": 0,
        "errors": [],
    }

    # Track filesystem function IDs to mark them
    filesystem_function_ids = set()

    # Process each discovered function
    for func_data in discovered_functions:
        function_id = func_data["id"]
        filesystem_function_ids.add(function_id)

        try:
            # Check if function already exists
            existing_function = Functions.get_function_by_id(function_id)

            if existing_function:
                # Check if content has changed
                if existing_function.content != func_data["content"]:
                    # Update existing function
                    Functions.update_function_by_id(
                        function_id,
                        {
                            "name": func_data["name"],
                            "type": func_data["type"],
                            "content": func_data["content"],
                            "meta": func_data["meta"],
                            "is_active": True,
                        }
                    )
                    results["updated"] += 1
                    log.info(f"Updated function from filesystem: {function_id}")
                else:
                    # Content unchanged, but ensure it's active
                    if not existing_function.is_active:
                        Functions.update_function_by_id(
                            function_id,
                            {"is_active": True}
                        )
                        log.info(f"Reactivated function from filesystem: {function_id}")
                    results["unchanged"] += 1
                    log.debug(f"Function unchanged: {function_id}")
            else:
                # Create new function
                form_data = FunctionForm(
                    id=function_id,
                    name=func_data["name"],
                    content=func_data["content"],
                    meta=FunctionMeta(**func_data["meta"]),
                )

                new_function = Functions.insert_new_function(
                    user_id=system_user_id,
                    type=func_data["type"],
                    form_data=form_data,
                )

                if new_function:
                    # Ensure it's active
                    Functions.update_function_by_id(function_id, {"is_active": True})
                    results["created"] += 1
                    log.info(f"Created new function from filesystem: {function_id}")
                else:
                    error_msg = f"Failed to create function: {function_id}"
                    results["errors"].append(error_msg)
                    log.error(error_msg)

        except Exception as e:
            error_msg = f"Error syncing function {function_id}: {str(e)}"
            results["errors"].append(error_msg)
            log.error(error_msg)

    # Log summary
    log.info(
        f"Filesystem function sync complete: "
        f"{results['created']} created, "
        f"{results['updated']} updated, "
        f"{results['unchanged']} unchanged, "
        f"{len(results['errors'])} errors"
    )

    return results
