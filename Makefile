.RECIPEPREFIX := >
.PHONY: setup doctor list preview render test verify save

setup:
>uv sync --locked --extra manim

doctor:
>uv run --locked --extra manim animoz doctor

list:
>uv run --locked --extra manim animoz list

preview:
>uv run --locked --extra manim animoz render intro motion --quality low

render:
>uv run --locked --extra manim animoz render intro all --quality low

test:
>uv run --locked --extra manim python -m unittest discover -s tests -v

verify:
>uv run --locked --extra manim python scripts/verify_renders.py media

save:
>uv run --locked --extra manim python scripts/verify_renders.py media --save-to videos/intro
