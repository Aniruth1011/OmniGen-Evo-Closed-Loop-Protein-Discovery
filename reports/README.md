# OmniEvo Final Presentation Package

- `final_report.md` — full scientific report and claim boundaries.
- `presentation_outline.md` — slide-by-slide headlines, visuals, and talking points.
- `video_script.md` — timed two-minute narration and recording directions.
- `../artifacts/presentation/OmniEvo_final_deck.pptx` — editable PowerPoint.
- `../artifacts/presentation/omnievo_deck.html` — full-screen browser deck.
- `../artifacts/presentation/omnigent_demo_trace.html` — recording-ready native orchestration transition.
- `../artifacts/presentation/01_...08_*.png` — high-resolution 16:9 figures.

Regenerate everything with:

```bash
MPLBACKEND=Agg MPLCONFIGDIR=/tmp/omnievo-matplotlib \
  .venv/bin/python scripts/generate_final_presentation.py
```
