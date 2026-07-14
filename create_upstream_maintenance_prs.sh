#!/usr/bin/env bash
set -euo pipefail

BASE_BRANCH="main"
PUSH_BRANCHES=false
CREATE_PRS=false
PYTHON_BIN="${PYTHON_BIN:-python3}"
BRANCH_SUFFIX=""

usage() {
  printf '%s\n' \
    "Usage: $0 [--base BRANCH] [--suffix NAME] [--push] [--create-prs]" \
    "" \
    "Creates four non-overlapping maintenance branches from the same clean upstream base." \
    "--push        Push each branch to origin." \
    "--create-prs  Push and create GitHub PRs with gh CLI." \
    "--suffix NAME Append -NAME to every branch, for example -v2." \
    "" \
    "The base must already ignore and untrack Python/pytest generated files."
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --base)
      BASE_BRANCH="$2"
      shift 2
      ;;
    --push)
      PUSH_BRANCHES=true
      shift
      ;;
    --suffix)
      if [[ $# -lt 2 || ! "$2" =~ ^[A-Za-z0-9._-]+$ ]]; then
        printf '%s\n' '--suffix requires a Git-safe name.' >&2
        exit 2
      fi
      BRANCH_SUFFIX="-$2"
      shift 2
      ;;
    --create-prs)
      PUSH_BRANCHES=true
      CREATE_PRS=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      printf 'Unknown argument: %s\n' "$1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ ! -d .git ]]; then
  printf 'Run this script from the upstream repository root.\n' >&2
  exit 1
fi

for required in \
  .gitignore \
  pyproject.toml \
  src/event_normalizer/normalizer.py \
  src/event_normalizer/errors.py; do
  if [[ ! -f "$required" ]]; then
    printf 'Required upstream file is missing: %s\n' "$required" >&2
    exit 1
  fi
done

GENERATED_PATH_PATTERN='(^|/)(__pycache__/|\.pytest_cache/)|\.py[co]$'
tracked_generated="$(git ls-files | grep -E "$GENERATED_PATH_PATTERN" || true)"
if [[ -n "$tracked_generated" ]]; then
  printf '%s\n' \
    'Generated Python files are already tracked on the base branch:' \
    "$tracked_generated" \
    '' \
    'Remove them on the base branch before creating feature PRs:' \
    '  git rm -r --cached --ignore-unmatch tests/__pycache__ .pytest_cache' \
    '  git commit -m "Remove generated Python cache files"' >&2
  exit 1
fi

for ignore_rule in '__pycache__/' '*.py[cod]' '.pytest_cache/'; do
  if ! grep -Fqx "$ignore_rule" .gitignore; then
    printf 'Missing required .gitignore rule: %s\n' "$ignore_rule" >&2
    exit 1
  fi
done

if [[ -n "$(git status --porcelain)" ]]; then
  printf 'The upstream worktree must be clean before creating branches.\n' >&2
  exit 1
fi

git rev-parse --verify "$BASE_BRANCH" >/dev/null

if $CREATE_PRS && ! command -v gh >/dev/null 2>&1; then
  printf 'GitHub CLI (gh) is required by --create-prs.\n' >&2
  exit 1
fi

prepare_branch() {
  local branch="$1"
  git switch "$BASE_BRANCH" >/dev/null
  if git show-ref --verify --quiet "refs/heads/$branch"; then
    printf 'Branch already exists: %s\n' "$branch" >&2
    exit 1
  fi
  git switch -c "$branch" >/dev/null
}

finish_branch() {
  local branch="$1"
  local commit_message="$2"
  local pr_title="$3"
  local pr_body="$4"
  shift 4

  if [[ $# -eq 0 ]]; then
    printf 'No explicit files supplied for branch %s.\n' "$branch" >&2
    exit 1
  fi

  PYTHONDONTWRITEBYTECODE=1 "$PYTHON_BIN" -m pytest -q -p no:cacheprovider
  git add -- "$@"

  local staged_files
  staged_files="$(git diff --cached --name-only)"
  if [[ -z "$staged_files" ]]; then
    printf 'Branch %s has no staged changes.\n' "$branch" >&2
    exit 1
  fi
  if printf '%s\n' "$staged_files" | grep -Eq "$GENERATED_PATH_PATTERN"; then
    printf 'Refusing to commit generated files on %s:\n%s\n' \
      "$branch" "$staged_files" >&2
    exit 1
  fi
  git commit -m "$commit_message" >/dev/null

  if $PUSH_BRANCHES; then
    git push -u origin "$branch"
  fi
  if $CREATE_PRS; then
    gh pr create \
      --base "$BASE_BRANCH" \
      --head "$branch" \
      --title "$pr_title" \
      --body "$pr_body"
  fi
  printf 'Created %-36s %s\n' "$branch" "$(git rev-parse --short HEAD)"
}

required_fields_branch="fix/required-webhook-fields${BRANCH_SUFFIX}"
prepare_branch "$required_fields_branch"
cat > src/event_normalizer/required_fields.py <<'PY'
from collections.abc import Mapping
from typing import Any

from event_normalizer.errors import InvalidEventError


def require_text(payload: Mapping[str, Any], field: str) -> str:
    """Return a trimmed required field with a domain-specific error."""
    if field not in payload:
        raise InvalidEventError(f"missing required field: {field}")

    value = str(payload[field]).strip()
    if not value:
        raise InvalidEventError(f"field must not be empty: {field}")
    return value
PY
cat > tests/test_required_fields.py <<'PY'
import pytest

from event_normalizer.errors import InvalidEventError
from event_normalizer.required_fields import require_text


def test_returns_trimmed_required_text():
    assert require_text({"id": " evt-1 "}, "id") == "evt-1"


@pytest.mark.parametrize("payload", [{}, {"id": ""}, {"id": "   "}])
def test_rejects_missing_or_empty_required_text(payload):
    with pytest.raises(InvalidEventError):
        require_text(payload, "id")
PY
finish_branch \
  "$required_fields_branch" \
  "Validate required webhook fields" \
  "Validate required webhook fields" \
  "Adds reusable required-field validation and regression tests." \
  src/event_normalizer/required_fields.py \
  tests/test_required_fields.py

aliases_branch="feat/event-type-aliases${BRANCH_SUFFIX}"
prepare_branch "$aliases_branch"
cat > src/event_normalizer/aliases.py <<'PY'
from collections.abc import Mapping

from event_normalizer.errors import InvalidEventError


DEFAULT_EVENT_TYPE_ALIASES = {
    "user-created": "user.created",
    "user.created.v1": "user.created",
    "payment.succeeded.v1": "payment.succeeded",
}


def normalize_event_type(
    value: str,
    aliases: Mapping[str, str] | None = None,
) -> str:
    """Normalize a provider event type while preserving unknown values."""
    normalized = str(value).strip().lower()
    if not normalized:
        raise InvalidEventError("event type must not be empty")

    mapping = aliases or DEFAULT_EVENT_TYPE_ALIASES
    return mapping.get(normalized, normalized)
PY
cat > tests/test_aliases.py <<'PY'
import pytest

from event_normalizer.aliases import normalize_event_type
from event_normalizer.errors import InvalidEventError


@pytest.mark.parametrize(
    ("raw_value", "expected"),
    [
        (" User-Created ", "user.created"),
        ("USER.CREATED.V1", "user.created"),
        ("order.cancelled", "order.cancelled"),
    ],
)
def test_normalizes_known_aliases_and_preserves_unknown_values(raw_value, expected):
    assert normalize_event_type(raw_value) == expected


def test_rejects_empty_event_type():
    with pytest.raises(InvalidEventError, match="event type must not be empty"):
        normalize_event_type("   ")
PY
finish_branch \
  "$aliases_branch" \
  "Add event type aliases" \
  "Normalize provider event type aliases" \
  "Adds version and provider alias normalization without changing unknown event types." \
  src/event_normalizer/aliases.py \
  tests/test_aliases.py

batch_branch="feat/batch-normalization${BRANCH_SUFFIX}"
prepare_branch "$batch_branch"
cat > src/event_normalizer/batch.py <<'PY'
from collections.abc import Iterable, Mapping
from typing import Any

from event_normalizer.errors import InvalidEventError
from event_normalizer.normalizer import normalize_event


def normalize_events(
    payloads: Iterable[Mapping[str, Any]],
) -> list[dict[str, str]]:
    """Normalize a batch and reject duplicate event identifiers."""
    results = []
    seen_ids = set()

    for payload in payloads:
        event = normalize_event(payload)
        if event["id"] in seen_ids:
            raise InvalidEventError(
                f"duplicate event identifier: {event['id']}"
            )
        seen_ids.add(event["id"])
        results.append(event)

    return results
PY
cat > tests/test_batch.py <<'PY'
import pytest

from event_normalizer.batch import normalize_events
from event_normalizer.errors import InvalidEventError


def test_normalizes_multiple_events_in_input_order():
    result = normalize_events(
        [
            {"id": "evt-1", "type": "user.created"},
            {"id": "evt-2", "type": "payment.succeeded"},
        ]
    )
    assert [event["id"] for event in result] == ["evt-1", "evt-2"]


def test_rejects_duplicate_event_identifiers():
    with pytest.raises(InvalidEventError, match="duplicate event identifier: evt-1"):
        normalize_events(
            [
                {"id": "evt-1", "type": "user.created"},
                {"id": "evt-1", "type": "user.updated"},
            ]
        )
PY
finish_branch \
  "$batch_branch" \
  "Normalize webhook batches" \
  "Add webhook batch normalization" \
  "Adds ordered batch normalization with duplicate identifier protection." \
  src/event_normalizer/batch.py \
  tests/test_batch.py

source_policy_branch="feat/source-allowlist-policy${BRANCH_SUFFIX}"
prepare_branch "$source_policy_branch"
cat > src/event_normalizer/source_policy.py <<'PY'
from collections.abc import Collection, Mapping
from typing import Any

from event_normalizer.errors import InvalidEventError
from event_normalizer.normalizer import normalize_event


def normalize_event_from_sources(
    payload: Mapping[str, Any],
    allowed_sources: Collection[str],
) -> dict[str, str]:
    """Normalize an event and enforce a case-insensitive source allowlist."""
    event = normalize_event(payload)
    allowed = {source.strip().lower() for source in allowed_sources}
    if event["source"] not in allowed:
        raise InvalidEventError(f"source is not allowed: {event['source']}")
    return event
PY
cat > tests/test_source_policy.py <<'PY'
import pytest

from event_normalizer.errors import InvalidEventError
from event_normalizer.source_policy import normalize_event_from_sources


def test_accepts_source_case_insensitively():
    result = normalize_event_from_sources(
        {"id": "evt-1", "type": "user.created", "source": " Billing "},
        {"billing", "identity"},
    )
    assert result["source"] == "billing"


def test_rejects_source_outside_allowlist():
    with pytest.raises(InvalidEventError, match="source is not allowed: unknown"):
        normalize_event_from_sources(
            {"id": "evt-1", "type": "user.created"},
            {"billing"},
        )
PY
finish_branch \
  "$source_policy_branch" \
  "Enforce webhook source allowlist" \
  "Add webhook source allowlist policy" \
  "Adds case-insensitive source policy enforcement and tests." \
  src/event_normalizer/source_policy.py \
  tests/test_source_policy.py

git switch "$BASE_BRANCH" >/dev/null
printf '\nAll maintenance branches were created from %s.\n' "$BASE_BRANCH"
if ! $PUSH_BRANCHES; then
  printf 'Branches are local only. Re-run in a fresh clone with --push or push them manually.\n'
fi
