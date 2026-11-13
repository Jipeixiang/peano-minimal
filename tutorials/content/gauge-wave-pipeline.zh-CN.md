# 从 Python 脚本到模拟结果：ExaGRyPE gauge wave 是怎么跑起来的

这篇教程面向刚接触 Peano / ExaHyPE 2 / ExaGRyPE 的人。它不讲 CCZ4 的物理，而是讲清楚一件事：
**从敲下第一条命令到拿到 lapse 误差，中间每一步在干什么、产生了哪些文件、出错时该去哪里找。**

例子是 gauge wave（规范波）测试：CCZ4 方程，四阶中心差分（FD4）加 RK4 时间积分，周期边界，每个方向 27 个网格点，跑一个周期（t = 1）。

命令以 peano-minimal 为准：它是 Peano 的精简版，只包含这个算例用到的代码。文中说的 `peano/src`、`peano/build` 对应 peano-minimal 里的 `src/`、`build/`，道理对完整的 Peano 仓库同样适用。

---

## 1. 全景：四个步骤

可以把整件事类比成**拼一台乐高 Technic 42100（Liebherr R 9800 遥控挖掘机），然后开着它挖土**。这一套有 4,108 个零件、7 个电机、2 个 Smart Hub，用手机上的 Control+ app 遥控：

| 步骤 | 命令 | 类比 | 实际在做什么 |
|---|---|---|---|
| 0 | 在 Peano 仓库里 `cmake` + `cmake --build` | 乐高工厂生产**通用零件**，比如 1×2 板（3023）、黑色短摩擦销（2780），装成分包 | 把 Peano 的 C++ 源码编译成静态库 `.a` |
| 1a | `python3 gauge-wave.py`（前半段 `generate()`） | 设计师设计 42100 这一套：画出**专属零件**的图纸，写好说明书 | Python 生成针对这个问题的 C++ 代码 |
| 1b | `python3 gauge-wave.py`（后半段 `build()`） | 按图纸压出专属零件，再和通用零件一起**照说明书拼成整车** | 编译生成的代码，和第 0 步的库链接成可执行文件 |
| 2 | `./gauge-wave` | **开机挖土**：打开 app 遥控挖掘机干活，边挖边拍照 | 真正的数值计算，输出快照 |
| 3 | `python3 analysis/check.py` | **对照照片检查**：和真 R 9800 的动作比，差多少 | 和精确解比较，算误差、画图 |

最重要的一点：**到 1b 结束为止，一个物理量都还没算过。** 就像挖掘机拼好之前，一铲土都还没挖。

![整个流程的乐高类比](content/img/lego/overview.zh-CN.svg)

*整个流程的类比：工厂生产通用零件 → 设计这一套 → 压零件、拼整车 → 开机挖土 → 对照检查。*


---

## 2. 第 0 步：编译 Peano 本体（通用零件）

```bash
cd peano-minimal
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j 8
```

这一步把 `src/` 下的 `.cpp` 编译成几个静态库，放在 `build/`。完整的 Peano 仓库有几千个 `.cpp`，还要额外打开 `-DENABLE_EXAHYPE=ON -DENABLE_EXAGRYPE=ON -DENABLE_BLOCKSTRUCTURED=ON -DENABLE_LOADBALANCING=ON`；peano-minimal 只包含这个算例需要的代码，不用这些开关。每个库负责一层：

- **Peano4Core**：最底层的网格引擎，负责 spacetree 网格、遍历网格的机制和并行，还包括 `tarch` 里的各种工具函数。
- **ToolboxBlockStructured / ToolboxLoadBalancing**：把网格单元组织成 patch（例如 9×9×9 的小块），在相邻 patch 之间交换 halo（重叠层），并做负载均衡。
- **ExaHyPE2Core**：通用的双曲型方程求解框架，负责时间步进的流程和输出快照。它**不知道**你解的是什么方程。
- **ExaGRyPECore**：CCZ4 方程本身的物理实现，包括通量、源项、非守恒项等。它建立在 ExaHyPE 2 之上。

**特点：**

- 和具体问题**无关**。不管跑 gauge wave、黑洞还是别的，用的都是同一批库。就像 1×2 板和摩擦销，挖掘机、跑车、城堡都要用。
- 只做一次。只有改了 `peano/src` 里的 **C++** 代码，或者换了编译模式（release / debug），才需要重做。
- 最慢，在笔记本上大约要十几分钟。

![三种通用零件](content/img/lego/parts.zh-CN.svg)

