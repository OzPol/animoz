# Working in animoz

- Use a separate branch with a simple hyphenated name. Do not use slashes in branch names.
- Open a pull request into main. Do not push commits directly to main or merge without a user instruction.
- Preserve the existing notebooks, saved GIFs, and other committed assets.
- Keep project-specific models, settings, and scenes together under src/animoz/projects/.
- Keep numerical models independent of Manim. Put shared rendering code in src/animoz/rendering/.
- Update relevant documentation, dependencies, configuration, examples, and checks alongside code changes.
- Use Python 3.12 by default and preserve Python 3.11 compatibility.
- Use Manim Community. Do not add direct Pillow imports or Pillow-based export code.
- Run the unit tests and render affected scenes. Check the resulting video frames before reporting success.
