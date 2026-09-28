"""Deterministic educational image prompt construction."""

PROMPT_VERSION = "semantic-v1"

_COMMON_REQUIREMENTS = (
    "Create a friendly children's educational illustration for children ages 2–11. "
    "Use clear shapes, bright approachable color, a simple uncluttered composition, "
    "and a prominent focal subject so the meaning is understandable without reading. "
    "Use a 1:1 square composition with appropriate visual scale. "
    "Avoid frightening or disturbing imagery, graphic violence, adult themes, sexual "
    "content, humiliating depictions, dangerous behavior presented as desirable, and "
    "age-inappropriate situations. "
    "Do not include Chinese characters, English letters, numbers, captions, labels, "
    "subtitles, logos, or watermarks."
)


def build_image_prompt(*, character: str, meaning: str, visual_description: str) -> str:
    """Build a model-neutral prompt from semantic vocabulary information.

    ``character`` is validated as source metadata but intentionally excluded from the
    generated prompt: models should illustrate the meaning, not render the character.
    """
    if not character.strip():
        raise ValueError("character must not be empty")
    if not meaning.strip():
        raise ValueError("meaning must not be empty")
    if not visual_description.strip():
        raise ValueError("visual_description must not be empty")

    return (
        f"Prompt version: {PROMPT_VERSION}. "
        f"Illustrate the meaning: {meaning.strip()}. "
        f"Visual description: {visual_description.strip()} "
        f"{_COMMON_REQUIREMENTS}"
    )