*三种通用零件（示意图）。第 0 步编译出的库就像它们：不管拼什么都要用。*

---

## 3. 第 1a 步：Python 生成代码（设计这一套）

```python
peano4_project.generate()
```

### 为什么要多这一步，不直接写 C++？

Peano 的设计思路是：**把问题的具体参数在编译前就写死进 C++ 代码。** 比如未知量有 59 个、patch 是 9×9×9、halo 宽 3 层，这些都写成常数，编译器就能针对它们优化，比如展开循环、在编译期确定数组大小。

所以 Python 在这里扮演的是**配置语言加代码生成器**：你在 `gauge-wave.py` 里描述"要什么"（CCZ4 方程、FD4 格式、RK4、周期边界、分辨率、结束时间），它替你写出"怎么做"的 C++。

类比：`gauge-wave.py` 是交给乐高设计师的**需求单**："做一台 Liebherr R 9800，要能回转、能挖、能走"。参数（59 个未知量、9×9×9 的 patch、RK4）就是需求单上的比例和配置。设计师把每个尺寸都在说明书里定死，比如这里用 15 孔的梁、那里用 3 单位的销，拼的人就不用现场量。编译器也是这样：尺寸都是已知常数，它就能提前把活安排好。

![需求单交给设计师，画出尺寸全部定死的说明书](content/img/lego/brief.zh-CN.svg)

*左边的需求单就是 `gauge-wave.py` 里的设置；`generate()` 是设计师，把它变成一本说明书，也就是 `code/` 里的 C++。说明书上每个尺寸都已标死：比例、梁的孔数、销的长度、patch 的 9×9×9，编译器拿到的全是常数。*

### 生成了哪些文件

生成的说明书可以拆成下面八个部分，每张卡片对应表格里的一行：

![说明书的八个部分](content/img/lego/booklet.zh-CN.svg)

*从左上到右下依次对应表格各行。`celldata/` 卡片里橙色的孔就是 halo，下面有放大图。*



| 生成物 | 作用 | 类比 |
|---|---|---|
| `Constants.h` | 计算域的位置和大小等常数 | 说明书封面上的尺寸和比例 |
| `AbstractCCZ4.h/.cpp` | 这次问题专用的求解器类，大小和参数都写死在里面 | 这台挖掘机的底盘和车架设计，尺寸都已定死 |
| `kernels/` | 数值格式的核心计算：FD4 差分、RK 线性组合等，分 2D 和 3D 两个版本 | 回转机构、动臂和挖斗：真正干活的部分 |
| `celldata/`、`facedata/` | 每个网格单元和每个面上存什么数据（patch 数组、halo 层），以及并行时怎么打包发送 | 每个模块上装什么，以及两个模块的接合处要预留哪些销孔（halo 就是相邻模块重叠的那几排孔） |
| `observers/` | Peano 是"遍历网格"驱动的：每个时间步要把网格扫好几遍。这里规定每一遍扫到每个单元或面时做什么，比如算 RK 的某一阶段、更新 halo、输出快照 | 说明书每一页上的步骤 |
| `repositories/` | 全局状态，以及这些"扫网格"的步骤按什么顺序执行 | 说明书的页码：先拼哪页、后拼哪页 |
| `gauge-wave-main.cpp` | `main()` 函数：初始化，然后循环推进，直到到达结束时间 | 说明书第 1 页："从这里开始" |
| `CMakeLists.txt`、`Makefile` | 怎么编译，以及去 `peano/build/` 的哪里找第 0 步的库 | 说明书背面的零件清单：要用哪些分包，去哪里拿 |

表里 `celldata/`、`facedata/` 那一行的 halo 值得放大看一下。网格被切成很多块 patch，每块就像一根 9 孔的梁（一个方向上 9 个格点）。FD4 算靠边的格点时要用到隔壁 patch 的值，所以每根梁两头各多留 3 个孔，每一步开始前先从邻居那里把值抄过来：

![halo：两根梁重叠的那几个孔](content/img/lego/halo.zh-CN.svg)

*灰色是模块 A，蓝色是模块 B，橙色是 halo。箭头表示每一步开始前的“抄值”：A 最后 3 个孔的值抄进 B 左边的 halo，B 前 3 个孔的值抄进 A 右边的 halo。`facedata/` 规定了这些值怎么存、并行时怎么打包发给邻居。*

![传动链：马达、齿轮、离合齿轮、回转台、挖斗](content/img/lego/drive.zh-CN.svg)

