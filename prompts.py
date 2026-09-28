"""Deterministic, model-neutral educational image prompt construction."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


PROMPT_VERSION = "semantic-v2"

_VISUAL_STRATEGIES = {
    "direct_object",
    "action_scene",
    "relationship_scene",
    "abstract_concept",
    "grammar_function",
}

_SCENE_SPECS = {
    "rabbit": (
        "A cute white rabbit sitting in a sunny green meadow, full body clearly "
        "visible, with long ears, round body, paws, and a small fluffy tail."
    ),
    "ball": (
        "One bright red ball, large and centered on a simple grassy play area, "
        "with its round shape immediately clear."
    ),
    "apple": (
        "One ripe red apple with a green leaf, large and centered on a simple "
        "light background, with its round fruit shape clearly visible."
    ),
    "run": (
        "One child running along a simple park path, with one foot lifted, arms "
        "moving, and a clear forward-moving pose."
    ),
    "rain": (
        "Gentle raindrops falling from a small gray cloud onto green grass, with "
        "the falling rain clearly visible and no storm danger."
    ),
    "hand": (
        "One open child-friendly hand with five fingers clearly visible, large and "
        "centered against a simple background."
    ),
    "happy": (
        "Two children smiling and laughing while proudly finishing a colorful block "
        "tower together, with joyful faces and the successful moment obvious."
    ),
    "far": (
        "A small child in the foreground looking toward a distant blue mountain, "
        "with a long open path and clear depth that makes the mountain look far away."
    ),
    "mooncake": (
        "One round golden-brown mooncake on a simple plate, with a plain decorated "
        "top that has no writing, symbols, or brand marks."
    ),
}

_POSITIVE_REQUIREMENTS = (
    "Create a friendly children's educational illustration for children ages 2-11. "
    "Use clear shapes, bright approachable colors, simple composition, and an "
    "obvious focal subject so the meaning is understandable without reading. "
    "Use a 1:1 square composition and avoid unnecessary background detail."
)

_NEGATIVE_REQUIREMENTS = (
    "Do not represent the vocabulary by writing or displaying its written form. "
    "No Chinese characters, Chinese words, English words, letters, numbers, captions, "
    "labels, subtitles, logos, watermarks, unnecessary signage, branded characters, "
    "copyrighted fictional characters, or fan art. No graphic violence, disturbing "
    "imagery, frightening imagery, adult or sexual content, humiliating depictions, "
    "dangerous behavior presented as desirable, advertising, screenshots, or clutter."
)


@dataclass(frozen=True)
class PromptPackage:
    """A provider-independent prompt plan for one vocabulary record."""

    dataset_id: str
    vocabulary: str
    meaning: str
    visual_strategy: str
    visual_scene: str
    positive_prompt: str
    negative_prompt: str
    final_prompt: str
    generation_ready: bool
    modality_note: str


def build_prompt_package(record: Mapping[str, object]) -> PromptPackage:
    """Build a deterministic prompt package from a controlled dataset record."""
    required = {"id", "text", "meaning", "visual_strategy"}
    missing = required.difference(record)
    if missing:
        raise ValueError(f"record is missing required fields: {sorted(missing)}")

    dataset_id = _required_text(record["id"], "id")
    vocabulary = _required_text(record["text"], "text")
    meaning = _required_text(record["meaning"], "meaning")
    visual_strategy = _required_text(record["visual_strategy"], "visual_strategy")
    if visual_strategy not in _VISUAL_STRATEGIES:
        raise ValueError(f"unsupported visual_strategy: {visual_strategy}")

    if visual_strategy == "grammar_function":
        return PromptPackage(
            dataset_id=dataset_id,
            vocabulary=vocabulary,
            meaning=meaning,
            visual_strategy=visual_strategy,
            visual_scene="",
            positive_prompt="",
            negative_prompt=_NEGATIVE_REQUIREMENTS,
            final_prompt=(
                "No image-generation prompt. This grammar/function-word item must "
                "use another educational modality rather than a literal image."
            ),
            generation_ready=False,
            modality_note=(
                "Use a future non-image modality such as an example sentence, "
                "relationship diagram, stroke/decomposition teaching, animation, or "
                "teacher/parent-assisted explanation."
            ),
        )

    visual_scene = _SCENE_SPECS.get(dataset_id)
    if visual_scene is None:
        raise ValueError(f"no visual scene specification for dataset id: {dataset_id}")

    positive_prompt = (
        f"Illustrate the meaning '{meaning}' for a Traditional Chinese vocabulary "
        f"learning activity. {visual_scene} {_POSITIVE_REQUIREMENTS}"
    )
    final_prompt = f"{positive_prompt}\n\nRestrictions: {_NEGATIVE_REQUIREMENTS}"
    return PromptPackage(
        dataset_id=dataset_id,
        vocabulary=vocabulary,
        meaning=meaning,
        visual_strategy=visual_strategy,
        visual_scene=visual_scene,
        positive_prompt=positive_prompt,
        negative_prompt=_NEGATIVE_REQUIREMENTS,
        final_prompt=final_prompt,
        generation_ready=True,
        modality_note="Generate one educational image candidate.",
    )


def build_image_prompt(*, character: str, meaning: str, visual_description: str) -> str:
    """Build a model-neutral prompt for an ad hoc direct-object test.

    ``character`` remains metadata only and is intentionally excluded from the
    returned prompt so models illustrate meaning rather than render the glyph.
    """
    _required_text(character, "character")
    meaning = _required_text(meaning, "meaning")
    visual_description = _required_text(visual_description, "visual_description")
    positive_prompt = (
        f"Illustrate the meaning '{meaning}' for a Traditional Chinese vocabulary "
        f"learning activity. {visual_description} {_POSITIVE_REQUIREMENTS}"
    )
    return f"{positive_prompt}\n\nRestrictions: {_NEGATIVE_REQUIREMENTS}"


def _required_text(value: object, field_name: str) -> str:
    text = str(value).strip()
    if not text:
        raise ValueError(f"{field_name} must not be empty")
    return text