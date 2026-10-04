#!/usr/bin/env python3
"""Build presentation-ready OmniEvo figures and a self-contained HTML deck."""

from __future__ import annotations

import json
import os
from collections import defaultdict
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/omnievo-matplotlib")
os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "runs/adaptive/omnigent_seed_000"
OUT = ROOT / "artifacts/presentation"

BG = "#0B1020"
PANEL = "#151D34"
GRID = "#33415F"
TEXT = "#F5F7FF"
MUTED = "#A8B3CF"
ACCENT = "#2DD4BF"
PURPLE = "#8B7CF6"
BLUE = "#43A5FF"
GOLD = "#F4C95D"
CORAL = "#FF6B6B"
GREEN = "#7EE787"

ACTION_ORDER = [
    "RANDOM_SAMPLE",
    "EXPLOIT_MODEL",
    "EXPLORE_UNCERTAIN",
    "EXPLORE_DIVERSE",
    "LOCAL_MUTATE",
]
ACTION_LABELS = {
    "RANDOM_SAMPLE": "Random",
    "EXPLOIT_MODEL": "Model exploit",
    "EXPLORE_UNCERTAIN": "Uncertainty",
    "EXPLORE_DIVERSE": "Diversity",
    "LOCAL_MUTATE": "Local mutate",
}
ACTION_COLORS = {
    "RANDOM_SAMPLE": "#64748B",
    "EXPLOIT_MODEL": BLUE,
    "EXPLORE_UNCERTAIN": PURPLE,
    "EXPLORE_DIVERSE": GOLD,
    "LOCAL_MUTATE": ACCENT,
}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def setup_ax(ax, title: str, subtitle: str | None = None):
    ax.set_facecolor(BG)
    ax.tick_params(colors=MUTED, labelsize=10)
    for spine in ax.spines.values():
        spine.set_color(GRID)
    ax.grid(color=GRID, alpha=0.35, linewidth=0.8)
    ax.set_title(title, loc="left", color=TEXT, fontsize=19, fontweight="bold", pad=18)
    if subtitle:
        ax.text(0, 1.01, subtitle, transform=ax.transAxes, color=MUTED, fontsize=10, va="bottom")


def save(fig, name: str):
    path = OUT / name
    fig.savefig(path, dpi=220, facecolor=BG, bbox_inches="tight")
    plt.close(fig)
    return path


def trajectory(rows):
    rows = sorted(rows, key=lambda x: x["assay_index_global"])
    x = np.array([row["assay_index_global"] for row in rows])
    y = np.array([row["fitness"] for row in rows])
    cumulative = np.maximum.accumulate(y)
    fig, ax = plt.subplots(figsize=(12.8, 7.2), facecolor=BG)
    for r, color in zip(range(1, 5), ["#11182A", "#151D34", "#11182A", "#151D34"]):
        ax.axvspan((r - 1) * 24 + 0.5, r * 24 + 0.5, color=color, zorder=0)
        ax.text((r - 0.5) * 24, 4.72, f"ROUND {r}", ha="center", color=MUTED, fontsize=9, fontweight="bold")
    for action in ACTION_ORDER:
        mask = np.array([row["source_action"] == action for row in rows])
        if mask.any():
            ax.scatter(x[mask], y[mask], s=32, alpha=0.72, color=ACTION_COLORS[action],
                       label=ACTION_LABELS[action], edgecolor="none", zorder=3)
    ax.step(x, cumulative, where="post", color=TEXT, linewidth=3.0, zorder=4, label="Best so far")
    for seq in ("CNGA", "INGA", "IYGV"):
        row = next(item for item in rows if item["sequence"] == seq)
        ax.scatter(row["assay_index_global"], row["fitness"], s=150, facecolor=CORAL,
                   edgecolor=TEXT, linewidth=1.5, zorder=5)
        offset = (8, 14) if seq != "IYGV" else (-76, 14)
        ax.annotate(f"{seq}  {row['fitness']:.3f}",
                    (row["assay_index_global"], row["fitness"]), xytext=offset,
                    textcoords="offset points", color=TEXT, fontsize=11, fontweight="bold",
                    arrowprops={"arrowstyle": "-", "color": MUTED})
    setup_ax(ax, "Discovery trajectory: 96 measurements, four decisions",
             "Dots are measured variants; the white line is the best fitness observed so far.")
    ax.set_xlim(0, 98)
    ax.set_ylim(-0.12, 5.0)
    ax.set_xlabel("Successful assay number", color=MUTED, fontsize=11)
    ax.set_ylabel("Measured GB1 fitness", color=MUTED, fontsize=11)
    ax.legend(ncol=3, loc="upper left", frameon=False, labelcolor=TEXT, fontsize=9)
    ax.text(0.99, 0.04, "Development run • seed 0 • single measurements",
            transform=ax.transAxes, ha="right", color=MUTED, fontsize=9)
    fig.tight_layout()
    return save(fig, "01_discovery_trajectory.png")


