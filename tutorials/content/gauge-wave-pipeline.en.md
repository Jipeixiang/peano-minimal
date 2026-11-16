# From a Python script to simulation results: how an ExaGRyPE gauge wave run works

This tutorial is for people who are new to Peano / ExaHyPE 2 / ExaGRyPE. It does not cover the physics of CCZ4. It explains one thing:
**what happens between the first command and the final lapse error, which files each step produces, and where to look when something goes wrong.**

The example is the gauge wave test: the CCZ4 equations, fourth-order central differences (FD4) with RK4 time integration, periodic boundaries, 27 grid points per direction, run for one period (t = 1).

The commands are for peano-minimal, a trimmed copy of Peano that contains only the code this example uses. Where the text says `peano/src` or `peano/build`, peano-minimal has `src/` and `build/`; the ideas apply to the full Peano repository as well.

---

## 1. The big picture: four steps

Think of it as **building LEGO Technic set 42100 (the Liebherr R 9800 remote-controlled excavator) and then digging with it**. The set has 4,108 pieces, 7 motors and 2 Smart Hubs, and you drive it with the Control+ app on a phone:

| Step | Command | Analogy | What actually happens |
|---|---|---|---|
| 0 | `cmake` + `cmake --build` in the Peano repository | The LEGO factory makes **standard parts**, such as the 1×2 plate (3023) and the black short friction pin (2780), and packs them into bags | Peano's C++ sources are compiled into static libraries (`.a`) |
| 1a | `python3 gauge-wave.py` (first half, `generate()`) | A designer designs set 42100: drawings for its **set-specific parts**, and the building instructions | Python generates C++ code specific to this problem |
| 1b | `python3 gauge-wave.py` (second half, `build()`) | The set-specific parts are moulded from the drawings, then **built into the excavator** together with the standard parts, following the instructions | The generated code is compiled and linked with the step 0 libraries into an executable |
| 2 | `./gauge-wave` | **Switch on and dig**: drive the excavator from the app and take photos as it works | The actual numerical computation; snapshots are written |
| 3 | `python3 analysis/check.py` | **Check the photos**: how far is each move from the real R 9800? | Compare with the exact solution, compute errors, plot |

The key point: **up to the end of 1b, not a single physical quantity has been computed**, just as no soil has been moved before the excavator is built.

![The LEGO analogy for the whole pipeline](content/img/lego/overview.en.svg)

*The analogy for the whole pipeline: the factory makes standard parts → design the set → mould and build → switch on and dig → check.*

---

## 2. Step 0: build Peano itself (the standard parts)

```bash
cd peano-minimal
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j 8
```

This compiles the `.cpp` files under `src/` into a few static libraries in `build/`. The full Peano repository has thousands of `.cpp` files and also needs `-DENABLE_EXAHYPE=ON -DENABLE_EXAGRYPE=ON -DENABLE_BLOCKSTRUCTURED=ON -DENABLE_LOADBALANCING=ON`; peano-minimal contains only what this example needs, so it does not use these switches. Each library is one layer:

- **Peano4Core**: the grid engine at the bottom. Spacetree grids, the mechanism for traversing them, parallelism, and the utilities in `tarch`.
- **ToolboxBlockStructured / ToolboxLoadBalancing**: groups grid cells into patches (for example 9×9×9 blocks), exchanges halos (overlap layers) between neighbouring patches, and balances the load.
- **ExaHyPE2Core**: a generic framework for hyperbolic PDEs. It handles time stepping and snapshot output, and it does **not** know which equations you solve.
- **ExaGRyPECore**: the physics of the CCZ4 equations: fluxes, sources, non-conservative products. It is built on top of ExaHyPE 2.

**In short:**

- It is **independent** of the problem. A gauge wave, a black hole or anything else uses the same libraries, just as excavators, sports cars and castles all use 1×2 plates and friction pins.
- You do it once. Redo it only after changing **C++** code in `peano/src`, or when switching build mode (release / debug).
- It is the slowest step, around ten minutes or more on a laptop.

