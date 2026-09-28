
import os
import replicate

# Check that the API token is available
if not os.environ.get("REPLICATE_API_TOKEN"):
    raise RuntimeError(
        "REPLICATE_API_TOKEN is not set. "
        "Set it in PowerShell before running this script."
    )

print("Sending request to Qwen Image 2...")

output = replicate.run(
    "qwen/qwen-image-2",
    input={
        "prompt": (
            "A cinematic Spartan warrior standing inside an ancient Greek "
            "temple at sunset, realistic detailed armor, dramatic lighting, "
            "highly detailed professional concept art, full body, "
            "wide composition"
        ),
        "aspect_ratio": "16:9",
        "enable_prompt_expansion": True,
    },
)

print("Generation completed.")
print("Output:", output)

# Save the generated image
with open("qwen_api_test.png", "wb") as f:
    f.write(output.read())

print("Saved image to:")
print(os.path.abspath("qwen_api_test.png"))
