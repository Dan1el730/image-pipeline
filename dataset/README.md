# Controlled Vocabulary Pilot Dataset

`vocabulary.json` is a deliberately small, controlled pilot for the first
educational image experiment. It is not the production Ngaam-Nou vocabulary
database.

## Selection Rationale

The ten items cover distinct semantic and visual challenges instead of selecting
ten random concrete nouns: a concrete animal, object, food, action, natural
phenomenon, body-related concept, simple abstract concept, spatial relationship,
culturally Chinese-specific concrete item, and grammatical/function word.

The final item, `的`, is deliberately included as a low-visualizability
`grammar_function` case. It should not be treated as a concept with one literal
image. Its role is to reveal the boundary where a single educational image is
not an appropriate explanation.

## Field Meanings

`visualizability` describes how directly a child can understand the meaning from
a single image:

- `high`: a familiar subject or observable event can be shown directly.
- `medium`: a scene can communicate the meaning, but interpretation matters.
- `low`: a single literal image is usually inadequate.

`visual_strategy` identifies the intended kind of visual explanation:

- `direct_object`: make the subject itself clear and prominent.
- `action_scene`: show an observable action.
- `relationship_scene`: show a relationship such as distance or position.
- `abstract_concept`: use a simple concrete scene to communicate an idea.
- `grammar_function`: identify a grammatical role that should not be forced into
  a literal standalone image.

This dataset contains no generated prompts, example sentences, image URLs,
provider-specific fields, generated images, or retrieved images. This statement
describes the dataset contents only; the repository's separate Step 6B benchmark
may generate images from these controlled records.