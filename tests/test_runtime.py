import tempfile
import unittest
from pathlib import Path

from animoz.runtime import load_runtime


class RuntimeTests(unittest.TestCase):
    def test_the_selected_font_is_in_the_installation_plan(self):
        runtime = load_runtime()
        self.assertIn(runtime.font_package, runtime.system_packages)
        self.assertEqual(
            len(runtime.system_packages), len(set(runtime.system_packages))
        )

    def test_invalid_package_names_and_schemas_fail_before_installation(self):
        for content in (
            '[font]\nfamily="Example"\npackage="--allow-unauthenticated"\n'
            '[system]\npackages=["ffmpeg"]',
            '[font]\nfamily="Example"\npackage="fonts-cmu"\n'
            '[system]\npackages=["ffmpeg; touch /tmp/unwanted"]',
            '[font]\nfamily=""\npackage="fonts-cmu"\n[system]\npackages=["ffmpeg"]',
            '[font]\nfamily="Example"\npackage="fonts-cmu"\n'
            '[system]\npackages="ffmpeg"',
            '[other]\npackages=["ffmpeg"]',
        ):
            with (
                self.subTest(content=content),
                tempfile.TemporaryDirectory() as directory,
            ):
                path = Path(directory) / "runtime.toml"
                path.write_text(content, encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_runtime(path)