![Three standard parts](content/img/lego/parts.en.svg)

*Three standard parts (sketch). The libraries from step 0 are like them: whatever you build, you need them.*

---

## 3. Step 1a: Python generates code (designing the set)

```python
peano4_project.generate()
```

### Why not write the C++ directly?

Peano's design is to **bake the specifics of your problem into the C++ code before it is compiled.** For example, 58 unknowns, 9×9×9 patches and a halo of 3 layers all become constants, so the compiler can optimise for them: unroll loops, size arrays at compile time.

So Python acts as a **configuration language and code generator**. In `gauge-wave.py` you describe *what* you want (CCZ4, FD4, RK4, periodic boundaries, resolution, end time), and it writes the C++ that does it.

Analogy: `gauge-wave.py` is the **brief** handed to the LEGO designer: "a Liebherr R 9800 that can slew, dig and drive". The parameters (58 unknowns, 9×9×9 patches, RK4) are the scale and options in the brief. The designer fixes every dimension in the instructions (a 15-hole beam here, a 3-long pin there), so whoever builds it never has to measure. The compiler is in the same position: when every size is a known constant, it can plan the work in advance.

![The brief goes to the designer, who draws a booklet with every size fixed](content/img/lego/brief.en.svg)

*The brief on the left is the set-up in `gauge-wave.py`; `generate()` is the designer, who turns it into a booklet: the C++ in `code/`. Every size in the booklet is fixed: the scale, the number of holes in a beam, the length of a pin, the 9×9×9 patch. The compiler sees only constants.*

### Which files it generates

The generated booklet comes in eight parts; each card matches one row of the table:

![The eight parts of the booklet](content/img/lego/booklet.en.svg)

*Left to right, top to bottom, they follow the rows of the table. The orange holes on the `celldata/` card are the halo, enlarged below.*



| Generated | Purpose | Analogy |
|---|---|---|
| `Constants.h` | Constants such as the position and size of the domain | Scale and dimensions on the cover of the instructions |
| `AbstractCCZ4.h/.cpp` | A solver class for this problem, with sizes and parameters fixed | The chassis and frame of this excavator, with every size fixed |
| `kernels/` | The core numerical kernels: FD4 differences, RK linear combinations, in 2D and 3D versions | The slewing ring, boom and bucket: the parts that do the work |
| `celldata/`, `facedata/` | What each cell and face stores (patch arrays, halo layers), and how it is packed for parallel exchange | What goes into each module, and which pin holes to leave free where two modules join (the halo is the rows of holes where neighbouring modules overlap) |
| `observers/` | Peano is driven by grid traversals: every time step sweeps the grid several times. These files say what to do at each cell or face during each sweep, for example one RK stage, a halo update, or writing a snapshot | The steps on each page of the instructions |
| `repositories/` | Global state and the order in which the sweeps run | The page numbers: which page to build first |
| `gauge-wave-main.cpp` | `main()`: initialise, then loop until the end time | Page 1 of the instructions: "start here" |
| `CMakeLists.txt`, `Makefile` | How to compile, and where in `peano/build/` to find the step 0 libraries | The parts list at the back of the instructions: which bags to use and where to get them |

The halo in the `celldata/` and `facedata/` row is worth a closer look. The grid is cut into many patches, each like a 9-hole beam (9 grid points along one direction). FD4 needs values from the next patch to update the points near the edge, so every beam keeps 3 extra holes at each end and copies their values from its neighbour before every step:

![The halo: the holes where two beams overlap](content/img/lego/halo.en.svg)

*Grey is module A, blue is module B, orange is the halo. The arrows are the copy before every step: the values of A's last 3 holes go into B's left halo, and B's first 3 holes go into A's right halo. `facedata/` says how these values are stored and packed for the neighbour in parallel runs.*

![The drive train: motor, gears, clutch gear, turntable, bucket](content/img/lego/drive.en.svg)

