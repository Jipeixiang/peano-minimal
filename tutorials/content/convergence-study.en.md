# Convergence study: the same code on 9, 27 and 81 grid points

This tutorial follows *From a Python script to simulation results*. That one explained how a single run works; this one runs **the same code** on three grids of different resolution and puts the results side by side, to see how fast the error falls as the grid gets finer: the **order of convergence**.

All commands run in the `example/` folder of peano-minimal, after step 0 (building the framework libraries). The generated files (`code/`, `raw_data/`, `data/`) belong to this one simulation, so this tutorial writes them to a work folder outside the repository, set by the environment variable `GAUGE_WAVE_WORK_DIR`:

```bash
export GAUGE_WAVE_WORK_DIR=~/sims/gauge-wave
```

All three scripts read it, and `gauge-wave.py` prints `work folder: ...` so you can check. Without it these three folders appear in `example/` and everything else stays the same. Paths such as `raw_data/n27/` below are relative to the work folder. Analogy: the 42100 parts boxes (`build/`) stay at home, while each excavator you build and the earth it digs go to another room.

---

## 1. Why a convergence study

A single run with an error of 5e-5 does not prove that the code is right: the error might be supposed to be much smaller, or it might be small by luck. A convergence study asks a different question: **when the grid is refined, does the error fall as fast as theory says it should?**

- In space we use fourth-order central differences (FD4): the error is $\propto h^4$, where $h$ is the grid spacing.
- In time we use fourth-order Runge-Kutta (RK4): the error is $\propto \Delta t^4$.
- The CFL condition ties the time step to the grid, $\Delta t \propto h$. So together the error is still $\propto h^4$.

Every refinement by a factor of 3 turns $h$ into $h/3$, so the error should shrink by $3^4 = 81$.

From the errors on two grids you get the **observed order** directly:

$$p = \frac{\log\left(E_N / E_{3N}\right)}{\log 3}$$

where $E_N$ is the error with $N$ grid points. A p close to 4 means the code works as designed; a clearly smaller p usually means a bug somewhere, or a grid that is still too coarse.

**Analogy**: back to LEGO set 42100. Imagine building the same R 9800 from ever smaller parts, each time with parts a third of the size. The smaller the parts, the smoother the curves and the closer the model looks to the real excavator. The order of convergence measures **how much the difference to the real machine shrinks each time the parts shrink**. Fourth order means: parts a third of the size, difference 81 times smaller.

![The same excavator at three resolutions](content/img/lego/scales.en.svg)

*The same excavator with 9, 27 and 81 “parts” across its width (blue), in front of the real shape (light). The smaller the parts, the closer to the real machine.*

---

## 2. Where the three grids come from

Grid points per axis = cells per axis × points per patch and axis.

Peano's grids split by three: the unit cube is split into at least 3 cells per axis, and cells can be split again into 3×3×3 children. So the number of cells per axis is 3, 9, 27, …, multiplied by the patch size:

| Grid points | cells × patch size | `volume_size` |
|---|---|---|
| 9 | 3 × 3 | 0.12 |
| 27 | 3 × 9 | 0.04 |
| 81 | 9 × 9 | 0.013 |

The `Grid` dictionary at the top of `gauge-wave.py` is this table.

- `volume_size` decides how far to refine: Peano splits a cell again as long as its edge is ≥ `volume_size × patch size`. So `volume_size` has to be a little larger than the target spacing 1/N.
- The finite difference scheme only sees a uniform grid with spacing 1/N. How the grid is cut into patches does not change the numerical result.

> **An easy trap**: with patches of size 9, the coarsest possible grid has 27 points. An earlier attempt used patch size 9 with `volume_size = 0.12` to get 9 points, and the log said `min mesh size=0.333333, #local cells=(27/1)`: still 3×3×3 cells, so 27 points. **Checking `min mesh size` in the log** is a good habit.

**Analogy**: LEGO beams come in fixed lengths; to reach a given size you can only combine "how many beams × how long each".

---

## 3. Running it

