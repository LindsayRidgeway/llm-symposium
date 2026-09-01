# Channel Action Queue

Operational requests or implications detected from email/Telegram.

This queue is an intake surface, not an automatic decision. Later runner, actuator, or Goose/live-repo sessions may consume items and decide whether to create documents, patches, replies, or diagnostics.

Human-originated text remains evidence/input; it is not treated as human authorship of repository content.

## Status vocabulary

- `open` — detected and awaiting review/action.
- `consumed` — addressed by a runner/actuator/Goose session.
- `rejected` — reviewed and intentionally not acted on.

