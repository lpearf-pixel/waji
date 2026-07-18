# Gate 0 Field Capture MVP Design

**Status:** Approved on 2026-07-18.

## 1. Mission

Deliver one executable, phone-first maintenance evidence loop:

```text
phone recorder -> mobile upload -> field context -> human Hypothesis
-> inspection/repair Decision -> Outcome or unresolved disposition
-> comparable post-repair capture -> completeness result
```

The MVP must help a quarry team collect auditable evidence without assuming fixed sensors, machine power, CAN access, or automatic diagnosis.

## 2. Required parent contracts

Read before implementation:

- `skills/engineering-machinery-health-systems/SKILL.md`
- `projects/waji/PROJECT-SKILL.md`
- `projects/waji/references/fault-triggered-field-capture.md`
- `projects/waji/references/data-contract.md`
- `projects/waji/references/diagnosis-review-contract.md`
- `projects/waji/references/validation-gates.md`

## 3. Scope

### Included

- Django authenticated, server-rendered, mobile-responsive pages.
- Machine registration and fault-event creation.
- Upload of phone-recorded audio and position photos.
- Field metadata, quality flags, Observation, Hypothesis, Decision, Outcome, and unresolved disposition.
- Raw-file SHA-256 and immutability.
- Conservative audio quality inspection.
- A derived light-denoise listening copy when the file can be decoded.
- Original and processed audio shown separately.
- Automatic `incomplete`, `complete`, and `verified_complete` evaluation.
- Django admin for recovery and review.

### Excluded

- Browser recording, native mobile applications, offline synchronization, fixed edge boxes, CAN transmit/read, automatic shutdown, automatic confirmed diagnosis, VMD production deployment, deep denoising models, fault-classifier accuracy claims, and fleet-wide rollout.

## 4. User roles

- **Collector:** creates events and uploads raw evidence.
- **Technician:** adds Observations, Hypotheses, and Decisions.
- **Reviewer:** establishes Outcome or unresolved disposition and closes a case.
- **Administrator:** manages users, machines, and recovery operations.

Django authentication supplies identity. The MVP does not invent an application-specific permission engine; ownership and staff review are recorded, while deployment administrators control account membership.

## 5. Mobile workflow

1. Select or register a machine.
2. Create a `FaultEvent` without asserting a confirmed failure.
3. Upload an ambient recording when feasible.
4. Upload one or more pre-repair recordings and a position photo.
5. Record component/area, landmark, distance, direction, enclosure state, action, load, RPM, repeat index, device label, and noise conditions.
6. Add factual Observations.
7. Add one or more ranked Hypotheses. Expert listening remains a Hypothesis.
8. Record the authorized Decision and work-order information.
9. Record Outcome, or an explicit unresolved disposition with owner and due date.
10. Upload a comparable post-repair capture.
11. Review system completeness and missing evidence.

## 6. Data model

All externally displayed identifiers are UUIDs.

### Machine

Fields: UUID, make, model, fleet ID, serial number, hours, active, timestamps.

### FaultEvent

Fields: UUID, machine, trigger, symptom, location, reporter, opened time, recent repair, attachment, environment, work-order ID, workflow status, unresolved reason/next condition/owner/due date, timestamps.

### Capture

Fields: UUID, event, stage (`ambient`, `pre`, `post`), raw file, original filename, MIME type, raw SHA-256, device label, component, position photo, position text, distance, direction, enclosure state, action, load, displayed RPM, gain mode, repeat index, quality status/reasons, duration, sample rate, channels, protocol version, operator, related pre-capture, processing status, processed file, processed SHA-256, processing manifest, timestamps.

### Observation

Fields: UUID, event, optional capture, statement, units, author, observed time, provenance, quality status.

### Hypothesis

Fields: UUID, event, suspected component/failure mode, proposer, support/contradiction text, alternatives, confidence, missing evidence, safest next verification, status, timestamps.

### Decision

Fields: UUID, event, decision, decider, urgency, risk, authority basis, reversibility, rollback action, work-order ID, status, timestamp.

### Outcome

Fields: UUID, one-to-one event, established by/at, disposition, confirmed or excluded component, failure mode, inspection/test evidence, parts, adjustments, before/after comparison, residual uncertainty, closure status, selected post captures.

