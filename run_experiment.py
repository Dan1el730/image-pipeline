import os
from pathlib import Path

import replicate


PROMPT = (
    "A cute white rabbit sitting in a sunny green meadow, clearly showing the "
    "characteristics of a rabbit, friendly children's educational illustration, "
    "simple composition, bright and clear visual meaning, suitable for children "
    "ages 2–11, square composition, no text, no Chinese characters, no English "
    "letters, no numbers, no captions, no logos, no watermark."
)

MODELS = (
    ("Qwen Image 2", "qwen/qwen-image-2", Path("results/qwen/rabbit_test.png")),
    (
        "Nano Banana 2",
        "google/nano-banana-2",
        Path("results/nano_banana/rabbit_test.png"),
    ),
)


def generate_image(name: str, model: str, output_path: Path) -> None:
    print(f"\nModel: {name} ({model})")
    print(f"Prompt: {PROMPT}")
    print(f"Output path: {output_path.resolve()}")

    try:
        output = replicate.run(
            model,
            input={
                "prompt": PROMPT,
                "aspect_ratio": "1:1",
            },
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(output.read())
    except Exception as error:
        print(f"Failure: {error}")
        return

    print("Success")
    print(f"Output path: {output_path.resolve()}")


def main() -> None:
    if not os.environ.get("REPLICATE_API_TOKEN"):
        raise RuntimeError(
            "REPLICATE_API_TOKEN is not set. "
            "Set it in PowerShell before running this script."
        )

    for name, model, output_path in MODELS:
        generate_image(name, model, output_path)


if __name__ == "__main__":
    main()