*The drive train of 42100 (sketch): the motor drives the turntable and the bucket through a reduction and a clutch gear, which slips under overload to protect the gears behind it. These working parts are what `kernels/` is.*

**In short:** in this step Python **only writes files**. It does no numerical work. The designer only draws and writes instructions, and builds nothing.

---

## 4. Step 1b: compile and link (mould the set-specific parts, build the excavator)

```python
peano4_project.build(make_clean_first=True)
```

In the run directory it does the following:

1. **`make clean`**: removes the previous build products, so this build starts from scratch. Analogy: take the last excavator apart and remould its set-specific parts.
2. **`make -j`**: the `Makefile` in the run directory is only a wrapper around cmake:
   - **Configure**: in `build.<project name>/`, cmake reads `CMakeLists.txt`, finds the step 0 libraries and sets compiler options (release mode turns on `-O3`). `CMakeCache.txt` and friends are created here. Analogy: put the standard bags from the parts list on the table and get the tools ready.
   - **Compile**: each `.cpp` generated in 1a goes to the compiler (clang on macOS) and becomes an object file `.o`. Analogy: mould the set-specific parts from the 1a drawings.
   - **Link**: the `.o` files and the step 0 `.a` libraries are joined into the executable. Analogy: follow the instructions and build the set-specific and standard parts into one excavator.

**In short:** this is the first time a compiler checks the code. A design mistake from 1a often shows up only now, when you start building.

---

## 5. Interlude: `.cpp`, `.o`, `.a` and linking

This section explains the file types that keep appearing in step 0 and step 1b.

![From source to executable](content/img/lego/chain.en.svg)

### `.o`: object file

- **Where it comes from**: the compiler translates **one** `.cpp` file (together with the headers it `#include`s) into machine code. One `.cpp` gives one `.o`.
- **What is inside**:
  - the functions defined in that file, already as instructions the CPU can execute;
  - a table of **what I provide**, for example "I define the function `CCZ4::flux`";
  - a table of **what I still need**, for example "I call `tarch::la::norm`, but it is not here".
- **Why it cannot run on its own**: it is a single part, and many of the things it needs are still missing.
- **Analogy**: **one shot from one mould**. A `.cpp` file is a mould; a mould can have several cavities, so one shot produces several different parts, and **each part is one function**. Every part has studs and holes: the studs are connections it offers to other parts ("what I provide"), and the holes only hold once another part is pushed in ("what I still need"). One shot of parts on its own does nothing.

![One shot from one mould](content/img/lego/mould.en.svg)

*A `.cpp` file is a mould; compiling it is one shot that produces a set of parts (one `.o`), and each part is a function. Studs are “what I provide”, holes are “what I still need”.*

### `.a`: static library (archive)

- **Where it comes from**: many `.o` files **packed** into one file with the `ar` command. It really is just an archive; `.a` stands for archive.
- Step 0 produces files of this kind.
- **Analogy**: the **numbered bags** inside a LEGO box. `ar` packs the bags, one library per bag. The difference: every LEGO set comes with its own bags, whereas Peano packs its `.a` files once and every simulation shares them.

### Linking: building the excavator

The linker:

1. takes all the `.o` files compiled in 1b;
2. collects everything they still need;
3. looks in the step 0 `.a` files for `.o` files that provide those functions, and **takes only what is needed**;
4. the `.o` files it takes in may need further things, so it keeps looking until nothing is missing;
5. joins everything into one executable that runs on its own.

Analogy: with a list of missing parts in your hand you open the bags in order and take only the parts you need. A part you take out may need yet another pin, so you keep looking until every hole is filled, and then the excavator is complete.

If something cannot be found, you get a link error:

```
Undefined symbols for architecture x86_64:
  "CCZ4::...", referenced from: ...
```

It means: somebody calls a CCZ4 function, but the linker was not told to look in the ExaGRyPE library. Analogy: the instructions say "put part X here", but none of the bags on the table contains X, most likely because a whole bag was never taken out of the box.

