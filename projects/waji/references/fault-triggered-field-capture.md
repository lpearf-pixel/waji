# Fault-Triggered Field Capture Protocol

## Event triggers

Create a `FaultEvent` for abnormal sound, weak action, overheating, leakage, warning code, intermittent behavior, post-repair verification, or a planned comparative inspection. Do not create a confirmed fault from the trigger text.

## Safety boundary

- The capture person does not operate machinery unless qualified and authorized.
- The qualified operator controls every movement and can stop the procedure.
- Keep personnel outside swing, travel, attachment, fan, belt, exhaust, hot-surface, high-pressure, and falling-object hazards.
- Never place a sensor or hand on a moving, pressurized, or unsafe surface.
- Stop capture when site conditions invalidate the agreed safe method.

## Event metadata

Record event ID, machine ID, make/model, serial or fleet ID, hours, date/time, location, reporter, symptom, recent repair, attachment, ambient weather, engine or oil temperature when available, active fault codes, and work-order link.

## Audio capture

For every capture record:

- component or area;
- position photo and text landmark;
- microphone distance and direction;
- enclosure/hood/door state;
- microphone and interface ID;
- gain or automatic-gain state;
- machine action, load, speed or displayed RPM;
- duration and repeat index;
- raw format, sample rate, channel count;
- clipping, low-level, wind, competing-machine, speech, contact-noise, and overload checks.

Record at least one ambient sample with the target machine stopped when safe. For each safe action, aim for three repetitions using the same position and settings. A failed-quality repetition is preserved but marked invalid and repeated.

## Temporary vibration or contact capture

Use only when audio is insufficient and the temporary sensor can be installed safely. Follow `sensor-installation-contract.md`; record exact coupling and orientation.

## Technician evidence

Save a free description or voice note, then create structured Hypotheses with suspected component, supporting observations, contradictions, alternatives, confidence, and the next verification action.

## Pre/post linkage

After adjustment, repair, exclusion, or replacement, repeat the safest comparable action at the same landmark, distance, direction, enclosure state, and settings when feasible. Link follow-up captures to the original event and work order.

## Complete-case rule

A complete case requires an event, at least one valid raw capture with context, a structured Hypothesis, a Decision, and either an Outcome or explicit unresolved disposition. A verified-complete case also has a comparable follow-up capture. A single recording or oral verdict is not a complete case.
