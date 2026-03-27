"""
█▀ █▄█ █▀▀ █░█ █▀▀ █░█
▄█ ░█░ █▄▄ █▀█ ██▄ ▀▄▀

Author: <Anton Sychev> (anton at sychev dot xyz) 
ai_memory_example.py (c) 2025 
Created:  2025-01-15 10:00:00 
Desc: Example of using Rocketstore with Markdown format for AI memories
      Compatible with Claude local memories and skill-search-in-files-ack
Docs: documentation
"""

from Rocketstore import Rocketstore

# Initialize Rocketstore with Markdown format
rs = Rocketstore(**{
    "data_storage_area": "./ai_memories",
    "data_format": Rocketstore._FORMAT_MD
})


def store_conversation_memory(session_id: str, user_message: str, ai_response: str, context: dict = None):
    """
    Store a conversation memory in Markdown format.
    
    This creates human-readable files that can be:
    - Edited manually
    - Searched with skill-search-in-files-ack
    - Used as context for future AI interactions
    """
    memory = {
        "session_id": session_id,
        "type": "conversation",
        "timestamp": context.get("timestamp") if context else None,
        "tags": context.get("tags", ["ai", "conversation"]) if context else ["ai", "conversation"],
        "user_message_preview": user_message[:100] + "..." if len(user_message) > 100 else user_message,
        "_content": f"""## User
{user_message}

## AI
{ai_response}
"""
    }
    
    result = rs.post("conversations", f"session_{session_id}", memory, Rocketstore._ADD_AUTO_INC)
    print(f"Stored memory: {result['key']}")
    return result


def store_skill_memory(skill_name: str, description: str, usage_examples: list, metadata: dict = None):
    """
    Store skill documentation in Markdown format.
    
    This is compatible with:
    - https://github.com/klich3/skill-search-in-files-ack
    - Claude's skill system
    """
    examples_md = "\n\n".join([f"### Example {i+1}\n```\n{ex}\n```" for i, ex in enumerate(usage_examples)])
    
    skill = {
        "skill_name": skill_name,
        "type": "skill",
        "version": metadata.get("version", "1.0") if metadata else "1.0",
        "author": metadata.get("author", "unknown") if metadata else "unknown",
        "tags": metadata.get("tags", ["skill"]) if metadata else ["skill"],
        "_content": f"""## Description
{description}

## Usage Examples
{examples_md}

## Metadata
- Created: {metadata.get('created', 'now') if metadata else 'now'}
- Last Updated: {metadata.get('updated', 'now') if metadata else 'now'}
"""
    }
    
    result = rs.post("skills", skill_name.lower().replace(" ", "_"), skill)
    print(f"Stored skill: {result['key']}")
    return result


def search_memories_by_tag(tag: str):
    """
    Search memories by tag using wildcards.
    """
    # Get all memories and filter by tag
    all_memories = rs.get("conversations", "*")
    
    matching = []
    if all_memories.get("result"):
        for i, record in enumerate(all_memories["result"]):
            tags = record.get("tags", [])
            if tag in tags:
                matching.append({
                    "key": all_memories["key"][i],
                    "record": record
                })
    
    return matching


def get_memory_content(key: str):
    """
    Retrieve full memory content.
    """
    result = rs.get("conversations", key)
    if result["count"] > 0:
        return result["result"][0]
    return None


def list_all_skills():
    """
    List all stored skills.
    """
    return rs.get("skills", "*")


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("Rocketstore AI Memory Example")
    print("=" * 60)
    
    # Clear previous data
    rs.delete()
    
    # Store conversation memories
    print("\n--- Storing Conversation Memories ---")
    
    store_conversation_memory(
        session_id="abc123",
        user_message="How do I implement a binary search in Python?",
        ai_response="Here's a Python implementation of binary search...",
        context={
            "timestamp": "2025-01-15T10:00:00",
            "tags": ["python", "algorithms", "binary-search"]
        }
    )
    
    store_conversation_memory(
        session_id="abc123",
        user_message="Can you explain the time complexity?",
        ai_response="Binary search has O(log n) time complexity...",
        context={
            "timestamp": "2025-01-15T10:05:00",
            "tags": ["python", "algorithms", "complexity"]
        }
    )
    
    # Store skill documentation
    print("\n--- Storing Skill Documentation ---")
    
    store_skill_memory(
        skill_name="Binary Search",
        description="Implement binary search algorithm in various languages",
        usage_examples=[
            "binary_search([1,2,3,4,5], 3) -> 2",
            "binary_search(['a','b','c'], 'b') -> 1"
        ],
        metadata={
            "version": "1.0",
            "author": "AI Assistant",
            "tags": ["algorithm", "search", "python"],
            "created": "2025-01-15"
        }
    )
    
    store_skill_memory(
        skill_name="Markdown Parser",
        description="Parse markdown files with YAML frontmatter",
        usage_examples=[
            "parse_markdown('---\\ntitle: Test\\n---') -> {'title': 'Test'}",
        ],
        metadata={
            "version": "2.0",
            "author": "AI Assistant",
            "tags": ["markdown", "parser", "yaml"],
            "created": "2025-01-15"
        }
    )
    
    # Retrieve and display
    print("\n--- Retrieving Memories ---")
    
    all_conversations = rs.get("conversations", "*")
    print(f"Total conversations: {all_conversations['count']}")
    for key in all_conversations.get("key", []):
        print(f"  - {key}")
    
    print("\n--- All Skills ---")
    all_skills = list_all_skills()
    print(f"Total skills: {all_skills['count']}")
    for i, record in enumerate(all_skills.get("result", [])):
        print(f"  - {record.get('skill_name')} (v{record.get('version')})")
        print(f"    Tags: {', '.join(record.get('tags', []))}")
    
    # Search by tag
    print("\n--- Searching by Tag 'python' ---")
    python_memories = search_memories_by_tag("python")
    print(f"Found {len(python_memories)} memories with tag 'python'")
    
    # Show full content of one memory
    if all_conversations["count"] > 0:
        print("\n--- Full Content of First Memory ---")
        first_key = all_conversations["key"][0]
        content = get_memory_content(first_key)
        if content:
            print(f"Session: {content.get('session_id')}")
            print(f"Tags: {content.get('tags')}")
            print(f"Content:\n{content.get('_content')}")
    
    print("\n" + "=" * 60)
    print("Files are stored in: ./ai_memories/")
    print("You can edit them manually with any text editor!")
    print("=" * 60)
    
    # Cleanup (optional)
    # rs.delete()
