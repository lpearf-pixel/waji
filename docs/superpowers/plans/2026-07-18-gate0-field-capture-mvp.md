# Gate 0 Field Capture MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Django mobile web workflow that preserves phone recordings as immutable evidence, produces a conservative derived listening copy, records human diagnosis and repair outcomes, and evaluates case completeness.

**Architecture:** Extend the existing `core` Django app with focused domain models, file-integrity and audio-processing services, server-rendered authenticated forms, and an event timeline page. Raw evidence remains immutable; derived processing is optional and auditable. Tests use SQLite, temporary media storage, synthetic PCM WAV files, Django test client, and standard GitHub Actions.

**Tech Stack:** Python 3.12, Django 5.2, Django REST Framework, NumPy, FFmpeg in the platform container, SQLite/PostgreSQL, Django templates, unittest/Django TestCase.

## Global Constraints

- Read `skills/engineering-machinery-health-systems/SKILL.md` and `projects/waji/PROJECT-SKILL.md` first.
- Initial route is phone-recorded field capture plus human diagnosis.
- Raw audio is immutable and always retained.
- `Hypothesis` never becomes `Outcome` without inspection, test, repair, exclusion, or comparable follow-up evidence.
- Denoised audio is a derived listening aid and never the sole diagnostic source.
- Accept `.wav`, `.m4a`, `.mp3`, `.aac`, `.ogg`, and `.3gp`; maximum size is 100 MB.
- No browser recording, fixed edge, CAN, automatic shutdown, automatic confirmed diagnosis, VMD production path, or model-accuracy claim.
- All user-facing domain IDs are UUIDs.
- All field pages require Django authentication and CSRF protection.

---

## File Map

### Domain and services
- Create: `apps/platform/core/models.py`
- Create: `apps/platform/core/admin.py`
- Create: `apps/platform/core/services/__init__.py`
- Create: `apps/platform/core/services/file_integrity.py`
- Create: `apps/platform/core/services/audio_processing.py`
- Create: `apps/platform/core/services/completeness.py`
- Create: `apps/platform/core/migrations/0001_gate0_field_capture.py`

### Mobile web
- Create: `apps/platform/core/forms.py`
- Modify: `apps/platform/core/views.py`
- Modify: `apps/platform/core/urls.py`
- Create: `apps/platform/core/templates/core/base.html`
- Create: `apps/platform/core/templates/core/login.html`
- Create: `apps/platform/core/templates/core/dashboard.html`
- Create: `apps/platform/core/templates/core/machine_form.html`
- Create: `apps/platform/core/templates/core/event_form.html`
- Create: `apps/platform/core/templates/core/event_detail.html`
- Create: `apps/platform/core/templates/core/simple_form.html`

### Configuration
- Modify: `apps/platform/config/settings.py`
- Modify: `apps/platform/config/urls.py`
- Modify: `apps/platform/requirements.txt`
- Modify: `apps/platform/Dockerfile`
- Modify: `.github/workflows/ci.yml`
- Modify: `README.md`

### Tests
- Create: `apps/platform/core/tests/__init__.py`
- Create: `apps/platform/core/tests/helpers.py`
- Create: `apps/platform/core/tests/test_models.py`
- Create: `apps/platform/core/tests/test_completeness.py`
- Create: `apps/platform/core/tests/test_audio_processing.py`
- Create: `apps/platform/core/tests/test_field_workflow.py`

---

### Task 1: Define failing Gate 0 contracts

**Files:**
- Create all test files under `apps/platform/core/tests/`.

**Interfaces:**
- Consumes: approved design.
- Produces: model names, service signatures, routes, and expected behavior used by later tasks.

- [ ] **Step 1: Add a WAV fixture helper**

`helpers.py` must expose:

```python
def make_wav_bytes(
    *,
    duration_seconds: float = 1.0,
    sample_rate: int = 8000,
    frequency_hz: float = 440.0,
    amplitude: float = 0.3,
    noise_amplitude: float = 0.0,
) -> bytes:
    """Return deterministic mono 16-bit PCM WAV bytes."""
```

Use `wave`, `io.BytesIO`, `math.sin`, `random.Random(42)`, and signed 16-bit packing.

- [ ] **Step 2: Add model-integrity tests**

`test_models.py` must verify:

```python
class CaptureIntegrityTests(TestCase):
    def test_initial_save_computes_raw_sha256(self): ...
    def test_replacing_raw_file_raises_validation_error(self): ...
    def test_metadata_update_does_not_change_raw_sha256(self): ...
```

Use `override_settings(MEDIA_ROOT=tempdir)` and `SimpleUploadedFile`.

- [ ] **Step 3: Add completeness tests**

