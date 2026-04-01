"""
Tool Executor — Execute tool calls with permission checks, hooks, and concurrency.

Extracted from Claude Code's tool execution pipeline:
- src/services/tools/toolExecution.ts — Core execution with pre/post hooks
- src/services/tools/toolOrchestration.ts — Batch orchestration (concurrent/serial)
- src/services/tools/toolHooks.ts — Pre/post tool hooks

Patterns implemented:
1. Sequential and concurrent tool execution
2. Pre/post execution hooks
3. Permission checking before execution
4. Result truncation and error handling
5. AG2-compatible tool execution wrapper
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable

from ag2_patterns.tools.schemas import PermissionBehavior, PermissionResult
from ag2_patterns.tools.tool_registry import ToolEntry, ToolRegistry

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

@dataclass
class ToolCallRequest:
    """A pending tool call request.

    Source: src/services/tools/toolExecution.ts — ToolUseBlock
    """
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class ToolCallResult:
    """Result of a tool execution.

    Source: src/Tool.ts — ToolResult<T>
    """
    id: str
    name: str
    success: bool
    output: str
    error: str | None = None
    duration_ms: float = 0
    was_denied: bool = False


# Hook types
PreHook = Callable[[ToolCallRequest], ToolCallRequest | None]
PostHook = Callable[[ToolCallRequest, ToolCallResult], ToolCallResult]


# ---------------------------------------------------------------------------
# Tool Executor
# ---------------------------------------------------------------------------

class ToolExecutor:
    """Execute tool calls with permission checks, hooks, and batching.

    Source: src/services/tools/toolExecution.ts + toolOrchestration.ts

    This implements the full Claude Code tool execution pipeline:
    1. Parse and validate tool call
    2. Run pre-hooks (can modify input or block execution)
    3. Check permissions
    4. Execute tool function
    5. Run post-hooks (can modify output)
    6. Truncate result if too long

    Example::

        executor = ToolExecutor(registry)
        executor.add_pre_hook(log_tool_calls)
        executor.add_post_hook(truncate_results)

        results = await executor.execute_batch([
            ToolCallRequest(id="1", name="read_file", arguments={"file_path": "main.py"}),
            ToolCallRequest(id="2", name="grep", arguments={"pattern": "TODO"}),
        ])
    """

    def __init__(
        self,
        registry: ToolRegistry,
        max_result_chars: int = 50_000,
        permission_checker: Callable[[str, dict[str, Any]], PermissionResult] | None = None,
    ):
        self.registry = registry
        self.max_result_chars = max_result_chars
        self.permission_checker = permission_checker
        self._pre_hooks: list[PreHook] = []
        self._post_hooks: list[PostHook] = []

    def add_pre_hook(self, hook: PreHook) -> None:
        """Add a pre-execution hook.

        Source: src/services/tools/toolHooks.ts — executePreToolHooks()

        Pre-hooks can:
        - Modify the tool input (return modified request)
        - Block execution (return None)
        """
        self._pre_hooks.append(hook)

    def add_post_hook(self, hook: PostHook) -> None:
        """Add a post-execution hook.

        Source: src/services/tools/toolHooks.ts — executePostToolHooks()

        Post-hooks can modify the tool result.
        """
        self._post_hooks.append(hook)

    def execute_single(self, request: ToolCallRequest) -> ToolCallResult:
        """Execute a single tool call synchronously.

        Source: src/services/tools/toolExecution.ts — core execution flow
        """
        start_time = time.time()

        # Step 1: Run pre-hooks
        current_request: ToolCallRequest | None = request
        for hook in self._pre_hooks:
            if current_request is None:
                break
            current_request = hook(current_request)

        if current_request is None:
            return ToolCallResult(
                id=request.id,
                name=request.name,
                success=False,
                output="",
                error="Blocked by pre-hook",
                was_denied=True,
            )
        request = current_request

        # Step 2: Look up tool
        entry = self.registry.get(request.name)
        if entry is None:
            return ToolCallResult(
                id=request.id,
                name=request.name,
                success=False,
                output="",
                error=f"Unknown tool: {request.name}",
            )

        # Step 3: Check permissions
        perm = self._check_permission(entry, request.arguments)
        if perm.behavior == PermissionBehavior.DENY:
            return ToolCallResult(
                id=request.id,
                name=request.name,
                success=False,
                output="",
                error=f"Permission denied: {perm.message}",
                was_denied=True,
            )

        # Use updated input if permission check modified it
        args = perm.updated_input if perm.updated_input else request.arguments

        # Step 4: Execute
        try:
            raw_result = entry.implementation(**args)
            output = self._format_output(raw_result)
            result = ToolCallResult(
                id=request.id,
                name=request.name,
                success=True,
                output=output,
                duration_ms=(time.time() - start_time) * 1000,
            )
        except Exception as exc:
            result = ToolCallResult(
                id=request.id,
                name=request.name,
                success=False,
                output="",
                error=str(exc),
                duration_ms=(time.time() - start_time) * 1000,
            )

        # Step 5: Run post-hooks
        for hook in self._post_hooks:
            result = hook(request, result)

        # Step 6: Truncate if needed
        if len(result.output) > self.max_result_chars:
            truncated = result.output[: self.max_result_chars]
            result.output = (
                truncated
                + f"\n\n[Output truncated: {len(result.output)} chars → {self.max_result_chars}]"
            )

        return result

    async def execute_single_async(self, request: ToolCallRequest) -> ToolCallResult:
        """Execute a single tool call asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.execute_single, request)

    async def execute_batch(
        self, requests: list[ToolCallRequest]
    ) -> list[ToolCallResult]:
        """Execute a batch of tool calls, respecting concurrency.

        Source: src/services/tools/toolOrchestration.ts — runTools()

        Uses the registry's partition_for_execution() to determine
        which calls can run concurrently and which must be serial.
        """
        # Convert requests to dicts for partitioning
        call_dicts = [
            {"name": r.name, "arguments": r.arguments, "_request": r}
            for r in requests
        ]

        batches = self.registry.partition_for_execution(call_dicts)
        results: list[ToolCallResult] = []

        for batch in batches:
            if len(batch) == 1:
                # Serial execution
                req = batch[0]["_request"]
                results.append(self.execute_single(req))
            else:
                # Concurrent execution
                tasks = [
                    self.execute_single_async(call["_request"])
                    for call in batch
                ]
                batch_results = await asyncio.gather(*tasks)
                results.extend(batch_results)

        return results

    def execute_batch_sync(
        self, requests: list[ToolCallRequest]
    ) -> list[ToolCallResult]:
        """Execute a batch synchronously (all serial, no async).

        Simpler alternative when you don't need async concurrency.
        """
        return [self.execute_single(req) for req in requests]

    def _check_permission(
        self, entry: ToolEntry, args: dict[str, Any]
    ) -> PermissionResult:
        """Check permissions for a tool call.

        Source: src/services/tools/toolExecution.ts — permission check step
        """
        # Global permission checker first
        if self.permission_checker:
            result = self.permission_checker(entry.name, args)
            if result.behavior == PermissionBehavior.DENY:
                return result

        # Tool-specific permission checker
        return entry.check_permissions(args)

    def _format_output(self, raw: Any) -> str:
        """Format tool output to string."""
        if isinstance(raw, str):
            return raw
        try:
            return json.dumps(raw, indent=2, default=str)
        except (TypeError, ValueError):
            return str(raw)


