# Health Uncertainty and Reliability Eval

Public benchmark artifacts evaluating how faithfully language models preserve evidence strength, uncertainty, and regulatory posture in health-facing answers.

This repository hosts two independent evaluation packages under the same umbrella. Each is self-contained with its own dataset, protocol, scripts, and reports.

## Packages

### [01 — Evidence-to-Recommendation Reliability Eval](01_evidence_to_recommendation_reliability_eval/)

Measures whether a model's patient-facing answer preserves the intended USPSTF-style recommendation grade (`A/B/C/D/I`), uncertainty language, and preference-sensitivity — rather than overclaiming or softening the underlying evidence.

Core questions:
- Does the model exaggerate or weaken `A/B/C/D/I` recommendation strength?
- Does it honestly disclose evidence insufficiency on `I statements`?
- Does it acknowledge patient preference on `C grade` topics?

### [02 — Drug Safety Update Sensitivity Eval](02_drug_safety_update_sensitivity_eval/)

Measures *update sensitivity*: does the same user question get an appropriately shifted answer when the model is given a new FDA post-market safety packet vs. the prior one?

Format: 90 items (30 FDA safety events × 3 user-question variants). Each event ships a `before_packet` and `after_packet`; the model is run on both, and the answer pair is scored on directional shift.

This is not a drug-QA benchmark — it evaluates context-mediated response shift, distinct from parametric knowledge staleness benchmarks.

## Positioning

These artifacts target a gap in the public health-benchmark landscape: neither broad conversation safety nor clinician-facing guideline adherence, but the narrower question of **how faithfully public evidence is transmitted to patient-facing answers**.

## Status

Pilot scaffolds with real model runs completed on both packages. See each package's `README.md` and `reports/` for protocol, results, and limitations.

## Repository layout

```
.
├── 01_evidence_to_recommendation_reliability_eval/
│   ├── data/          # examples, rubric schema, prompt packs
│   ├── prompts/       # system + judge prompts
│   ├── scripts/       # run + judge utilities
│   ├── runs/          # per-run manifests, outputs, summaries
│   ├── reports/       # qualitative cases, manuscript drafts, freeze notes
│   ├── figures/       # comparison plots
│   └── docs/          # annotation guide, methodology, limitations
│
├── 02_drug_safety_update_sensitivity_eval/
│   ├── data/          # before/after packets, user-question variants
│   ├── eval/          # evaluation driver + outputs
│   ├── scripts/       # run utilities
│   ├── tests/         # unit tests
│   ├── reports/       # analyses and writeups
│   ├── figures/       # per-model result plots
│   └── docs/
│
├── LICENSE            # Apache-2.0 — applies to code (scripts, eval harness, tests)
└── LICENSE-DATA       # CC BY-NC 4.0 — applies to dataset, prompts, rubrics, figures, reports
```

## Reproducibility notes

- All model runs require API keys provided via environment (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`). No keys are committed.
- Raw run outputs under each package's `runs/` or `eval/output/` are the canonical artifacts; summary tables and figures are regenerated from them.
- Each package pins its evaluation protocol in its own `README.md` and `docs/methodology.md` (where present).

## License

This repository is dual-licensed by asset type.

- **Code** (everything under `scripts/`, `eval/`, `tests/`, and any `.py` file): **Apache License 2.0**. See [LICENSE](LICENSE). Commercial and non-commercial use permitted, including patent grant.
- **Data, prompts, rubrics, figures, reports** (everything under `data/`, `prompts/`, `figures/`, `reports/`, `runs/`, `research/`, `docs/`, and all `*.md`, `*.csv`, `*.jsonl`, `*.json`, `*.svg`, `*.png` files): **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)**. See [LICENSE-DATA](LICENSE-DATA). Non-commercial use permitted with attribution. **Commercial use of the dataset, prompts, or rubrics requires a separate license.**

### Commercial licensing

For commercial use of the dataset or prompts (including use in commercial product evaluations, internal benchmarking within for-profit AI products, or redistribution as part of a commercial offering), please open a GitHub issue titled `commercial-license` with your use case and contact information, or reach out via the repository owner's GitHub profile.

Internal research use at for-profit institutions that does not enter a product pipeline generally qualifies as non-commercial under CC BY-NC 4.0, but if uncertain, please ask.

### Attribution

If you use this benchmark in academic work, please cite the repository URL and the specific package (`01_evidence_to_recommendation_reliability_eval` or `02_drug_safety_update_sensitivity_eval`).
