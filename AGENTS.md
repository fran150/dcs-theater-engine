# Project Instructions

## Comment Style

- Use short, plain-language comments that explain the purpose of a small group of lines.
- Prefer comments that help orient the reader to framework wiring, setup code, or project structure.
- Keep comments practical and concise; avoid long formal explanations for obvious code.
- Match the existing local style when adding or editing comments.

## Campaign Runtime Design

- Do not assume the campaign engine needs frame-rate or second-precision simulation.
- Prefer coarse campaign steps, scheduled events, and statistical resolution for campaign-level outcomes.
- Treat wall-clock time as approximate pacing; campaign correctness should not depend on exact real elapsed seconds.
- The UI may poll slowly or consume published updates, but it should not drive campaign tick rules.
