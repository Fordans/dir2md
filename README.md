# dir2md

一个强大的Python命令行工具，用于将目录结构转换为美观的Markdown格式树状结构文件。

## 功能特性

-  **目录树生成**: 将目录结构转换为清晰的Markdown树状格式
-  **智能过滤**: 默认忽略常见的无关目录（如 `.git`、`node_modules` 等）
-  **统计信息**: 自动生成目录数、文件数、总大小等统计信息
-  **GUI可视化**: 支持生成图形化界面查看目录结构
-  **高度可定制**: 丰富的命令行参数满足各种需求

## 安装

### 系统要求

- Python 3.6 或更高版本

### 安装步骤

1. 将 `dir2md.py` 下载到本地
2. （可选）将脚本添加到系统PATH，或创建别名以便全局使用

```bash
# Windows (PowerShell)
# 将脚本复制到系统PATH目录，或创建别名
New-Alias dir2md python C:\path\to\dir2md.py

# Linux/macOS
chmod +x dir2md.py
sudo cp dir2md.py /usr/local/bin/dir2md
```

## 使用方法

### 基本用法

```bash
# 扫描当前目录，生成 structure.md
python dir2md.py .

# 扫描指定目录
python dir2md.py /path/to/directory

# 扫描指定目录并指定输出文件名
python dir2md.py ./project -n project-structure.md
```

### 命令行参数

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `--all` | `-a` | 包括所有目录和文件（不忽略默认目录） | 否 |
| `--name` | `-n` | 指定输出文件名 | `structure.md` |
| `--outputdir` | `-opd` | 指定输出目录 | 当前目录 |
| `--onlydir` | `-od` | 只包含目录，不包含文件 | 否 |
| `--depth` | `-d` | 指定最大目录深度 | 无限制 |
| `--size` | `-s` | 在输出中包含文件大小信息 | 否 |
| `--graph` | - | 生成GUI可视化脚本 | 否 |

### 使用示例

#### 1. 生成基本的目录结构

```bash
python dir2md.py ./my-project
```

这将生成 `structure.md` 文件，包含项目的基本目录结构。

#### 2. 包含文件大小信息

```bash
python dir2md.py ./my-project -s
```

生成的结构文件将包含每个文件的大小信息。

#### 3. 限制目录深度

```bash
python dir2md.py ./my-project -d 3
```

只显示3层深度的目录结构。

#### 4. 只显示目录（不包含文件）

```bash
python dir2md.py ./my-project -od
```

生成的Markdown文件将只包含目录，不包含文件。

#### 5. 包括所有目录（包括.git等）

```bash
python dir2md.py ./my-project -a
```

默认情况下，工具会忽略 `.git`、`node_modules` 等目录。使用 `-a` 参数可以包括所有这些目录。

#### 6. 指定输出目录和文件名

```bash
python dir2md.py ./my-project -n project.md -opd ./docs
```

将生成的Markdown文件保存到 `./docs/project.md`。

#### 7. 生成GUI可视化工具

```bash
python dir2md.py ./my-project -graph
```

这将生成两个文件：
- `structure.md`: Markdown格式的目录结构
- `structure.py`: GUI可视化脚本

运行GUI脚本：
```bash
python structure.py
```

GUI功能特点：
-  **可折叠/展开**: 点击目录节点可以折叠或展开子目录
-  **全部展开/折叠按钮**: 工具栏提供快速展开/折叠所有节点的功能
-  **文件大小显示**: 如果使用了`-s`参数，GUI会显示文件大小
-  **颜色区分**: 目录和文件使用不同颜色显示，便于区分

#### 8. 组合使用多个参数

```bash
python dir2md.py ./my-project -s -d 4 -n deep-structure.md -graph
```

生成包含文件大小、深度限制为4层的目录结构，并同时生成GUI脚本。

## 输出格式

生成的Markdown文件包含以下部分：

1. **标题**: 目录结构的标题
2. **目录树**: 使用ASCII字符绘制的树状结构
   - 📁 表示目录
   - 📄 表示文件
3. **统计信息**: 
   - 目录数量
   - 文件数量（如果包含文件）
   - 总大小（如果使用 `-s` 参数）

### 示例输出

```markdown
# 目录结构: my-project

```
📁 my-project/
├── 📁 src/
│   ├── 📄 main.py (1.23 KB)
│   └── 📄 utils.py (2.45 KB)
├── 📁 tests/
│   └── 📄 test_main.py (0.89 KB)
└── 📄 README.md (3.12 KB)
```

## 统计信息

- **目录数**: 2
- **文件数**: 4
- **总大小**: 7.69 KB
```

## 默认忽略的目录

以下目录和文件默认会被忽略（可使用 `-a` 参数包含）：

- 版本控制目录: `.git`, `.svn`, `.hg`, `.bzr`
- Python缓存: `__pycache__`, `.pytest_cache`, `.mypy_cache`
- Node.js相关: `node_modules`, `.next`, `.nuxt`
- 缓存目录: `cache`, `.cache`, `tmp`, `temp`
- IDE配置: `.idea`, `.vscode`, `.vs`
- 构建输出: `dist`, `build`, `.build`
- 虚拟环境: `.venv`, `venv`, `env`, `.env`
- 系统文件: `.DS_Store`, `Thumbs.db`

## GUI可视化

使用 `-graph` 参数可以生成一个GUI应用程序，用于可视化查看目录结构。

### 功能特点

- **树形结构展示**: 使用Treeview控件展示目录树，清晰直观
- **折叠/展开功能**: 
  - 点击目录节点前的箭头可以展开/折叠该目录
  - 使用工具栏的"全部展开"按钮可以展开所有节点
  - 使用工具栏的"全部折叠"按钮可以折叠所有节点
- **文件大小显示**: 如果使用了`-s`参数，会在右侧列显示文件大小
- **颜色区分**: 目录和文件使用不同颜色显示（目录为青色，文件为橙色）
- **滚动支持**: 支持水平和垂直滚动，方便浏览大型目录结构

### 运行GUI

```bash
# 生成GUI脚本
python dir2md.py ./my-project -graph

# 运行GUI
python structure.py
```

### 使用GUI

1. **展开/折叠单个目录**: 点击目录节点前的展开/折叠图标
2. **展开所有目录**: 点击工具栏的"全部展开"按钮
3. **折叠所有目录**: 点击工具栏的"全部折叠"按钮
4. **查看文件大小**: 如果生成时使用了`-s`参数，文件大小会显示在右侧列中

## 常见问题

### Q: 如何包含隐藏文件？

A: 使用 `-a` 参数可以包含所有文件，包括以 `.` 开头的隐藏文件。

### Q: 可以忽略特定目录吗？

A: 当前版本使用默认的忽略列表。如果需要更灵活的过滤，可以修改脚本中的 `DEFAULT_IGNORE_DIRS` 集合。

### Q: GUI脚本需要什么依赖？

A: GUI脚本使用Python标准库的 `tkinter`，通常Python安装已包含。如果没有，请安装相应的Python-tk包。

### Q: 支持Windows吗？

A: 是的，完全支持Windows、Linux和macOS。

## 许可证

本项目采用 MIT 许可证。

## 贡献

欢迎提交Issue和Pull Request！

## 更新日志

### v1.0.0
- 初始版本
- 支持基本的目录结构生成
- 支持所有命令行参数
- 支持GUI可视化功能

