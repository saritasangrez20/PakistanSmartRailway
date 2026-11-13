"""One page CISO executive dashboard (HTML, plus PDF when Playwright and Chromium are available).

Every number comes from outputs/metrics.json (scoring.py) and outputs/evaluation/evaluation.json.

Run:  python run.py dashboard          (python run.py dashboard --no-pdf to skip the PDF)
"""
from __future__ import annotations

import glob
import json
from datetime import date
from pathlib import Path

import pandas as pd
from jinja2 import Environment, FileSystemLoader, select_autoescape

from .config import ASSESSMENTS, OUTPUTS
from .scoring import main as compute_metrics

TEMPLATES = Path(__file__).resolve().parent / "templates"
HTML_OUT = OUTPUTS / "ciso_dashboard.html"
PDF_OUT = OUTPUTS / "ciso_dashboard.pdf"


def pct_status(p: float) -> tuple[str, str]:
    if p >= 75:
        return "good", "Strong"
    if p >= 50:
        return "warning", "Moderate"
    if p >= 25:
        return "serious", "Weak"
    return "critical", "Critical"


def risk_status(score: float) -> tuple[str, str]:
    if score >= 16:
        return "critical", "Critical"
    if score >= 10:
        return "serious", "High"
    if score >= 5:
        return "warning", "Medium"
    return "good", "Low"


def count_status(n: int, warn: int, bad: int) -> tuple[str, str]:
    if n >= bad:
        return "critical", "Act now"
    if n >= warn:
        return "serious", "Elevated"
    return "good", "Contained"


def build_tiles(m: dict) -> list[dict]:
    r, c, cp, rd, a = m["risk"], m["controls"], m["compliance"], m["readiness"], m["audit"]
    ai = m.get("ai_automation")

    def tile(label, value, unit, status, detail, help_text):
        return {"label": label, "value": value, "unit": unit, "status": status[0], "status_label": status[1],
                "detail": detail, "help": help_text}

    tiles = [
        tile("Governance maturity", f"{m['maturity']['score']}", " / 5", pct_status(m["maturity"]["score"] / 5 * 100),
             f"Year 3 target {m['maturity']['target_year3']}", "Average of 10 capability scores"),
        tile("Overall risk score", f"{r['avg_current']:.1f}", " / 25", risk_status(r["avg_current"]),
             f"inherent {r['avg_inherent']:.1f}, target {r['avg_target']:.1f}", "Average current residual L x I"),
        tile("High / Critical risks", f"{r['high_critical_current']}", f" of {r['total_risks']}",
             count_status(r["high_critical_current"], 5, 10),
             f"{r['critical_inherent']} Critical inherent", "Risks rated High or Critical after current controls"),
        tile("Control effectiveness", f"{c['effectiveness_pct']}", "%", pct_status(c["effectiveness_pct"]),
             f"weighted {c['effectiveness_weighted_pct']}%", "Implemented / applicable controls"),
        tile("Compliance", f"{cp['compliance_pct']}", "%", pct_status(cp["compliance_pct"]),
             f"{cp['satisfied']:g} of {cp['applicable']} requirement cells", "A2 heat map, weighted"),
        tile("Audit findings", f"{a['findings']}", "", count_status(a["by_severity"]["Critical"], 1, 3),
             f"{a['by_severity']['Critical']} Critical, {a['by_severity']['High']} High", "A2 audit plus A3 post-incident review"),
        tile("Critical control gaps", f"{c['critical_control_gaps']}", "", count_status(c["critical_control_gaps"], 1, 3),
             ", ".join(c["critical_control_gap_ids"]), "Gap controls that treat a Critical risk"),
        tile("IAM readiness", f"{rd['IAM']['pct']}", "%", pct_status(rd["IAM"]["pct"]),
             f"{rd['IAM']['obtained']:g} of {rd['IAM']['maximum']} checks", "IAM checklist, Y=1 P=0.5 N=0"),
        tile("BC/DR readiness", f"{rd['BCDR']['pct']}", "%", pct_status(rd["BCDR"]["pct"]),
             f"{rd['BCDR']['obtained']:g} of {rd['BCDR']['maximum']} checks", "BC/DR checklist"),
        tile("Incident readiness", f"{rd['IR']['pct']}", "%", pct_status(rd["IR"]["pct"]),
             f"{rd['IR']['obtained']:g} of {rd['IR']['maximum']} checks", "Incident response checklist"),
        tile("AI governance readiness", f"{rd['AI']['score_out_of_10']}", " / 10",
             pct_status(rd["AI"]["score_out_of_10"] * 10), f"{rd['AI']['obtained']:g} of {rd['AI']['maximum']} checks",
             "AI readiness = obtained / maximum x 10"),
        tile("AI automation impact", f"{ai['automation_gain_pct']}" if ai else "n/a", "%" if ai else "",
             pct_status(ai["automation_gain_pct"]) if ai else ("warning", "Not run"),
             f"trust score {ai['trust_score_pct']}%" if ai else "run map and evaluate", "Automation gain of control mapping"),
    ]
    return tiles


def ai_panel(m: dict) -> dict | None:
    ai = m.get("ai_automation")
    if not ai:
        return None
    method = f"Ollama LLM ({ai['model']}) + retrieval" if ai["backend"] == "ollama" else "Retrieval baseline (no LLM)"
    return {**ai, "method": method, "manual_hrs": round(ai["manual_minutes"] / 60, 1),
            "ai_hrs": round(ai["ai_assisted_minutes"] / 60, 1)}


def render(metrics: dict) -> str:
    env = Environment(loader=FileSystemLoader(TEMPLATES), autoescape=select_autoescape(["html", "j2"]))
    targets = dict(pd.read_csv(ASSESSMENTS / "maturity.csv")[["capability", "target_year3"]].values)
    return env.get_template("dashboard.html.j2").render(
        m=metrics, org=metrics["organisation"], generated=date.today().isoformat(),
        tiles=build_tiles(metrics), ai=ai_panel(metrics), targets={k: float(v) for k, v in targets.items()})


def export_pdf(html_path: Path, pdf_path: Path) -> bool:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright not installed: open the HTML in a browser and print to PDF (A4 landscape).")
        return False
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch()
        except Exception:
            found = sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux*/chrome"))
            if not found:
                print("Chromium not found: run `python -m playwright install chromium`, or print the HTML to PDF.")
                return False
            browser = p.chromium.launch(executable_path=found[-1], args=["--no-sandbox"])
        page = browser.new_page()
        page.goto(html_path.resolve().as_uri())
        page.pdf(path=str(pdf_path), format="A4", landscape=True, print_background=True,
                 margin={"top": "8mm", "bottom": "8mm", "left": "8mm", "right": "8mm"})
        browser.close()
    return True


def main(pdf: bool = True) -> Path:
    metrics = compute_metrics(quiet=True)
    HTML_OUT.write_text(render(metrics), encoding="utf-8")
    print(f"Written: {HTML_OUT.relative_to(OUTPUTS.parent)}")
    if pdf and export_pdf(HTML_OUT, PDF_OUT):
        print(f"Written: {PDF_OUT.relative_to(OUTPUTS.parent)}")
    return HTML_OUT


if __name__ == "__main__":
    main()
