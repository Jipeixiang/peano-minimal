"""
Compare one gauge wave run with the exact solution.

Exact solution: lapse(x, t) = sqrt(1 - A sin(2 pi (x - t))), A = 0.1, a wave moving along x with speed 1.

Usage (after gauge-wave.py --points 27 --run, from the example folder):

    python3 analysis/check.py --points 27

Works in the same folder as gauge-wave.py: $GAUGE_WAVE_WORK_DIR if set, else the example folder.

Reads  raw_data/n27/  (the snapshots, read only)
Writes data/n27/:
    centre.csv, check-centre.png     lapse at the centre (0.5, 0.5, 0.5) over time
    profile.csv, check-profile.png   lapse along x (y = z = 0.5) in the last snapshot
    errors.csv                       max and L2 error along that line in every snapshot

convergence.py imports read_run() and errors() from here.
"""

import argparse
import contextlib
import csv
import importlib
import io
import os
import sys

import numpy as np

AnalysisDir = os.path.dirname(os.path.abspath(__file__))
ExampleDir = os.path.dirname(AnalysisDir)
PeanoRoot = os.path.dirname(ExampleDir)
sys.path.insert(0, os.path.join(PeanoRoot, "src"))
sys.path.insert(0, ExampleDir)

gauge_wave = importlib.import_module("gauge-wave")  # the grids and the folder layout
from tarch.plotter.api.output.Visualiser import Visualiser
from tarch.plotter.api.input.PatchFileParser import unknown_names_from_description

Amplitude = 0.1
LineY, LineZ = 0.5, 0.5


def exact_lapse(x, t):
    return np.sqrt(1.0 - Amplitude * np.sin(2.0 * np.pi * (np.asarray(x) - t)))


class CrossesLine:
    """Patch filter: keep only patches whose box contains the line y = LineY, z = LineZ."""

    def __call__(self, offset, size):
        return (offset[1] <= LineY <= offset[1] + size[1]) and (offset[2] <= LineZ <= offset[2] + size[2])


def lapse_along_line(visualiser, snapshot):
    """Return x (cell centres) and lapse along y = z = 0.5 for one snapshot."""
    with contextlib.redirect_stdout(io.StringIO()):
        data = visualiser.parse_snapshot(snapshot)
    (patch_data,) = data.values()  # the file holds one data set, CCZ4Q
    dof, unknowns = patch_data._dof, patch_data._unknowns
    lapse_index = unknown_names_from_description(patch_data._description, unknowns).index("lapse")

    x, lapse = [], []
    for patch in patch_data._cell_data:
        # cells are stored with x running fastest, then y, then z
        j = min(int((LineY - patch.offset[1]) / patch.size[1] * dof), dof - 1)
        k = min(int((LineZ - patch.offset[2]) / patch.size[2] * dof), dof - 1)
        for i in range(dof):
            cell = (k * dof + j) * dof + i
            x.append(patch.offset[0] + (i + 0.5) * patch.size[0] / dof)
            lapse.append(patch.values[cell * unknowns + lapse_index])
    order = np.argsort(x)
    return np.asarray(x)[order], np.asarray(lapse)[order]


def read_run(raw_dir):
    """
    Read every snapshot of one run.

    Returns (times, x, lapse) with lapse[s, i] the value in snapshot s at x[i] on the line y = z = 0.5.
    """
    meta_file = os.path.join(raw_dir, "solution-CCZ4.peano-patch-file")
    if not os.path.exists(meta_file):
        sys.exit(f"no snapshots in {raw_dir}. Run gauge-wave.py with --run first.")
    visualiser = Visualiser(meta_file, 0, sys.maxsize)
    visualiser.show_progress = False
    visualiser.patch_filter = CrossesLine()
    with contextlib.redirect_stdout(io.StringIO()):
        visualiser.read_metadata()

    times, profiles, x = [], [], None
    for snapshot in visualiser.snapshots:
        # The index file stores the absolute paths the simulation wrote to. If the folder has been
        # moved since (another machine, a renamed directory), look for the files next to the index.
        snapshot.filenames = [
            name if os.path.exists(name) else os.path.join(raw_dir, os.path.basename(name))
            for name in snapshot.filenames
        ]
        x_s, lapse_s = lapse_along_line(visualiser, snapshot)
        if x is None:
            x = x_s
        times.append(snapshot.timestamp)
        profiles.append(lapse_s)
    return np.asarray(times), x, np.vstack(profiles)


