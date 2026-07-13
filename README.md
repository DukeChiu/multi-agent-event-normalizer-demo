# Event Normalizer Demo

A small Python 3.10 service library that normalizes incoming webhook events into a stable
internal representation.

## Behavior

`normalize_event` returns a dictionary containing:

- `id`: event identifier as trimmed text.
- `type`: lowercase event type.
- `source`: lowercase source name, defaulting to `unknown`.

## Test

```bash
pytest -q
```

This repository is the base branch fixture for the Multi-Agent Code Review real GitHub demo.
Apply the sibling `github-event-normalizer-pr.patch` on a feature branch to create the example
pull request.
