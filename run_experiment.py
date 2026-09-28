"""Dataset-aware AI benchmark runner.

Runs in dry-run mode by default. Only ``--execute`` may submit Replicate calls.
"""
from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping, TextIO
from uuid import uuid4

from prompts import PROMPT_VERSION, PromptPackage, build_prompt_package


PROJECT_ROOT = Path(__file__).resolve().parent
DATASET_PATH = PROJECT_ROOT / "dataset" / "vocabulary.json"
RESULTS_PATH = PROJECT_ROOT / "results"
MANIFEST_PATH = RESULTS_PATH / "manifest.jsonl"
RUN_CONFIRMATION = "RUN_BENCHMARK"
NANO_BANANA_PROJECT_BENCHMARK_ESTIMATE = 0.067


@dataclass(frozen=True)
class ModelAdapter:
    key: str
    name: str
    model_id: str
    estimated_cost_per_image: float


@dataclass(frozen=True)
class BenchmarkPlan:
    record: Mapping[str, object]
    prompt: PromptPackage
    adapter: ModelAdapter
    output_path: Path
    model_input: dict[str, object] | None


MODEL_ADAPTERS = (
    ModelAdapter("qwen", "Qwen Image 2", "qwen/qwen-image-2", 0.035),
    ModelAdapter(
        "nano_banana",
        "Nano Banana 2",
        "google/nano-banana-2",
        NANO_BANANA_PROJECT_BENCHMARK_ESTIMATE,
    ),
)


def load_dataset() -> list[dict[str, object]]:
    """Load the controlled pilot dataset without adding provider-specific fields."""
    data = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("dataset/vocabulary.json must contain a JSON list")
    if len(data) != 10:
        raise ValueError("the controlled pilot must contain exactly 10 records")
    if not all(isinstance(record, dict) for record in data):
        raise ValueError("each dataset record must be an object")
    return data


def build_model_input(prompt: PromptPackage, adapter: ModelAdapter) -> dict[str, object]:
    """Adapt a shared semantic package only to each model's input schema."""
    if not prompt.generation_ready:
        raise ValueError("grammar/function-word records do not have an image payload")

    if adapter.key == "qwen":
        return {
            "prompt": prompt.positive_prompt,
            "negative_prompt": prompt.negative_prompt,
            "aspect_ratio": "1:1",
            "enable_prompt_expansion": False,
        }
    if adapter.key == "nano_banana":
        return {
            "prompt": prompt.final_prompt,
            "aspect_ratio": "1:1",
            "resolution": "1K",
            "output_format": "png",
            "google_search": False,
            "image_search": False,
        }
    raise ValueError(f"unknown model adapter: {adapter.key}")


def build_benchmark_plan() -> list[BenchmarkPlan]:
    """Create the deterministic 10-item x 2-model plan without contacting models."""
    plans: list[BenchmarkPlan] = []
    for record in load_dataset():
        prompt = build_prompt_package(record)
        for adapter in MODEL_ADAPTERS:
            output_path = RESULTS_PATH / adapter.key / f"{prompt.dataset_id}.png"
            model_input = build_model_input(prompt, adapter) if prompt.generation_ready else None
            plans.append(BenchmarkPlan(record, prompt, adapter, output_path, model_input))
    return plans


def select_execution_plans(
    plans: list[BenchmarkPlan],
    *,
    model_key: str | None = None,
    limit: int | None = None,
) -> list[BenchmarkPlan]:
    """Return an execution subset without changing the full benchmark plan."""
    selected = [plan for plan in plans if model_key is None or plan.adapter.key == model_key]
    if limit is None:
        return selected

    eligible = [plan for plan in selected if plan.model_input]
    return eligible[:limit]


def with_run_output_paths(plans: list[BenchmarkPlan], *, run_id: str) -> list[BenchmarkPlan]:
    """Place each execution output under its unique run directory."""
    return [
        replace(
            plan,
            output_path=RESULTS_PATH / plan.adapter.key / run_id / f"{plan.prompt.dataset_id}.png",
        )
        for plan in plans
    ]


def eligible_request_count(plans: list[BenchmarkPlan]) -> int:
    """Count the plans that can submit an image-generation request."""
    return sum(plan.model_input is not None for plan in plans)


def estimated_cost(plans: list[BenchmarkPlan]) -> float:
    """Return the configured estimate for eligible image-generation requests."""
    return sum(plan.adapter.estimated_cost_per_image for plan in plans if plan.model_input)


