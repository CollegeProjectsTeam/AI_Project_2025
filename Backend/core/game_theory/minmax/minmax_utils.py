from __future__ import annotations

import json
from typing import Any, Dict, List, Tuple

from Backend.services.logging_service import Logger

log = Logger("MinMax.Utils")

TreeNode = Dict[str, Any]

def is_leaf(node: TreeNode) -> bool:
    return isinstance(node, dict) and "value" in node and "children" not in node

def validate_tree(node: Any) -> Tuple[bool, str]:
    if not isinstance(node, dict):
        return False, "tree must be an object/dict"

    if is_leaf(node):
        v = node.get("value")
        if not isinstance(v, int):
            return False, "leaf.value must be int"
        return True, ""

    children = node.get("children")
    if not isinstance(children, list) or not children:
        return False, "internal node must have non-empty children list"

    for i, ch in enumerate(children):
        ok, err = validate_tree(ch)
        if not ok:
            return False, f"child[{i}]: {err}"

    return True, ""


def tree_to_ascii(root: TreeNode, root_player: str = "MAX") -> str:
    root_player = (root_player or "MAX").strip().upper()
    if root_player not in ("MAX", "MIN"):
        root_player = "MAX"

    lines: List[str] = []

    def rec(node: TreeNode, player: str, depth: int) -> None:
        indent = "  " * depth
        if is_leaf(node):
            lines.append(f"{indent}[{node['value']}]")
            return

        lines.append(f"{indent}{player}")
        next_player = "MIN" if player == "MAX" else "MAX"
        for ch in node.get("children", []):
            rec(ch, next_player, depth + 1)

    rec(root, root_player, 0)
    return "\n".join(lines)


def build_instance_string(instance_params: Dict[str, Any]) -> str:
    root_player = (instance_params.get("root_player") or "MAX").strip().upper()
    tree = instance_params.get("tree") or {}

    ok, err = validate_tree(tree)
    if not ok:
        log.warn("Invalid tree for instance_string", {"err": err})
        pretty = json.dumps(instance_params, indent=2, ensure_ascii=False)
        return "\n" + pretty + "\n"

    ascii_tree = tree_to_ascii(tree, root_player)
    meta = {
        "root_player": root_player,
        "note": "left-to-right child order",
    }
    meta_str = json.dumps(meta, indent=2, ensure_ascii=False)
    return "\n" + meta_str + "\n\n" + ascii_tree + "\n"
