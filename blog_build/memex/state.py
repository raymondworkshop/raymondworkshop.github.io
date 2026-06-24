from typing import Any

_memex_ctx: dict[str, Any] = {}


def get_ctx() -> dict[str, Any]:
    return _memex_ctx


def set_ctx(ctx: dict[str, Any]) -> None:
    global _memex_ctx
    _memex_ctx = ctx