> **Library order matters.** The linker goes through the bags in order and never goes back to a bag it has passed. ExaGRyPE's parts need parts from the ExaHyPE 2 bag, so ExaGRyPE must come **before** ExaHyPE 2; then its gaps can be filled from the bags after it.
>
> A big numbered LEGO bag often contains small bags of tiny parts that are needed everywhere, such as black short friction pins (2780) and blue long friction pins (6558). Peano's counterpart is the lowest layer, Tarch (logging, timing, linear algebra). Almost every library needs it, so it goes last, where it can supply the pins every library before it is missing. CMake usually works this order out from the dependencies; you only have to think about it when you write link commands by hand.

![The linker opens the bags in order](content/img/lego/bags.en.svg)

*The linker opens the bags in order: ExaGRyPE needs parts from ExaHyPE 2, so it comes first; every bag needs the Tarch pins, so that bag comes last.*

### Why does step 1b produce `.o` files too?

Because 1a produced **new C++ source code**, and every `.cpp` has to become a `.o` first. The linker only accepts `.o` and `.a` files.

| | Compiles which `.cpp` | Where the `.o` goes |
|---|---|---|
| Step 0 | The generic code in `peano/src/` | Packed into `.a` files in `peano/build/` |
| 1b | The problem-specific code generated in 1a | Stays in `build.<project name>/CMakeFiles/...` and goes straight to the linker |

In terms of the analogy: the step 0 bags only hold **standard parts**, such as 3023 and 2780. The **set-specific parts** of this excavator have to be moulded from the 1a drawings before you build; that is the compile part of 1b. They are used by this one excavator only, so they go straight onto the table instead of into a bag (`.a`).

![Linear actuators: retracted, extended, and on the machine pushing the boom and the stick](content/img/lego/actuator.en.svg)

*The linear actuators of 42100 (sketch): turning the input axle extends or retracts the rod, which pushes the boom and the stick. Parts made for one specific mechanism like these are the set-specific parts that 1b compiles.*

### Why split things this way

1. **It saves time**: Peano has thousands of `.cpp` files. Once they are in `.a` files, a new problem only needs the few dozen files generated in 1a to be compiled and then linked, which takes a minute or two.
2. **It separates errors**:
   - **Compile errors** (`unknown type name`, `undeclared identifier`): a `.cpp` file itself is wrong. Look at the source. Analogy: the mould itself is faulty and the part cannot be made.
   - **Link errors** (`Undefined symbols`): every part is fine, but a part is missing during assembly, usually a library that was not linked. Look at `CMakeLists.txt`.
3. **Static vs dynamic**: a `.a` file is a static library. Linking **copies** its code into the executable, so the finished program runs even after `peano/build/` is deleted. Dynamic libraries (`.dylib` on macOS, `.so` on Linux) are loaded at run time, so they must be found when the program starts. MPI on a supercomputer is usually a dynamic library, which is why you `module load` it before running.

   Analogy: static libraries are like beams, pins and gears; they are clicked into the excavator while you build it, and once it is built you can throw the empty bags away. A dynamic library is like 42100's Control+ app. The excavator holds 7 motors and 2 Smart Hubs, but the app is not in the box: you install it on a phone and connect it to the hubs when you switch on. Without the app, or with a version that does not match, the excavator sits still; that is the program stopping at start-up with `Library not loaded` (macOS) or `error while loading shared libraries` (Linux). `module load` on a supercomputer is opening the app and connecting to the hubs before you start.

   ![Static and dynamic libraries](content/img/lego/app.en.svg)

   *A static library's code is copied into the program at link time; a dynamic library is only loaded when the program starts, like the app you connect at switch-on.*

### Try it yourself

```bash
cd peano/build
find . -name "*.a"                    # all static libraries from step 0
ar t <some.a> | head                  # which .o files are packed inside
nm -C <some.a> | grep " T " | head    # T: functions this library provides
nm -C <some.a> | grep " U " | head    # U: functions this library still needs (undefined)
```

