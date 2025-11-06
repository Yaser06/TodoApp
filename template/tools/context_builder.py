#!/usr/bin/env python3
"""
Aggregate YAML from the AI project template into structured JSON payload with lazy loading support.

NEW: Supports core/work/reference directory structure for token-optimized loading.
Agents can request minimal (core only), standard (core+work), or full (all) context.
"""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Tuple

try:
    import yaml  # type: ignore
except ImportError as exc:  # pragma: no cover - graceful error for missing dependency
    raise SystemExit(
        "PyYAML bulunamadı. Lütfen `pip install pyyaml` komutu ile yükleyin."
    ) from exc


def load_frontmatter(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    try:
        _, remainder = text.split("---", 1)
        front_raw, _ = remainder.split("---", 1)
    except ValueError:
        return {}
    data = yaml.safe_load(front_raw) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Front matter must be a mapping: {path}")
    return data


def normalise_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def merge_command_lists(
    global_list: List[Dict[str, Any]], stack_list: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    merged: List[Dict[str, Any]] = []
    stack_index = {item.get("name"): deepcopy(item) for item in stack_list if item.get("name")}
    for item in global_list:
        name = item.get("name")
        stack_item = stack_index.pop(name, None)
        combined = deepcopy(item)
        if stack_item:
            for key, value in stack_item.items():
                if value not in (None, "", []):
                    combined[key] = value
        if not combined.get("command") and stack_item:
            combined["command"] = stack_item.get("command")
        merged.append(combined)
    merged.extend(stack_index.values())
    return merged


def merge_quality_gates(
    base: Dict[str, Any], stack: Dict[str, Any]
) -> Dict[str, Any]:
    result = deepcopy(base)
    for key, value in stack.items():
        if isinstance(value, list):
            existing = normalise_list(result.get(key))
            appended = [item for item in value if item not in existing]
            result[key] = existing + appended
        elif value not in ("", None):
            result[key] = value
    return result


def merge_monitoring(
    base: List[Dict[str, Any]], stack: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    if not base:
        return stack
    if not stack:
        return base
    result = deepcopy(base)
    existing_keys = {(item.get("metric"), item.get("target")) for item in result}
    for item in stack:
        key = (item.get("metric"), item.get("target"))
        if key not in existing_keys:
            result.append(item)
    return result


def merge_auto_tasks(
    base: List[Dict[str, Any]], stack: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    if not base:
        return stack
    if not stack:
        return base
    result = deepcopy(base)
    trigger_index = {item.get("trigger"): item for item in result if item.get("trigger")}
    for item in stack:
        trigger = item.get("trigger")
        if not trigger:
            result.append(item)
            continue
        existing = trigger_index.get(trigger)
        if existing:
            base_actions = normalise_list(existing.get("actions"))
            new_actions = [act for act in normalise_list(item.get("actions")) if act not in base_actions]
            existing["actions"] = base_actions + new_actions
        else:
            clone = deepcopy(item)
            result.append(clone)
            trigger_index[trigger] = clone
    return result


def merge_automation(
    global_runbook: Dict[str, Any], stack_runbook: Dict[str, Any]
) -> Dict[str, Any]:
    merged: Dict[str, Any] = {}
    sections = ["setup", "dev", "test", "build", "deploy"]
    for section in sections:
        merged[section] = merge_command_lists(
            normalise_list(global_runbook.get(section)),
            normalise_list(stack_runbook.get(section)),
        )
    merged["qualityGates"] = merge_quality_gates(
        global_runbook.get("qualityGates", {}), stack_runbook.get("qualityGates", {})
    )
    merged["monitoring"] = merge_monitoring(
        normalise_list(global_runbook.get("monitoring")),
        normalise_list(stack_runbook.get("monitoring")),
    )
    merged["autoTasks"] = merge_auto_tasks(
        normalise_list(global_runbook.get("autoTasks")),
        normalise_list(stack_runbook.get("autoTasks")),
    )
    merged["updatedAt"] = stack_runbook.get("updatedAt") or global_runbook.get("updatedAt", "")
    merged["updatedBy"] = stack_runbook.get("updatedBy") or global_runbook.get("updatedBy", "")
    return merged


def load_yaml_file(path: Path) -> Dict[str, Any]:
    """Load pure YAML file (not Markdown with frontmatter)"""
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    data = yaml.safe_load(text) or {}
    if not isinstance(data, dict):
        raise ValueError(f"YAML must be a mapping: {path}")
    return data


def validate_and_fallback_stack(
    stack_id: str, validation_file: Path
) -> Tuple[str, bool, str]:
    """
    Validate stack_id and apply fallback if needed.

    Returns:
        Tuple[str, bool, str]: (actual_stack_id, is_fallback_used, warning_message)
    """
    if not validation_file.exists():
        # No validation file, allow any stack
        return stack_id, False, ""

    validation = load_yaml_file(validation_file)

    valid_stacks = validation.get("validStacks", [])
    fallback_mapping = validation.get("fallbackMapping", {})

    # Check if stack is valid
    if stack_id in valid_stacks:
        return stack_id, False, ""

    # Check fallback mapping
    if stack_id in fallback_mapping:
        fallback_stack = fallback_mapping[stack_id]
        warning = f"""
⚠️  Stack Warning:
   Requested: {stack_id}
   Not available in agents-stack/
   Using fallback: {fallback_stack}

   To add {stack_id} support, create agents-stack/{stack_id}/ with required files.
"""
        return fallback_stack, True, warning

    # No fallback, use generic
    warning = f"""
⚠️  Stack Warning:
   Requested: {stack_id}
   Not available in agents-stack/
   No fallback mapping defined.
   Using: generic (universal rules)

   To add {stack_id} support, create agents-stack/{stack_id}/ with required files.
   Or add fallback mapping in memory-bank/stack-validation.yaml
"""
    return "generic", True, warning


def build_context(
    template_root: Path,
    override_stack_id: str | None = None,
    mode: str = "minimal"  # minimal | standard | full
) -> Dict[str, Any]:
    """
    Build context payload with lazy loading support.

    Modes:
    - minimal: core/ only (~3K tokens)
    - standard: core/ + work/ (~5K tokens)
    - full: core/ + work/ + reference/ (~15K tokens)
    """
    memory_dir = template_root / "memory-bank"
    automation_dir = template_root / "automation"
    stack_dir = template_root / "agents-stack"

    # Load core (always)
    core_dir = memory_dir / "core"
    project_yaml = load_yaml_file(core_dir / "project.yaml")
    active_yaml = load_yaml_file(core_dir / "active.yaml")

    stack_id = override_stack_id or project_yaml.get("STACK_ID")
    if not stack_id:
        raise SystemExit("STACK_ID missing in memory-bank/core/project.yaml")

    # Validate stack and apply fallback if needed
    validation_file = memory_dir / "stack-validation.yaml"
    validated_stack_id, is_fallback, warning = validate_and_fallback_stack(stack_id, validation_file)

    if warning:
        print(warning, file=sys.stderr)

    # Use validated stack_id
    stack_id = validated_stack_id

    # Core context (always loaded)
    core_context = {
        "project": project_yaml,
        "active": active_yaml,
        "strategy": load_frontmatter(memory_dir / "context-strategy.md"),
        "tokenMonitoring": load_frontmatter(memory_dir / "token-monitoring.md"),
    }

    # Work context (standard mode)
    work_context = {}
    if mode in ("standard", "full"):
        work_dir = memory_dir / "work"
        work_context = {
            "backlog": load_yaml_file(work_dir / "backlog.yaml"),
            "sprintMetrics": load_yaml_file(work_dir / "sprint-metrics.yaml"),
            "progressDelta": {},  # JSON file, handle separately
        }

        delta_file = memory_dir / "progress-delta.json"
        if delta_file.exists():
            import json
            work_context["progressDelta"] = json.loads(delta_file.read_text())

    # Reference context (full mode only)
    reference_context = {}
    if mode == "full":
        ref_dir = memory_dir / "reference"
        reference_context = {
            "techStack": load_yaml_file(ref_dir / "tech-stack.yaml"),
            "patterns": load_yaml_file(ref_dir / "patterns.yaml"),
            "delivery": load_yaml_file(ref_dir / "delivery.yaml"),
            "history": load_yaml_file(ref_dir / "history.yaml"),
        }

    # Load stack profiles (only in full mode or explicit)
    stack_profiles = {}
    if mode == "full":
        stack_path = stack_dir / str(stack_id)
        if stack_path.exists():
            stack_profiles = {
                "techProfile": load_frontmatter(stack_path / "techProfile.md"),
                "patternProfile": load_frontmatter(stack_path / "patternProfile.md"),
                "stackRules": load_frontmatter(stack_path / "agentsrules"),
                "automation": load_frontmatter(stack_path / "automation.md"),
            }

    # Load automation (only in standard/full)
    automation_context = {}
    if mode in ("standard", "full"):
        global_runbook = load_frontmatter(automation_dir / "runbook.md")
        if stack_profiles:
            merged_automation = merge_automation(
                global_runbook, stack_profiles.get("automation", {})
            )
            automation_context = {
                "global": global_runbook,
                "stack": stack_profiles.get("automation", {}),
                "merged": merged_automation,
            }
        else:
            automation_context = {"global": global_runbook}

    # Load global rules (only in full)
    global_rules = {}
    if mode == "full":
        global_rules = load_frontmatter(template_root / "agentsrules")

    # Assemble context based on mode
    context = {
        "version": "2.0",
        "mode": mode,
        "stackId": stack_id,
        "core": core_context,
        "work": work_context,
        "reference": reference_context,
        "stackProfiles": stack_profiles,
        "automation": automation_context,
        "globalRules": global_rules,
        "estimatedTokens": _estimate_tokens(mode, core_context, work_context, reference_context),
    }
    return context


def _estimate_tokens(mode: str, core: Dict, work: Dict, ref: Dict) -> Dict[str, int]:
    """Rough token estimation"""
    import json

    core_tokens = len(json.dumps(core)) // 4
    work_tokens = len(json.dumps(work)) // 4 if work else 0
    ref_tokens = len(json.dumps(ref)) // 4 if ref else 0

    return {
        "core": core_tokens,
        "work": work_tokens,
        "reference": ref_tokens,
        "total": core_tokens + work_tokens + ref_tokens,
        "mode": mode,
    }


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build AI project context with lazy loading support."
    )
    parser.add_argument(
        "--template-root",
        default=Path(__file__).resolve().parent.parent,
        type=Path,
        help="Path to the template directory (default: script/../..)",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output.",
    )
    parser.add_argument(
        "--stack-id",
        type=str,
        help="Override STACK_ID from core/project.yaml",
    )
    parser.add_argument(
        "--mode",
        choices=["minimal", "standard", "full"],
        default="minimal",
        help="Context loading mode: minimal (~3K tokens), standard (~5K), full (~15K)",
    )
    args = parser.parse_args(argv)

    context = build_context(
        args.template_root.resolve(),
        override_stack_id=args.stack_id,
        mode=args.mode
    )

    json_kwargs: Dict[str, Any] = {"ensure_ascii": False}
    if args.pretty:
        json_kwargs["indent"] = 2

    json.dump(context, sys.stdout, **json_kwargs)
    sys.stdout.write("\n")

    # Print token estimate to stderr for monitoring
    if "estimatedTokens" in context:
        est = context["estimatedTokens"]
        sys.stderr.write(f"\n[context_builder] Mode: {est['mode']}, Tokens: {est['total']}\n")
        sys.stderr.write(f"  core: {est['core']}, work: {est['work']}, reference: {est['reference']}\n")

    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry
    raise SystemExit(main())
