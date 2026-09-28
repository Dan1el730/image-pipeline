# Ngaam-Nou Image Lab

A standalone, disposable experiment repository for evaluating AI-generated
educational images for Traditional Chinese vocabulary learning. The intended
audience is children approximately ages 2-11.

## Current Status

- Step 1: API verification - complete.
- Step 2: two-model runner - implementation complete; the Qwen versus Nano
        Banana experiment is pending.
- Step 3: semantic-v1 prompt and policy - complete.
- Step 4: image retrieval and licensing research - complete.
- Step 5: controlled vocabulary dataset - created and validation passed.
- Step 6A: dataset-aware experiment runner - complete.
- Step 6B: paid AI benchmark - complete. The benchmark evaluated 9 visual
        vocabulary cases with 18 generated images: 9 from Qwen Image 2 and 9 from
        Nano Banana 2. `的` was intentionally skipped as a non-visual
        grammar/function case. Benchmark run ID: `9b99ee062f9f40d088a6444a1a916984`.
- Step 7: retrieval policy and specification - documentation complete; policy
        only, not implemented.
- Steps 8-12: not started.

`IMAGE_RETRIEVAL_AND_LICENSING.md` documents the proposed retrieval fallback.
`dataset/vocabulary.json` contains the current 10-item controlled pilot, and
`dataset/README.md` explains the pilot dataset. `RETRIEVAL_POLICY.md` defines
the proposed retrieval policy. No Step 5 image generation or retrieval has been
performed.

The models under evaluation are:

- Qwen Image 2: `qwen/qwen-image-2`
- Nano Banana 2: `google/nano-banana-2`

## Current Architecture

```text
Vocabulary dataset record
        |
semantic-v2 prompt builder (current candidate)
        |
generation
        |
manual evaluation using PROMPT_TEST_SET.md rubric
        |
AI asset (primary path)
        |
generation failure or unsuitable result
        |
future retrieval fallback
        |
license/source + visual + educational verification
        |
retrieved asset or NO_SAFE_VISUAL_FOUND
```

`prompts.py` creates deterministic, model-neutral educational image prompts.
Semantic-v2 is the current prompt candidate. The adapter preserves equivalent
meaning and restrictions rather than requiring byte-identical provider prompts.

## Provider Payloads

The current schemas were checked against the official Replicate model READMEs:

- Common fields: both models receive a `prompt` and `aspect_ratio: "1:1"`.
- Qwen Image 2 fields: `prompt`, `negative_prompt`, `aspect_ratio`, and
        `enable_prompt_expansion: false`. Qwen documents `negative_prompt` as the
        supported exclusion field. Prompt expansion is disabled because it is enabled
        by default and could alter the controlled semantic baseline.
- Nano Banana 2 fields: `prompt`, `aspect_ratio: "1:1"`, `resolution: "1K"`,
        `output_format: "png"`, `google_search: false`, and `image_search: false`.
        Nano's schema does not expose a separate negative-prompt field, so the same
        restrictions are appended to its model-neutral prompt. Web and image search
        are explicitly disabled to keep generation self-contained.

The Qwen Image 2 value of `$0.035` per eligible image and Nano Banana 2 value
of `$0.067` per eligible image are project benchmark estimates, not guaranteed
or current provider prices.

## Current Evaluation Stage

Current stage: generation -> manual evaluation using the
`PROMPT_TEST_SET.md` rubric. Automated AI quality gates do not exist yet and
are future work.

AI generation is the primary path. Retrieval is a future fallback only; it must
never bypass license, source, visual-style, or educational-suitability
verification.

`decomp.py` is a separate deterministic CJK character decomposition component
backed by data in `assets/`. It is not integrated with image generation in the
current project stage.

## Local Setup

Create and activate a local virtual environment, then install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Set the Replicate token only in the current PowerShell environment:

```powershell
$env:REPLICATE_API_TOKEN="YOUR_TOKEN"
```

Run the original single-model API verification:

```powershell
python .\test_api.py
```

Inspect the default safe plan (it does not send requests):

```powershell
python .\run_experiment.py
```

Submit paid requests only after reviewing the warning and typing the required
confirmation token:

```powershell
python .\run_experiment.py --execute
```

For a bounded manual trial, restrict execution without changing the full
20-slot evaluation plan:

```powershell
python .\run_experiment.py --execute --model nano_banana --limit 2
```

The full plan contains 20 evaluation slots (10 vocabulary records x 2 models),
18 eligible image-generation requests, and 2 `SKIPPED_NON_VISUAL` grammar
slots. Execution appends records to `results/manifest.jsonl`; each execution
record includes a unique `run_id`, and prior manifest records are retained.

Generated output under `results/` and the original `qwen_api_test.png` are
intentionally ignored by Git.

## Project Stages

- Step 1: API verification - complete
- Step 2: two-model runner - implementation complete; Qwen versus Nano Banana
        experiment pending
- Step 3: semantic-v1 prompt and policy - complete
- Step 4: image retrieval and licensing research - complete
- Step 5: controlled vocabulary dataset - created and validation passed
- Step 6A: dataset-aware experiment runner - complete
- Step 6B: paid AI benchmark - complete; 9 visual vocabulary cases, 18 generated
        images (9 Qwen Image 2, 9 Nano Banana 2), and `的` intentionally skipped
        as non-visual. Run ID: `9b99ee062f9f40d088a6444a1a916984`
- Step 7: retrieval policy and specification - documentation complete; policy
        only, not implemented
- Step 8: retrieval implementation - not started
- Step 9: license / visual / educational gates - not started
- Step 10: 10-word end-to-end pilot - not started
- Step 11: decomp.py integration - not started
- Step 12: larger benchmark - not started