def allocation():
    allocations = {
        1: {"RANDOM_SAMPLE": 24},
        **{r: read_json(RUN / f"round_{r:02d}/planner_decision.json")["allocation"] for r in (2, 3, 4)},
    }
    fig, ax = plt.subplots(figsize=(12.8, 7.2), facecolor=BG)
    bottoms = np.zeros(4)
    rounds = np.arange(1, 5)
    for action in ACTION_ORDER:
        values = np.array([allocations[r].get(action, 0) for r in rounds])
        bars = ax.bar(rounds, values, bottom=bottoms, color=ACTION_COLORS[action], width=0.68,
                      label=ACTION_LABELS[action], edgecolor=BG, linewidth=1.2)
        for bar, value, bottom in zip(bars, values, bottoms):
            if value >= 2:
                ax.text(bar.get_x() + bar.get_width() / 2, bottom + value / 2, str(int(value)),
                        ha="center", va="center", color=BG if action in {"EXPLORE_DIVERSE", "LOCAL_MUTATE"} else TEXT,
                        fontsize=11, fontweight="bold")
        bottoms += values
    setup_ax(ax, "Omnigent changed the assay allocation after every evidence update",
             "Each column is exactly 24 assays. The strategy mix—not the surrogate family—changed.")
    ax.set_xticks(rounds, ["R1\ncommon init", "R2\nexplore", "R3\nconfirm ridge", "R4\ntest interactions"])
    ax.set_ylim(0, 27)
    ax.set_ylabel("Assay slots", color=MUTED)
    ax.legend(ncol=5, loc="upper center", bbox_to_anchor=(0.5, -0.10), frameon=False,
              labelcolor=TEXT, fontsize=9)
    ax.text(2.5, 25.4, "8 low-yield exploration slots → exploit/local", color=GOLD,
            ha="center", fontsize=10, fontweight="bold")
    ax.annotate("", xy=(3, 24.6), xytext=(2, 24.6), arrowprops={"arrowstyle": "->", "color": GOLD, "lw": 2})
    ax.text(3.5, 25.4, "Plateau → 15 local + targeted doubles", color=ACCENT,
            ha="center", fontsize=10, fontweight="bold")
    fig.tight_layout()
    return save(fig, "02_adaptive_allocation.png")


def source_performance(rows):
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["source_action"]].append(float(row["fitness"]))
    order = ["RANDOM_SAMPLE", "EXPLORE_DIVERSE", "EXPLORE_UNCERTAIN", "LOCAL_MUTATE", "EXPLOIT_MODEL"]
    fig, ax = plt.subplots(figsize=(12.8, 7.2), facecolor=BG)
    rng = np.random.default_rng(7)
    for i, action in enumerate(order):
        values = np.array(grouped[action])
        jitter = rng.uniform(-0.13, 0.13, len(values))
        ax.scatter(values, np.full(len(values), i) + jitter, s=35, alpha=0.62,
                   color=ACTION_COLORS[action], edgecolor="none")
        ax.scatter(values.max(), i, s=150, marker="D", color=CORAL, edgecolor=TEXT, linewidth=1.2, zorder=5)
        ax.text(4.52, i, f"n={len(values)}   mean={values.mean():.2f}   max={values.max():.2f}",
                va="center", color=MUTED, fontsize=10)
    setup_ax(ax, "What each acquisition source returned",
             "Every dot is a measured variant; red diamonds mark each source maximum.")
    ax.set_yticks(range(len(order)), [ACTION_LABELS[a] for a in order])
    ax.set_xlabel("Measured fitness", color=MUTED)
    ax.set_xlim(-0.1, 6.2)
    ax.grid(axis="x", color=GRID, alpha=0.35)
    ax.grid(axis="y", visible=False)
    ax.axvline(2.83147206953, color=TEXT, linestyle="--", alpha=0.6)
    ax.text(2.86, 4.5, "INGA benchmark entering R4", color=MUTED, fontsize=9)
    fig.tight_layout()
    return save(fig, "03_source_performance.png")