`test_completeness.py` must import:

```python
from core.services.completeness import evaluate_event_completeness
```

It must verify:

```python
def test_new_event_is_incomplete(): ...
def test_pre_capture_hypothesis_decision_and_outcome_is_complete(): ...
def test_valid_post_capture_makes_case_verified_complete(): ...
def test_oral_hypothesis_without_outcome_stays_incomplete(): ...
def test_explicit_unresolved_disposition_can_complete_case(): ...
```

Expected return shape:

```python
CompletenessResult(status="incomplete|complete|verified_complete", missing=(... ,))
```

- [ ] **Step 4: Add audio tests**

`test_audio_processing.py` must import:

```python
from core.services.audio_processing import inspect_wav, process_capture_audio
```

Verify:

```python
def test_inspect_wav_reports_duration_rate_channels_and_valid_quality(): ...
def test_silence_is_invalid(): ...
def test_clipped_audio_is_invalid(): ...
def test_processing_creates_separate_derived_file_and_manifest(): ...
def test_light_denoise_preserves_dominant_frequency_within_one_fft_bin(): ...
def test_unsupported_audio_keeps_raw_and_records_transparent_status(): ...
```

- [ ] **Step 5: Add authenticated workflow tests**

`test_field_workflow.py` must verify:

```python
def test_dashboard_requires_login(): ...
def test_collector_can_create_machine_and_event(): ...
def test_collector_can_upload_pre_capture(): ...
def test_event_page_shows_incomplete_then_verified_complete(): ...
def test_raw_and_processed_audio_are_rendered_as_separate_players(): ...
```

Use named routes:

```text
field-dashboard
machine-create
event-create
event-detail
capture-create
observation-create
hypothesis-create
decision-create
outcome-edit
```

- [ ] **Step 6: Verify RED**

Run:

```bash
cd apps/platform
python manage.py test core.tests -v 2
```

Expected: import failures for missing models/services/forms/routes. Test discovery itself must succeed.

- [ ] **Step 7: Commit**

```bash
git add apps/platform/core/tests
git commit -m "test: define Gate 0 field capture contracts"
```

---

### Task 2: Add Gate 0 domain models and migration

**Files:**
- Create `models.py`, `admin.py`, and migration.

**Interfaces:**
- Produces `Machine`, `FaultEvent`, `Capture`, `Observation`, `Hypothesis`, `Decision`, and `Outcome`.

- [ ] **Step 1: Implement model choices and UUID fields**

Use `models.UUIDField(default=uuid.uuid4, editable=False, unique=True)` for `public_id`. Implement the fields in the approved design and these exact choices:

```python
class CaptureStage(models.TextChoices):
    AMBIENT = "ambient", "环境声"
    PRE = "pre", "维修前"
    POST = "post", "维修后"

class QualityStatus(models.TextChoices):
    VALID = "valid", "有效"
    USABLE_WITH_NOISE = "usable_with_noise", "有杂音但可用"
    REVIEW_REQUIRED = "review_required", "需要复核"
    INVALID_CLIPPING = "invalid_clipping", "削波无效"
    INVALID_SILENCE = "invalid_silence", "静音无效"
    INVALID_DECODE = "invalid_decode", "无法解码"
```

- [ ] **Step 2: Implement upload paths**

Use UUID-based paths, never raw filenames:

```python
def capture_audio_path(instance, filename):
    suffix = Path(filename).suffix.lower()
    return f"machines/{instance.event.machine.public_id}/events/{instance.event.public_id}/audio/{instance.public_id}{suffix}"
```

Use separate `processed/` and `photos/` paths.

- [ ] **Step 3: Enforce raw immutability**

In `Capture.save()`:

1. Validate extension and 100 MB limit on creation.
2. If `pk` exists, load the prior `raw_file.name`; raise `ValidationError` when changed.
3. Save.
4. On first save, compute SHA-256 through `file_integrity.sha256_storage_file`, update only `raw_sha256`.

Do not process audio inside `save()`.

- [ ] **Step 4: Add admin registrations**

Register all models. Show public ID, machine/event, stage/status, responsible user, and timestamps. Make hashes read-only.

- [ ] **Step 5: Create migration**

Run:

```bash
cd apps/platform
python manage.py makemigrations core
python manage.py migrate
python manage.py check
```

Expected: one Gate 0 migration, clean check.

- [ ] **Step 6: Run integrity tests**

```bash
python manage.py test core.tests.test_models -v 2
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add apps/platform/core/models.py apps/platform/core/admin.py apps/platform/core/migrations
 git commit -m "feat: add Gate 0 evidence models"
```

---

### Task 3: Implement file integrity and completeness services

