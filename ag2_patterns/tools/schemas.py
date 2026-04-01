"""
Tool Schemas — Pydantic-based tool definition schemas for AG2.

Extracted from Claude Code's tool type system:
- src/Tool.ts — Core Tool interface, inputSchema, outputSchema
- src/types/permissions.ts — Permission types

Patterns implemented:
1. Pydantic models mirroring the TS Tool interface
2. JSON Schema generation compatible with AG2/OpenAI function calling
3. Permission behavior definitions
4. Tool metadata (concurrency, read-only, destructive flags)
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Permission types (from src/types/permissions.ts)
# ---------------------------------------------------------------------------

class PermissionBehavior(str, Enum):
    """Permission decision for a tool call.

    Source: src/types/permissions.ts — PermissionBehavior
    """
    ALLOW = "allow"
    DENY = "deny"
    ASK = "ask"


class PermissionResult(BaseModel):
    """Result of a permission check.

    Source: src/utils/permissions/PermissionResult.ts
    """
    behavior: PermissionBehavior
    message: str = ""
    updated_input: dict[str, Any] | None = None


# ---------------------------------------------------------------------------
# Tool definition schema (from src/Tool.ts)
# ---------------------------------------------------------------------------

class ToolParameter(BaseModel):
    """A single parameter in a tool's input schema.

    Maps to properties within the Zod inputSchema in src/Tool.ts.
    """
    name: str
    type: str = "string"
    description: str = ""
    required: bool = True
    enum: list[str] | None = None
    default: Any = None


class ToolDefinition(BaseModel):
    """Schema for defining a tool compatible with AG2 and OpenAI function calling.

    Source: src/Tool.ts — Tool<Input, Output, P> interface

    This captures the essential metadata of a Claude Code tool and can
    generate the JSON Schema that AG2 and OpenAI APIs expect.
    """
    name: str = Field(..., description="Unique tool identifier")
    description: str = Field("", description="What the tool does")
    parameters: list[ToolParameter] = Field(default_factory=list)

    # Behavioral flags from src/Tool.ts
    is_read_only: bool = Field(False, description="Tool only reads, never modifies state")
    is_concurrency_safe: bool = Field(False, description="Safe to run in parallel")
    is_destructive: bool = Field(False, description="Can cause irreversible changes")
    max_result_size_chars: int = Field(50_000, description="Max output length")

    # Aliases (from src/Tool.ts — aliases field)
    aliases: list[str] = Field(default_factory=list)

    def to_function_schema(self) -> dict[str, Any]:
        """Convert to OpenAI function-calling schema.

        This is the format AG2 expects when registering tools via
        `function_map` or `@register_function`.

        Returns:
            Dict compatible with OpenAI's function schema format.
        """
        properties: dict[str, Any] = {}
        required: list[str] = []

        for param in self.parameters:
            prop: dict[str, Any] = {"type": param.type}
            if param.description:
                prop["description"] = param.description
            if param.enum:
                prop["enum"] = param.enum
            if param.default is not None:
                prop["default"] = param.default
            properties[param.name] = prop
            if param.required:
                required.append(param.name)

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }

    def to_ag2_tool_schema(self) -> dict[str, Any]:
        """Convert to AG2's tool schema format.

        AG2 uses a slightly different format for tool registration.
        """
        schema = self.to_function_schema()
        return schema["function"]


# ---------------------------------------------------------------------------
# Pre-built tool definitions matching Claude Code's built-in tools
# ---------------------------------------------------------------------------

FILE_READ_TOOL = ToolDefinition(
    name="read_file",
    description="Read the contents of a file at the given path.",
    parameters=[
        ToolParameter(name="file_path", type="string", description="Absolute path to the file"),
        ToolParameter(name="offset", type="integer", description="Line number to start from", required=False, default=0),
        ToolParameter(name="limit", type="integer", description="Max lines to read", required=False, default=2000),
    ],
    is_read_only=True,
    is_concurrency_safe=True,
)

FILE_EDIT_TOOL = ToolDefinition(
    name="file_edit",
    description="Edit a file by replacing an exact string match with new content.",
    parameters=[
        ToolParameter(name="file_path", type="string", description="Absolute path to the file"),
        ToolParameter(name="old_string", type="string", description="Exact string to find and replace"),
        ToolParameter(name="new_string", type="string", description="Replacement string"),
    ],
    is_read_only=False,
    is_concurrency_safe=False,
    is_destructive=False,
)

FILE_WRITE_TOOL = ToolDefinition(
    name="file_write",
    description="Create or overwrite a file with the given content.",
    parameters=[
        ToolParameter(name="file_path", type="string", description="Absolute path to the file"),
        ToolParameter(name="content", type="string", description="Content to write"),
    ],
    is_read_only=False,
    is_concurrency_safe=False,
    is_destructive=True,
)

BASH_TOOL = ToolDefinition(
    name="bash",
    description="Execute a bash command and return its output.",
    parameters=[
        ToolParameter(name="command", type="string", description="The command to execute"),
        ToolParameter(name="timeout", type="integer", description="Timeout in seconds", required=False, default=120),
    ],
    is_read_only=False,
    is_concurrency_safe=False,
    is_destructive=True,
)

GREP_TOOL = ToolDefinition(
    name="grep",
    description="Search file contents using regex patterns.",
    parameters=[
        ToolParameter(name="pattern", type="string", description="Regex pattern to search for"),
        ToolParameter(name="path", type="string", description="Directory or file to search", required=False),
        ToolParameter(name="glob", type="string", description="File glob filter", required=False),
    ],
    is_read_only=True,
    is_concurrency_safe=True,
)

GLOB_TOOL = ToolDefinition(
    name="glob",
    description="Find files matching a glob pattern.",
    parameters=[
        ToolParameter(name="pattern", type="string", description="Glob pattern (e.g. '**/*.py')"),
        ToolParameter(name="path", type="string", description="Base directory", required=False),
    ],
    is_read_only=True,
    is_concurrency_safe=True,
)

# All built-in tool definitions
BUILTIN_TOOLS: list[ToolDefinition] = [
    FILE_READ_TOOL,
    FILE_EDIT_TOOL,
    FILE_WRITE_TOOL,
    BASH_TOOL,
    GREP_TOOL,
    GLOB_TOOL,
]


# ---------------------------------------------------------------------------
# Quick test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json

    for tool in BUILTIN_TOOLS:
        schema = tool.to_function_schema()
        print(f"\n{tool.name} (read_only={tool.is_read_only}, concurrent={tool.is_concurrency_safe}):")
        print(json.dumps(schema, indent=2))
