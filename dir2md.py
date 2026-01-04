#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
dir2md - 目录结构转Markdown工具
将指定目录的结构转换为Markdown格式的树状结构文件
"""

import os
import sys
import argparse
from pathlib import Path
# 默认忽略的目录列表
DEFAULT_IGNORE_DIRS = {
    '.git', '.svn', '.hg', '.bzr',  # 版本控制目录
    '__pycache__', '.pytest_cache', '.mypy_cache',  # Python缓存
    'node_modules', '.next', '.nuxt',  # Node.js相关
    'cache', '.cache', 'tmp', 'temp',  # 缓存和临时目录
    '.idea', '.vscode', '.vs',  # IDE配置
    'dist', 'build', '.build',  # 构建输出
    '.venv', 'venv', 'env', '.env',  # 虚拟环境
    '.DS_Store', 'Thumbs.db',  # 系统文件
}


class TreeNode:
    """树节点"""
    def __init__(self, name, is_dir, size=0, path=None):
        self.name = name
        self.is_dir = is_dir
        self.size = size
        self.path = path
        self.children = []


class DirectoryTree:
    """目录树生成器"""
    
    def __init__(self, root_path, ignore_dirs=None, include_all=False, 
                 only_dirs=False, max_depth=None, include_size=False):
        self.root_path = Path(root_path).resolve()
        self.ignore_dirs = ignore_dirs or set()
        self.include_all = include_all
        self.only_dirs = only_dirs
        self.max_depth = max_depth
        self.include_size = include_size
        self.dir_count = 0
        self.file_count = 0
        self.total_size = 0
        
    def should_ignore(self, name):
        """判断是否应该忽略该目录或文件"""
        if self.include_all:
            return False
        return name in self.ignore_dirs or name.startswith('.')
    
    def format_size(self, size):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"
    
    def build_tree(self, path, depth=0):
        """构建目录树结构"""
        if self.max_depth is not None and depth > self.max_depth:
            return None
        
        node = TreeNode(path.name, path.is_dir(), 0, path)
        
        if path.is_dir():
            self.dir_count += 1
            try:
                items = []
                for item in sorted(path.iterdir()):
                    if self.should_ignore(item.name):
                        continue
                    
                    child_node = self.build_tree(item, depth + 1)
                    if child_node:
                        items.append(child_node)
                
                node.children = items
            except (PermissionError, OSError):
                pass
        else:
            if not self.only_dirs:
                self.file_count += 1
                try:
                    node.size = path.stat().st_size
                    self.total_size += node.size
                except (OSError, PermissionError):
                    node.size = 0
            else:
                return None
        
        return node
    
    def generate_tree(self):
        """生成目录树"""
        self.dir_count = 0
        self.file_count = 0
        self.total_size = 0
        return self.build_tree(self.root_path)


class MarkdownGenerator:
    """Markdown生成器"""
    
    def __init__(self, tree_generator, root_name=None):
        self.tree_generator = tree_generator
        self.root_name = root_name or tree_generator.root_path.name
        
    def tree_to_lines(self, node, prefix="", is_last=True):
        """递归生成树形结构的行"""
        lines = []
        
        # 当前节点
        if node.name != self.tree_generator.root_path.name:
            connector = "└── " if is_last else "├── "
            marker = "📁" if node.is_dir else "📄"
            
            size_str = ""
            if self.tree_generator.include_size and not node.is_dir:
                size_str = f" ({self.tree_generator.format_size(node.size)})"
            
            lines.append(f"{prefix}{connector}{marker} {node.name}{size_str}\n")
        
        # 子节点
        if node.is_dir and node.children:
            children = node.children
            for i, child in enumerate(children):
                is_last_child = (i == len(children) - 1)
                if node.name == self.tree_generator.root_path.name:
                    # 根节点
                    child_prefix = prefix
                else:
                    child_prefix = prefix + ("    " if is_last else "│   ")
                
                lines.extend(self.tree_to_lines(child, child_prefix, is_last_child))
        
        return lines
    
    def generate_markdown(self):
        """生成Markdown内容"""
        root_node = self.tree_generator.generate_tree()
        
        if root_node is None:
            return "# 目录结构\n\n目录为空或无法访问。\n"
        
        lines = []
        lines.append(f"# 目录结构: {self.root_name}\n\n")
        lines.append("```\n")
        
        # 添加根目录
        root_marker = "📁" if root_node.is_dir else "📄"
        lines.append(f"{root_marker} {self.root_name}/\n")
        
        # 生成树形结构
        if root_node.children:
            for i, child in enumerate(root_node.children):
                is_last = (i == len(root_node.children) - 1)
                lines.extend(self.tree_to_lines(child, "", is_last))
        
        lines.append("```\n")
        
        # 添加统计信息
        lines.append("\n## 统计信息\n\n")
        lines.append(f"- **目录数**: {self.tree_generator.dir_count}\n")
        if not self.tree_generator.only_dirs:
            lines.append(f"- **文件数**: {self.tree_generator.file_count}\n")
            if self.tree_generator.include_size:
                lines.append(f"- **总大小**: {self.tree_generator.format_size(self.tree_generator.total_size)}\n")
        
        return "".join(lines)


def generate_gui_script(md_filename, output_dir):
    """生成GUI展示脚本"""
    script_name = md_filename.replace('.md', '.py')
    script_path = Path(output_dir) / script_name
    
    gui_code = f'''#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
目录树图形化展示工具
自动生成用于可视化目录结构的GUI程序
支持折叠/展开功能
"""

