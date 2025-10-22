from pathlib import Path
from esgx.cli import demo

def test_demo(tmp_path: Path):
    out = tmp_path / "artifacts"
    demo.callback = None  # Typer appeasement
    demo(inputs="data/sample/reports", out=str(out))
    assert (out / "esg_summary.md").exists()
    assert (out / "esg_summary.json").exists()