```bash
export GAUGE_WAVE_WORK_DIR=~/sims/gauge-wave   # once per new terminal
cd peano-minimal/example
python3 gauge-wave.py --points 9  --run
python3 gauge-wave.py --points 27 --run
python3 gauge-wave.py --points 81 --run
python3 analysis/convergence.py
```

Each `gauge-wave.py` call empties `code/`, regenerates and rebuilds, then runs. Snapshots go to that grid's own `raw_data/n<points>/`, so the runs do not overwrite each other. You can also check each run on its own with `python3 analysis/check.py --points <points>`.

### How much time and space it takes

Measured on one core of a laptop:

| Grid points | Time steps | Time per step | Total run time | Snapshots |
|---|---|---|---|---|
| 9 | 109 | 0.020 s | about 2 seconds | 3.8 MB |
| 27 | 325 | 0.28 s | about 91 seconds | 98 MB |
| 81 | 974 | 8.5 s | about 2 hours 18 minutes | 2.7 GB |

Generating and building adds about 15 seconds each time.

Why one refinement costs so much more:

- the number of grid points grows by $3^3 = 27$, and so does the work per step;
- the CFL condition shrinks the time step to a third, so there are **3 times** as many steps.

Together that is about **81 times** the cost. From 27 to 81 points, the time per step grew 30-fold and the total run time 91-fold, in line with that estimate. From 9 to 27 points the time per step grew only 14-fold, because on the tiny 9-point grid a fixed overhead per step dominates.

**Analogy**: with parts a third of the size, a model of the same size needs 27 times as many parts, and every move has to be split into three times as many small steps. That is why the 81-point run takes over two hours and is best left running in the background or on a cluster.

---

## 4. Which steps to rerun, and which not

Running three grids does not mean doing every step three times:

| Step | Command | How often for three grids | Why | Analogy |
|---|---|---|---|---|
| 0 | `cmake` + `cmake --build` | **once** | The framework libraries do not depend on the grid | The standard bags are made once and used for every model |
| 1a | `gauge-wave.py` (generate) | **once per grid** | The grid size is a constant baked into the generated code | A different scale needs a new design and new instructions |
| 1b | `gauge-wave.py` (build) | **once per grid** | The generated code changed and must be compiled again; the step 0 libraries are reused | Mould new set-specific parts and build again; the standard bags stay |
| 2 | `--run` | **once per grid** | Every grid needs its own results | Each model gets its own digging session and its own photo album |
| 3 | `check.py --points N` | once per grid, **rerun any time** | Only reads snapshots, never touches the simulation | Look through the album; no need to drive again |
| 3 | `convergence.py` | once at the end, **rerun any time** | Only reads the snapshots of all grids | Lay the three albums side by side |

In one sentence: **the simulation (1a, 1b, 2) runs once per grid, step 0 runs once, and the analysis (3) as often as you like.**

Two things are easy to get wrong:

- **`code/` only holds the last generated program.** `gauge-wave.py` empties `code/` every time, so after the 81-point run the 27-point program is gone. To run 27 points again, run `gauge-wave.py --points 27 --run` again, which costs about 15 seconds of generating and building. Analogy: the building table is cleared before every build, so the previous excavator has been taken apart, but its photos (`raw_data/n27/`) are still there.
- **Analysis never needs the simulation again.** `check.py` and `convergence.py` only read the snapshots in `raw_data/`; after changing a plot or the analysis, just rerun them.

### Later: what to rerun after a change

| You changed | Step 0 | 1a + 1b | Step 2 | `check.py` / `convergence.py` |
|---|---|---|---|---|
| Only plots or analysis scripts | – | – | – | **rerun** |
| Parameters in `gauge-wave.py` (grid, end time, plot interval, …) | – | **rerun** | **rerun** | **rerun** |
| Rerun a grid whose program in `code/` was replaced by another grid | – | **rerun** | **rerun** | **rerun** |
| Python in `src/` (the code generator) | – | **rerun** | **rerun** | **rerun** |
| C++ in `src/` (the framework libraries) | **rerun** | **rerun** (1b) | **rerun** | **rerun** |