def epistasis(rows):
    fitness = {row["sequence"]: float(row["fitness"]) for row in rows}
    bg = fitness["INGA"]
    pairs = [
        ("IYGV", fitness["IYGA"] + fitness["INGV"] - bg),
        ("FNGV", fitness["FNGA"] + fitness["INGV"] - bg),
        ("WNGV", fitness["WNGA"] + fitness["INGV"] - bg),
    ]
    expected = [value for _, value in pairs]
    observed = [fitness[seq] for seq, _ in pairs]
    labels = [seq for seq, _ in pairs]
    x = np.arange(len(labels))
    width = 0.34
    fig, ax = plt.subplots(figsize=(12.8, 7.2), facecolor=BG)
    ax.bar(x - width / 2, expected, width, color="#64748B", label="Additive expectation")
    bars = ax.bar(x + width / 2, observed, width, color=[ACCENT, CORAL, CORAL], label="Observed double")
    for i, bar in enumerate(bars):
        epsilon = observed[i] - expected[i]
        ax.text(bar.get_x() + bar.get_width() / 2, max(observed[i], 0) + 0.12,
                f"ε = {epsilon:+.2f}", ha="center", color=TEXT, fontsize=12, fontweight="bold")
    setup_ax(ax, "The winning double exposed sign-variable epistasis",
             "Additive expectation = single A + single B − INGA background. All values are single measurements.")
    ax.set_xticks(x, labels)
    ax.set_ylabel("Fitness", color=MUTED)
    ax.set_ylim(0, 5.1)
    ax.legend(frameon=False, labelcolor=TEXT, loc="upper right")
    ax.text(0, 4.72, "Strong positive synergy", ha="center", color=ACCENT, fontsize=11, fontweight="bold")
    ax.text(1.5, 4.72, "Antagonistic combinations", ha="center", color=CORAL, fontsize=11, fontweight="bold")
    fig.tight_layout()
    return save(fig, "04_epistasis.png")


def model_diagnostics():
    reports = [read_json(RUN / f"round_{r:02d}/surrogate_report.json") for r in range(1, 5)]
    rmse = [x["diagnostics"]["observed_cv_rmse"] for x in reports]
    rho = [x["diagnostics"]["observed_cv_spearman_rank_proxy"] for x in reports]
    n = [x["train_n"] for x in reports]
    rounds = np.arange(1, 5)
    fig, ax = plt.subplots(figsize=(12.8, 7.2), facecolor=BG)
    bars = ax.bar(rounds - 0.16, rmse, width=0.32, color=CORAL, alpha=0.9, label="CV RMSE")
    ax2 = ax.twinx()
    ax2.plot(rounds + 0.16, rho, color=ACCENT, marker="o", markersize=9, linewidth=3, label="CV Spearman")
    for r, b, size in zip(rounds, bars, n):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.03, f"n={size}", ha="center", color=MUTED, fontsize=9)
    setup_ax(ax, "The surrogate became rank-useful—but missed the breakthrough magnitude",
             "Observed-data-only cross-validation; ensemble spread is not calibrated posterior uncertainty.")
    ax.set_xticks(rounds, ["R1", "R2", "R3", "R4"])
    ax.set_ylabel("CV RMSE", color=CORAL)
    ax2.set_ylabel("CV Spearman rank proxy", color=ACCENT)
    ax2.tick_params(colors=ACCENT)
    ax2.spines["right"].set_color(ACCENT)
    ax.set_ylim(0, 0.9)
    ax2.set_ylim(-0.3, 0.8)
    ax.text(2.92, 0.79, "IYGV predicted 1.846\nobserved 4.388\nresidual +2.54",
            color=TEXT, fontsize=12, fontweight="bold",
            bbox={"boxstyle": "round,pad=0.5", "facecolor": PANEL, "edgecolor": PURPLE})
    handles = [bars, ax2.lines[0]]
    ax.legend(handles, ["CV RMSE", "CV Spearman"], frameon=False, labelcolor=TEXT, loc="upper left")
    fig.tight_layout()
    return save(fig, "05_model_diagnostics.png")