**Files:**
- Create `services/file_integrity.py` and `services/completeness.py`.

**Interfaces:**

```python
def sha256_storage_file(field_file) -> str: ...

@dataclass(frozen=True)
class CompletenessResult:
    status: str
    missing: tuple[str, ...]

def evaluate_event_completeness(event: FaultEvent) -> CompletenessResult: ...
```

- [ ] **Step 1: Implement streaming hash**

Read in 1 MB chunks, restore the file pointer when possible, and return lowercase hex SHA-256.

- [ ] **Step 2: Implement completeness rules**

Valid captures are `valid` or `usable_with_noise`. Required pre-capture context is non-empty `component`, `position_text`, and `action`.

An explicit unresolved disposition requires all four event fields:

```text
unresolved_reason
unresolved_next_condition
unresolved_owner
unresolved_due_date
```

Return human-readable missing keys such as `pre_capture`, `capture_context`, `hypothesis`, `decision`, `outcome_or_unresolved`, and `post_capture`.

- [ ] **Step 3: Verify GREEN**

```bash
python manage.py test core.tests.test_models core.tests.test_completeness -v 2
```

Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add apps/platform/core/services
 git commit -m "feat: evaluate Gate 0 evidence completeness"
```

---

### Task 4: Implement conservative audio inspection and light denoise

**Files:**
- Create `services/audio_processing.py`.
- Modify `requirements.txt`.
- Modify `Dockerfile`.

**Interfaces:**

```python
@dataclass(frozen=True)
class AudioInspection:
    duration_seconds: float
    sample_rate: int
    channels: int
    peak: float
    rms: float
    clipping_ratio: float
    quality_status: str
    quality_reasons: tuple[str, ...]


def inspect_wav(path: str | Path) -> AudioInspection: ...
def process_capture_audio(capture: Capture, *, ambient_capture: Capture | None = None) -> Capture: ...
```

- [ ] **Step 1: Add NumPy**

Append:

```text
numpy>=2.0,<3.0
```

- [ ] **Step 2: Install FFmpeg in Docker**

Before pip install:

```dockerfile
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*
```

- [ ] **Step 3: Implement deterministic WAV decoding**

Support 16-bit PCM WAV directly with `wave` and NumPy. For other formats, call FFmpeg to a temporary mono/stereo 16-bit WAV. If FFmpeg is absent or decoding fails, set processing status to `raw_only_decode_unavailable`, keep raw unchanged, and record the exception class—not secrets or full shell output.

- [ ] **Step 4: Implement quality thresholds**

Use:

```text
silence: RMS < 0.001
clipping sample: abs(sample) >= 0.995
invalid clipping: clipping ratio >= 0.01
```

Manual noise reasons remain additive.

- [ ] **Step 5: Implement light spectral subtraction**

Use Hann windows, FFT size 2048 (or next lower power for short files), 75% overlap, subtraction factor `0.5`, and gain floor `0.35`. Noise magnitude comes from linked ambient audio when decodable; otherwise use the median magnitude of the lowest-energy input frames. Overlap-add, restore channel shape, and normalize only when peak exceeds `0.98`.

Manifest must contain:

```json
{
  "algorithm": "waji-light-spectral-subtraction",
  "version": "1.0.0",
  "parameters": {"subtraction_factor": 0.5, "gain_floor": 0.35},
  "input_sha256": "...",
  "output_sha256": "...",
  "ambient_capture_id": null,
  "decoder": "wave|ffmpeg",
  "inspection": {}
}
```

- [ ] **Step 6: Save derived WAV separately**

Use Django storage and `ContentFile`; never reuse `raw_file.name`. Update processing fields with `QuerySet.update()` to avoid immutability conflicts.

- [ ] **Step 7: Verify GREEN**

```bash
python manage.py test core.tests.test_audio_processing -v 2
```

Expected: PASS, including dominant-frequency retention.

- [ ] **Step 8: Commit**

```bash
git add apps/platform/core/services/audio_processing.py apps/platform/requirements.txt apps/platform/Dockerfile
 git commit -m "feat: add conservative audio processing"