---

## 6. Steps 2 and 3: run and analyse

```bash
export GAUGE_WAVE_WORK_DIR=~/sims/gauge-wave   # results outside the repository (optional, see section 10)
cd peano-minimal/example
python3 gauge-wave.py --points 27 --run    # 1a + 1b + 2
python3 analysis/check.py --points 27               # 3
```

- With `--run`, `gauge-wave.py` starts the program right after building it. The program sweeps the grid again and again until t = 1 and writes the snapshots `solution-CCZ4*.peano-patch-file` to `raw_data/n27/` in the work folder (`$GAUGE_WAVE_WORK_DIR` if set, otherwise `example/`), together with a copy of its screen output in `run.log`. About 90 seconds on one core of a laptop.
- `check.py` reads the snapshots, compares the lapse with the exact solution $\alpha(x,t) = \sqrt{1 - A\sin\big(2\pi(x-t)\big)}$ ($A = 0.1$), prints the error, and writes CSV files and the plots `check-centre.png` and `check-profile.png` to `data/n27/`.
- **Reference result**: with 27 points and RK4, the maximum lapse error at t = 1 is about **5e-5**.
- Running the same code on 9, 27 and 81 points and measuring the order of convergence is the topic of the tutorial *Convergence study*.

Analogy: step 2 is switching on the app and putting the excavator through a full work cycle (up to t = 1), taking a photo every so often (the snapshots). Step 3 is holding the photos against the real R 9800's standard moves and measuring how far off each position is (comparing with the exact solution).

![Switch on and dig, taking snapshots](content/img/lego/dig.en.svg)

*Step 2: switch on and dig, taking a snapshot every so often. Step 3: hold the snapshots against the real excavator.*

![A real Liebherr R 9200 mining excavator](content/img/photos/liebherr-r9200.jpg)