def orchestration():
    fig, ax = plt.subplots(figsize=(12.8, 7.2), facecolor=BG)
    ax.set_xlim(0, 12.8)
    ax.set_ylim(0, 7.2)
    ax.axis("off")
    ax.add_patch(FancyBboxPatch((1.4, 1.35), 10.0, 4.7, boxstyle="round,pad=0.18,rounding_size=0.2",
                                facecolor=PANEL, edgecolor=PURPLE, linewidth=2.2))
    ax.text(1.7, 5.68, "DATABRICKS OMNIGENT CONTROL PLANE", color=PURPLE, fontsize=12, fontweight="bold")
    boxes = [
        (0.2, 2.8, 1.55, 1.0, "Returned\nmeasurements", BLUE),
        (2.0, 3.65, 1.65, 1.0, "Hypothesis\nScientist", ACCENT),
        (4.0, 3.65, 1.65, 1.0, "Surrogate +\ncandidate tools", BLUE),
        (6.0, 3.65, 1.65, 1.0, "Scientific\nCritic", GOLD),
        (8.0, 3.65, 1.65, 1.0, "Experiment\nPlanner", PURPLE),
        (10.15, 2.8, 1.65, 1.0, "Virtual lab\n24 assays", CORAL),
    ]
    for x, y, w, h, label, color in boxes:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.12,rounding_size=0.12",
                                    facecolor=BG, edgecolor=color, linewidth=2))
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", color=TEXT, fontsize=10, fontweight="bold")
    centers = [(1.75, 3.3), (3.65, 4.15), (5.65, 4.15), (7.65, 4.15), (9.65, 4.15), (10.15, 3.3)]
    for start, end in zip(centers[:-1], centers[1:]):
        ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=15, color=MUTED, linewidth=1.8))
    ax.add_patch(FancyArrowPatch((11.8, 2.8), (11.8, 1.65), arrowstyle="-|>", mutation_scale=15, color=CORAL, linewidth=1.8))
    ax.add_patch(FancyArrowPatch((11.8, 1.65), (0.95, 2.75), connectionstyle="arc3,rad=-0.13",
                                 arrowstyle="-|>", mutation_scale=15, color=CORAL, linewidth=1.8))
    ax.plot([10.0, 10.0], [0.7, 6.45], linestyle="--", color=CORAL, linewidth=1.5)
    ax.text(10.06, 0.78, "HIDDEN-ORACLE BOUNDARY", rotation=90, color=CORAL, fontsize=9, fontweight="bold")
    ax.text(10.25, 1.02, "Full GB1 table\nnever enters agent context", color=MUTED, fontsize=10)
    ax.text(0.2, 6.65, "Evidence → critique → changed allocation → assay → evidence", color=TEXT, fontsize=22, fontweight="bold")
    ax.text(0.2, 6.25, "The adaptive decision is visible in Omnigent; deterministic tools enforce budgets and hidden data.", color=MUTED, fontsize=11)
    return save(fig, "06_omnigent_orchestration.png")


def adaptation_story():
    fig, ax = plt.subplots(figsize=(12.8, 7.2), facecolor=BG)
    ax.set_xlim(0, 12.8)
    ax.set_ylim(0, 7.2)
    ax.axis("off")
    panels = [
        (0.25, "ROUND 2 EVIDENCE", "INGA = 2.831", ["Exploit: 2/4 strong hits", "Uncertainty: 0/8 record hits", "Diversity: 0/6 record hits"], BLUE),
        (4.45, "ROUND 3 RESPONSE", "Allocation changed", ["Exploit 4→8", "Local 6→10", "Exploration 14→6", "Ridge mapped; best unchanged"], GOLD),
        (8.65, "ROUND 4 DECISION", "Test interactions", ["Local expanded to 15", "Targeted Hamming-2 doubles", "IYGV = 4.388", "+55% over entering best"], ACCENT),
    ]
    for x, heading, big, lines, color in panels:
        ax.add_patch(FancyBboxPatch((x, 1.35), 3.65, 4.65, boxstyle="round,pad=0.18,rounding_size=0.18",
                                    facecolor=PANEL, edgecolor=color, linewidth=2.2))
        ax.text(x + 0.25, 5.55, heading, color=color, fontsize=10, fontweight="bold")
        ax.text(x + 0.25, 4.78, big, color=TEXT, fontsize=20, fontweight="bold")
        for i, line in enumerate(lines):
            ax.text(x + 0.28, 4.05 - i * 0.62, f"• {line}", color=MUTED, fontsize=11)
    for x in (4.12, 8.32):
        ax.add_patch(FancyArrowPatch((x - 0.18, 3.65), (x + 0.18, 3.65), arrowstyle="-|>", mutation_scale=22,
                                     color=TEXT, linewidth=2))
    ax.text(0.25, 6.65, "The 2-minute story: Omnigent reacted to evidence, then found the breakthrough", color=TEXT, fontsize=20, fontweight="bold")
    ax.text(0.25, 0.62, "Representative development run only; adaptive value versus fixed mixture remains a paired-seed hypothesis.", color=MUTED, fontsize=10)
    return save(fig, "07_adaptation_story.png")