import tkinter as tk
from tkinter import ttk
from pathlib import Path
import re


class TreeNode:
    """树节点数据结构"""
    def __init__(self, name, is_dir, size=""):
        self.name = name
        self.is_dir = is_dir
        self.size = size
        self.children = []
        self.parent = None


class DirectoryTreeViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("目录结构查看器 - {script_name}")
        self.root.geometry("900x700")
        
        # 创建主框架
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # 标题和工具栏框架
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        header_frame.columnconfigure(0, weight=1)
        
        # 标题标签
        title_label = ttk.Label(header_frame, text="目录结构树", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        # 工具栏按钮
        toolbar_frame = ttk.Frame(header_frame)
        toolbar_frame.grid(row=0, column=1, sticky=tk.E)
        
        expand_btn = ttk.Button(toolbar_frame, text="全部展开", command=self.expand_all)
        expand_btn.pack(side=tk.LEFT, padx=2)
        
        collapse_btn = ttk.Button(toolbar_frame, text="全部折叠", command=self.collapse_all)
        collapse_btn.pack(side=tk.LEFT, padx=2)
        
        # 创建Treeview
        tree_frame = ttk.Frame(main_frame)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # 创建滚动条
        scrollbar_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        scrollbar_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        scrollbar_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # 创建Treeview
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("size",),
            show="tree headings",
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set
        )
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)
        
        # 配置列
        self.tree.column("#0", width=400, minwidth=200)
        self.tree.column("size", width=100, minwidth=80)
        self.tree.heading("#0", text="名称", anchor=tk.W)
        self.tree.heading("size", text="大小", anchor=tk.W)
        
        # 配置标签样式
        self.tree.tag_configure("directory", foreground="#4EC9B0")
        self.tree.tag_configure("file", foreground="#CE9178")
        
        # 存储树节点映射（tree_item_id -> TreeNode）
        self.item_to_node = {{}}
        
        # 加载目录结构
        self.load_directory_tree()
        
    def parse_tree_lines(self, lines):
        """解析树形结构的文本行，构建树结构"""
        if not lines:
            return None
        
        # 解析根节点（第一行）
        root_line = lines[0].strip()
        root_match = re.match(r'📁\\s+(.+?)/?$', root_line)
        if not root_match:
            return None
        
        root_name = root_match.group(1)
        root_node = TreeNode(root_name, True, "")
        self.item_to_node["root"] = root_node
        
        # 解析子节点
        # stack存储 (node, indent_level)
        stack = [(root_node, -1)]  # 根节点的层级为-1
        
        for line in lines[1:]:
            if not line.strip():
                continue
            
            # 计算缩进（原始行的前导空格和│字符）
            # 计算实际内容开始的位置
            # 匹配模式: 可能的前导空格 + (│ + 3个空格)* + (├──或└──) + 标记 + 名称 + 大小
            stripped = line.lstrip()
            if not stripped:
                continue
            
            # 计算前导字符数（包括│字符）
            leading_chars = len(line) - len(stripped)
            
            # 解析内容部分
            # 匹配: (├──或└──) + (标记📁或📄) + 名称 + (可选的大小)
            content_match = re.match(r'([├└]──\\s+)?([📁📄])\\s+(.+?)(?:\\s+\\(([^)]+)\\))?$', stripped)
            if not content_match:
                continue
            
            connector, marker, name, size = content_match.groups()
            is_dir = marker == "📁"
            size = size or ""
            
            # 计算层级：每4个前导字符为一级
            # 但需要考虑到│字符也占位置
            # 实际上，树形结构中：4个字符（├── + 空格）为第一层，8个字符（│   + ├── + 空格）为第二层
            level = leading_chars // 4
            
            # 创建节点
            node = TreeNode(name, is_dir, size)
            
            # 找到正确的父节点：栈中最后一个层级小于当前层级的节点
            while len(stack) > 1 and stack[-1][1] >= level:
                stack.pop()
            
            if stack:
                parent_node, _ = stack[-1]
                parent_node.children.append(node)
                node.parent = parent_node
            
            # 如果是目录，加入栈中
            if is_dir:
                stack.append((node, level))
        
        return root_node
    
    def build_treeview(self, node, parent=""):
        """将TreeNode结构转换为Treeview项目"""
        if node.name == "":
            return
        
        # 确定图标和标签
        text = node.name
        if node.is_dir:
            tags = ("directory",)
        else:
            tags = ("file",)
        
        # 插入到Treeview
        item_id = self.tree.insert(
            parent,
            tk.END,
            text=text,
            values=(node.size,),
            tags=tags
        )
        
        # 存储映射
        self.item_to_node[item_id] = node
        
        # 递归插入子节点
        for child in node.children:
            self.build_treeview(child, item_id)
    
    def load_directory_tree(self):
        """加载目录结构"""
        md_file = Path(__file__).parent / "{md_filename}"
        
        if not md_file.exists():
            error_label = ttk.Label(
                self.tree,
                text=f"错误: 找不到文件 {{md_file}}",
                foreground="red"
            )
            error_label.pack()
            return
        
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取代码块中的内容
            pattern = r'```\\n(.*?)```'
            match = re.search(pattern, content, re.DOTALL)
            
            if match:
                tree_content = match.group(1)
                lines = tree_content.strip().split("\\n")
                
                # 解析树结构
                root_node = self.parse_tree_lines(lines)
                
                if root_node:
                    # 构建Treeview（只显示根节点的子节点，不显示根节点本身）
                    for child in root_node.children:
                        self.build_treeview(child)
                    # 默认展开第一层
                    for child_id in self.tree.get_children():
                        self.tree.item(child_id, open=True)
            else:
                error_label = ttk.Label(
                    self.tree,
                    text="错误: 无法解析目录结构",
                    foreground="red"
                )
                error_label.pack()
                
        except Exception as e:
            error_label = ttk.Label(
                self.tree,
                text=f"错误: 无法读取文件 - {{str(e)}}",
                foreground="red"
            )
            error_label.pack()
    
    def expand_all(self):
        """展开所有节点"""
        def expand_children(item):
            self.tree.item(item, open=True)
            for child in self.tree.get_children(item):
                expand_children(child)
        
        for child in self.tree.get_children():
            expand_children(child)
    
    def collapse_all(self):
        """折叠所有节点"""
        def collapse_children(item):
            self.tree.item(item, open=False)
            for child in self.tree.get_children(item):
                collapse_children(child)
        
        for child in self.tree.get_children():
            collapse_children(child)


