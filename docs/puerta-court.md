# Puerta Court

The project has a measured site explainer, an explained motion model, and two
camera-controlled scenes. All world dimensions are inches. East is +x, north
is +y, and height is +z. Camera changes never move or rescale individual objects.

## Watch and explore

The [complete film](../videos/puerta-court/presentation.mp4) connects the survey,
physics, and synchronized camera replays with fades and chapter markers.
The [individual saved videos](../videos/puerta-court/) include the survey and physics
explainers and replays from every preset. Explanatory scenes have accompanying
captions, chapter times, and transcripts.

```bash
animoz explore puerta-court
```

Open the printed HTML file in a browser. It works offline. Select measured site
or motion hypothesis, scrub time, rotate the camera, and change zoom. The viewer
prints a Manim command for saving the current camera as an MP4. It uses states
sampled directly from the Python model, not a second implementation of its physics.

```bash
animoz views puerta-court
animoz render puerta-court replay --view all
animoz render puerta-court survey-view --view beneva
animoz render puerta-court replay --phi 45 --theta -130 --zoom 0.9
animoz render puerta-court all --quality high --view all
```

`--view all` saves separate timestamped runs, including their exact camera inputs.
Every replay uses the same clock and physical coordinates. North-up, Beneva,
access-road, and south are presets in the project's `project.toml`; custom camera
angles are visualization choices, not inferred driver-eye positions.

## Measurements

`measurements.json` preserves the complete source constraint packet from
`Beneva_Inch_Model_Views.zip`, reconciled on November 15, 2026. The packet's
`Beneva_Measured_Collision_Simulation.pdf` explains the endpoints and their limits.
The [measurement ledger](../src/animoz/projects/puerta_court/measurement-ledger.csv)
retains every original measurement, including equal values with different endpoints.
The model derives coordinates from the original measurement IDs rather than
copying the coordinate table into Python.

- A=(0,60), Q1=(55,39), Q2=(58,22), Q3=(68,1), B=(94,0), in inches.
- Corner projections: 16+78=94 inches east-west and 68−8=60 inches north-south.
- The sidewalk is 59 inches wide. Its displayed placement uses the documented
  31-inch face assignment and is conditional on that interpretation.
- The 1.5-inch closure difference is preserved. It is not rounded away.
- The bend is sampled, not fitted to an invented circular or smooth wall.
- The 70-inch and 72-inch wall heights remain separate local references.
- The 197.2×72.8×58.5-inch Avalon envelope uses the supplied Toyota specification.
  Axle positions, overhang split, and body details have not been invented.

Toyota source: <https://media.toyota.ca/content/dam/media-toyota/general/specifications/07avalon_spec_e.pdf>

## Physics and what the replay represents

The default motion settings are an explicit hypothesis: peak car speed 1 mph,
bicycle speed 9 mph, two seconds of approach/braking, a one-second full stop,
two seconds of creep, and two seconds of kinematic continuation. These are
configurable study inputs, not measured speed histories or a reconstructed impact.

The approach uses a smooth velocity decrease. With u=t/T,

$$v(t)=v_{peak}(1-3u^2+2u^3).$$

Creep uses $$v(t)=v_{peak}\sin^2(\pi u).$$

Position is the analytic integral of velocity. The westbound car's x velocity
is −v. The bicycle's north coordinate decreases at constant study speed.
Position and velocity remain continuous at the stop and creep boundaries.
At the reference time the car stops; subsequent bicycle motion is kinematic
continuation, not an impact-response calculation.

The default replay uses a relative frame because lane position and precise stop
clearance are not registered. A moving interval preserves the unmeasured numeric
contact offset on the passenger half of the front bumper. The interval is not
a measured offset range. This avoids selecting the previously invented six inches.
The model does not substitute a car corner for the described bumper contact.

`[registration]` is disabled by default. Its numeric placeholders have no physical
effect until explicitly enabled with registered lane and positive passenger-side
contact-offset values. They must come from evidence. Driver-eye pose, rider shape,
wall thickness/returns, and the wall surface between samples are still needed
before first visibility can be computed. Camera cropping is not driver occlusion.

No mass, deformation, restitution, friction, injury, or responsibility calculation
is inferred from this incomplete evidence.

## Change and save

Copy only the TOML entries you want to change into a local override file, then use
`--config path/to/settings.toml`. Unknown keys and invalid numbers fail before
rendering. To save updated examples after rendering all scenes:

```bash
python scripts/verify_renders.py media --project puerta-court --save-to videos/puerta-court
animoz explore puerta-court --output videos/puerta-court/viewer.html
animoz assemble puerta-court
```

`render-info.json` records settings, software, camera view, duration, codec
dimensions, and file hashes. The saved artifacts stay in the project PR.
