#!/usr/bin/env python3
"""Tests for tools/check.py: each one copies the catalog to a temporary folder, breaks
one thing and runs the check there (python3 tools/test_check.py; CI runs it too)."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = 'url = "https://github.com/bromigos-org/extensions"'


class CheckTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = os.path.join(self.tmp.name, "catalog")
        tracked = subprocess.run(["git", "-C", ROOT, "ls-files", "-z"], capture_output=True, text=True,
                                 check=True).stdout.split("\0")
        for rel in filter(None, tracked):
            os.makedirs(os.path.dirname(os.path.join(self.root, rel)), exist_ok=True)
            shutil.copy2(os.path.join(ROOT, rel), os.path.join(self.root, rel), follow_symlinks=False)
        # check.py is under test as it is in the working tree, committed or not
        shutil.copy2(os.path.join(ROOT, "tools", "check.py"), os.path.join(self.root, "tools", "check.py"))

    def tearDown(self):
        self.tmp.cleanup()

    def edit(self, rel, old, new):
        path = os.path.join(self.root, rel)
        with open(path, encoding="utf-8") as f:
            text = f.read()
        self.assertIn(old, text)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text.replace(old, new, 1))

    def append(self, rel, text):
        with open(os.path.join(self.root, rel), "a", encoding="utf-8") as f:
            f.write(text)

    def check(self):
        """(exit code, output) of the check on the copy, with its files in a git index."""
        subprocess.run(["git", "init", "-q", self.root], check=True)
        subprocess.run(["git", "-C", self.root, "add", "-A"], check=True)
        done = subprocess.run([sys.executable, os.path.join(self.root, "tools", "check.py")],
                              capture_output=True, text=True)
        return done.returncode, done.stdout + done.stderr

    def assertFails(self, message):
        code, out = self.check()
        self.assertEqual(code, 1, out)
        self.assertNotIn("Traceback", out)
        self.assertIn(message, out)

    def test_the_catalog_as_committed_passes(self):
        code, out = self.check()
        self.assertEqual(code, 0, out)
        self.assertIn(", 0 errors", out)

    def test_this_repository_is_recognised_however_its_url_is_spelled(self):
        for url in ("https://github.com/Bromigos-Org/Extensions", "https://github.com/bromigos-org/extensions.git/",
                    "ssh://git@github.com/bromigos-org/extensions.git", "git@github.com:bromigos-org/extensions",
                    "https://www.github.com/bromigos-org/extensions"):
            with self.subTest(url=url):
                self.tearDown()
                self.setUp()
                self.edit("index.toml", HERE, f'url = "{url}"')       # the first example: teal-glass
                self.edit("examples/teal-glass/bromigos-ext.toml", 'name = "teal-glass"', 'name = "other"')
                self.assertFails("the manifest calls it 'other'")

    def test_another_repository_is_not_checked_as_a_folder_here(self):
        self.edit("index.toml", HERE, 'url = "https://github.com/someone/extensions"')
        self.edit("index.toml", 'path = "examples/teal-glass"\n', "")
        self.assertFails("examples/teal-glass: no entry in index.toml lists it")

    def test_an_example_folder_without_an_entry_fails(self):
        os.makedirs(os.path.join(self.root, "examples", "unlisted"))
        self.append("examples/unlisted/bromigos-ext.toml", "broken = [\n")
        self.assertFails("examples/unlisted: no entry in index.toml lists it")

    def test_a_manifest_that_is_not_toml_is_an_error_not_a_crash(self):
        self.append("examples/load-panel/bromigos-ext.toml", "\nname = = broken\n")
        self.assertFails("load-panel (examples/load-panel) bromigos-ext.toml: not valid TOML")

    def test_a_part_without_a_kind_is_an_error_not_a_crash(self):
        self.append("examples/hello-deck/bromigos-ext.toml", '\n[[provides]]\npath = "deck.py"\n')
        self.assertFails("'kind' is a required property")

    def test_an_index_that_is_not_toml_is_an_error_not_a_crash(self):
        self.append("index.toml", "\n[[extension\n")
        self.assertFails("index.toml: not valid TOML")

    def test_a_field_of_the_wrong_type_is_an_error_not_a_crash(self):
        self.edit("index.toml", 'preview = "previews/wick.jpg"', "preview = 5")
        self.assertFails("5 is not of type 'string'")


if __name__ == "__main__":
    unittest.main()
