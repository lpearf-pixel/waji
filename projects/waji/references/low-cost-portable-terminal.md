# Low-Cost Portable Terminal Contract

## Role

The terminal is carried by a technician and used temporarily at a fault or inspection site. It is not a permanently installed vehicle monitor and does not control the machine.

## Cost and supply strategy

- Design BOM target: **人民币 1,000–2,500 元**.
- Use mature, replaceable commodity modules and small-batch PCB, enclosure, cable, and harness work.
- Exceeding the target requires a written explanation of the evidence quality or field reliability that cannot be achieved inside the target.
- Do not pay for industrial appearance, custom moulds, or premium acquisition hardware before field evidence justifies them.

## Required capabilities

- battery powered and independent of machine power and control;
- replaceable compute, screen, battery, storage, audio interface, microphone, and cable modules;
- reliable external audio input and raw lossless or low-loss recording;
- visible level, clipping, low-level, and background-noise checks;
- guided machine, component, position, action, load, distance, and repeat metadata;
- offline operation with local integrity checks;
- export by Wi-Fi, USB, or removable storage;
- technician voice/text note and position photo;
- pre-repair and post-repair case linkage;
- self-test for storage, battery, microphone, channel, clock, and export;
- calibration or reference-check record for replaceable sensor modules.

## Optional modules

Contact piezo pickup, three-axis MEMS vibration, temperature probe, speed input, local spectrum, and historical-case comparison are optional and must not block the base audio workflow.

## Field reliability

Keep one known-good microphone/cable set and replaceable spares. A module swap creates a new device or calibration version. The application rejects or flags clipping, severe noise, missing context, clock error, low storage, and failed self-test.

## Prohibited shortcuts and claims

- Do not claim industrial vehicle-grade reliability for the first prototype.
- Do not connect to CAN for transmission or automatic control.
- Do not discard raw evidence to save storage.
- Do not display similarity or an algorithm score as a confirmed fault.
- Do not make fixed edge the default next step.
