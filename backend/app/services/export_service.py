"""Generates downloadable report files (JSON and Markdown) for a project."""
import json
from datetime import datetime, timezone
from typing import Any


def build_report_dict(project: dict[str, Any], endpoints: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project": {
            "name": project["name"],
            "description": project.get("description"),
            "source_type": project["source_type"],
            "base_url": project.get("base_url"),
            "auth_type": project.get("auth_type"),
            "ai_summary": project.get("ai_summary"),
            "risk_report": project.get("risk_report"),
            "endpoint_count": len(endpoints),
        },
        "endpoints": endpoints,
    }


def export_as_json(project: dict[str, Any], endpoints: list[dict[str, Any]]) -> str:
    return json.dumps(build_report_dict(project, endpoints), indent=2, default=str)


def export_as_markdown(project: dict[str, Any], endpoints: list[dict[str, Any]]) -> str:
    lines = [
        f"# {project['name']} — API Investigation Report",
        "",
        f"*Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}*",
        "",
        "## Overview",
        project.get("description") or "_No description provided._",
        "",
        f"- **Source type:** {project['source_type']}",
        f"- **Base URL:** {project.get('base_url') or 'N/A'}",
        f"- **Auth type:** {project.get('auth_type') or 'Unknown'}",
        f"- **Total endpoints:** {len(endpoints)}",
        "",
        "## AI Summary",
        project.get("ai_summary") or "_No summary generated yet._",
        "",
    ]

    risk = project.get("risk_report")
    if risk:
        lines += [
            "## Risk Report",
            f"- High severity: {risk.get('high', 0)}",
            f"- Medium severity: {risk.get('medium', 0)}",
            f"- Low severity: {risk.get('low', 0)}",
            "",
        ]
        for issue in risk.get("issues", [])[:30]:
            lines.append(f"- **[{issue['severity'].upper()}]** `{issue['endpoint']}` — {issue['issue']}")
        lines.append("")

    lines.append("## Endpoints")
    for e in endpoints:
        lines.append(f"### `{e['method']} {e['path']}`")
        if e.get("summary"):
            lines.append(f"**Summary:** {e['summary']}")
        if e.get("description"):
            lines.append(f"\n{e['description']}\n")
        if e.get("ai_explanation"):
            lines.append(f"**AI Explanation:** {e['ai_explanation']}")
        lines.append("")

    return "\n".join(lines)
