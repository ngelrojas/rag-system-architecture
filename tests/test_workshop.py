"""Chapter 0 — the workbench works.

These tests don't test the system (there is no system yet). They prove the
three tools from 0.5 are wired: the test harness runs, the packages exist,
and the interpreter is the version the book pins.
"""

import importlib
import sys


def test_python_version_is_pinned() -> None:
    assert sys.version_info >= (3, 12), "The book uses Python 3.12 or later (0.5)"


def test_packages_exist() -> None:
    for name in ("domain", "adapters"):
        assert importlib.import_module(name) is not None
