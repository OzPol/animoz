# Development and saved videos

## Branch workflow

Use simple names such as `manim-intro`, `puerta-court`, and `systolic-array`.
Create a working branch, commit there, and open a PR targeting `main`.
Merging is a separate user decision.

## Checks

```bash
make test
make render
make verify
```

The tests cover known kinematic results, signed motion and turning points,
unit conversions, configuration validation, and preservation of previous render
outputs. The render check uses FFprobe to check final H.264 MP4s and compare
their durations with the model timeline.

CI runs those checks on Python 3.11 and 3.12, renders all three introductory
scenes, and attaches the final MP4s and their render metadata to the workflow run.
A second job builds the Docker image, checks it, and renders the welcome scene.

The workflow uses read-only repository permissions. It does not merge PRs or
publish videos to an external service.

## Where videos go

| Path | Contents |
| --- | --- |
| `videos/<project>/` | Selected finished MP4s committed to the repository |
| `media/<project>/<automatic-run-name>/` | Working videos, intermediate frames, and render records |
| GitHub Actions artifacts | Preview MP4s and records for each CI run |
| `notebooks/output/` | Previously saved GIFs |

Working renders are ignored by Git. Selected finished clips under `videos/`
are tracked. The source and saved examples can therefore be cloned together
and played without YouTube or Google Drive.

After rendering all intro scenes, run `make save` to verify and copy the three
final MP4s into `videos/intro/`. It also records their settings, software versions,
durations, dimensions, frame rates, and file hashes in `render-info.json`.
Review those files and include them in the project's working branch.

Use compact previews for committed examples. If future videos grow beyond
GitHub's regular file limits, choose Git LFS or release assets at that point.
See [GitHub's large-file guidance](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github).