*42100 的传动链（示意图）：马达经过齿轮减速和离合齿轮，带动回转台和挖斗。离合齿轮在阻力太大时打滑，保护后面的齿轮。这一串真正干活的零件对应 `kernels/`。*

**特点：** Python 在这一步**只是写文件**，不做任何数值计算。设计师只画图、写说明书，自己不动手拼。

---

## 4. 第 1b 步：编译和链接（压出专属零件，拼成整车）

```python
peano4_project.build(make_clean_first=True)
```

它在运行目录里依次做这些事：

1. **`make clean`**：清掉上一次的编译产物，保证这次从头编译。类比：把上次拼好的车拆掉，专属零件也回炉重做。
2. **`make -j`**：运行目录里的 `Makefile` 只是一层外壳，它会调用 cmake：
   - **配置**：在 `build.<项目名>/` 里根据 `CMakeLists.txt` 找到第 0 步的库，设置编译选项（release 模式会打开 `-O3` 优化）。`CMakeCache.txt` 等文件就生成在这里。类比：按零件清单把要用的通用分包摆上桌，备好工具。
   - **编译**：把 1a 生成的每个 `.cpp` 交给编译器（macOS 上是 clang），翻译成目标文件 `.o`。类比：按 1a 的图纸注塑，压出这一套的专属零件。
   - **链接**：把这些 `.o` 和第 0 步的 `.a` 拼在一起，得到可执行文件。类比：照说明书把专属零件和通用零件拼成整车。

**特点：** 编译器在这一步第一次真正检查代码对不对。1a 里设计错的地方，往往要到 1b 动手拼的时候才发现。

---

## 5. 插曲：`.cpp`、`.o`、`.a` 和链接

这一节解释第 0 步和 1b 里反复出现的文件类型。

![从源码到可执行文件](content/img/lego/chain.zh-CN.svg)

### `.o`：目标文件（object file）

- **怎么来的**：编译器把**一个** `.cpp`（连同它 `#include` 的头文件）翻译成机器码。一个 `.cpp` 对应一个 `.o`。
- **里面有什么**：
  - 这个文件里定义的函数，已经是 CPU 能直接执行的指令；
  - 一张"**我提供什么**"的表，例如"我定义了函数 `CCZ4::flux`"；
  - 一张"**我还缺什么**"的表，例如"我调用了 `tarch::la::norm`，但它不在我这里"。
- **为什么不能直接运行**：它只是一个零件，里面还有很多缺的东西没有着落。
- **类比**：一副模具一次注塑压出来的**一板零件**。一个 `.cpp` 是一副模具，一副模具可以有好几个型腔，一次压出好几种零件；**每个零件就是一个函数**。每个零件上都有凸点和孔：凸点是它能给别的零件用的连接，也就是"我提供什么"；孔要等别的零件插进来才能固定，也就是"我还缺什么"。单独一板零件什么也干不了。

![一副模具一次压出一板零件](content/img/lego/mould.zh-CN.svg)

*一个 `.cpp` 是一副模具，编译一次压出一板零件（一个 `.o`），每个零件是一个函数。凸点是“我提供什么”，孔是“我还缺什么”。*

### `.a`：静态库（archive）

- **怎么来的**：把很多 `.o` **打包**成一个文件（`ar` 命令）。本质上就是一个归档包，`.a` 就是 archive 的意思。
- 第 0 步生成的就是这种文件。
- **类比**：**零件分包**。打开乐高的盒子，里面是一袋一袋印着编号的分包；`ar` 打包就是装袋，每个库是一包。不同的是，乐高每个套装各装一份分包，而 Peano 的 `.a` 只装一次，所有算例共用同一批分包。

### 链接：把零件拼成整车

链接器做的事情：

1. 拿到 1b 编译出来的所有 `.o`；
2. 汇总它们"还缺什么"；
3. 到第 0 步的 `.a` 里找能提供这些函数的 `.o`，**只拿需要的**；
4. 新拿进来的 `.o` 可能又缺别的东西，就继续找，直到所有缺口都补上；
5. 拼成一个能独立运行的可执行文件。

类比：手里拿着一张缺件清单，按顺序打开分包，只取用得上的零件。取出来的零件可能还要配别的销子，那就接着找，直到每个孔都插上了，车也就拼好了。

缺口补不上时，就会出现链接错误：

```
Undefined symbols for architecture x86_64:
  "CCZ4::...", referenced from: ...
```