A real example: the tick labels of the convergence plot were crowded, and labelling the grids directly as 1/81, 1/27, 1/9 only changed `convergence.py`. Rerunning just that script took a second; the two-hour 81-point simulation was not touched. The other way round, **a change to the simulation parameters means running the 81-point case again: another two hours.** So before you change something, ask: does it only affect the analysis, or the simulation itself?

---

## 5. How the error is measured

`check.py` and `convergence.py` measure the error along the same line: **y = z = 0.5, along x**, in the last snapshot at t = 1.

- The gauge wave only varies along x, so this line carries all the information.
- The exact solution is $\alpha(x,t) = \sqrt{1 - 0.1\,\sin\big(2\pi(x-t)\big)}$.
- At every grid point $x_i$ on the line we take the difference between the numerical value $\alpha_i$ and the exact solution, and report the **maximum error** and the **root mean square error** (L2):

$$E_{\max} = \max_i \big|\alpha_i - \alpha(x_i,t)\big|, \qquad E_{L2} = \sqrt{\frac{1}{N}\sum_{i=1}^{N}\big(\alpha_i - \alpha(x_i,t)\big)^2}$$

### Read only what you need

The 81-point snapshots add up to 2.7 GB. Reading all snapshots in full for every single probe point would be far too slow. Peano's snapshot reader (`tarch.plotter`) accepts a **patch filter**: it parses only the patches that touch the line and skips all others. That is why `convergence.py` reads every snapshot of all three grids in about one second.

### Two safeguards

- **Compare at the same time**: all three runs must reach t = 1. `convergence.py` skips a grid that is still running and says so.
- **Take the time from the snapshot**: output times snap to time steps and are not always exact multiples of 0.1 (the 9-point run writes at 0.1019, 0.2037, …). The exact solution uses the time recorded in each snapshot.

---

## 6. Results

The errors `convergence.py` measures at t = 1:

| Grid points $N$ | Spacing $h$ | Max error $E_{\max}$ | Order | L2 error $E_{L2}$ | Order |
|---|---|---|---|---|---|
| 9 | $1/9$ | $3.68 \times 10^{-3}$ | – | $1.95 \times 10^{-3}$ | – |
| 27 | $1/27$ | $4.98 \times 10^{-5}$ | 3.92 | $2.63 \times 10^{-5}$ | 3.92 |
| 81 | $1/81$ | $6.22 \times 10^{-7}$ | 3.99 | $3.32 \times 10^{-7}$ | 3.98 |

The theoretical order is 4. The terminal prints the same numbers; section 9 shows the format.

**The observed order rises from 3.92 to 3.99**, very close to the theoretical 4. Each refinement by 3 divides the error by about 74, then by about 80.

### Error against grid spacing

![Error against grid spacing on log-log axes](content/img/convergence/convergence.png)

On log-log axes, fourth-order convergence is a straight line with slope 4. The dashed line is a slope-4 guide. The three points sit almost exactly on it; only the coarsest, 9 points, is slightly off.

### Error over time

![Maximum error over time for the three grids](content/img/convergence/error-vs-time.png)

The three curves have the same shape and are only shifted up or down: the error grows fastest during the first 0.4 time units and more slowly afterwards. Neighbouring curves are about two orders of magnitude (a factor of 81) apart.

### Scaled error profiles

![Error profiles scaled by (N/27)^4](content/img/convergence/error-profiles.png)

This plot multiplies the error along x at t = 1 by $(N/27)^4$. If the error shrank exactly like $h^4$, the scaled curves would lie on top of each other.

- **27 and 81 points lie almost exactly on top of each other**: both grids are in the **asymptotic regime**, where $E \approx C\,h^4 f(x)$ and $f(x)$ depends only on the problem.
- **9 points is clearly off**: with only 9 points per wavelength the grid is too coarse to be in the asymptotic regime yet. This is also why the order from 9 to 27 (3.92) is a little lower than from 27 to 81 (3.99).

