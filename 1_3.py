import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import tkinter.font as tkfont


class TextEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("简易文本编辑器")
        self.root.geometry("900x600")
        self.root.minsize(700, 400)

        # 当前打开文件路径（None 表示新建未保存）
        self.current_file = None

        # 默认字体设置
        self.font_family = "Consolas"
        self.font_size = 12

        # ====== 全局样式 ======
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        bg_main = "#f5f7fb"
        bg_card = "#ffffff"

        self.root.configure(bg=bg_main)
        style.configure("Main.TFrame", background=bg_main)
        style.configure("Card.TFrame", background=bg_card)

        # 放大菜单栏字体（“文件 / 编辑”标题）
        self.root.option_add('*Menu.Font', ('Microsoft YaHei', 13))

        # ====== 菜单栏 ======
        menubar = tk.Menu(self.root)

        # --- 文件菜单 ---
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="新建", command=self.new_file)
        file_menu.add_command(label="打开…", command=self.open_file)
        file_menu.add_command(label="保存", command=self.save_file)
        file_menu.add_command(label="另存为…", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        menubar.add_cascade(label="文件", menu=file_menu)

        # --- 编辑菜单 ---
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="撤销", command=self.undo_text)
        edit_menu.add_command(label="重做", command=self.redo_text)
        edit_menu.add_separator()
        edit_menu.add_command(label="剪切", command=self.cut_text)
        edit_menu.add_command(label="复制", command=self.copy_text)
        edit_menu.add_command(label="粘贴", command=self.paste_text)
        edit_menu.add_separator()
        edit_menu.add_command(label="全选", command=self.select_all)
        menubar.add_cascade(label="编辑", menu=edit_menu)

        self.root.config(menu=menubar)

        # ====== 外层框架 ======
        main_frame = ttk.Frame(self.root, style="Main.TFrame", padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        card = ttk.Frame(main_frame, style="Card.TFrame", padding=(8, 6))
        card.pack(fill=tk.BOTH, expand=True)

        # ====== 字体工具栏 ======
        toolbar = ttk.Frame(card, style="Card.TFrame")
        toolbar.pack(fill=tk.X, pady=(0, 6))

        ttk.Label(toolbar, text="字体：", style="TLabel").pack(side=tk.LEFT, padx=(0, 4))

        # 常用字体列表
        common_fonts = ["Consolas", "微软雅黑", "宋体", "黑体",
                        "Times New Roman", "Arial"]

        self.font_family_var = tk.StringVar(value=self.font_family)
        self.font_family_box = ttk.Combobox(
            toolbar,
            textvariable=self.font_family_var,
            values=common_fonts,
            width=15,
            state="readonly"
        )
        self.font_family_box.pack(side=tk.LEFT)
        self.font_family_box.bind("<<ComboboxSelected>>", self.on_font_change)

        ttk.Label(toolbar, text="  大小：", style="TLabel").pack(side=tk.LEFT, padx=(10, 4))

        size_list = [str(s) for s in (8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24, 28, 32)]
        self.font_size_var = tk.StringVar(value=str(self.font_size))
        self.font_size_box = ttk.Combobox(
            toolbar,
            textvariable=self.font_size_var,
            values=size_list,
            width=4
        )
        self.font_size_box.pack(side=tk.LEFT)
        self.font_size_box.bind("<<ComboboxSelected>>", self.on_font_change)
        self.font_size_box.bind("<Return>", self.on_font_change)  # 手动输入数字回车也生效

        # ====== 文本编辑区 ======
        text_frame = ttk.Frame(card, style="Card.TFrame")
        text_frame.pack(fill=tk.BOTH, expand=True)

        self.text = tk.Text(
            text_frame,
            wrap="word",   # 始终自动换行
            undo=True,
            font=(self.font_family, self.font_size),
            relief="flat",
            padx=6,
            pady=4
        )
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scroll_y = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.text.yview)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.configure(yscrollcommand=scroll_y.set)

        # ====== 右键菜单（剪切/复制/粘贴/全选）======
        self.context_menu = tk.Menu(self.text, tearoff=0)
        self.context_menu.add_command(label="剪切", command=self.cut_text)
        self.context_menu.add_command(label="复制", command=self.copy_text)
        self.context_menu.add_command(label="粘贴", command=self.paste_text)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="全选", command=self.select_all)

        # 右键绑定
        self.text.bind("<Button-3>", self.show_context_menu)

        # ====== 状态栏：当前文件名 & 字数 ======
        status_frame = ttk.Frame(card, style="Card.TFrame")
        status_frame.pack(fill=tk.X, pady=(4, 0))

        self.status_label = ttk.Label(
            status_frame,
            text="当前文件：未保存新文件",
            font=("Microsoft YaHei", 9)
        )
        self.status_label.pack(side=tk.LEFT, anchor="w")

        self.count_label = ttk.Label(
            status_frame,
            text="字数：0",
            font=("Microsoft YaHei", 9)
        )
        self.count_label.pack(side=tk.RIGHT, anchor="e")

        # 文本变化时更新字数
        self.text.bind("<<Modified>>", self.on_text_modified)

        self.set_title_and_status()

    # ========= 字体相关 =========

    def on_font_change(self, event=None):
        """当字体或字号改变时，更新 Text 的字体"""
        family = self.font_family_var.get().strip() or self.font_family
        size_str = self.font_size_var.get().strip()
        try:
            size = int(size_str)
        except ValueError:
            size = self.font_size  # 输入乱七八糟就保持原样
            self.font_size_var.set(str(size))

        # 最小字号限制
        if size < 6:
            size = 6
            self.font_size_var.set("6")

        self.font_family = family
        self.font_size = size
        self.text.config(font=(self.font_family, self.font_size))

    # ========= 文件相关 =========

    def set_title_and_status(self):
        filename = self.current_file if self.current_file else "未保存新文件"
        self.root.title(f"简易文本编辑器 - {filename}")
        self.status_label.config(text=f"当前文件：{filename}")

    def new_file(self):
        if self.confirm_discard_changes():
            self.text.delete("1.0", tk.END)
            self.current_file = None
            self.set_title_and_status()
            self.update_char_count()

    def open_file(self):
        if not self.confirm_discard_changes():
            return

        file_path = filedialog.askopenfilename(
            title="打开文本文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            messagebox.showerror("错误", f"无法打开文件：{e}")
            return

        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, content)
        self.current_file = file_path
        self.set_title_and_status()
        self.update_char_count()
        self.text.edit_modified(False)

    def save_file(self):
        if self.current_file is None:
            self.save_file_as()
        else:
            self._write_to_file(self.current_file)

    def save_file_as(self):
        file_path = filedialog.asksaveasfilename(
            title="另存为",
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if not file_path:
            return
        self._write_to_file(file_path)
        self.current_file = file_path
        self.set_title_and_status()

    def _write_to_file(self, file_path):
        content = self.text.get("1.0", tk.END)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            messagebox.showinfo("保存成功", f"文件已保存到：\n{file_path}")
            self.text.edit_modified(False)
        except Exception as e:
            messagebox.showerror("错误", f"保存失败：{e}")

    def confirm_discard_changes(self):
        """如果内容被修改过，提示是否放弃修改"""
        if self.text.edit_modified():
            result = messagebox.askyesnocancel("提示", "当前文本有未保存的更改，是否保存？")
            if result is None:      # 取消
                return False
            if result:              # 是 -> 保存
                self.save_file()
        return True

    # ========= 编辑功能 =========

    def undo_text(self):
        try:
            self.text.edit_undo()
        except tk.TclError:
            pass

    def redo_text(self):
        try:
            self.text.edit_redo()
        except tk.TclError:
            pass

    def cut_text(self):
        self.text.event_generate("<<Cut>>")

    def copy_text(self):
        self.text.event_generate("<<Copy>>")

    def paste_text(self):
        self.text.event_generate("<<Paste>>")

    def select_all(self):
        self.text.tag_add("sel", "1.0", "end-1c")
        self.text.mark_set("insert", "1.0")
        self.text.see("insert")

    # ========= 右键菜单 =========

    def show_context_menu(self, event):
        """在右键位置弹出菜单"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    # ========= 状态栏 & 字数 =========

    def update_char_count(self):
        text = self.text.get("1.0", tk.END)
        count = len(text.rstrip("\n"))
        self.count_label.config(text=f"字数：{count}")

    def on_text_modified(self, event=None):
        if self.text.edit_modified():
            self.update_char_count()
            self.text.edit_modified(False)


if __name__ == "__main__":
    root = tk.Tk()
    app = TextEditorApp(root)
    root.mainloop()