def confirmation_gap():
    fig, ax = plt.subplots(figsize=(12.8, 7.2), facecolor=BG)
    ax.axis("off")
    ax.text(0.04, 0.90, "What this run proves—and what it does not", transform=ax.transAxes,
            color=TEXT, fontsize=22, fontweight="bold")
    cards = [
        (0.04, 0.54, 0.43, 0.26, "✓ DEMONSTRATED", ["96/96 hidden-lab assays", "Real Omnigent child-agent handoffs", "Three evidence-linked allocation changes", "Round-4 best: IYGV 4.388"], ACCENT),
        (0.53, 0.54, 0.43, 0.26, "△ PRELIMINARY", ["Sign-variable epistasis", "Surrogate rank signal", "Local + double-search value", "All top measurements unreplicated"], GOLD),
        (0.04, 0.15, 0.43, 0.26, "○ NOT YET ESTIMATED", ["Terminal performance distribution", "Top-1% / top-0.1% hit rate", "Confidence interval across seeds", "Robustness to initialization"], BLUE),
        (0.53, 0.15, 0.43, 0.26, "✕ NOT YET CLAIMABLE", ["Adaptive > fixed mixture", "Agentic value beyond surrogate", "Statistical superiority", "Generalization beyond GB1"], CORAL),
    ]
    for x, y, w, h, heading, lines, color in cards:
        ax.add_patch(FancyBboxPatch((x, y), w, h, transform=ax.transAxes, boxstyle="round,pad=0.015",
                                    facecolor=PANEL, edgecolor=color, linewidth=2))
        ax.text(x + 0.025, y + h - 0.055, heading, transform=ax.transAxes, color=color, fontsize=12, fontweight="bold")
        for i, line in enumerate(lines):
            ax.text(x + 0.03, y + h - 0.115 - i * 0.043, f"• {line}", transform=ax.transAxes, color=MUTED, fontsize=10)
    return save(fig, "08_evidence_status.png")