意思是：有人调用了 CCZ4 的函数，但链接器没被告知去 ExaGRyPE 的库里找。类比：说明书写着"这里插一个零件 X"，翻遍桌上所有分包都找不到 X，多半是有一整包根本没拿出来。

> **库的顺序很重要。** 链接器按顺序翻分包，翻过去的分包不会再回头。ExaGRyPE 的零件要用到 ExaHyPE 2 分包里的零件，所以 ExaGRyPE 要排在 ExaHyPE 2 **前面**，它的缺口才能在后面的分包里补上。
>
> 乐高的大分包（上面印着数字）里常常还套着小分包，装的是黑色短摩擦销（2780）、蓝色长摩擦销（6558）这种到处都要用的小零件。Peano 里对应的是最底层的 Tarch（日志、计时、线性代数），几乎每个库都要用，所以它要排在最后，前面所有库缺的销子都能在它那里补齐。CMake 一般会按依赖关系自动排好这个顺序，只有手写链接命令时才要自己操心。

![链接器按顺序翻分包](content/img/lego/bags.zh-CN.svg)

*链接器按顺序翻分包：ExaGRyPE 要用 ExaHyPE 2 的零件，所以排在前面；Tarch 这包销子大家都要用，放在最后。*

### 为什么 1b 也会生成 `.o`？

因为 1a 生成的是**新的 C++ 源码**，而任何 `.cpp` 都必须先编译成 `.o`，链接器只认 `.o` 和 `.a`。

| | 编译谁的 `.cpp` | `.o` 去哪 |
|---|---|---|
| 第 0 步 | `peano/src/` 里的通用代码 | 打包成 `.a`，放在 `peano/build/` |
| 1b | 1a 生成的专用代码 | 留在 `build.<项目名>/CMakeFiles/...`，直接拿去链接 |

用类比来说：第 0 步的分包里只有**通用零件**，比如 3023 和 2780。这台挖掘机独有的**专属零件**得在拼装前按 1a 的图纸先压出来，这就是 1b 的编译。它们只给这一台用，所以直接放在桌上，不用再装进分包（`.a`）。

![线性执行器：收回、伸出，以及装在车上推动动臂和斗杆](content/img/lego/actuator.zh-CN.svg)

*42100 里的线性执行器（伸缩杆，示意图）：马达转动输入轴，杆就伸出或收回，用来推动动臂和斗杆。这种为特定机构准备的零件，就像 1b 编译出来的专属零件。*

### 这样分的意义

1. **省时间**：Peano 有几千个 `.cpp`，打成 `.a` 之后，每跑一个新问题只需要编译 1a 生成的几十个文件，再链接一下，一两分钟就够了。
2. **分开排错**：
   - **编译错误**（`unknown type name`、`undeclared identifier`）：某个 `.cpp` 自己写得不对，去查源码。类比：模具本身有问题，零件压不出来。
   - **链接错误**（`Undefined symbols`）：零件都没问题，但拼的时候缺零件，通常是少链接了某个库，去查 `CMakeLists.txt`。
3. **静态 vs 动态**：`.a` 是静态库，链接时会把代码**复制进**可执行文件，所以编译好的程序即使删掉 `peano/build/` 也能运行。与之相对的是动态库（macOS 上是 `.dylib`，Linux 上是 `.so`），它们在运行时才加载，所以运行时必须能找到它们。超算上的 MPI 一般是动态库，这也是为什么要先 `module load` 再运行。

   类比：静态库就像梁、销、齿轮这些机械零件，拼的时候已经卡进车里，拼完以后分包袋扔掉也不影响。动态库就像 42100 的 Control+ app：挖掘机里装着 7 个电机和 2 个 Smart Hub，但 app 不在盒子里，要在开机的时候装在手机上、连上 Hub，车才动得起来。手机上没装 app，或者版本对不上，挖掘机就趴着不动，对应程序一启动就报 `Library not loaded`（macOS）或 `error while loading shared libraries`（Linux）。超算上的 `module load` 就像开机前先打开 app、连上 Hub。

   ![静态库和动态库](content/img/lego/app.zh-CN.svg)

   *静态库的代码在链接时就复制进了程序；动态库要等程序启动时才加载，就像开机时才连上的 app。*

### 动手看一看

```bash
cd peano/build
find . -name "*.a"                    # 第 0 步生成的所有静态库
ar t <某个.a> | head                  # 库里打包了哪些 .o
nm -C <某个.a> | grep " T " | head    # T：这个库"提供"的函数
nm -C <某个.a> | grep " U " | head    # U：这个库"还缺"的函数（undefined）
```

