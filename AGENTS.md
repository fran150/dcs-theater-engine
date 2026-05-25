# Project Instructions

## Comment Style

- Use short, plain-language comments that explain the purpose of a small group of lines.
- Prefer comments that help orient the reader to framework wiring, setup code, or project structure.
- Keep comments practical and concise; avoid long formal explanations for obvious code.
- Match the existing local style when adding or editing comments.

## Public API Documentation

- Add descriptive docstrings for public classes and dataclasses whose fields are part of the constructor or caller-facing API.
- For dataclasses, include an `Attributes:` section that explains each constructor field in plain language.
- When changing constructor fields, runtime behavior, or public methods, update the related docstring in the same change.
- Prefer docstrings for caller-facing documentation and short inline comments for local implementation context.

## Campaign Runtime Design

- Do not assume the campaign engine needs frame-rate or second-precision simulation.
- Prefer coarse campaign steps, scheduled events, and statistical resolution for campaign-level outcomes.
- Treat wall-clock time as approximate pacing; campaign correctness should not depend on exact real elapsed seconds.
- The UI may poll slowly or consume published updates, but it should not drive campaign tick rules.