def write_deck():
    slides = [
        ("Adaptive Agentic Directed Evolution", "96 assays. Four rounds. One hidden GB1 landscape.", None),
        ("The scientific question", "Does evidence-driven strategy switching add value beyond the same surrogate model?", "06_omnigent_orchestration.png"),
        ("The discovery run", "A visible 4-round trajectory from initialization to a high-fitness double mutant.", "01_discovery_trajectory.png"),
        ("The agent changed its mind", "Omnigent shifted budget away from low-yield exploration and toward local/interaction tests.", "02_adaptive_allocation.png"),
        ("Evidence → strategy change → result", "The exact transition to show in the demo video.", "07_adaptation_story.png"),
        ("The biological surprise", "IYGV showed strong positive epistasis while related combinations were antagonistic.", "04_epistasis.png"),
        ("Why both model and agent mattered", "The surrogate ranked the winner highly enough to test—but badly underpredicted its magnitude.", "05_model_diagnostics.png"),
        ("Where the assays paid off", "Model exploitation found the terminal best; local mutation found the best single mutant.", "03_source_performance.png"),
        ("The honest conclusion", "A compelling development run, not yet a causal superiority result.", "08_evidence_status.png"),
    ]
    sections = []
    for index, (title, subtitle, image) in enumerate(slides, 1):
        media = f'<img src="{image}" alt="{title}">' if image else (
            '<div class="hero"><div class="pill">DATABRICKS OMNIGENT × GB1</div>'
            '<div class="metric">IYGV&nbsp;&nbsp;<span>4.388</span></div>'
            '<p>Best observed fitness after exactly 96 hidden-lab measurements</p></div>'
        )
        sections.append(f'''<section class="slide{' active' if index == 1 else ''}">
          <header><div><h1>{title}</h1><p>{subtitle}</p></div><b>{index:02d}</b></header>
          <main>{media}</main>
          <footer>OmniEvo • development run seed 0 • use paired baselines for performance claims</footer>
        </section>''')
    navigation_script = """<script>
const slides = [...document.querySelectorAll('.slide')];
let current = 0;
function show(next) {
  slides[current].classList.remove('active');
  current = (next + slides.length) % slides.length;
  slides[current].classList.add('active');
}
addEventListener('keydown', event => {
  if (['ArrowRight', ' ', 'PageDown'].includes(event.key)) show(current + 1);
  if (['ArrowLeft', 'PageUp'].includes(event.key)) show(current - 1);
});
</script>"""
    html = '''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>OmniEvo Final Presentation</title><style>
*{{box-sizing:border-box}} body{{margin:0;background:{BG};color:{TEXT};font-family:Inter,ui-sans-serif,system-ui,sans-serif;overflow:hidden}}
.slide{{display:none;width:100vw;height:100vh;padding:4vh 5vw;background:radial-gradient(circle at 90% 5%,#192747 0,{BG} 38%)}}
.slide.active{{display:grid;grid-template-rows:auto 1fr auto;gap:2vh}} header{{display:flex;justify-content:space-between;align-items:flex-start}}
h1{{font-size:clamp(30px,4vw,62px);line-height:1.02;margin:0;letter-spacing:-.035em}} header p{{color:{MUTED};font-size:clamp(15px,1.5vw,24px);margin:.7rem 0 0}}
header b{{color:{PURPLE};font-size:20px}} main{{display:flex;align-items:center;justify-content:center;min-height:0}} main img{{max-width:100%;max-height:76vh;object-fit:contain;border-radius:14px}}
footer{{color:#7886a6;font-size:12px;letter-spacing:.04em}} .hero{{text-align:center}} .pill{{display:inline-block;padding:10px 18px;border:1px solid {PURPLE};border-radius:999px;color:{PURPLE};font-weight:700;letter-spacing:.12em}}
.metric{{font-size:clamp(72px,13vw,190px);font-weight:900;letter-spacing:-.07em;margin:3vh 0 0}} .metric span{{color:{ACCENT}} .hero p{{color:{MUTED};font-size:24px}}
.hint{{position:fixed;right:18px;bottom:12px;color:#64748b;font-size:11px}}
</style></head><body>__SECTIONS__<div class="hint">← → to navigate • F11 for full screen</div>
__NAVIGATION__</body></html>'''
    html = html.replace("{{", "{").replace("}}", "}")
    for marker, value in {
        "{BG}": BG,
        "{TEXT}": TEXT,
        "{MUTED}": MUTED,
        "{PURPLE}": PURPLE,
        "{ACCENT}": ACCENT,
        "__SECTIONS__": "".join(sections),
        "__NAVIGATION__": navigation_script,
    }.items():
        html = html.replace(marker, value)
    (OUT / "omnievo_deck.html").write_text(html, encoding="utf-8")


