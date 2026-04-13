# Contributing to Drug Safety Update Sensitivity Eval

Thank you for your interest in contributing. This benchmark evaluates whether AI models appropriately shift their answers when given updated FDA post-market safety information. Contributions that strengthen the benchmark's rigor, scope, or usability are welcome.

## Ways to contribute

### 1. Report benchmark issues

If you find an error in a before_packet, after_packet, must_mention list, or any other dataset content, please open a GitHub Issue with:

- The `case_id` (e.g., `DSU-019-patient_plain_language`)
- The specific field that is incorrect
- The FDA source (Drug Safety Communication or SrLC) that contradicts the current content
- A proposed correction (paraphrased, not verbatim FDA text)

### 2. Propose new safety events

The v1 dataset is frozen at 30 events (90 items). A future v2 may expand. To propose a new event, open an Issue with the `new event` label and include:

- Drug name (brand + active ingredient)
- Application type: must be NDA or BLA (no ANDA)
- Update date (must fall inside the evaluation window — currently 2024-01-01 to 2026-03-31)
- Section changed (one of the six allowed values; see `data/schema.json`)
- Direction: `risk_increase`, `risk_decrease`, or `stable`
- FDA source URL (DSC or SrLC)
- Short rationale for why this event is a good test case

### 3. Improve the rubric or judge prompt

Changes to the rubric (`docs/methodology.md`) or judge prompt (`eval/prompts.py`) are significant methodological changes. Please open an Issue first to discuss. Include:

- The specific change proposed
- Concrete examples where the current rubric fails
- How the change would score a small sample of existing items

### 4. Add a model run

If you run the benchmark on a model not yet evaluated and want to contribute the results:

- Use `claude-haiku-4-5-20251001` as the judge to keep scoring comparable
- Store your results under `eval/output/<your_model_name>/` with a `run_manifest.json`
- Include a short report at `reports/<your_model_name>.md`
- Open a Pull Request — we will review for consistency with other runs

### 5. Code improvements

Bug fixes, test additions, type hints, and documentation improvements are welcome via Pull Request. Please include tests for any behavior change.

## Development setup

```bash
# Clone
git clone https://github.com/jang1563/drug-safety-update-sensitivity-eval.git
cd drug-safety-update-sensitivity-eval

# Create virtual environment (Python 3.8 or later)
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r eval/requirements.txt pytest

# Run tests
pytest tests/ -v

# Run a smoke evaluation (no API calls)
python eval/run_mock_eval.py --output eval/output/mock_run
```

## Testing

All tests should pass before a PR is merged:

```bash
pytest tests/ -v
```

If your change affects:

- The judge prompt or scoring logic → update `tests/test_scoring.py`
- The dataset → update `tests/test_dataset_audit.py`
- The runner → update `tests/test_runners.py`
- The report generator → update `tests/test_report_generator.py`
- The comparison reporter → update `tests/test_comparison_report.py`
- Judge sensitivity → update `tests/test_judge_sensitivity.py`

## Source rights and paraphrasing

All benchmark packets are **human-authored paraphrases** of FDA source material. Never copy FDA Drug Safety Communication text, SrLC entries, or DailyMed label text verbatim. Always preserve source URLs.

See `docs/methodology.md` (Source Rights section) for detailed rules.

## Pull Request checklist

Before opening a Pull Request:

- [ ] Tests pass (`pytest tests/ -v`)
- [ ] No verbatim FDA text in any added content
- [ ] Source URLs preserved for any new content
- [ ] Dataset changes do not break `data/schema.json` validation
- [ ] Relevant documentation updated (`README.md`, `docs/methodology.md`, etc.)
- [ ] PR description explains the change and any methodological implications

## License for contributions

By contributing to this repository, you agree that:

- Code contributions will be licensed under the project's Apache 2.0 code license
- Non-code contributions (dataset, docs, figures, reports) will be licensed under CC BY-NC 4.0

See [LICENSE](LICENSE) and [LICENSE-DATA](LICENSE-DATA) for the full terms.

## Code of Conduct

Be respectful. Assume good faith. This is a small project; please report harassment or any concerns directly to the maintainer via GitHub Issues.
