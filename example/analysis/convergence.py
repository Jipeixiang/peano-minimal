"""
Convergence study: compare the gauge wave on 9, 27 and 81 grid points per axis.

Usage (after running gauge-wave.py --run for at least two grids, from the example folder):

    python3 analysis/convergence.py

Works in the same folder as gauge-wave.py: $GAUGE_WAVE_WORK_DIR if set, else the example folder.

Reads  raw_data/n9/, n27/, n81/   (whichever exist and have reached the end time)
Writes data/convergence/:
    convergence.csv        error at the last snapshot and the observed order, per resolution
    convergence.png        error against grid spacing h on log-log axes, with a slope-4 guide
    error-vs-time.png      max error along the line over time, per resolution
    error-profiles.png     error along x at the last snapshot, scaled by (N / 27)^4

FD4 in space and RK4 in time both have order 4, and the time step shrinks with h,
so the error should fall like h^4: each refinement by 3 divides it by 3^4 = 81.
The observed order between two grids N and 3N is  p = log(E_N / E_3N) / log(3).
"""

import argparse
import csv
import importlib
import os
import sys

import numpy as np

AnalysisDir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AnalysisDir)
import check  # also puts the example folder on sys.path

gauge_wave = importlib.import_module("gauge-wave")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--work-dir", default=gauge_wave.default_work_dir(),
                        help=f"the folder that holds raw_data/ and data/ (default: ${gauge_wave.WorkDirVariable}, "
                             "or the example folder if it is not set)")
    args = parser.parse_args()
    work_dir = os.path.abspath(os.path.expanduser(args.work_dir))

    runs = []  # (points, times, x, lapse)
    for points in sorted(gauge_wave.Grid):
        raw = gauge_wave.folders(work_dir, points)["raw"]
        if not os.path.exists(os.path.join(raw, "solution-CCZ4.peano-patch-file")):
            print(f"skipping {points} points: no snapshots in {raw}")
            continue
        print(f"reading {points} points ...")
        times, x, lapse = check.read_run(raw)
        if times[-1] < gauge_wave.EndTime - 1e-6:
            print(f"skipping {points} points: the run only reached t = {times[-1]:.4f} (still running?)")
            continue
        runs.append((points, times, x, lapse))
    if len(runs) < 2:
        sys.exit("need at least two grids. Run e.g. "
                 "python3 gauge-wave.py --points 9 --run and --points 27 --run first.")

    out_dir = os.path.join(work_dir, "data", "convergence")
    os.makedirs(out_dir, exist_ok=True)

    # errors at the last snapshot of each run
    rows = []
    for points, times, x, lapse in runs:
        max_error, l2_error = check.errors(times, x, lapse)
        rows.append({"points": points, "h": 1.0 / points, "t_end": times[-1],
                     "max_error": max_error[-1], "l2_error": l2_error[-1]})
    t_ends = [r["t_end"] for r in rows]
    if max(t_ends) - min(t_ends) > 1e-6:
        print(f"warning: the runs end at different times {t_ends}; errors are not directly comparable")

    for coarse, fine in zip(rows, rows[1:]):
        ratio = coarse["h"] / fine["h"]
        fine["order_max"] = np.log(coarse["max_error"] / fine["max_error"]) / np.log(ratio)
        fine["order_l2"] = np.log(coarse["l2_error"] / fine["l2_error"]) / np.log(ratio)

    with open(os.path.join(out_dir, "convergence.csv"), "w", newline="") as f:
        fields = ["points", "h", "t_end", "max_error", "l2_error", "order_max", "order_l2"]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: (f"{r[k]:.6e}" if k in r else "") for k in fields})

    print(f"\nerror of the lapse along x (y = z = 0.5) at t = {t_ends[-1]:.4f}:")
    print("{:>7} {:>10} {:>12} {:>10} {:>12} {:>10}".format("points", "h", "max error", "order", "L2 error", "order"))
    for r in rows:
        om = f"{r['order_max']:.2f}" if "order_max" in r else "-"
        ol = f"{r['order_l2']:.2f}" if "order_l2" in r else "-"
        print("{:>7} {:>10.5f} {:>12.3e} {:>10} {:>12.3e} {:>10}".format(
            r["points"], r["h"], r["max_error"], om, r["l2_error"], ol))
    print("(expected order: 4)")

    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("\nmatplotlib is not installed, skipping the plots")
        return

    # 1. error against h, with a slope-4 guide through the finest run
    h = np.array([r["h"] for r in rows])
    fig, ax = plt.subplots(figsize=(6, 4.5))
    ax.loglog(h, [r["max_error"] for r in rows], "o-", label="max error")
    ax.loglog(h, [r["l2_error"] for r in rows], "s-", label="L2 error")
    h_guide = np.array([h.min(), h.max()])
    ax.loglog(h_guide, rows[-1]["max_error"] * (h_guide / h.min()) ** 4, "k--", linewidth=1, label="slope 4")
    for r in rows:
        ax.annotate(f"{r['points']}", (r["h"], r["max_error"]), textcoords="offset points", xytext=(6, 4))
    # label the grids themselves (1/9, 1/27, 1/81) instead of the crowded default log ticks
    from matplotlib.ticker import NullFormatter
    ax.set_xticks(h)
    ax.set_xticklabels([f"1/{r['points']}" for r in rows])
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.set_xlabel("grid spacing h = 1 / points")
    ax.set_ylabel(f"lapse error at t = {t_ends[-1]:.2f}")
    ax.legend()
    ax.grid(True, which="both", alpha=0.3)
    fig.savefig(os.path.join(out_dir, "convergence.png"), dpi=120, bbox_inches="tight")

    # 2. max error over time
    fig, ax = plt.subplots(figsize=(7, 4))
    for points, times, x, lapse in runs:
        max_error, _ = check.errors(times, x, lapse)
        ax.semilogy(times[1:], max_error[1:], "o-", markersize=3, label=f"{points} points")
    ax.set_xlabel("t")
    ax.set_ylabel("max lapse error along x")
    ax.legend()
    ax.grid(True, which="both", alpha=0.3)
    fig.savefig(os.path.join(out_dir, "error-vs-time.png"), dpi=120, bbox_inches="tight")

    # 3. pointwise error at the end, scaled so that 4th-order convergence makes the curves coincide
    fig, ax = plt.subplots(figsize=(7, 4))
    for points, times, x, lapse in runs:
        error = lapse[-1] - check.exact_lapse(x, times[-1])
        ax.plot(x, error * (points / 27.0) ** 4, "o-", markersize=3, label=f"{points} points")
    ax.axhline(0.0, color="k", linewidth=0.5)
    ax.set_xlabel("x (y = z = 0.5)")
    ax.set_ylabel(f"error x (N/27)^4 at t = {t_ends[-1]:.2f}")
    ax.legend()
    fig.savefig(os.path.join(out_dir, "error-profiles.png"), dpi=120, bbox_inches="tight")

    print(f"\nwrote convergence.csv, convergence.png, error-vs-time.png, error-profiles.png to {out_dir}")


if __name__ == "__main__":
    main()