## 7. Evidence and file integrity

- Raw upload bytes are never overwritten.
- Initial save computes SHA-256 by streaming the stored file.
- Updating a `Capture` may edit metadata but may not replace `raw_file`.
- A derived file uses a different path and SHA-256.
- Processing records input hash, output hash, algorithm name/version, parameters, decoder, noise-reference capture, quality before/after, and creation time.
- Unsupported or failed processing preserves the raw file and records a transparent status; upload success never depends on denoise success.

## 8. Accepted formats

Raw upload accepts: `.wav`, `.m4a`, `.mp3`, `.aac`, `.ogg`, and `.3gp`.

Limits:

- 100 MB per file.
- Audio extension and content type are checked conservatively.
- Position-photo upload is optional but strongly requested.
- The original format is retained.

Docker installs FFmpeg so common phone formats can be decoded. The Python processor also handles 16-bit PCM WAV directly, allowing deterministic tests and graceful operation when FFmpeg is absent.

## 9. Quality inspection

For decoded PCM, calculate:

- duration, sample rate, and channels;
- peak amplitude and RMS;
- clipping ratio;
- silence/very-low-level condition;
- invalid-decode condition.

Quality states:

- `valid`
- `usable_with_noise`
- `review_required`
- `invalid_clipping`
- `invalid_silence`
- `invalid_decode`

Manual noise flags include wind, speech, handling/contact noise, competing machine, overload, and unknown interference. Automated checks never erase manual evidence.

## 10. Conservative light denoise

The purpose is a listening aid, not a replacement for raw evidence.

Processing:

1. Decode to PCM float audio.
2. Remove DC offset.
3. Estimate a noise spectrum from a linked ambient capture when available; otherwise use a short low-energy estimate from the input.
4. Apply mild spectral subtraction with a non-zero gain floor so impact and harmonic information is not fully removed.
5. Avoid aggressive smoothing or voice-oriented enhancement.
6. Normalize only to prevent clipping; do not change time scale or pitch.
7. Write a derived WAV and manifest.

Initial implementation uses NumPy FFT/STFT. It must preserve a synthetic dominant tone within one FFT bin and retain at least a configured fraction of peak energy in tests. Complex VMD, EWT, SVD, sparse coding, and neural denoising remain experimental paths after real Waji cases exist.

## 11. Completeness

```text
complete = event
         + at least one valid/usable pre capture with required context
         + at least one Hypothesis
         + at least one Decision
         + Outcome or explicit unresolved disposition

verified_complete = complete
                  + at least one valid/usable post capture
```

The UI lists missing requirements. A single recording or oral verdict never closes a case.

## 12. Routes and pages

- `/accounts/login/`
- `/field/` dashboard
- `/field/machines/new/`
- `/field/events/new/`
- `/field/events/<uuid>/`
- `/field/events/<uuid>/captures/new/`
- `/field/events/<uuid>/observations/new/`
- `/field/events/<uuid>/hypotheses/new/`
- `/field/events/<uuid>/decisions/new/`
- `/field/events/<uuid>/outcome/`

The event detail page is the case timeline and completeness checklist.

## 13. Storage

Development uses Django `MEDIA_ROOT`. Upload paths include machine and event UUIDs. The database stores file names as object URIs so a later S3/MinIO storage backend can replace local storage without changing domain records.

## 14. Security and safety

- Login is mandatory for field pages.
- CSRF protection stays enabled.
- File size and extension are validated.
- User-supplied filenames are not used as storage paths.
- Media must not be treated as executable content.
- The application never authorizes machine operation, sensor placement on unsafe surfaces, automatic stop, CAN communication, or confirmed diagnosis from sound alone.

## 15. Gate 0 acceptance

A reviewer can demonstrate one rehearsal containing:

- one machine;
- one event;
- one ambient or documented unavailable condition;
- one valid pre capture with position/context;
- one Observation;
- one Hypothesis;
- one Decision;
- one Outcome or explicit unresolved disposition;
- one comparable post capture;
- a `verified_complete` result;
- raw SHA-256, immutable raw file, derived-file provenance, and original/processed playback.

Gate 0 proves protocol executability only. It does not prove diagnostic accuracy or justify Gate 1, a portable terminal, or fixed monitoring.
