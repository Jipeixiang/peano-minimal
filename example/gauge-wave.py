"""
CCZ4 gauge wave with fourth-order finite differences (FD4) and Runge-Kutta.

Usage (from this folder, after step 0 has built the libraries in ../build):

    python3 gauge-wave.py --points 27          # steps 1a + 1b: generate C++ and build the executable
    python3 gauge-wave.py --points 27 --run    # ... and step 2: run the simulation

--points is the number of grid points per axis: 9, 27 or 81.

Folders (all created next to this script; none of them is tracked by git):

    code/            steps 1a + 1b: generated C++, Makefile, build files, the executable.
                     Shared by all grids and emptied before each generation.
    raw_data/n27/    step 2: snapshots written by the simulation, plus run.log
    data/n27/        step 3: what analysis/check.py makes from them
    data/convergence/      what analysis/convergence.py makes from all grids

To put code/, raw_data/ and data/ somewhere else (outside the repository, on a scratch file system),
set the environment variable once, and all three scripts use it:

    export GAUGE_WAVE_WORK_DIR=~/sims/gauge-wave

--work-dir <folder> does the same for one command and wins over the variable.
"""

import argparse
import os
import shutil
import subprocess
import sys

Here = os.path.dirname(os.path.abspath(__file__))
PeanoRoot = os.path.abspath(os.path.join(Here, ".."))  # the repository root, with build/ from step 0

# Grid points per axis = (cells per axis) x (points per patch and axis).
# Peano splits the unit cube into 3 cells per axis at least, and splits a cell again into 3x3x3
# as long as its edge is >= volume_size * patch_size. So:
#    9 points = 3 cells x 3 points per patch
#   27 points = 3 cells x 9 points per patch
#   81 points = 9 cells x 9 points per patch
# The finite difference scheme only sees a uniform grid with spacing 1/points; how the grid is cut
# into patches does not change the result.
Grid = {  # points per axis: (patch_size, volume_size)
    9: (3, 0.12),
    27: (9, 0.04),
    81: (9, 0.013),
}
RKOrder = 4            # Runge-Kutta order
EndTime = 1.0          # the gauge wave has period 1: run one period
TimeBetweenPlots = 0.1


WorkDirVariable = "GAUGE_WAVE_WORK_DIR"


def default_work_dir():
    """$GAUGE_WAVE_WORK_DIR if set, else the example folder. Shared with the analysis scripts."""
    value = os.environ.get(WorkDirVariable, "").strip()
    return os.path.abspath(os.path.expanduser(value)) if value else Here


def folders(work_dir, points):
    """The folders of one grid. Shared with analysis/check.py and analysis/convergence.py."""
    return {
        "code": os.path.join(work_dir, "code"),
        "raw": os.path.join(work_dir, "raw_data", f"n{points}"),
        "data": os.path.join(work_dir, "data", f"n{points}"),
    }


def parse_arguments():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--points", type=int, choices=sorted(Grid), default=27,
                        help="grid points per axis (default 27)")
    parser.add_argument("--run", action="store_true",
                        help="run the simulation after building it")
    parser.add_argument("--work-dir", default=default_work_dir(),
                        help=f"where code/, raw_data/ and data/ go (default: ${WorkDirVariable}, "
                             "or next to this script if it is not set)")
    return parser.parse_args()