# ---------------------------------------------------------------------------
# AG2 Integration: Tool execution wrapper for agents
# ---------------------------------------------------------------------------

def create_ag2_tool_executor(
    registry: ToolRegistry,
    max_result_chars: int = 50_000,
) -> dict[str, Callable[..., str]]:
    """Create an AG2-compatible function_map with built-in execution pipeline.

    This wraps each tool's implementation with:
    - Permission checking
    - Result truncation
    - Error handling
    - Logging

    Returns:
        Dict mapping tool_name → wrapped callable, for use with
        AG2's `register_function(function_map=...)`.

    Example::

        function_map = create_ag2_tool_executor(registry)
        user_proxy = UserProxyAgent(
            "executor",
            function_map=function_map,
            code_execution_config=False,
        )
    """
    executor = ToolExecutor(registry, max_result_chars=max_result_chars)

    def make_wrapper(tool_name: str) -> Callable[..., str]:
        def wrapper(**kwargs: Any) -> str:
            request = ToolCallRequest(
                id=f"call_{tool_name}_{id(kwargs)}",
                name=tool_name,
                arguments=kwargs,
            )
            result = executor.execute_single(request)
            if result.success:
                return result.output
            return f"Error: {result.error}"

        wrapper.__name__ = tool_name
        wrapper.__doc__ = f"Execute {tool_name} tool"
        return wrapper

    return {name: make_wrapper(name) for name in registry.tool_names}


# ---------------------------------------------------------------------------
# Quick test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from ag2_patterns.tools.schemas import BUILTIN_TOOLS

    # Set up registry with mock implementations
    registry = ToolRegistry()
    for tool_def in BUILTIN_TOOLS:
        registry.register(
            tool_def,
            implementation=lambda **kw: f"Mock result: {list(kw.keys())}",
        )

    # Create executor
    executor = ToolExecutor(registry)

    # Add a logging pre-hook
    def log_hook(req: ToolCallRequest) -> ToolCallRequest:
        print(f"  [pre-hook] Executing: {req.name}({list(req.arguments.keys())})")
        return req

    executor.add_pre_hook(log_hook)

    # Execute some tool calls
    requests = [
        ToolCallRequest(id="1", name="read_file", arguments={"file_path": "test.py"}),
        ToolCallRequest(id="2", name="grep", arguments={"pattern": "TODO"}),
        ToolCallRequest(id="3", name="bash", arguments={"command": "echo hello"}),
        ToolCallRequest(id="4", name="unknown_tool", arguments={}),
    ]

    print("Executing tool calls:")
    for req in requests:
        result = executor.execute_single(req)
        status = "OK" if result.success else f"FAIL: {result.error}"
        print(f"  {req.name}: {status}")

    # Test AG2 wrapper
    print("\nAG2 function_map:")
    fmap = create_ag2_tool_executor(registry)
    for name, fn in fmap.items():
        print(f"  {name}: {fn(test='value')}")