def main():
    root = tk.Tk()
    app = DirectoryTreeViewer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
'''
    
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(gui_code)
    
    # 在Windows上设置可执行权限
    if os.name != 'nt':
        os.chmod(script_path, 0o755)
    
    return script_path


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='将目录结构转换为Markdown格式的树状结构文件',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  %(prog)s ./project                    # 生成当前目录的structure.md
  %(prog)s ./project -n project.md      # 指定输出文件名
  %(prog)s ./project -d 3               # 限制深度为3层
  %(prog)s ./project -s -graph          # 包含文件大小并生成GUI
  %(prog)s ./project -od -opd ./output  # 只包含目录，输出到指定目录
        '''
    )
    
    parser.add_argument('directory', nargs='?', default='.',
                       help='要扫描的目录路径（默认为当前目录）')
    parser.add_argument('-a', '--all', dest='include_all', action='store_true',
                       help='包括所有目录和文件（不忽略默认目录）')
    parser.add_argument('-n', '--name', dest='output_name', default='structure.md',
                       help='输出文件名（默认: structure.md）')
    parser.add_argument('-opd', '--outputdir', dest='output_dir', default='.',
                       help='输出目录（默认: 当前目录）')
    parser.add_argument('-od', '--onlydir', dest='only_dirs', action='store_true',
                       help='只包含目录，不包含文件')
    parser.add_argument('-d', '--depth', dest='max_depth', type=int, default=None,
                       help='最大目录深度（默认: 无限制）')
    parser.add_argument('-s', '--size', dest='include_size', action='store_true',
                       help='在输出中包含文件大小信息')
    parser.add_argument('-graph', dest='generate_gui', action='store_true',
                       help='生成GUI可视化脚本')
    
    args = parser.parse_args()
    
    # 验证输入目录
    input_dir = Path(args.directory)
    if not input_dir.exists():
        print(f"错误: 目录不存在: {input_dir}", file=sys.stderr)
        sys.exit(1)
    
    if not input_dir.is_dir():
        print(f"错误: 不是一个目录: {input_dir}", file=sys.stderr)
        sys.exit(1)
    
    # 准备输出目录
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建目录树生成器
    ignore_dirs = set() if args.include_all else DEFAULT_IGNORE_DIRS
    tree_generator = DirectoryTree(
        root_path=input_dir,
        ignore_dirs=ignore_dirs,
        include_all=args.include_all,
        only_dirs=args.only_dirs,
        max_depth=args.max_depth,
        include_size=args.include_size
    )
    
    # 生成Markdown
    md_generator = MarkdownGenerator(tree_generator)
    markdown_content = md_generator.generate_markdown()
    
    # 写入文件
    output_file = output_dir / args.output_name
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    try:
        print(f"✓ 成功生成: {output_file}")
    except UnicodeEncodeError:
        print(f"[OK] 成功生成: {output_file}")
    
    print(f"  - 目录数: {tree_generator.dir_count}")
    if not args.only_dirs:
        print(f"  - 文件数: {tree_generator.file_count}")
        if args.include_size:
            print(f"  - 总大小: {tree_generator.format_size(tree_generator.total_size)}")
    
    # 生成GUI脚本
    if args.generate_gui:
        gui_script = generate_gui_script(args.output_name, output_dir)
        try:
            print(f"✓ 成功生成GUI脚本: {gui_script}")
        except UnicodeEncodeError:
            print(f"[OK] 成功生成GUI脚本: {gui_script}")
        print(f"  运行命令: python {gui_script}")


if __name__ == '__main__':
    main()

