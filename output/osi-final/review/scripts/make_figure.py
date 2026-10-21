"""Plot archived, validated engine output. No inference or fitted-parameter changes."""
import csv
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "output/osi-final/review"
source = ROOT / "artifacts/temperature_decision_flagship.json"
data = json.loads(source.read_text(encoding="utf-8"))
assert [r["ordering"] for r in data["selected_rankings"]] == [[1, 2, 3], [3, 2, 1]]
colors = {1: "#167d80", 2: "#b16c2d", 3: "#6964b9"}
plt.rcParams.update({"font.size": 10, "axes.spines.top": False,
                     "axes.spines.right": False, "font.family": "DejaVu Sans"})
fig, ax = plt.subplots(figsize=(9.6, 3.8), layout="constrained")
rows = []
for material in data["materials"]:
    rid = material["record"]["row_id"]
    for regime in ("LT", "HT"):
        points = [(p["temperature_k"], v["conductivity_s_cm"])
                  for p in data["curve_points"] for v in p["values"]
                  if v["row_id"] == rid and v["regime"] == regime]
        ax.plot([p[0] for p in points], [p[1] for p in points], color=colors[rid],
                lw=2.1, label=f"Row {rid}" if regime == "LT" else None)
        rows.extend({"row_id": rid, "regime": regime, "temperature_K": t,
                     "calculated_conductivity_S_per_cm": s} for t, s in points)
    ax.axvline(material["transition_k"], color=colors[rid], ls="--", lw=.7, alpha=.45)
for event in data["events"]:
    if event["kind"] == "CONTINUOUS_MODEL_CROSSOVER":
        t = event["temperature_k"]
        ax.plot([t, t], [1.08e-5, 1.7e-5], color="#334c58", lw=1.2)
        ax.text(t, 1.9e-5, f"~{t:.0f} K", rotation=90, ha="center", va="bottom", fontsize=8)
for rank in data["selected_rankings"]:
    t = rank["temperature_k"]
    ax.axvline(t, color="#334c58", lw=.8, alpha=.35)
    for value in rank["values"]:
        ax.scatter(t, value["conductivity_s_cm"], s=26, color=colors[value["row_id"]], zorder=5)
ax.text(690, .18, "700 K\n1 > 2 > 3", ha="center", color="#183f48", weight="bold")
ax.text(1000, .18, "1000 K\n3 > 2 > 1", ha="center", color="#183f48", weight="bold")
ax.set(yscale="log", xlim=(600, 1100), ylim=(1e-5, .6),
       xlabel="Temperature (K)", ylabel=r"Calculated $\sigma$ (S/cm)")
ax.grid(axis="y", alpha=.13)
ax.legend(loc="lower right", frameon=False, ncols=3)
fig.savefig(OUT / "flagship-conductivity.png", dpi=240)
fig.savefig(OUT / "flagship-conductivity.svg")
with (OUT / "flagship-plot-input.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
(OUT / "figure-provenance.json").write_text(json.dumps({
    "source": "artifacts/temperature_decision_flagship.json",
    "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    "dataset": data["source"], "code_version": data["code_version"],
    "equation": data["equation"], "roots_K": [e["temperature_k"] for e in data["events"]
        if e["kind"] == "CONTINUOUS_MODEL_CROSSOVER"],
    "method": "Archived production curve points; LT and HT plotted separately, no joined fit boundary",
    "qualification": "Model-derived intersections; no measured crossovers or uncertainty intervals",
}, indent=2) + "\n", encoding="utf-8")
print("FIGURE=PASS archived engine data; separate LT/HT branches")