def generate_and_build(points, f):
    """Steps 1a and 1b: Python generates C++ into code/, then make compiles and links it."""
    if not os.path.exists(os.path.join(PeanoRoot, "build", "PeanoTargets.cmake")):
        sys.exit(f"{os.path.join(PeanoRoot, 'build')} has no Peano libraries yet. Do step 0 first:\n"
                 f"  cd {PeanoRoot} && cmake -S . -B build -DCMAKE_BUILD_TYPE=Release && cmake --build build -j")

    sys.path.insert(0, os.path.join(PeanoRoot, "src"))
    import peano4.api
    import exahype2.api
    import exagrype.api
    from peano4.api.Logger import Logger

    patch_size, volume_size = Grid[points]

    # Start from an empty code/: the generator only overwrites what it writes this time,
    # and kernel files are appended to, so leftovers of an earlier generation would leak in.
    shutil.rmtree(f["code"], ignore_errors=True)
    os.makedirs(f["code"])
    os.makedirs(f["raw"], exist_ok=True)
    # The generator writes a log of what it did when Python exits; keep it with the generated code.
    Logger().file_name = os.path.join(f["code"], "log.md")

    project = exahype2.api.Project(
        namespace=["runs", "gaugewave"],
        project_name="gauge-wave",
        directory=f["code"],
        executable="gauge-wave",
    )

    solver = exagrype.api.CCZ4Solver(
        "CCZ4",
        initial_condition=exagrype.api.initialvalues.gauge_wave(),
    )
    # Fourth-order central differences + Runge-Kutta, the scheme ExaGRyPE uses in production.
    # (The finite volume schemes do not compile with CCZ4 at the moment, and FD4 is far more
    # accurate: tutorial 521 reports a lapse error of 5e-5 instead of 4e-2 with 27 points.)
    solver.numerical_scheme = exahype2.api.rkfd4.CentralDifferencesWithRungeKutta(
        solver, patch_size, rk_order=RKOrder
    )
    solver.grid_construction = exahype2.api.rkfd4.SetupSimulationOverRegularGrid(
        solver, volume_size=volume_size
    )
    solver.plotter = exahype2.api.rkfd4.PlotAsVTKFile(
        solver,
        first_plot_time_stamp=0.0,
        time_in_between_plots=TimeBetweenPlots,
        output_path=f["raw"],  # snapshots solution-CCZ4*.peano-patch-file go here
    )
    project.add_solver(solver)

    project.set_global_simulation_parameters(
        dimensions=3,
        offset=[0.0, 0.0, 0.0],
        size=[1.0, 1.0, 1.0],
        min_end_time=EndTime,
        max_end_time=EndTime,
        periodic_BC=[True, True, True],
    )

    project.set_Peano4_installation(PeanoRoot, peano4.api.output.CompileMode.RELEASE)
    peano4_project = project.generate_Peano4_project(verbosity=peano4.api.LoggerVerbosity.TEXT)
    peano4_project.generate()                       # step 1a
    peano4_project.build(make_clean_first=True)     # step 1b


def run(f):
    """Step 2: run the executable inside raw_data/n<points>/ and keep a copy of its output in run.log."""
    executable = os.path.join(f["code"], "gauge-wave")
    # Old snapshots of this grid would be mixed with the new ones, so start empty.
    shutil.rmtree(f["raw"], ignore_errors=True)
    os.makedirs(f["raw"])
    log_path = os.path.join(f["raw"], "run.log")
    print(f"running {executable} in {f['raw']}")
    with open(log_path, "w") as log:
        process = subprocess.Popen([executable], cwd=f["raw"],
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            sys.stdout.write(line)
            log.write(line)
        process.wait()
    if process.returncode != 0:
        sys.exit(f"the simulation stopped with exit code {process.returncode}, see {log_path}")


def main():
    args = parse_arguments()
    work_dir = os.path.abspath(os.path.expanduser(args.work_dir))
    print(f"work folder: {work_dir}")
    f = folders(work_dir, args.points)
    generate_and_build(args.points, f)
    if args.run:
        run(f)
        print(f"\ndone. snapshots are in {f['raw']}")
        print(f"next: python3 analysis/check.py --points {args.points}")
    else:
        print(f"\nbuilt {os.path.join(f['code'], 'gauge-wave')}")
        print(f"run it with: cd {f['raw']} && {os.path.join(f['code'], 'gauge-wave')}")


if __name__ == "__main__":
    main()
