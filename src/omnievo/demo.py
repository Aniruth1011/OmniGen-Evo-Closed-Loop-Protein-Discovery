"""Generate a dependency-free dashboard shell from real, completed artifacts."""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

from .artifacts import write_json


def build_dashboard(state: dict[str, Any], output_dir: str | Path) -> list[str]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    write_json(output / "demo_state.json", state)
    title = html.escape(str(state.get("title", "OmniEvo — GB1 Directed Evolution")))
    assays = html.escape(str(state.get("assays_used", "—")))
    best = html.escape(str(state.get("current_best", "—")))
    allocation = html.escape(str(state.get("allocation", "Awaiting real Omnigent run")))
    rationale = html.escape(str(state.get("policy_change_reason", "No result fabricated.")))
    trace = html.escape(str(state.get("handoff", "Critic → Planner → Virtual Lab")))
    document = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>{title}</title><style>
body{{font-family:Inter,system-ui,sans-serif;background:#0b1020;color:#eef3ff;margin:0;padding:2rem}}
main{{max-width:980px;margin:auto}} .grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:1rem}}
.card{{background:#151d34;border:1px solid #2a365d;border-radius:14px;padding:1.25rem}}
.wide{{grid-column:1/-1}} h1{{font-size:2rem}} .value{{font-size:2rem;color:#65d8ff}}
.trace{{font-size:1.4rem;color:#b9f3c5}} small{{color:#9eabc8}} @media(max-width:700px){{.grid{{grid-template-columns:1fr}}}}
</style></head><body><main><h1>{title}</h1><p>96 assays · four rounds · hidden GB1 oracle</p>
<section class="grid"><div class="card"><small>Assays used</small><div class="value">{assays} / 96</div></div>
<div class="card"><small>Current best fitness</small><div class="value">{best}</div></div>
<div class="card wide"><small>Current allocation</small><h2>{allocation}</h2></div>
<div class="card wide"><small>Why the plan changed</small><p>{rationale}</p></div>
<div class="card wide"><small>Visible Omnigent handoff</small><p class="trace">{trace}</p></div></section>
<p><small>This dashboard must be populated only from a completed real run; representative traces are labeled separately from aggregate conclusions.</small></p>
</main></body></html>"""
    dashboard_path = output / "index.html"
    dashboard_path.write_text(document, encoding="utf-8")
    return [str(output / "demo_state.json"), str(dashboard_path)]

