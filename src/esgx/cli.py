from typer import Typer, Option
from rich import print
from pathlib import Path
from .utils import load_yaml, read_texts
from .extract import extract_metrics
from .normalize import normalize_candidates
from .mapping import map_to_taxonomy
from .validate import run_validations, load_previous
from .generate import generate_outputs
from .audit import write_audit_log

app = Typer(help="ESGx Disclosure AI CLI")

@app.command()
def demo(inputs: str = Option("data/sample/reports", help="Folder with ESG reports (txt/md)"),
         out: str = Option("artifacts/demo", help="Output directory"),
         config: str = Option("configs/pipeline.yaml", help="Pipeline config")):
    cfg = load_yaml(config)
    outp = Path(out); outp.mkdir(parents=True, exist_ok=True)
    docs = read_texts(inputs, readers=cfg["ingestion"]["readers"])
    candidates, hits = extract_metrics(docs, cfg["extraction"]["patterns"])
    canonical = normalize_candidates(candidates, units_path=cfg["normalization"]["units"])
    mapped = map_to_taxonomy(canonical, cfg["mapping"]["taxonomy"])
    prev = load_previous("data/sample/previous_year_summary.json")
    results, flags = run_validations(mapped, prev, cfg)
    outputs = generate_outputs(results, flags, outp, cfg)
    write_audit_log(outp, {"hits": hits, "outputs": outputs})
    print(f"[bold green]Done.[/bold green] Artifacts in {outp}")

if __name__ == "__main__":
    app()