def write_pptx():
    try:
        from pptx import Presentation
        from pptx.dml.color import RGBColor
        from pptx.enum.text import PP_ALIGN
        from pptx.util import Inches, Pt
    except ImportError:
        print("python-pptx is unavailable; skipped editable PowerPoint generation")
        return None

    def rgb(hex_color: str):
        value = hex_color.lstrip("#")
        return RGBColor(*(int(value[i:i + 2], 16) for i in (0, 2, 4)))

    slides = [
        ("Adaptive Agentic Directed Evolution", "96 assays. Four rounds. One hidden GB1 landscape.", None),
        ("The scientific question", "Does evidence-driven strategy switching add value beyond the same surrogate model?", "06_omnigent_orchestration.png"),
        ("The discovery run", "A visible 4-round trajectory from initialization to a high-fitness double mutant.", "01_discovery_trajectory.png"),
        ("The agent changed its mind", "Omnigent shifted budget away from low-yield exploration and toward local/interaction tests.", "02_adaptive_allocation.png"),
        ("Evidence → strategy change → result", "The core Omnigent transition for the demo video.", "07_adaptation_story.png"),
        ("The biological surprise", "IYGV showed strong positive epistasis while related combinations were antagonistic.", "04_epistasis.png"),
        ("Why both model and agent mattered", "The surrogate ranked the winner—but badly underpredicted its magnitude.", "05_model_diagnostics.png"),
        ("Where the assays paid off", "Model exploitation found the terminal best; local mutation found the best single.", "03_source_performance.png"),
        ("The honest conclusion", "A compelling development run, not yet a causal superiority result.", "08_evidence_status.png"),
    ]
    deck = Presentation()
    deck.slide_width = Inches(13.333333)
    deck.slide_height = Inches(7.5)
    blank = deck.slide_layouts[6]
    for index, (title, subtitle, image) in enumerate(slides, 1):
        slide = deck.slides.add_slide(blank)
        background = slide.background.fill
        background.solid()
        background.fore_color.rgb = rgb(BG)

        title_box = slide.shapes.add_textbox(Inches(0.55), Inches(0.28), Inches(11.7), Inches(0.55))
        paragraph = title_box.text_frame.paragraphs[0]
        paragraph.text = title
        paragraph.font.name = "Aptos Display"
        paragraph.font.size = Pt(30 if image else 38)
        paragraph.font.bold = True
        paragraph.font.color.rgb = rgb(TEXT)

        sub_box = slide.shapes.add_textbox(Inches(0.58), Inches(0.83), Inches(11.8), Inches(0.38))
        paragraph = sub_box.text_frame.paragraphs[0]
        paragraph.text = subtitle
        paragraph.font.name = "Aptos"
        paragraph.font.size = Pt(14)
        paragraph.font.color.rgb = rgb(MUTED)

        number_box = slide.shapes.add_textbox(Inches(12.25), Inches(0.32), Inches(0.5), Inches(0.3))
        paragraph = number_box.text_frame.paragraphs[0]
        paragraph.text = f"{index:02d}"
        paragraph.alignment = PP_ALIGN.RIGHT
        paragraph.font.size = Pt(12)
        paragraph.font.bold = True
        paragraph.font.color.rgb = rgb(PURPLE)

        if image:
            slide.shapes.add_picture(str(OUT / image), Inches(1.55), Inches(1.28), height=Inches(5.68))
        else:
            metric = slide.shapes.add_textbox(Inches(1.0), Inches(2.25), Inches(11.3), Inches(1.55))
            paragraph = metric.text_frame.paragraphs[0]
            paragraph.text = "IYGV   4.388"
            paragraph.alignment = PP_ALIGN.CENTER
            paragraph.font.name = "Aptos Display"
            paragraph.font.size = Pt(70)
            paragraph.font.bold = True
            paragraph.font.color.rgb = rgb(ACCENT)
            note = slide.shapes.add_textbox(Inches(2.0), Inches(4.05), Inches(9.3), Inches(0.5))
            paragraph = note.text_frame.paragraphs[0]
            paragraph.text = "Best observed fitness after exactly 96 hidden-lab measurements"
            paragraph.alignment = PP_ALIGN.CENTER
            paragraph.font.size = Pt(18)
            paragraph.font.color.rgb = rgb(MUTED)

        footer = slide.shapes.add_textbox(Inches(0.58), Inches(7.15), Inches(12.0), Inches(0.2))
        paragraph = footer.text_frame.paragraphs[0]
        paragraph.text = "OmniEvo • development run seed 0 • paired baselines required for performance claims"
        paragraph.font.size = Pt(8)
        paragraph.font.color.rgb = rgb("#7886A6")

    output = OUT / "OmniEvo_final_deck.pptx"
    deck.save(output)
    return output


