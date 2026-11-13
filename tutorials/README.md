# Peano 学习图册 / Peano Notebook

学习 Peano / ExaHyPE 2 / ExaGRyPE 时画的流程图和写的教程，中英双语。双击 `index.html` 就能在浏览器里看；右上角切换语言。

这个目录是 peano-minimal 仓库的一部分（`peano-minimal/tutorials/`），也通过 GitHub Pages 在线发布。Archify 的记录文件（`diagrams/*.json`、`diagrams/receipts/`）和 claude.ai 副本 `_artifact/` 里有本机路径，只留在本地，不进 git。

## 目录

```
site-data.json            首页列出哪些流程图和教程（标题、简介、日期，中英各一份）
content/                  教程 Markdown，每种语言一个文件：<slug>.zh-CN.md、<slug>.en.md
diagrams/src/             Archify 源文件：<id>.zh-CN.json、<id>.en.json
diagrams/<id>.<lang>.html Archify 生成的交互流程图（旁边的 *.delivery.json 是 Archify 的交付记录，不要挪走）
diagrams/static/          流程图的静态截图（只给 claude.ai 上的副本用）
diagrams/receipts/        Archify 的检查记录
content/img/              教程里用到的图片：lego/ 是原创示意图（make_images.py 生成，中英各一份），
                          photos/ 是 Wikimedia Commons 上自由授权的照片，来源和授权见 photos/CREDITS.md
site.css, i18n.js         样式和语言切换
vendor/marked.min.js      Markdown 渲染器（marked 12.0.2）
build.py                  生成下面这些文件

index.html, view.html, tutorial-*.html, site-data.js   生成的本地网站，不要手改
_artifact/                                             生成的 claude.ai 副本，不要手改
```

## 改教程

编辑 `content/` 里的 `.md`，然后：

```bash
python3 build.py
```

## 加一张流程图

1. 在 `diagrams/src/` 写 `<id>.zh-CN.json` 和 `<id>.en.json`（`meta.locale` 分别是 `zh-CN`、`en`，`meta.output` 是 `diagrams/<id>.<lang>.html`）。
2. 在本目录用 Archify 生成，`<type>` 是 `workflow`、`tree` 等：

   ```bash
   node ~/.claude/skills/archify/bin/archify.mjs finalize <type> diagrams/src/<id>.zh-CN.json diagrams/<id>.zh-CN.html --quality showcase --json
   node ~/.claude/skills/archify/bin/archify.mjs finalize <type> diagrams/src/<id>.en.json    diagrams/<id>.en.html    --quality showcase --json
   ```

3. 生成静态截图（claude.ai 副本用）：

   ```bash
   node ~/.claude/skills/archify/bin/archify.mjs visual-check diagrams/<id>.<lang>.html --summary --out-dir /tmp/vc
   cp /tmp/vc/*2048x1320.light.png diagrams/static/<id>.<lang>.png
   ```

4. 在 `site-data.json` 的 `diagrams` 里加一项，然后 `python3 build.py`。

改已有的图时，`finalize` 要加一个新的 `--out-dir diagrams/receipts/<新名字>`，因为旧的检查记录绑定在原来的 HTML 上。

## 加一篇教程

1. 写 `content/<slug>.zh-CN.md` 和 `content/<slug>.en.md`。
2. 在 `site-data.json` 的 `tutorials` 里加一项，然后 `python3 build.py`。

## 放到 GitHub Pages

把整个目录推到一个 GitHub 仓库，在 Settings → Pages 里选择这个分支的根目录即可。`_artifact/`、`diagrams/receipts/` 可以不上传。
