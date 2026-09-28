# Retrieval Policy

**Current status: Policy proposal — not implemented.**

This policy defines the gates a future image-retrieval fallback must follow when
AI generation fails or produces an educationally unsuitable result. It does not
implement retrieval, authorize downloading, or authorize reuse of a particular
asset.

No automated system can guarantee zero copyright or legal risk. In this policy,
an asset is **approved** only when it has passed Ngaam-Nou's defined verification
procedure. Provider metadata is evidence, not an absolute legal guarantee, and
individual asset and source-page verification are required.

## Provider Roles

### Primary Candidate Sources

- OpenClipart, subject to current provider, API, and license verification.
- Openverse.
- Wikimedia Commons.

### Secondary or Future Sources

- Pixabay or other providers only after separate policy review.

### Do Not Automatically Use

- Google Images.
- Bing Images.
- Pinterest.
- Social-media searches.
- Arbitrary website scraping.
- Unknown image URLs.
- Search results with no verifiable license or source.

Search results do not themselves establish reuse rights, provenance, or the
absence of third-party rights.

## License Gate

The initial automatic license allowlist is deliberately narrow.

```text
ALLOW:  CC0, Public Domain, Public Domain Mark
REVIEW: CC BY, CC BY-SA, licenses requiring attribution, ShareAlike,
        or other additional obligations
REJECT: unknown or missing license metadata; contradictory license metadata;
        non-commercial-only licenses; unclear provenance; conditions
        incompatible with the intended product use
```

`CC BY` and `CC BY-SA` are not inherently unsafe. They require attribution,
ShareAlike analysis, or other compliance work, so this initial policy routes them
to a later manual-review tier rather than approving them automatically.

An automatic approval requires all of the following:

```text
license in {CC0, PUBLIC_DOMAIN, PUBLIC_DOMAIN_MARK}
license metadata present and internally consistent
source page verified
license terms verified against source page
no known incompatible product-use condition
```

## Required Provenance Record

Every approved retrieved asset must retain this record:

```json
{
  "asset_type": "retrieved",
  "provider": "",
  "source_id": "",
  "source_url": "",
  "image_url": "",
  "title": "",
  "creator": "",
  "creator_url": "",
  "license": "",
  "license_version": "",
  "license_url": "",
  "attribution_required": false,
  "license_verified": false,
  "verification_method": "",
  "retrieved_at": "",
  "visual_style": "",
  "educational_check": "",
  "verification_status": ""
}
```

This record supports provenance and auditability. It does not prove ownership,
prove legal safety, clear third-party rights, or replace individual verification.

## Visual-Style Gate

Prefer candidates described or visibly assessed as:

- cartoon, illustration, clipart, vector-like artwork, or simple shapes;
- friendly expression, bright and clear presentation, and child-friendly design;
- uncluttered composition with an obvious focal subject.

Avoid or reject candidates with:

- realistic photography where a suitable illustration exists;
- graphic, disturbing, frightening, sexual, or adult content;
- a visible watermark, advertising, or heavy text;
- logos, trademarks, branded characters, copyrighted fictional characters, or
  fan art;
- screenshots; or
- visually ambiguous content.

Search query wording is not proof of a result's style. For `兔`, a retrieval
layer may construct queries such as `rabbit cartoon`, `rabbit illustration`,
`rabbit clipart`, and `rabbit children illustration`; every returned image must
still pass visual inspection and the other gates.

## Candidate Pipeline

```text
concept
  -> query expansion
  -> provider search
  -> candidate normalization
  -> license metadata check
  -> source-page verification
  -> rights-risk filter
  -> visual-style filter
  -> educational suitability filter
  -> provenance record
  -> approved / rejected
```

License validation and educational suitability are independent requirements. A
candidate that is educationally appropriate but unverified is rejected; a
license-verified candidate that is unsuitable for children is also rejected.

## Machine-Checkable Rejection Reasons

Use one or more of these stable reason codes when a candidate fails a gate:

```text
LICENSE_UNKNOWN
LICENSE_NOT_ALLOWED
SOURCE_UNVERIFIED
THIRD_PARTY_RIGHTS_RISK
WATERMARK
LOGO_OR_BRAND
TEXT_HEAVY
UNSUITABLE_STYLE
INAPPROPRIATE_CONTENT
LOW_QUALITY
SEMANTIC_MISMATCH
AMBIGUOUS_VISUAL
```

Suggested gate mapping:

| Gate | Example rejection reasons |
| --- | --- |
| License metadata | `LICENSE_UNKNOWN`, `LICENSE_NOT_ALLOWED` |
| Source-page verification | `SOURCE_UNVERIFIED` |
| Rights-risk assessment | `THIRD_PARTY_RIGHTS_RISK`, `LOGO_OR_BRAND` |
| Visual style | `WATERMARK`, `TEXT_HEAVY`, `UNSUITABLE_STYLE`, `AMBIGUOUS_VISUAL` |
| Educational suitability | `INAPPROPRIATE_CONTENT`, `LOW_QUALITY`, `SEMANTIC_MISMATCH` |

## Educational Suitability Gate

A candidate must visually represent the requested concept, be suitable for
children ages 2-11, communicate a non-misleading meaning, have sufficient image
quality, and present a clear subject with limited distraction. This gate also
applies the visual-style exclusions above.

The current controlled dataset sets the expected interpretation:

- High-visualizability items normally use direct-object images.
- Medium-visualizability items may require scenes or relationships.
- Low-visualizability grammar/function words must not be forced into literal
  images.

## Fallback Behavior

```text
AI generation succeeds and passes quality checks
  -> use AI result

AI generation fails or is educationally unsuitable
  -> attempt retrieval

Retrieval candidate passes every required gate
  -> use retrieved asset

No candidate passes
  -> report NO_SAFE_VISUAL_FOUND
  -> do not return a random web image
  -> allow another educational modality
```

Alternative educational modalities include an example sentence, relationship
diagram, animation, stroke or decomposition teaching, and teacher- or
parent-assisted explanation. The retrieval system must not convert a failed
image search into an unverified random-web-image result.

## Startup / Production Considerations

A future implementation must define operational treatment for:

- provenance retention and audit logs;
- attribution generation and presentation where required;
- provider terms changes and periodic license re-verification;
- asset removal and replacement when a source, license, or rights concern changes;
- caching versus permanent storage;
- API rate limits and provider outages;
- human review and escalation; and
- jurisdiction-specific legal review before commercial launch.

Retrieved candidates should not automatically become a permanent internal
dataset. Provider terms and individual asset conditions must be rechecked before
production use or when material changes are detected.

## Relationship to Research

This policy operationalizes the principles in
`IMAGE_RETRIEVAL_AND_LICENSING.md`. It does not supersede provider-specific
terms, license text, or jurisdictional legal review.