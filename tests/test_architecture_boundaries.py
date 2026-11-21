# tests/test_architecture_boundaries.py — 3.6
#
# A boundary test that asserts the contract directly, as a backstop
# independent of import-linter's configuration.
import ast
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_core_has_no_adapter_imports() -> None:
    core_files = (ROOT / "app" / "core").rglob("*.py")
    for file in core_files:
        tree = ast.parse(file.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert not alias.name.startswith("app.adapters"), (
                        f"{file} imports {alias.name} — core must not depend on adapters"
                    )
            if isinstance(node, ast.ImportFrom) and node.module:
                assert not node.module.startswith("app.adapters"), (
                    f"{file} imports from {node.module} — core must not depend on adapters"
                )


def test_core_imports_no_vendor_sdk() -> None:
    vendors = ("openai", "qdrant_client", "fastapi", "psycopg", "langgraph")
    for file in (ROOT / "app" / "core").rglob("*.py"):
        for node in ast.walk(ast.parse(file.read_text())):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            for name in names:
                assert name.split(".")[0] not in vendors, f"{file} imports vendor SDK {name}"
