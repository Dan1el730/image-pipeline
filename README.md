# Ngaam-Nou Image Lab

A standalone, disposable experiment repository for evaluating AI-generated
educational images for Traditional Chinese vocabulary learning. The intended
audience is children approximately ages 2-11.

## Current Status

Step 3 is complete. Step 4 has not started.

The models under evaluation are:

- Qwen Image 2: `qwen/qwen-image-2`
- Nano Banana 2: `google/nano-banana-2`

## Current Architecture

```text
Vocabulary semantic description
        |
semantic-v1 prompt builder
        |
Qwen Image 2 / Nano Banana 2
        |
local generated image
```

`prompts.py` creates deterministic, model-neutral educational image prompts.
The baseline uses the same final semantic prompt for both models so comparisons
measure model behavior rather than model-specific prompt wording.

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

Run the two-model experiment (this submits paid generation requests):

```powershell
python .\run_experiment.py
```

Generated output under `results/` and the original `qwen_api_test.png` are
intentionally ignored by Git.

## Project Stages

- Step 1: API verification - complete
- Step 2: two-model runner - complete
- Step 3: semantic-v1 prompt and policy - complete
- Step 4: vocabulary dataset - not started
- Step 5: hooks, validation, and budget controls - planned
- Step 6: pilot benchmark - planned
- Step 7: decomp.py integration - planned
- Step 8: larger benchmark - planned