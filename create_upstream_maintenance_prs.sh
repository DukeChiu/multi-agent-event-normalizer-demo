#!/usr/bin/env bash
set -euo pipefail

BASE_BRANCH="main"
PUSH_BRANCHES=false
CREATE_PRS=false
PYTHON_BIN="${PYTHON_BIN:-python3}"
BRANCH_SUFFIX=""
CREATED_BRANCHES=()

usage() {
  printf '%s\n' \
    "Usage: $0 [--base BRANCH] [--suffix NAME] [--push] [--create-prs]" \
    "" \
    "Creates ten non-overlapping maintenance branches from the same clean upstream base." \
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

prepare_new_module() {
  local branch="$1"
  local source_file="$2"
  local test_file="$3"

  git switch "$BASE_BRANCH" >/dev/null
  if [[ -e "$source_file" || -e "$test_file" ]]; then
    printf 'SKIP %-39s module already exists on %s\n' "$branch" "$BASE_BRANCH"
    return 1
  fi
  prepare_branch "$branch"
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
    git switch "$BASE_BRANCH" >/dev/null
    git branch -D "$branch" >/dev/null
    printf 'SKIP %-39s no content change\n' "$branch"
    return 0
  fi
  if printf '%s\n' "$staged_files" | grep -Eq "$GENERATED_PATH_PATTERN"; then
    printf 'Refusing to commit generated files on %s:\n%s\n' \
      "$branch" "$staged_files" >&2
    exit 1
  fi
  git commit -m "$commit_message" >/dev/null
  CREATED_BRANCHES+=("$branch")

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
if prepare_new_module \
  "$required_fields_branch" \
  src/event_normalizer/required_fields.py \
  tests/test_required_fields.py; then
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
fi

aliases_branch="feat/event-type-aliases${BRANCH_SUFFIX}"
if prepare_new_module \
  "$aliases_branch" \
  src/event_normalizer/aliases.py \
  tests/test_aliases.py; then
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
fi

batch_branch="feat/batch-normalization${BRANCH_SUFFIX}"
if prepare_new_module \
  "$batch_branch" \
  src/event_normalizer/batch.py \
  tests/test_batch.py; then
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
fi

source_policy_branch="feat/source-allowlist-policy${BRANCH_SUFFIX}"
if prepare_new_module \
  "$source_policy_branch" \
  src/event_normalizer/source_policy.py \
  tests/test_source_policy.py; then
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
fi

routing_branch="feat/event-routing${BRANCH_SUFFIX}"
if prepare_new_module \
  "$routing_branch" \
  src/event_normalizer/routing.py \
  tests/test_routing.py; then
cat > src/event_normalizer/routing.py <<'PY'
from collections.abc import Mapping
from typing import Any

from event_normalizer.errors import InvalidEventError
from event_normalizer.normalizer import normalize_event


def select_event_route(
    payload: Mapping[str, Any],
    routes: Mapping[str, str],
    *,
    default_route: str = "unmatched",
) -> str:
    """Select a destination from a normalized event type."""
    event = normalize_event(payload)
    normalized_routes = {
        str(event_type).strip().lower(): str(route).strip()
        for event_type, route in routes.items()
    }
    destination = normalized_routes.get(event["type"], default_route).strip()
    if not destination:
        raise InvalidEventError("event route must not be empty")
    return destination
PY
cat > tests/test_routing.py <<'PY'
import pytest

from event_normalizer.errors import InvalidEventError
from event_normalizer.routing import select_event_route


def test_selects_route_using_normalized_event_type():
    route = select_event_route(
        {"id": "evt-1", "type": " User.Created "},
        {"user.created": "identity-events"},
    )
    assert route == "identity-events"


def test_uses_default_route_for_unknown_event_type():
    route = select_event_route(
        {"id": "evt-1", "type": "order.cancelled"},
        {},
        default_route="audit-events",
    )
    assert route == "audit-events"


def test_rejects_empty_route():
    with pytest.raises(InvalidEventError, match="event route must not be empty"):
        select_event_route(
            {"id": "evt-1", "type": "user.created"},
            {"user.created": "   "},
        )
PY
finish_branch \
  "$routing_branch" \
  "Route normalized webhook events" \
  "Add normalized event routing" \
  "Adds deterministic routing by normalized event type with a default destination." \
  src/event_normalizer/routing.py \
  tests/test_routing.py
fi

redaction_branch="feat/sensitive-field-redaction${BRANCH_SUFFIX}"
if prepare_new_module \
  "$redaction_branch" \
  src/event_normalizer/redaction.py \
  tests/test_redaction.py; then
cat > src/event_normalizer/redaction.py <<'PY'
from collections.abc import Collection, Mapping
from typing import Any

from event_normalizer.errors import InvalidEventError


DEFAULT_SENSITIVE_FIELDS = frozenset({"authorization", "password", "token"})


def redact_payload(
    payload: Mapping[str, Any],
    sensitive_fields: Collection[str] = DEFAULT_SENSITIVE_FIELDS,
    *,
    replacement: str = "[REDACTED]",
) -> dict[str, Any]:
    """Return a copy with configured top-level sensitive fields redacted."""
    if not isinstance(payload, Mapping):
        raise InvalidEventError("payload must be a mapping")
    if not replacement:
        raise InvalidEventError("redaction replacement must not be empty")

    blocked = {str(field).strip().lower() for field in sensitive_fields}
    return {
        str(key): replacement if str(key).strip().lower() in blocked else value
        for key, value in payload.items()
    }
PY
cat > tests/test_redaction.py <<'PY'
import pytest

from event_normalizer.errors import InvalidEventError
from event_normalizer.redaction import redact_payload


def test_redacts_sensitive_fields_without_mutating_input():
    payload = {"id": "evt-1", "Authorization": "secret", "token": "abc"}
    result = redact_payload(payload)

    assert result == {
        "id": "evt-1",
        "Authorization": "[REDACTED]",
        "token": "[REDACTED]",
    }
    assert payload["token"] == "abc"


def test_supports_custom_sensitive_fields():
    result = redact_payload({"email": "user@example.com"}, {"email"})
    assert result["email"] == "[REDACTED]"


def test_rejects_empty_replacement():
    with pytest.raises(InvalidEventError, match="replacement must not be empty"):
        redact_payload({"token": "abc"}, replacement="")
PY
finish_branch \
  "$redaction_branch" \
  "Redact sensitive webhook fields" \
  "Add sensitive field redaction" \
  "Adds non-mutating, case-insensitive redaction for webhook secrets." \
  src/event_normalizer/redaction.py \
  tests/test_redaction.py
fi

fingerprint_branch="feat/event-fingerprints${BRANCH_SUFFIX}"
if prepare_new_module \
  "$fingerprint_branch" \
  src/event_normalizer/fingerprint.py \
  tests/test_fingerprint.py; then
cat > src/event_normalizer/fingerprint.py <<'PY'
import hashlib
import json
from collections.abc import Mapping
from typing import Any

from event_normalizer.normalizer import normalize_event


def event_fingerprint(payload: Mapping[str, Any]) -> str:
    """Build a stable SHA-256 fingerprint from normalized event fields."""
    event = normalize_event(payload)
    canonical = json.dumps(
        event,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
PY
cat > tests/test_fingerprint.py <<'PY'
from event_normalizer.fingerprint import event_fingerprint


def test_fingerprint_is_stable_after_normalization():
    left = event_fingerprint(
        {"id": "evt-1", "type": " User.Created ", "source": " Billing "}
    )
    right = event_fingerprint(
        {"source": "billing", "type": "user.created", "id": "evt-1"}
    )
    assert left == right
    assert len(left) == 64


def test_fingerprint_changes_with_event_identity():
    left = event_fingerprint({"id": "evt-1", "type": "user.created"})
    right = event_fingerprint({"id": "evt-2", "type": "user.created"})
    assert left != right
PY
finish_branch \
  "$fingerprint_branch" \
  "Add stable event fingerprints" \
  "Fingerprint normalized webhook events" \
  "Adds canonical SHA-256 fingerprints for idempotency and audit correlation." \
  src/event_normalizer/fingerprint.py \
  tests/test_fingerprint.py
fi

retry_branch="feat/delivery-retry-policy${BRANCH_SUFFIX}"
if prepare_new_module \
  "$retry_branch" \
  src/event_normalizer/retry_policy.py \
  tests/test_retry_policy.py; then
cat > src/event_normalizer/retry_policy.py <<'PY'
from event_normalizer.errors import InvalidEventError


def retry_delay_seconds(
    attempt: int,
    *,
    base_seconds: int = 2,
    maximum_seconds: int = 300,
) -> int:
    """Return a capped exponential delay for a zero-based delivery attempt."""
    if isinstance(attempt, bool) or attempt < 0:
        raise InvalidEventError("retry attempt must be a non-negative integer")
    if base_seconds <= 0 or maximum_seconds <= 0:
        raise InvalidEventError("retry delays must be positive")
    return min(maximum_seconds, base_seconds * (2**attempt))
PY
cat > tests/test_retry_policy.py <<'PY'
import pytest

from event_normalizer.errors import InvalidEventError
from event_normalizer.retry_policy import retry_delay_seconds


def test_calculates_capped_exponential_delay():
    assert retry_delay_seconds(0) == 2
    assert retry_delay_seconds(3) == 16
    assert retry_delay_seconds(20) == 300


@pytest.mark.parametrize("attempt", [-1, True])
def test_rejects_invalid_attempt(attempt):
    with pytest.raises(InvalidEventError, match="non-negative integer"):
        retry_delay_seconds(attempt)
PY
finish_branch \
  "$retry_branch" \
  "Add webhook delivery retry policy" \
  "Add capped delivery retry backoff" \
  "Adds validated exponential backoff with a deterministic maximum delay." \
  src/event_normalizer/retry_policy.py \
  tests/test_retry_policy.py
fi

partition_branch="feat/event-partitioning${BRANCH_SUFFIX}"
if prepare_new_module \
  "$partition_branch" \
  src/event_normalizer/partitioning.py \
  tests/test_partitioning.py; then
cat > src/event_normalizer/partitioning.py <<'PY'
import hashlib
from collections.abc import Mapping
from typing import Any

from event_normalizer.errors import InvalidEventError
from event_normalizer.normalizer import normalize_event


def event_partition(payload: Mapping[str, Any], partition_count: int) -> int:
    """Map an event identifier to a stable zero-based partition."""
    if isinstance(partition_count, bool) or partition_count <= 0:
        raise InvalidEventError("partition count must be a positive integer")
    event = normalize_event(payload)
    digest = hashlib.blake2b(event["id"].encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(digest, byteorder="big") % partition_count
PY
cat > tests/test_partitioning.py <<'PY'
import pytest

from event_normalizer.errors import InvalidEventError
from event_normalizer.partitioning import event_partition


def test_assigns_same_event_to_same_partition():
    payload = {"id": "evt-42", "type": "user.created"}
    assert event_partition(payload, 16) == event_partition(payload, 16)
    assert 0 <= event_partition(payload, 16) < 16


@pytest.mark.parametrize("partition_count", [0, -1, True])
def test_rejects_invalid_partition_count(partition_count):
    with pytest.raises(InvalidEventError, match="positive integer"):
        event_partition({"id": "evt-1", "type": "user.created"}, partition_count)
PY
finish_branch \
  "$partition_branch" \
  "Add stable event partitioning" \
  "Partition events by normalized identifier" \
  "Adds deterministic partition selection for parallel webhook processing." \
  src/event_normalizer/partitioning.py \
  tests/test_partitioning.py
fi

expiration_branch="feat/event-expiration${BRANCH_SUFFIX}"
if prepare_new_module \
  "$expiration_branch" \
  src/event_normalizer/expiration.py \
  tests/test_expiration.py; then
cat > src/event_normalizer/expiration.py <<'PY'
from datetime import datetime, timedelta, timezone

from event_normalizer.errors import InvalidEventError


def is_event_expired(
    occurred_at: str,
    ttl_seconds: int,
    *,
    now: datetime | None = None,
) -> bool:
    """Return whether an ISO-8601 event timestamp is older than its TTL."""
    if isinstance(ttl_seconds, bool) or ttl_seconds < 0:
        raise InvalidEventError("event TTL must be a non-negative integer")
    try:
        parsed = datetime.fromisoformat(str(occurred_at).replace("Z", "+00:00"))
    except ValueError as exc:
        raise InvalidEventError("event timestamp must be ISO-8601") from exc
    if parsed.tzinfo is None:
        raise InvalidEventError("event timestamp must include a timezone")

    reference = now or datetime.now(timezone.utc)
    if reference.tzinfo is None:
        raise InvalidEventError("reference time must include a timezone")
    return parsed + timedelta(seconds=ttl_seconds) < reference
PY
cat > tests/test_expiration.py <<'PY'
from datetime import datetime, timezone

import pytest

from event_normalizer.errors import InvalidEventError
from event_normalizer.expiration import is_event_expired


NOW = datetime(2026, 7, 14, 12, 0, tzinfo=timezone.utc)


def test_detects_expired_and_active_events():
    assert is_event_expired("2026-07-14T11:00:00Z", 1800, now=NOW) is True
    assert is_event_expired("2026-07-14T11:45:00Z", 1800, now=NOW) is False


def test_rejects_timestamp_without_timezone():
    with pytest.raises(InvalidEventError, match="include a timezone"):
        is_event_expired("2026-07-14T11:00:00", 1800, now=NOW)
PY
finish_branch \
  "$expiration_branch" \
  "Add webhook event expiration checks" \
  "Validate webhook event expiration" \
  "Adds timezone-aware TTL checks for rejecting stale webhook deliveries." \
  src/event_normalizer/expiration.py \
  tests/test_expiration.py
fi

git switch "$BASE_BRANCH" >/dev/null
printf '\nCreated %s maintenance branch(es) from %s.\n' \
  "${#CREATED_BRANCHES[@]}" "$BASE_BRANCH"
if [[ ${#CREATED_BRANCHES[@]} -gt 0 ]]; then
  printf 'Recommended merge and scan order:\n'
  branch_number=1
  for created_branch in "${CREATED_BRANCHES[@]}"; do
    printf '  %02d. %s\n' "$branch_number" "$created_branch"
    branch_number=$((branch_number + 1))
  done
fi
if ! $PUSH_BRANCHES; then
  printf 'Branches are local only. Re-run in a fresh clone with --push or push them manually.\n'
fi
