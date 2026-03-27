"""
█▀ █▄█ █▀▀ █░█ █▀▀ █░█
▄█ ░█░ █▄▄ █▀█ ██▄ ▀▄▀

Author: <Anton Sychev> (anton at sychev dot xyz) 
markdown.py (c) 2025 
Created:  2025-01-15 10:00:00 
Desc: Rocket Store (Python) - Markdown utilities for parsing and serializing
      Supports YAML frontmatter and header-based markdown formats
Docs: documentation
License: 
    * MIT: (c) Paragi 2017, Simon Riget.
"""

import re
import yaml
from typing import Dict, Any, Optional


def detect_markdown_format(content: str) -> str:
    """
    Detect the format of markdown content.
    
    Returns:
        "frontmatter" - if content starts with --- (YAML frontmatter)
        "headers" - if content uses # headers for fields
        "unknown" - if format cannot be determined
    """
    content = content.strip()
    
    if content.startswith("---"):
        return "frontmatter"
    
    # Check for header pattern like # key: value or # key
    header_pattern = r"^#\s+\w+"
    if re.search(header_pattern, content, re.MULTILINE):
        return "headers"
    
    return "unknown"


def parse_frontmatter(content: str) -> Dict[str, Any]:
    """
    Parse YAML frontmatter from markdown content.
    
    Format:
        ---
        key1: value1
        key2: value2
        ---
        # Title
        Content...
    
    Returns:
        dict with frontmatter fields + '_content' for body
    """
    result = {}
    
    # Match frontmatter pattern
    pattern = r"^---\s*\n(.*?)\n---\s*\n?(.*)$"
    match = re.match(pattern, content, re.DOTALL)
    
    if match:
        frontmatter_text = match.group(1)
        body = match.group(2).strip()
        
        try:
            result = yaml.safe_load(frontmatter_text) or {}
            if body:
                result["_content"] = body
        except yaml.YAMLError as e:
            result["_parse_error"] = str(e)
            result["_raw"] = content
    else:
        result["_raw"] = content
    
    return result


def parse_headers(content: str) -> Dict[str, Any]:
    """
    Parse markdown with header-based fields.
    
    Format:
        # title: My Title
        # author: John Doe
        
        Content here...
    
    Returns:
        dict with header fields + '_content' for body
    """
    result = {}
    lines = content.split("\n")
    body_lines = []
    in_headers = True
    
    for line in lines:
        if in_headers:
            header_match = re.match(r"^#\s+(\w+):\s*(.*)$", line)
            if header_match:
                key = header_match.group(1)
                value = header_match.group(2).strip()
                result[key] = value
            elif line.strip() == "":
                continue
            else:
                in_headers = False
                body_lines.append(line)
        else:
            body_lines.append(line)
    
    body = "\n".join(body_lines).strip()
    if body:
        result["_content"] = body
    
    return result


def parse_markdown(content: str) -> Dict[str, Any]:
    """
    Parse markdown content auto-detecting format.
    
    Args:
        content: Raw markdown content
        
    Returns:
        dict with parsed fields
    """
    content = content.strip()
    
    if not content:
        return {}
    
    format_type = detect_markdown_format(content)
    
    if format_type == "frontmatter":
        return parse_frontmatter(content)
    elif format_type == "headers":
        return parse_headers(content)
    else:
        # Try to parse as plain markdown with _content
        return {"_content": content}


def serialize_frontmatter(data: Dict[str, Any]) -> str:
    """
    Serialize dict to YAML frontmatter format.
    
    Args:
        data: Dictionary to serialize
        
    Returns:
        Markdown string with YAML frontmatter
    """
    # Separate content from metadata
    content = data.pop("_content", "")
    
    # Convert to YAML
    frontmatter = yaml.dump(
        data,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False
    )
    
    result = f"---\n{frontmatter}---\n"
    
    if content:
        result += f"\n{content}\n"
    
    return result


def serialize_headers(data: Dict[str, Any]) -> str:
    """
    Serialize dict to header-based markdown format.
    
    Args:
        data: Dictionary to serialize
        
    Returns:
        Markdown string with headers
    """
    content = data.pop("_content", "")
    lines = []
    
    for key, value in data.items():
        if not key.startswith("_"):
            lines.append(f"# {key}: {value}")
    
    if content:
        lines.append("")
        lines.append(content)
    
    return "\n".join(lines) + "\n"


def serialize_markdown(data: Dict[str, Any], format_type: str = "frontmatter") -> str:
    """
    Serialize dictionary to markdown format.
    
    Args:
        data: Dictionary to serialize
        format_type: "frontmatter" or "headers"
        
    Returns:
        Markdown formatted string
    """
    if format_type == "frontmatter":
        return serialize_frontmatter(data.copy())
    elif format_type == "headers":
        return serialize_headers(data.copy())
    else:
        raise ValueError(f"Unknown markdown format: {format_type}")


def is_markdown_file(filename: str) -> bool:
    """
    Check if filename has markdown extension.
    
    Args:
        filename: File name to check
        
    Returns:
        True if .md, .markdown, .mdx extension
    """
    ext = filename.lower().split(".")[-1] if "." in filename else ""
    return ext in ("md", "markdown", "mdx")
