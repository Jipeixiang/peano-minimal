# peano-minimal

A minimal, self-contained copy of [Peano](https://www.peano-framework.org) / ExaHyPE 2 / ExaGRyPE that runs one simulation: the **CCZ4 gauge wave** with fourth-order finite differences (FD4) and Runge-Kutta time stepping, on a 3D periodic regular grid.

Every file in `src/` and `example/` is used by that run. Nothing else is included, so you can follow the whole path from a Python script to a running simulation.

**Tutorials** (English and Chinese, with diagrams): <https://Jipeixiang.github.io/peano-minimal/tutorials/>, or open [`tutorials/index.html`](tutorials/) after downloading. 教程（中英双语，带流程图）见上面的链接，下载后也可以直接打开 `tutorials/index.html`。

[English](#english) · [中文](#中文)

---

## English

### What you need

- A C++20 compiler (clang or gcc) and `make`. On macOS, install the Xcode Command Line Tools with `xcode-select --install`.
- Python 3.12 or newer.
- About 10 minutes for the first build and one run; the 81-point run of the convergence study takes about 2 hours and 2.7 GB of disk.

### Repository layout

```
peano-minimal/
├── src/                     the Peano / ExaHyPE 2 / ExaGRyPE code this example needs
├── CMakeLists.txt           step 0: builds the Peano libraries into build/
├── requirements.txt         Python packages
├── LICENSE                  Peano's license
├── tutorials/               the tutorials and diagrams as a small website (index.html)
├── build/                   step 0 output                      (generated, not in git)
└── example/
    ├── gauge-wave.py        steps 1a, 1b, 2: generate, build, run
    ├── analysis/            step 3: programs that process the data
    │   ├── check.py         one run against the exact solution
    │   └── convergence.py   9, 27 and 81 points together: order of convergence
    ├── code/                steps 1a + 1b output: generated C++ and the executable  (generated)
    ├── raw_data/n27/        step 2 output: snapshots and run.log, one folder per grid (generated)
    └── data/n27/            step 3 output: CSV files and plots; data/convergence/    (generated)
```

Everything marked "generated" is listed in `.gitignore`, so the repository stays clean however often you run. `code/` is shared by all grids and emptied before each generation; `raw_data/` and `data/` keep one folder per grid.

### Step 0: Download and install (once)

```bash
git clone <this repository> peano-minimal
cd peano-minimal

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j
```

The last command compiles the six Peano libraries into `build/`. You only do this once. In every new terminal, activate the environment again with `source .venv/bin/activate`.

On macOS, if you clone into a folder that iCloud syncs (Documents, Desktop), give the clone a name ending in `.nosync`, e.g. `git clone <this repository> peano-minimal.nosync`. Otherwise iCloud creates conflict copies such as "kernels 2" while hundreds of files are regenerated.

### Step 1: Generate, compile and run one simulation (about 2 minutes)

```bash
cd example
python3 gauge-wave.py --points 27 --run 2>&1 | tee build.log
```

`gauge-wave.py` describes the simulation in Python. Peano turns it into C++ code in `code/`, compiles it into the executable `code/gauge-wave`, and `--run` starts it right away. The log shows the simulation time growing up to `t=1`; the snapshots at t = 0, 0.1, …, 1.0 go to `raw_data/n27/`.

If it fails, look at `tail -30 build.log`. Without `--run`, the script only builds, and prints the command that starts the simulation.

### Step 2: Compare with the exact solution

```bash
python3 analysis/check.py --points 27
```

The exact lapse is `sqrt(1 - 0.1 sin(2π(x - t)))`. The last lines should read:

```
profile along x at t = 1.0000, 27 points:
  max error = 4.976e-05
  L2 error  = 2.628e-05
```

CSV files and two plots are written to `data/n27/`: `check-profile.png` (the lapse along x at y = z = 0.5, t = 1) and `check-centre.png` (the lapse at the centre over time).

### Step 3: Convergence study on 9, 27 and 81 points

```bash
python3 gauge-wave.py --points 9  --run     # a few seconds
python3 gauge-wave.py --points 27 --run     # about 1.5 minutes
python3 gauge-wave.py --points 81 --run     # about 2 hours 20 minutes, 2.7 GB of snapshots
python3 analysis/convergence.py
```

`convergence.py` reads every grid that has finished, prints the error at t = 1 and the observed order of convergence, and writes `convergence.csv` and three plots to `data/convergence/`. FD4 with RK4 should converge with order 4: refining the grid by 3 divides the error by about 81.

### Which steps to rerun

| You changed | Step 0 | Steps 1a, 1b, 2 | Step 3 (analysis) |
|---|---|---|---|
| Only plots or analysis scripts | – | – | rerun |
| A parameter in `gauge-wave.py` (grid, end time, plot interval, …) | – | rerun | rerun |
| Want to run a grid whose program in `code/` was replaced by another grid | – | rerun | rerun |
| Python in `src/` (the code generator) | – | rerun | rerun |
| C++ in `src/` (the framework libraries) | rerun | rerun | rerun |

The analysis scripts only read `raw_data/`; they never need the simulation again.

### How to test

**Quick test** (about 3 minutes after step 0; leaves out the 81-point run):

```bash
cd example
python3 gauge-wave.py --points 9  --run
python3 gauge-wave.py --points 27 --run
python3 analysis/check.py --points 9
python3 analysis/check.py --points 27
python3 analysis/convergence.py
```

Expected end of the output:

```
 points          h    max error      order     L2 error      order
      9    0.11111    3.680e-03          -    1.951e-03          -
     27    0.03704    4.976e-05       3.92    2.628e-05       3.92
```

Then check that:

- `raw_data/n9/`, `raw_data/n27/` hold `solution-CCZ4*.peano-patch-file` and `run.log`;
- `data/n9/`, `data/n27/` hold `centre.csv`, `profile.csv`, `errors.csv`, `check-centre.png`, `check-profile.png`;
- `data/convergence/` holds `convergence.csv`, `convergence.png`, `error-vs-time.png`, `error-profiles.png`;
- `git status` shows no new files: everything generated is ignored.

**Full test**: add the 81-point run and run the analysis again.

```bash
python3 gauge-wave.py --points 81 --run      # about 2 hours 20 minutes
python3 analysis/check.py --points 81
python3 analysis/convergence.py
```

Expected: max error 6.217e-07 for 81 points, observed order 3.99.

**Clean up** afterwards, from `example/`:

```bash
rm -rf code raw_data data      # everything steps 1a-3 produced
rm -rf ../build                # also step 0, to start again from a fresh clone
```

### Changing parameters

The parameters are at the top of `example/gauge-wave.py`: the grids (`Grid`), Runge-Kutta order, end time, plot interval. They are compiled into the program, so after a change just run `gauge-wave.py` again: it empties `code/` and regenerates everything. Running a grid again first empties its own `raw_data/n<points>/`; rename that folder if you want to keep the old result.

### Keeping the generated files outside the repository

Everything in `code/`, `raw_data/` and `data/` belongs to this one simulation set-up; only `build/` (step 0) is shared by all simulations. To keep them outside the repository, for example on a scratch file system of a cluster, set an environment variable once:

```bash
export GAUGE_WAVE_WORK_DIR=~/sims/gauge-wave   # add it to ~/.zshrc or ~/.bashrc to keep it
```

`gauge-wave.py`, `check.py` and `convergence.py` all read it, so the commands above stay the same, and `gauge-wave.py` prints the work folder it uses. Without the variable everything goes into `example/` as before. `--work-dir <folder>` sets the folder for one command and wins over the variable.

Use one work folder per set-up: if you change a parameter (say the Runge-Kutta order), point the variable at a new folder, otherwise the new run overwrites `raw_data/n<points>/` of the old one.

### What happens in a run

```
gauge-wave.py --points N ──(Python API in src/)──▶ code/  (generated C++)
                                                     │
                            headers in src/ + libraries in build/
                                                     ▼
                                             code/gauge-wave ──▶ raw_data/nN/
                                                                    │
                                        analysis/check.py --points N ──▶ data/nN/
                                        analysis/convergence.py      ──▶ data/convergence/
```

### Limitations

- Only this setup is supported: 3D, release mode, FD4 with Runge-Kutta, regular grid, serial. Finite volumes, adaptive mesh refinement, MPI or OpenMP need the full Peano repository.
- Tested on macOS 14 with Python 3.12 and Apple clang 14. Linux should work but has not been tested.
- The snapshot index `raw_data/nN/solution-CCZ4.peano-patch-file` stores absolute paths. If you move the project, the analysis scripts look for the snapshots next to the index instead.

### License and credits

The code is taken from Peano, ExaHyPE 2 and ExaGRyPE and is distributed under Peano's license, see [LICENSE](LICENSE). The only changes are removed files and a few small edits that remove the dependency of the FD4 scheme on the finite volume code.

The tutorials in `tutorials/` were written for this repository. Their LEGO drawings are original sketches; LEGO is a trademark of the LEGO Group, which does not sponsor or endorse them. The one photo is credited in [tutorials/content/img/photos/CREDITS.md](tutorials/content/img/photos/CREDITS.md). `tutorials/vendor/` holds unmodified copies of marked (MIT) and MathJax (Apache 2.0).

---

## 中文

### 需要准备什么

- 支持 C++20 的编译器（clang 或 gcc）和 `make`。macOS 上运行 `xcode-select --install` 安装命令行工具即可。
- Python 3.12 或更新版本。
- 第一次编译加运行一次大约 10 分钟；收敛分析里 81 点那次约 2 小时，占 2.7 GB 磁盘。

### 仓库结构

```
peano-minimal/
├── src/                     这个算例用到的 Peano / ExaHyPE 2 / ExaGRyPE 代码
├── CMakeLists.txt           第 0 步：把 Peano 库编译到 build/
├── requirements.txt         Python 依赖
├── LICENSE                  Peano 的许可证
├── tutorials/               教程和流程图，一个小网站（index.html）
├── build/                   第 0 步的产物                       （生成的，不进 git）
└── example/
    ├── gauge-wave.py        第 1a、1b、2 步：生成、编译、运行
    ├── analysis/            第 3 步：处理数据的程序
    │   ├── check.py         一次运行和精确解对比
    │   └── convergence.py   9、27、81 三种网格一起：收敛阶
    ├── code/                1a + 1b 的产物：生成的 C++ 和可执行文件   （生成的）
    ├── raw_data/n27/        第 2 步的产物：快照和 run.log，每种网格一个  （生成的）
    └── data/n27/            第 3 步的产物：CSV 和图；还有 data/convergence/ （生成的）
```

标着"生成的"都写在 `.gitignore` 里，跑多少次仓库都保持干净。`code/` 所有网格共用，每次生成前清空；`raw_data/` 和 `data/` 每种网格各一个目录。

### 第 0 步：下载和安装（只做一次）

```bash
git clone <本仓库地址> peano-minimal
cd peano-minimal

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j
```

最后一条命令把 6 个 Peano 库编译到 `build/` 里，只需要做一次。每开一个新终端，都要用 `source .venv/bin/activate` 重新激活环境。

在 macOS 上，如果克隆到 iCloud 同步的目录（"文稿"、"桌面"），目录名最好以 `.nosync` 结尾，例如 `git clone <本仓库地址> peano-minimal.nosync`。否则重新生成几百个文件时，iCloud 会造出 "kernels 2" 这样的冲突副本。

### 第 1 步：生成、编译并运行一次模拟（约 2 分钟）

```bash
cd example
python3 gauge-wave.py --points 27 --run 2>&1 | tee build.log
```

`gauge-wave.py` 用 Python 描述这个模拟。Peano 把它翻译成 C++ 代码放进 `code/`，编译成可执行文件 `code/gauge-wave`，`--run` 让它编译完马上运行。日志里的模拟时间会一直增长到 `t=1`；t = 0, 0.1, …, 1.0 的快照写在 `raw_data/n27/`。

如果失败，看 `tail -30 build.log`。不加 `--run` 时只编译，并打印启动模拟的命令。

### 第 2 步：和精确解对比

```bash
python3 analysis/check.py --points 27
```

精确解是 lapse = `sqrt(1 - 0.1 sin(2π(x - t)))`。最后几行应该是：

```
profile along x at t = 1.0000, 27 points:
  max error = 4.976e-05
  L2 error  = 2.628e-05
```

CSV 文件和两张图写在 `data/n27/`：`check-profile.png`（t = 1 时沿 x 轴、y = z = 0.5 的 lapse）和 `check-centre.png`（域中心的 lapse 随时间的变化）。

### 第 3 步：9、27、81 三种网格的收敛分析

```bash
python3 gauge-wave.py --points 9  --run     # 几秒钟
python3 gauge-wave.py --points 27 --run     # 约 1.5 分钟
python3 gauge-wave.py --points 81 --run     # 约 2 小时 20 分，快照共 2.7 GB
python3 analysis/convergence.py
```

`convergence.py` 读取所有跑完的网格，打印 t = 1 时的误差和实测收敛阶，并把 `convergence.csv` 和三张图写到 `data/convergence/`。FD4 加 RK4 应该是四阶收敛：网格加密 3 倍，误差大约变为 1/81。

### 哪些步骤要重跑

| 你改了 | 第 0 步 | 第 1a、1b、2 步 | 第 3 步（分析） |
|---|---|---|---|
| 只改了画图、分析脚本 | – | – | 重跑 |
| `gauge-wave.py` 里的参数（网格、结束时间、输出间隔……） | – | 重跑 | 重跑 |
| 想再跑某种网格，但 `code/` 已经被别的网格覆盖 | – | 重跑 | 重跑 |
| `src/` 里的 Python（代码生成器） | – | 重跑 | 重跑 |
| `src/` 里的 C++（框架库） | 重跑 | 重跑 | 重跑 |

分析脚本只读 `raw_data/`，永远不需要重跑模拟。

### 如何测试

**快速测试**（第 0 步之后约 3 分钟，不跑 81 点）：

```bash
cd example
python3 gauge-wave.py --points 9  --run
python3 gauge-wave.py --points 27 --run
python3 analysis/check.py --points 9
python3 analysis/check.py --points 27
python3 analysis/convergence.py
```

输出最后应该是：

```
 points          h    max error      order     L2 error      order
      9    0.11111    3.680e-03          -    1.951e-03          -
     27    0.03704    4.976e-05       3.92    2.628e-05       3.92
```

然后检查：

- `raw_data/n9/`、`raw_data/n27/` 里有 `solution-CCZ4*.peano-patch-file` 和 `run.log`；
- `data/n9/`、`data/n27/` 里有 `centre.csv`、`profile.csv`、`errors.csv`、`check-centre.png`、`check-profile.png`；
- `data/convergence/` 里有 `convergence.csv`、`convergence.png`、`error-vs-time.png`、`error-profiles.png`；
- `git status` 不显示任何新文件：生成的东西都被忽略了。

**完整测试**：再加上 81 点，然后重新做分析。

```bash
python3 gauge-wave.py --points 81 --run      # 约 2 小时 20 分
python3 analysis/check.py --points 81
python3 analysis/convergence.py
```

预期结果：81 点的最大误差 6.217e-07，实测收敛阶 3.99。

**测试完清理**（在 `example/` 里）：

```bash
rm -rf code raw_data data      # 第 1a 到第 3 步产生的所有东西
rm -rf ../build                # 连第 0 步也删掉，回到刚克隆下来的状态
```

### 修改参数

参数在 `example/gauge-wave.py` 开头：网格（`Grid`）、Runge-Kutta 阶数、结束时间、输出间隔。参数是编译进程序的，改完直接重新运行 `gauge-wave.py` 就行，它会清空 `code/` 并重新生成。重跑同一种网格会先清空它自己的 `raw_data/n<点数>/`，想保留旧结果就先把那个目录改个名字。

### 把生成的文件放到仓库外面

`code/`、`raw_data/`、`data/` 里的东西都只属于这一次模拟设置，只有第 0 步的 `build/` 是所有模拟共用的。想把它们放到仓库外面（比如超算的 scratch 文件系统），设一次环境变量就行：

```bash
export GAUGE_WAVE_WORK_DIR=~/sims/gauge-wave   # 想一直生效就写进 ~/.zshrc 或 ~/.bashrc
```

`gauge-wave.py`、`check.py`、`convergence.py` 都会读这个变量，所以上面的命令一个字都不用改，`gauge-wave.py` 开头会打印它用的工作目录。不设这个变量，就和以前一样全放在 `example/` 里。`--work-dir <目录>` 只对这一条命令生效，并且优先于环境变量。

一种设置用一个工作目录：改了参数（比如 Runge-Kutta 阶数）就把变量指到新的目录，不然新结果会覆盖旧的 `raw_data/n<点数>/`。

### 一次运行发生了什么

```
gauge-wave.py --points N ──(src/ 里的 Python API)──▶ code/（生成的 C++）
                                                       │
                              src/ 里的头文件 + build/ 里的库
                                                       ▼
                                               code/gauge-wave ──▶ raw_data/nN/
                                                                      │
                                          analysis/check.py --points N ──▶ data/nN/
                                          analysis/convergence.py      ──▶ data/convergence/
```

### 限制

- 只支持这一种配置：3D、release 模式、FD4 + Runge-Kutta、规则网格、串行。有限体积、自适应网格加密、MPI 或 OpenMP 需要完整的 Peano 仓库。
- 在 macOS 14 + Python 3.12 + Apple clang 14 上测试过。Linux 应该可以，但没有测试。
- 快照索引 `raw_data/nN/solution-CCZ4.peano-patch-file` 里记的是绝对路径。项目挪了位置以后，分析脚本会改到索引旁边去找快照。

### 许可证和来源

代码取自 Peano、ExaHyPE 2 和 ExaGRyPE，按 Peano 的许可证发布，见 [LICENSE](LICENSE)。改动只有删除文件，以及几处小修改，去掉了 FD4 格式对有限体积代码的依赖。

`tutorials/` 里的教程是为这个仓库写的。乐高示意图是原创手绘；LEGO 是乐高集团的商标，乐高集团与本教程无关。唯一一张照片的来源见 [tutorials/content/img/photos/CREDITS.md](tutorials/content/img/photos/CREDITS.md)。`tutorials/vendor/` 里是未修改的 marked（MIT）和 MathJax（Apache 2.0）。