---

## 6. 第 2 步和第 3 步：运行和分析

```bash
export GAUGE_WAVE_WORK_DIR=~/sims/gauge-wave   # 结果写到仓库外面（可选，见第 10 节）
cd peano-minimal/example
python3 gauge-wave.py --points 27 --run    # 1a + 1b + 2
python3 analysis/check.py --points 27               # 3
```

- 加了 `--run`，`gauge-wave.py` 编译完就运行程序。程序把网格遍历一遍又一遍，推进到 t = 1，把快照 `solution-CCZ4*.peano-patch-file` 写到工作目录的 `raw_data/n27/`（设了 `GAUGE_WAVE_WORK_DIR` 就在那里，否则在 `example/` 里），屏幕输出同时存进那里的 `run.log`。在笔记本上单线程大约 90 秒。
- `check.py` 读取快照，把 lapse 和精确解 $\alpha(x,t) = \sqrt{1 - A\sin\big(2\pi(x-t)\big)}$（$A = 0.1$）比较，输出误差，并把 CSV 和两张图 `check-centre.png`、`check-profile.png` 写到 `data/n27/`。
- **参考结果**：27 点、RK4、t = 1 时，lapse 最大误差约 **5e-5**。
- 同一份代码在 9、27、81 三种网格上跑，再一起分析收敛阶，见教程《收敛性分析》。

类比：第 2 步是打开 app 开着挖掘机干一整轮活（推进到 t = 1），每隔一段时间拍一张照片（快照）。第 3 步是把照片和真 R 9800 的标准动作对照，看每个位置差多少（和精确解比）。

![开机挖土，边挖边拍快照](content/img/lego/dig.zh-CN.svg)

*第 2 步开机挖土，每隔一段时间拍一张快照；第 3 步拿快照和真挖掘机对照。*

![真实的 Liebherr R 9200 矿用挖掘机](content/img/photos/liebherr-r9200.jpg)