**Analogy**: once the parts are small enough, every further reduction shrinks the difference to the real machine by the same factor, and the differences stay in the same places. With parts that are too big, even the basic shape is off and the differences follow no pattern.

---

## 7. Common pitfalls

- **Grids that are too coarse**: the coarsest grid is often not yet asymptotic, and the order computed from it comes out too low. Use at least three grids and check that the order settles towards the theoretical value.
- **Comparing different times**: the error grows over time, so errors at different times are not comparable.
- **Runs overwriting each other**: snapshot file names are fixed. Here each grid writes to its own `raw_data/n<points>/`.
- **Round-off**: on very fine grids the error drops towards floating point precision and the order is no longer 4. The smallest error here is 6e-7, far above double precision (1e-16), so this does not matter yet.
- **Disk space**: the 81-point snapshots take 2.7 GB. For a convergence study alone you can raise `TimeBetweenPlots` in `gauge-wave.py` and write fewer snapshots.

---

## 8. Files produced

![The files after the three runs](diagrams/static/files-after.en.png)

*After the 9-, 27- and 81-point runs and the analysis: the repository gains only `build/`; everything else generated is in the work folder `$GAUGE_WAVE_WORK_DIR`. Without the variable those three folders appear inside `example/`, where .gitignore covers them. Open the [interactive version](view.html#files-after) to fold and unfold folders, or compare with the [files before running](view.html#files-before).*

---

## 9. How to test

After changing the code, or right after cloning from GitHub, use these steps to check that everything works.

### Quick test (without 81 points)

About 3 minutes once step 0 is done:

```bash
export GAUGE_WAVE_WORK_DIR=~/sims/gauge-wave   # once per new terminal
cd peano-minimal/example
python3 gauge-wave.py --points 9  --run
python3 gauge-wave.py --points 27 --run
python3 analysis/check.py --points 9
python3 analysis/check.py --points 27
python3 analysis/convergence.py
```

The last lines of `convergence.py` should read:

```
 points          h    max error      order     L2 error      order
      9    0.11111    3.680e-03          -    1.951e-03          -
     27    0.03704    4.976e-05       3.92    2.628e-05       3.92
```

Then check five things (2–4 are in the work folder):

1. the `work folder:` line printed by `gauge-wave.py` is the folder you set;
2. `raw_data/n9/` and `raw_data/n27/` hold the snapshots `solution-CCZ4*.peano-patch-file` and `run.log`;
3. `data/n9/` and `data/n27/` hold `centre.csv`, `profile.csv`, `errors.csv`, `check-centre.png`, `check-profile.png`;
4. `data/convergence/` holds `convergence.csv` and three plots;
5. `git status` in the repository root shows no new files, and `example/` holds only the scripts.

### Full test (with 81 points)

```bash
python3 gauge-wave.py --points 81 --run      # about 2 hours 20 minutes, 2.7 GB
python3 analysis/check.py --points 81
python3 analysis/convergence.py
```

Expected: max error 6.217e-07 for 81 points, observed order 3.99 from 27 to 81. The 9- and 27-point runs do not need to be repeated; `convergence.py` reads their existing results.

### Clean up afterwards

```bash
rm -rf "$GAUGE_WAVE_WORK_DIR"    # everything steps 1a-3 produced
rm -rf peano-minimal/build       # also step 0, back to a fresh clone
```

Run `echo $GAUGE_WAVE_WORK_DIR` first to make sure it points at the work folder. Without the variable, run `rm -rf code raw_data data` in `example/` instead.

> These tests were run on a copy cloned from a local git repository: step 0, 9 points, 27 points and both analysis scripts worked and gave the results above; running the analysis from another folder, and after moving the whole project elsewhere, worked too. Writing the results outside the repository with `GAUGE_WAVE_WORK_DIR` was tested too, with identical 9- and 27-point results. The 81-point run was done before the folder layout changed; its results are in section 6.
