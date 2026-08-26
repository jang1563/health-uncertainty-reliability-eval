# Data

- checked_on: `2026-04-16`
- project: `Evidence-to-Recommendation Reliability Eval`
- status: `frozen pilot + supporting 40-row stress test + canonical 120-row release substrate`

## Purpose

This directory contains the benchmark rows, rubric schema, blank templates, and prompt packs used by the release candidate.

## Canonical vs Supporting Sets

- `examples.csv`
  - original `20`-row pilot
- `examples_v1_40.csv`
  - frozen same-set supporting stress test
- `examples_v1_120.csv`
  - canonical full-v1 benchmark release substrate

The `40`-row slice is a supporting stress test. The `120`-row slice is the primary release benchmark.

## Key Files

- `source_topic_pool.csv`
  - original source-topic pool used to build the pilot and early expansion
- `source_topic_pool_v1.csv`
  - expanded source-topic pool for the canonical `120`-row set
- `rubric_schema.json`
  - rubric dimensions, failure taxonomy, and score scale
- `model_outputs_template*.csv`
  - blank response templates
- `annotations_template*.csv`
  - blank scoring templates with benchmark context already merged
- `*_prompt_pack.jsonl`
  - JSONL prompt packs for batch or API-based runs

## Current Principles

- paraphrase-first row construction
- no long verbatim source copying
- `required_points` and `forbidden_moves` are human-authored derived fields
- `C` and `I` rows are intentionally emphasized because they are the main posture-sensitive cases

## Current Full-v1 Shape

- total rows: `120`
- grade counts: `A=16,B=24,C=32,D=16,I=32`
- max rows per source-topic slice: `4`

## Current Limits

- `medlineplus_url` coverage remains partial
- the benchmark is still primarily `USPSTF`-anchored rather than multi-guideline
- taxonomy changes are intentionally frozen until the Sonnet adjudication packet is completed

## Release Notes

If you need the public release substrate, start with:

- `examples_v1_120.csv`
- `model_outputs_template_v1_120.csv`
- `annotations_template_v1_120.csv`
- `examples_v1_120_prompt_pack.jsonl`