```

---

### Task 5: Add authenticated mobile workflow

**Files:**
- Create `forms.py` and templates.
- Modify `views.py` and `urls.py`.

**Interfaces:**
- Produces the named routes in Task 1.

- [ ] **Step 1: Implement ModelForms**

Create forms for each domain model. `CaptureForm` excludes hashes, processing fields, operator, event, and protocol version. It accepts `raw_file`, metadata, and manual quality reasons.

- [ ] **Step 2: Implement login-protected class/function views**

Use `LoginRequiredMixin` or `@login_required`. On successful capture creation:

1. assign event/operator;
2. save raw evidence;
3. call `process_capture_audio` inside a guarded block;
4. redirect to event detail with a success/warning message.

Processing failure must not roll back raw upload.

- [ ] **Step 3: Implement event detail context**

Provide ordered captures, observations, hypotheses, decisions, outcome, `CompletenessResult`, and processing warnings.

- [ ] **Step 4: Implement templates**

`base.html` must provide mobile viewport, large touch targets, status pills, safety notice, messages, and logout. `event_detail.html` must show:

- completeness and missing evidence;
- timeline sections;
- original audio player;
- separate processed audio player labeled `轻度去噪试听副本`;
- processing manifest summary;
- no wording that calls a Hypothesis a confirmed fault.

- [ ] **Step 5: Verify GREEN**

```bash
python manage.py test core.tests.test_field_workflow -v 2
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add apps/platform/core/forms.py apps/platform/core/views.py apps/platform/core/urls.py apps/platform/core/templates
 git commit -m "feat: add mobile field capture workflow"
```

---

### Task 6: Configure media, authentication, and platform URLs

**Files:**
- Modify `config/settings.py` and `config/urls.py`.

- [ ] **Step 1: Add settings**

```python
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "field-dashboard"
LOGOUT_REDIRECT_URL = "login"
DATA_UPLOAD_MAX_MEMORY_SIZE = 110 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024
```

- [ ] **Step 2: Add URLs**

Include Django auth URLs with the custom login template and field routes at `/field/`. Serve media only when `DEBUG` is true.

- [ ] **Step 3: Run all tests**

```bash
python manage.py test core.tests -v 2
python manage.py check
```

Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add apps/platform/config
 git commit -m "chore: configure Gate 0 media and login"
```

---

### Task 7: Strengthen CI and documentation

**Files:**
- Modify `.github/workflows/ci.yml` and `README.md`.

- [ ] **Step 1: Extend backend CI**

After `manage.py check`, run:

```yaml
- run: python apps/platform/manage.py test core.tests -v 2
```

- [ ] **Step 2: Correct README first-stage route**

Describe phone-first field capture, human diagnosis, repair outcome, post-repair capture, and later portable/fixed gates. Add local commands:

```bash
python apps/platform/manage.py migrate
python apps/platform/manage.py createsuperuser
python apps/platform/manage.py runserver
```

- [ ] **Step 3: Verify complete suite**

```bash
cd apps/platform
python manage.py test core.tests -v 2
python manage.py check
cd ../..
python -m compileall services/audio_ai/app
cargo check --manifest-path edge/agent/Cargo.toml
python -m unittest tests.skills.test_waji_skills -v
```

Expected: all commands exit 0.

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/ci.yml README.md
 git commit -m "ci: verify Gate 0 field capture workflow"
```

---

### Task 8: PR validation and Gate 0 rehearsal guide

**Files:**
- Create `docs/gate0-rehearsal.md`.
- Create draft PR from `feature/gate0-field-capture` to `develop`.

- [ ] **Step 1: Add rehearsal guide**

Include account creation, machine/event setup, ambient/pre/post upload, Hypothesis/Decision/Outcome entry, completeness checks, raw/processed comparison, safety boundary, and evidence screenshots to retain.

- [ ] **Step 2: Inspect branch scope**

```bash
git diff --check develop...HEAD
git diff --stat develop...HEAD
```

Expected: only Gate 0 code, tests, design/plan, documentation, requirements, container, CI, and configuration.

- [ ] **Step 3: Open draft PR**

Title:

```text
feat: add Gate 0 phone field capture MVP
```

PR body must disclose:

- phone-system-recorder upload route;
- raw immutability and SHA-256;
- conservative derived denoise copy;
- human-only authority and evidence states;
- completeness criteria;
- supported formats and FFmpeg dependency;
- tests and CI;
- no field case, diagnostic-accuracy, fixed-edge, or safety-control claim.

- [ ] **Step 4: Verify GitHub Actions**

Required jobs: `backend`, `audio-ai`, `edge-agent`, and `skill-contracts`. Do not mark ready or merge until all pass and the user reviews the Gate 0 workflow.

---

## Self-review

- Spec coverage: all approved design sections map to Tasks 1–8.
- Generic/project boundary: no change to generic skill is needed.
- TDD: domain, completeness, audio, and workflow behavior begin with failing tests.
- No placeholders: implementation names, thresholds, paths, commands, and expected results are explicit.
- Type consistency: `Capture`, `CompletenessResult`, `AudioInspection`, `evaluate_event_completeness`, `inspect_wav`, and `process_capture_audio` are named once and reused consistently.