*A real Liebherr R 9200 mining excavator (a sister model of the R 9800) at bauma 2016. In the analogy it is the “exact solution” every model is compared with. Photo: Neuwieser, [CC BY-SA 2.0](https://creativecommons.org/licenses/by-sa/2.0/), via [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Bauma_2016_%2826667207701%29.jpg).*

---

## 7. All the commands

```bash
# --- Step 0: environment and Peano itself (once) ---
cd peano-minimal
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt       # includes cmake

cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j 8

# --- Steps 1 and 2: generate, build, run ---
export GAUGE_WAVE_WORK_DIR=~/sims/gauge-wave   # optional: generated files outside the repository
cd example
python3 gauge-wave.py --points 27 --run 2>&1 | tee build.log

# --- Step 3: analyse ---
python3 analysis/check.py --points 27
```

`gauge-wave.py` uses two important paths:

- `exahype2.api.Project(..., directory=<work folder>/code)`: generated code and the executable go here;
- `project.set_Peano4_installation(<absolute path to peano-minimal>, build_mode)`: tells the generated `CMakeLists.txt` where to find the step 0 libraries.

Without `GAUGE_WAVE_WORK_DIR`, the generated `code/`, `raw_data/` and `data/` all live in `example/` and are listed in `.gitignore`, so the repository stays clean however often you run. All three belong to this one simulation set-up (only `build/` is shared by every simulation). To keep them outside the repository, for example on a cluster's scratch file system, set an environment variable once, `export GAUGE_WAVE_WORK_DIR=~/sims/gauge-wave`; all three scripts use it and the commands stay the same. `--work-dir` does the same for a single command. Analogy: the 42100 parts boxes (`build/`) stay at home, while each excavator you build and the earth it digs (`code/`, `raw_data/`, `data/`) go to another room, one room per set-up.

---

## 8. What to redo after a change

| You changed | Redo |
|---|---|
| C++ in `peano/src` | 0 → 1b → 2 |
| Python in `peano/src` (the code generator) | 1a → 1b → 2 |
| Parameters in `gauge-wave.py` (resolution, end time, …) | 1a → 1b → 2 |
| Only the analysis script | 3 |
| Nothing, you just want to run again | 2 |

---

## 9. Where to look when something fails

The step in which the error appears tells you roughly where the problem is:

| Error appears in | Typical message | Problem is usually in |
|---|---|---|
| 1a (Python) | `AttributeError`, `ImportError` | The code generator (Python under `peano/src`) or your script |
| 1b compile | `unknown type name`, `use of undeclared identifier` | The C++ generated in 1a is incomplete (for example a missing `#include`) |
| 1b link | `Undefined symbols` | A library is not linked, or the library order is wrong. Check `CMakeLists.txt` |
| 2 run | Assertion failures, NaN, crashes | Numerics or physics |

Note: **the step where a bug lives is not always the step where it is reported.** If 1a writes a faulty file, Python stays quiet and the problem shows up only in 1b, at compile or link time. A real example: one version of the code had three generator bugs. All three live in 1a, but each is reported somewhere else:

| Bug | Lives in | Reported in |
|---|---|---|
| The FD4 scheme lacks a `halo_size` attribute | 1a (a field of the brief is left empty) | 1a, Python raises `AttributeError` (the designer hands the brief straight back) |
| Generated kernel headers miss their `#include` lines | 1a (one page of the instructions does not show the parts for that step) | 1b compile (you only notice at that page, when you do not know which parts to use) |
| The `CMakeLists.txt` template does not link the ExaGRyPE library | 1a (the parts list forgets one bag) | 1b link (parts are missing at the very end) |

---

## 10. How to organise the files

### Separate what is disposable from what is valuable

| Type | Produced by | When you run 1a + 1b again |
|---|---|---|
| Generated C++ code | 1a | **Overwritten** by 1a |
| Build products (`.o`, executable) | 1b | **Removed** by `make clean`, then rebuilt |
| Simulation results | 2 | Untouched, but the next run writes files with **the same names** and overwrites them |
| Processed data | 3 | Untouched, but can be overwritten in the same way |

- Code and build products can be regenerated at any time. They are **disposable**.
- Simulation results and processed data are what is **valuable**.

Analogy: `code/` is the building table, cleared before each build; `raw_data/` holds the photos from each digging session; `data/` holds what you found by checking them. Clear the table whenever you like, but keep the photos and the findings.

### The layout in peano-minimal

Fresh from GitHub, before any step has run, there is only the framework source and your scripts:

![Files before running](diagrams/static/files-before.en.png)

With `GAUGE_WAVE_WORK_DIR=~/sims/gauge-wave` set, after the 9-, 27- and 81-point runs and the analysis the repository gains only `build/`, and `code/`, `raw_data/`, `data/` are in the work folder:

![Files after the three runs](diagrams/static/files-after.en.png)

*Without the variable, the three work-folder folders appear inside `example/` with the same structure, covered by .gitignore. The interactive versions can fold and unfold folders: [before](view.html#files-before), [after](view.html#files-after).*

Notes:

- **Do not split generated code from build products.** Peano writes the generated code, `CMakeLists.txt` and `Makefile` into one directory and builds there. Splitting them means fighting the framework.
- **Keep results and data per run.** File names are fixed (always `solution-CCZ4.peano-patch-file`), so without separate folders the next run overwrites the previous one. On a supercomputer every job has its own directory anyway, so this rarely comes up there.
- **Empty `code/` before every 1a.** 1a only overwrites the files it generates this time; files from an earlier generation that are no longer generated stay behind. Some versions of the generator also append to old kernel files. `gauge-wave.py` does this for you.
- **Do not commit generated files.** They are all listed in `.gitignore`; only your own scripts go under version control. Note that `git clean -fdx` also deletes ignored files, simulation results included.
- **iCloud**: if the project sits in a folder that iCloud syncs (such as Documents), give the clone a name ending in `.nosync`, e.g. `peano-minimal.nosync`. iCloud then leaves it alone and does not create conflict copies such as "xxx 2" when hundreds of files are regenerated.