def write_trace_demo():
    critic = read_json(RUN / "round_03/critic_report.json")
    planner = read_json(RUN / "round_04/planner_decision.json")
    allocation = planner["allocation"]
    allocation_text = " · ".join(
        f"{ACTION_LABELS[action]} {allocation.get(action, 0)}"
        for action in ("EXPLOIT_MODEL", "LOCAL_MUTATE", "EXPLORE_UNCERTAIN", "EXPLORE_DIVERSE")
    )
    verdict = str(critic.get("verdict", critic.get("status", "modify"))).upper()
    html = '''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>OmniEvo Native Omnigent Trace</title><style>
*{{box-sizing:border-box}} body{{margin:0;background:{BG};color:{TEXT};font-family:Inter,system-ui,sans-serif;padding:34px}}
.wrap{{max-width:1200px;margin:auto}} h1{{font-size:42px;margin:0}} .sub{{color:{MUTED};font-size:17px;margin:8px 0 28px}}
.status{{display:flex;gap:12px;margin-bottom:25px}} .pill{{padding:8px 12px;border-radius:999px;background:{PANEL};border:1px solid {GRID};color:{MUTED}}} .ok{{color:{ACCENT};border-color:{ACCENT}}}
.flow{{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;align-items:stretch}} .card{{background:{PANEL};border:1px solid {GRID};border-radius:16px;padding:20px;min-height:270px;position:relative}}
.card:not(:last-child):after{{content:'→';position:absolute;right:-19px;top:45%;z-index:2;color:{TEXT};font-size:25px;font-weight:bold}}
.n{{color:{PURPLE};font-size:12px;font-weight:800;letter-spacing:.12em}} h2{{font-size:21px;margin:12px 0}} .value{{font-size:29px;font-weight:900;color:{ACCENT};margin:16px 0}} p,li{{color:{MUTED};line-height:1.45;font-size:14px}} code{{color:{GOLD}}} .footer{{margin-top:24px;padding:18px;border-radius:14px;background:#10172a;color:{MUTED};display:flex;justify-content:space-between}}
.danger{{color:{CORAL}}} a{{color:{BLUE}}} @media(max-width:900px){{.flow{{grid-template-columns:1fr}}.card:not(:last-child):after{{content:'↓';right:50%;top:auto;bottom:-25px}}}}
</style></head><body><div class="wrap"><h1>Native Omnigent discovery transition</h1>
<div class="sub">Round 3 evidence → critic → planner → budgeted lab tool → Round 4 measurement</div>
<div class="status"><div class="pill ok">✓ 96/96 assays</div><div class="pill ok">✓ leakage check PASS</div><div class="pill">session a1fb…ee4d1</div><div class="pill">development seed 0</div></div>
<div class="flow">
<div class="card"><div class="n">01 · MEASUREMENTS</div><h2>Round 3 plateau</h2><div class="value">Best 2.831</div><p>Local ridge confirmed, but 24 new assays did not beat INGA.</p><p><code>round_03/measurements.csv</code></p></div>
<div class="card"><div class="n">02 · SCIENTIFIC CRITIC</div><h2>Verdict: __VERDICT__</h2><div class="value">Change policy</div><p>Reduce low-yield uncertainty/diversity. Test local structure and the missing Hamming-2 interaction space.</p><p><code>round_03/critic_report.json</code></p></div>
<div class="card"><div class="n">03 · HANDOFF</div><h2>Critic → Planner</h2><div class="value">HO-r04</div><p>Validated fairness and leakage clearance before the final 24 slots could be allocated.</p><p><code>omnigent_handoffs.jsonl</code></p></div>
<div class="card"><div class="n">04 · EXPERIMENT PLANNER</div><h2>Round 4 allocation</h2><div class="value">15 local</div><p>__ALLOCATION__</p><p><code>round_04/planner_decision.json</code></p></div>
<div class="card"><div class="n">05 · VIRTUAL LAB</div><h2>24 measured</h2><div class="value">IYGV 4.388</div><p><code>execute_planner_round</code> returned the terminal best with no oracle leakage and no unavailable assays.</p><p><code>round_04/measurements.csv</code></p></div>
</div>
<div class="footer"><span>Full native transcript: <a href="../../runs/adaptive/omnigent_seed_000/omnigent_trace_round_04.json">omnigent_trace_round_04.json</a></span><span class="danger">Single development run • measurements unreplicated</span></div>
</div></body></html>'''
    html = html.replace("{{", "{").replace("}}", "}")
    for marker, value in {
        "{BG}": BG,
        "{TEXT}": TEXT,
        "{MUTED}": MUTED,
        "{PANEL}": PANEL,
        "{GRID}": GRID,
        "{ACCENT}": ACCENT,
        "{PURPLE}": PURPLE,
        "{GOLD}": GOLD,
        "{CORAL}": CORAL,
        "{BLUE}": BLUE,
        "__VERDICT__": verdict,
        "__ALLOCATION__": allocation_text,
    }.items():
        html = html.replace(marker, value)
    path = OUT / "omnigent_demo_trace.html"
    path.write_text(html, encoding="utf-8")
    return path


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = read_jsonl(RUN / "assay_ledger.jsonl")
    if len(rows) != 96:
        raise SystemExit(f"expected 96 canonical assay rows, found {len(rows)}")
    artifacts = [
        trajectory(rows), allocation(), source_performance(rows), epistasis(rows),
        model_diagnostics(), orchestration(), adaptation_story(), confirmation_gap(),
    ]
    write_deck()
    pptx_path = write_pptx()
    trace_path = write_trace_demo()
    summary = {
        "run_id": "adaptive_omnigent_seed_000",
        "development_seed": 0,
        "successful_assays": 96,
        "best_sequence": "IYGV",
        "best_fitness": 4.38774529032,
        "figures": [path.name for path in artifacts],
        "deck": "omnievo_deck.html",
        "powerpoint": pptx_path.name if pptx_path else None,
        "trace_demo": trace_path.name,
        "claim_boundary": "Representative development run; paired fixed-mixture evaluation is pending.",
    }
    (OUT / "presentation_data.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {len(artifacts)} figures and HTML deck in {OUT}")


if __name__ == "__main__":
    main()