def errors(times, x, lapse):
    """Max and L2 error along the line, one value per snapshot."""
    diff = lapse - exact_lapse(x[None, :], times[:, None])
    return np.max(np.abs(diff), axis=1), np.sqrt(np.mean(diff**2, axis=1))


def write_csv(path, header, columns):
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for row in zip(*columns):
            writer.writerow([f"{v:.10e}" for v in row])


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--points", type=int, choices=sorted(gauge_wave.Grid), default=27)
    parser.add_argument("--work-dir", default=gauge_wave.default_work_dir(),
                        help=f"the folder that holds raw_data/ and data/ (default: ${gauge_wave.WorkDirVariable}, "
                             "or the example folder if it is not set)")
    args = parser.parse_args()

    f = gauge_wave.folders(os.path.abspath(os.path.expanduser(args.work_dir)), args.points)
    os.makedirs(f["data"], exist_ok=True)

    times, x, lapse = read_run(f["raw"])
    if len(x) != args.points:
        print(f"warning: found {len(x)} points along x, expected {args.points}")
    max_error, l2_error = errors(times, x, lapse)

    # 1. the centre over time
    centre = np.argmin(np.abs(x - 0.5))
    centre_num = lapse[:, centre]
    centre_exact = exact_lapse(x[centre], times)
    write_csv(os.path.join(f["data"], "centre.csv"), ["t", "numerical", "exact", "error"],
              [times, centre_num, centre_exact, centre_num - centre_exact])
    print(f"lapse at the centre ({x[centre]:.4f}, 0.5, 0.5):")
    print("{:>8} {:>12} {:>12} {:>12}".format("t", "numerical", "exact", "error"))
    for t, n, e in zip(times, centre_num, centre_exact):
        print("{:>8.4f} {:>12.6f} {:>12.6f} {:>12.3e}".format(t, n, e, abs(n - e)))

    # 2. the profile along x in the last snapshot
    profile_exact = exact_lapse(x, times[-1])
    write_csv(os.path.join(f["data"], "profile.csv"), ["x", "numerical", "exact", "error"],
              [x, lapse[-1], profile_exact, lapse[-1] - profile_exact])
    write_csv(os.path.join(f["data"], "errors.csv"), ["t", "max_error", "l2_error"],
              [times, max_error, l2_error])
    print(f"\nprofile along x at t = {times[-1]:.4f}, {len(x)} points:")
    print(f"  max error = {max_error[-1]:.3e}")
    print(f"  L2 error  = {l2_error[-1]:.3e}")

    # 3. plots (optional)
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("\nmatplotlib is not installed, skipping the plots")
        return

    t_fine = np.linspace(0.0, times[-1], 400)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(t_fine, exact_lapse(x[centre], t_fine), "k-", linewidth=1, label="exact")
    ax.plot(times, centre_num, "o", markersize=3, label=f"ExaGRyPE, {args.points} points")
    ax.set_xlabel("t")
    ax.set_ylabel("lapse at the centre")
    ax.legend()
    fig.savefig(os.path.join(f["data"], "check-centre.png"), dpi=100, bbox_inches="tight")

    x_fine = np.linspace(0.0, 1.0, 400)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(x_fine, exact_lapse(x_fine, times[-1]), "k-", linewidth=1, label="exact")
    ax.plot(x, lapse[-1], "o", markersize=3, label=f"ExaGRyPE, {args.points} points, t = {times[-1]:.2f}")
    ax.set_xlabel("x (y = z = 0.5)")
    ax.set_ylabel("lapse")
    ax.legend()
    fig.savefig(os.path.join(f["data"], "check-profile.png"), dpi=100, bbox_inches="tight")
    print(f"\nwrote CSV files and check-centre.png, check-profile.png to {f['data']}")


if __name__ == "__main__":
    main()
