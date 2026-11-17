# Intro videos

These MP4s are stored in the repository and can be downloaded or cloned with
the source. They use CMU Serif on a light canvas with dark text.

| Video | Content |
| --- | --- |
| [welcome.mp4](welcome.mp4) | Separate the model, scene, and camera layers |
| [motion.mp4](motion.mp4) | Animate position and velocity from one equation |
| [cameras.mp4](cameras.mp4) | Replay the same motion from three viewpoints |

The [render record](render-info.json) lists each clip's settings, software
versions, font, dimensions, frame rate, duration, and SHA-256 hash.

To regenerate the working previews:

```bash
make render
```

To verify and copy the resulting final clips into this directory:

```bash
make save
```

Commit changed videos through the project's working branch and PR.