*真实的 Liebherr R 9200 矿用挖掘机（R 9800 的同系列机型），摄于 bauma 2016。在类比里它就是“精确解”：模型做得好不好，要和它比。照片：Neuwieser，[CC BY-SA 2.0](https://creativecommons.org/licenses/by-sa/2.0/)，来自 [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Bauma_2016_%2826667207701%29.jpg)。*

---

## 7. 完整操作流程

```bash
# --- 第 0 步：环境和 Peano 本体（只做一次） ---
cd peano-minimal
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt       # 包括 cmake

cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j 8

# --- 第 1、2 步：生成、编译、运行 ---
export GAUGE_WAVE_WORK_DIR=~/sims/gauge-wave   # 可选：生成的文件写到仓库外面
cd example
python3 gauge-wave.py --points 27 --run 2>&1 | tee build.log

# --- 第 3 步：分析 ---
python3 analysis/check.py --points 27
```

`gauge-wave.py` 里有两个关键路径：

- `exahype2.api.Project(..., directory=<工作目录>/code)`：生成的代码和可执行文件放在这里；
- `project.set_Peano4_installation(<peano-minimal 的绝对路径>, build_mode)`：告诉生成的 `CMakeLists.txt` 去哪里找第 0 步的库。

不设 `GAUGE_WAVE_WORK_DIR` 时，生成的 `code/`、`raw_data/`、`data/` 都在 `example/` 里，并且写进了 `.gitignore`，所以跑多少次仓库都保持干净。这三个目录都只属于这一次模拟设置（只有 `build/` 是所有模拟共用的），想放到仓库外面，比如超算的 scratch 目录，就设一次环境变量 `export GAUGE_WAVE_WORK_DIR=~/sims/gauge-wave`，三个脚本都会用它，命令不用改；只想对一条命令生效就用 `--work-dir`。类比：同一套 42100 的零件盒（`build/`）留在家里，每次搭出来的挖掘机和它挖的土（`code/`、`raw_data/`、`data/`）都搬到另一间屋子，换一个设置就换一间屋子。

---

## 8. 改了什么，要重做哪一步

| 你改了 | 需要重做 |
|---|---|
| `peano/src` 里的 C++ | 0 → 1b → 2 |
| `peano/src` 里的 Python（代码生成器） | 1a → 1b → 2 |
| `gauge-wave.py` 里的参数（分辨率、结束时间等） | 1a → 1b → 2 |
| 只改了分析脚本 | 3 |
| 什么都没改，只想再跑一次 | 2 |

---

## 9. 出错了去哪找

看报错出现在哪个阶段，就知道问题大概在哪：

| 报错出现在 | 典型样子 | 问题通常在 |
|---|---|---|
| 1a（Python） | `AttributeError`、`ImportError` | 代码生成器（`peano/src` 下的 Python），或者你的脚本 |
| 1b 编译 | `unknown type name`、`use of undeclared identifier` | 1a 生成的 C++ 不完整（例如漏了 `#include`） |
| 1b 链接 | `Undefined symbols` | 少链接了某个库，或者库的顺序不对，去查 `CMakeLists.txt` |
| 2 运行 | 断言失败、NaN、崩溃 | 数值或物理问题 |

注意：**出错的阶段和报错的阶段不一定相同。** 1a 生成的文件有缺陷时，Python 不会报错，要到 1b 编译或链接时才暴露。下面是一个真实例子：某个版本的代码里有三个生成器 bug，它们都出在 1a，却分别在三个不同的地方报错：

| Bug | 出错在 | 报错在 |
|---|---|---|
| FD4 格式缺少 `halo_size` 属性 | 1a（需求单少填了一项） | 1a，Python 直接 `AttributeError`（设计师当场退回需求单） |
| 生成 kernel 头文件时漏写 `#include` | 1a（说明书某一页漏印了这一步要用的零件） | 1b 编译（拼到这一页才发现不知道该用哪些零件） |
| `CMakeLists.txt` 模板没有链接 ExaGRyPE 库 | 1a（零件清单漏写了一个分包） | 1b 链接（拼到最后发现缺件） |

---

## 10. 文件该怎么组织

### 先分清"一次性的"和"有价值的"

| 类型 | 哪步生成 | 再跑一次 1a+1b 时会怎样 |
|---|---|---|
| 生成的 C++ 代码 | 1a | 被 1a **覆盖** |
| 编译产物（`.o`、可执行文件） | 1b | 被 `make clean` **清掉**，再重新编译 |
| 模拟结果 | 2 | 不受影响，但下次运行会用**同样的文件名**覆盖它们 |
| 处理后的数据 | 3 | 不受影响，但同样可能被覆盖 |

- 代码和编译产物随时可以重新生成，是**一次性的**。
- 模拟结果和处理后的数据才是**有价值的**。

类比：`code/` 是拼装台，每次开工前清空；`raw_data/` 是每次开机挖土拍下的照片；`data/` 是对照照片得出的检查结果。拼装台可以随时清，照片和检查结果要好好收着。

### peano-minimal 的布局

刚克隆下来、一步都还没跑的时候，只有框架源码和你写的脚本：

![跑之前的文件结构](diagrams/static/files-before.zh-CN.png)

设了 `GAUGE_WAVE_WORK_DIR=~/sims/gauge-wave`，跑完 9、27、81 三组和分析以后：仓库里只多了 `build/`，`code/`、`raw_data/`、`data/` 都在工作目录里：

![跑完三组以后的文件结构](diagrams/static/files-after.zh-CN.png)

*不设这个变量时，工作目录下的三个目录会出现在 `example/` 里，结构相同，并且都写在 .gitignore 里。交互版可以折叠、展开：[跑之前](view.html#files-before)、[跑完以后](view.html#files-after)。*

几点说明：

- **生成代码和编译产物不要拆开。** Peano 把生成的代码、`CMakeLists.txt` 和 `Makefile` 都写进同一个目录，编译也在这个目录里进行，硬拆开就是和框架对着干。
- **结果和数据按运行分。** 文件名是固定的（每次都叫 `solution-CCZ4.peano-patch-file`），不分开的话，后一次运行会覆盖前一次。在超算上，每个作业天然就有自己的目录，所以通常不会遇到这个问题。
- **每次 1a 之前先清空 `code/`。** 1a 只覆盖它这次生成的文件，上次生成过、这次不再生成的文件会残留下来；某些版本的生成器还会往旧的 kernel 文件后面追加内容。`gauge-wave.py` 会自动做这一步。
- **生成的文件不要提交到 git。** 它们都写在 `.gitignore` 里，只有你自己写的脚本进版本管理。注意 `git clean -fdx` 会把被忽略的文件也删掉，模拟结果会跟着一起没了。
- **iCloud**：如果项目放在 iCloud 同步的目录里（比如"文稿"），克隆时把目录名取成以 `.nosync` 结尾，例如 `peano-minimal.nosync`。这样 iCloud 不会同步它，重新生成几百个文件时也就不会出现 “xxx 2” 这样的冲突副本。