def manifest_record(
    plan: BenchmarkPlan,
    *,
    run_id: str,
    status: str,
    error: str | None = None,
) -> dict[str, object]:
    """Return provenance for a planned or attempted AI candidate."""
    return {
        "run_id": run_id,
        "dataset_id": plan.prompt.dataset_id,
        "vocabulary": plan.prompt.vocabulary,
        "meaning": plan.prompt.meaning,
        "category": plan.record["category"],
        "visualizability": plan.record["visualizability"],
        "visual_strategy": plan.prompt.visual_strategy,
        "model": plan.adapter.model_id,
        "prompt_version": PROMPT_VERSION,
        "final_prompt": plan.prompt.final_prompt,
        "model_specific_settings": plan.model_input or {},
        "status": status,
        "output_path": str(plan.output_path),
        "error": error,
        "estimated_cost": plan.adapter.estimated_cost_per_image if plan.model_input else 0,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def print_dry_run(plans: list[BenchmarkPlan]) -> None:
    """Print the benchmark plan without creating files or sending requests."""
    eligible = [plan for plan in plans if plan.model_input]
    skipped = [plan for plan in plans if not plan.model_input]
    project_cost = estimated_cost(eligible)

    print("DRY RUN: no API calls will be made.")
    print(f"Planned evaluation slots: {len(plans)}")
    print(f"Image-generation requests eligible: {len(eligible)}")
    print(f"Non-visual grammar slots skipped: {len(skipped)}")
    print(f"Project benchmark estimate: ${project_cost:.3f}")
    for plan in plans:
        status = "PLANNED" if plan.model_input else "SKIPPED_NON_VISUAL"
        print(
            f"{status}: {plan.prompt.dataset_id} | {plan.adapter.key} | "
            f"{plan.output_path.relative_to(PROJECT_ROOT)}"
        )


def execute_benchmark(plans: list[BenchmarkPlan], *, run_id: str) -> None:
    """Submit the plan once per eligible slot; no automatic retries are performed."""
    if not os.environ.get("REPLICATE_API_TOKEN"):
        raise RuntimeError("REPLICATE_API_TOKEN is not set.")

    import replicate

    RESULTS_PATH.mkdir(parents=True, exist_ok=True)
    with MANIFEST_PATH.open("a", encoding="utf-8") as manifest:
        for plan in plans:
            if not plan.model_input:
                _write_manifest(
                    manifest,
                    manifest_record(plan, run_id=run_id, status="SKIPPED_NON_VISUAL"),
                )
                continue

            try:
                output = replicate.run(plan.adapter.model_id, input=plan.model_input)
                plan.output_path.parent.mkdir(parents=True, exist_ok=True)
                plan.output_path.write_bytes(output.read())
            except Exception as error:
                _write_manifest(
                    manifest,
                    manifest_record(plan, run_id=run_id, status="FAILED", error=str(error)),
                )
                print(f"FAILED: {plan.prompt.dataset_id} | {plan.adapter.key} | {error}")
                continue

            _write_manifest(manifest, manifest_record(plan, run_id=run_id, status="SUCCEEDED"))
            print(f"SUCCEEDED: {plan.prompt.dataset_id} | {plan.adapter.key}")


def _write_manifest(manifest: TextIO, record: Mapping[str, object]) -> None:
    manifest.write(json.dumps(record, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run or inspect the image benchmark plan.")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="submit paid Replicate requests; omit for the safe dry run",
    )
    parser.add_argument(
        "--model",
        choices=[adapter.key for adapter in MODEL_ADAPTERS],
        help="limit paid execution to one model; does not change the dry-run plan",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="limit paid execution to this many eligible image-generation requests",
    )
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be at least 1")

    plans = build_benchmark_plan()
    if args.execute:
        execution_plans = select_execution_plans(plans, model_key=args.model, limit=args.limit)
        request_count = eligible_request_count(execution_plans)
        execution_cost = estimated_cost(execution_plans)
        print(f"WARNING: this will submit {request_count} paid requests.")
        print(f"Estimated cost: ${execution_cost:.3f}.")
        confirmation = input(f"Type {RUN_CONFIRMATION} to continue: ")
        if confirmation.strip() != RUN_CONFIRMATION:
            print("Benchmark cancelled. No API calls were made.")
            return
        run_id = uuid4().hex
        execute_benchmark(with_run_output_paths(execution_plans, run_id=run_id), run_id=run_id)
    else:
        print_dry_run(plans)


if __name__ == "__main__":
    main()