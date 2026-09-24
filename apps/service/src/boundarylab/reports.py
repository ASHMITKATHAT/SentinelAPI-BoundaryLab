from __future__ import annotations

import html
import json
from typing import Any


def json_report(report: dict[str, Any]) -> bytes:
    return (json.dumps(report, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def html_report(report: dict[str, Any]) -> bytes:
    escape = lambda value: html.escape(str(value))
    case_count = len(report.get("cases", []))
    real_probe = report.get("policy_version") == "read-boundary-v1"
    scope_text = (
        f"This assessment applies only to the {case_count} declared read-boundary cases, configured identities, "
        "resource marker and target build."
        if real_probe
        else f"This assessment applies only to the {case_count} declared invoice-sharing cases and this build."
    )
    case_rows = "".join(
        "<tr>"
        f"<td><code>{escape(case['case_id'])}</code></td>"
        f"<td>{escape(case['name'])}</td>"
        f"<td><span class='status {escape(case['verdict'])}'>{escape(case['verdict'])}</span></td>"
        f"<td>{escape(case['expected'])}</td>"
        f"<td>{escape(case['observed'])}</td>"
        "</tr>"
        for case in report.get("cases", [])
    )
    counts = report.get("counts", {})
    document = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BoundaryLab report · {escape(report.get('target_alias'))}</title>
<style>
:root{{--navy:#0c1b33;--navy2:#172a46;--red:#c9343b;--redsoft:#fff0f1;--grey:#667085;--line:#d8dee8;--paper:#fff;--canvas:#f4f6f9;--green:#16724a;--amber:#925f00}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--canvas);color:var(--navy);font:14px/1.55 system-ui,sans-serif}}main{{max-width:1180px;margin:0 auto;padding:40px 24px}}header{{background:var(--navy);color:white;padding:28px;border-radius:16px}}h1{{margin:4px 0;font-size:30px}}h2{{margin-top:32px}}.eyebrow{{text-transform:uppercase;letter-spacing:.12em;font-size:11px;color:#c8d4e8}}.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:18px}}.metric{{background:white;color:var(--navy);border-radius:10px;padding:14px}}.metric b{{display:block;font-size:24px}}.assessment{{background:{'#fff0f1' if report.get('assessment') == 'blocked' else '#eaf7f0'};color:{'#9e2028' if report.get('assessment') == 'blocked' else '#14643f'};padding:7px 10px;border-radius:999px;font-weight:750}}.panel{{margin-top:18px;background:white;border:1px solid var(--line);border-radius:14px;padding:20px;overflow:auto}}table{{width:100%;border-collapse:collapse;min-width:880px}}th,td{{text-align:left;padding:11px;border-bottom:1px solid #e8ecf2;vertical-align:top}}th{{color:var(--grey);font-size:12px}}code{{font-family:ui-monospace,monospace}}.status{{font-weight:750}}.status.violation{{color:var(--red)}}.status.pass{{color:var(--green)}}.status.inconclusive{{color:var(--amber)}}.scope{{color:var(--grey)}}@media print{{body{{background:white}}main{{padding:0}}header{{border-radius:0}}}}
</style></head><body><main>
<header><div class="eyebrow">SentinelAPI BoundaryLab · tested-scope report</div><h1>{escape(report.get('target_alias'))}</h1>
<p>Build <code>{escape(report.get('build_id'))}</code> · Policy <code>{escape(report.get('policy_version'))}</code></p>
<span class="assessment">{escape(report.get('assessment'))}</span>
<div class="grid"><div class="metric"><span>Pass</span><b>{escape(counts.get('pass', 0))}</b></div><div class="metric"><span>Violations</span><b>{escape(counts.get('violation', 0))}</b></div><div class="metric"><span>Inconclusive</span><b>{escape(counts.get('inconclusive', 0))}</b></div><div class="metric"><span>Requests</span><b>{escape(report.get('request_count', 0))}</b></div></div></header>
<section class="panel"><h2>Executive interpretation</h2><p>{escape(scope_text)} A blocked result contains a policy violation or legitimate-use regression. A pass does not establish security outside the tested scope.</p><p class="scope">Cleanup: {escape(report.get('cleanup_status'))} · Incomplete context: {escape(report.get('has_incomplete_cases'))} · Execution error: {escape(report.get('execution_error'))}</p></section>
<section class="panel"><h2>Case evidence</h2><table><thead><tr><th>Case</th><th>Promise</th><th>Verdict</th><th>Expected</th><th>Observed</th></tr></thead><tbody>{case_rows}</tbody></table></section>
</main></body></html>"""
    return document.encode("utf-8")
