import tkinter as tk
from tkinter import ttk, messagebox


class ScoreApp:
    def __init__(self, root):
        self.root = root
        self.root.title("班级分数统计")
        self.root.geometry("540x420")
        self.root.resizable(False, False)  # 固定窗口大小

        # ========== 全局样式设置 ==========
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        # 颜色配置
        bg_main = "#f5f7fb"
        bg_card = "#ffffff"
        accent = "#4f46e5"

        self.root.configure(bg=bg_main)

        # Frame / Label / Button 样式
        style.configure("Card.TFrame", background=bg_card)
        style.configure("Main.TFrame", background=bg_main)

        style.configure(
            "Title.TLabel",
            background=bg_card,
            foreground="#111827",
            font=("Microsoft YaHei", 14, "bold")
        )
        style.configure(
            "TLabel",
            background=bg_card,
            foreground="#4b5563",
            font=("Microsoft YaHei", 10)
        )

        style.configure(
            "Accent.TButton",
            font=("Microsoft YaHei", 10),
            padding=6
        )
        style.map(
            "Accent.TButton",
            background=[("!disabled", accent), ("pressed", "#4338ca"), ("active", "#4338ca")],
            foreground=[("!disabled", "#ffffff")]
        )

        style.configure(
            "Secondary.TButton",
            font=("Microsoft YaHei", 10),
            padding=6,
            background="#e5e7eb",
            foreground="#374151"
        )
        style.map(
            "Secondary.TButton",
            background=[("!disabled", "#e5e7eb"), ("pressed", "#d1d5db"), ("active", "#d1d5db")]
        )

        # Treeview 样式
        style.configure(
            "Custom.Treeview",
            background="#ffffff",
            fieldbackground="#ffffff",
            foreground="#111827",
            bordercolor="#e5e7eb",
            rowheight=24
        )
        style.configure(
            "Custom.Treeview.Heading",
            background="#f9fafb",
            foreground="#374151",
            font=("Microsoft YaHei", 10, "bold")
        )

        # ========== 外层主框架 ==========
        main_frame = ttk.Frame(self.root, style="Main.TFrame", padding=16)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 卡片式容器
        card = ttk.Frame(main_frame, style="Card.TFrame", padding=(18, 16, 18, 16))
        card.pack(fill=tk.BOTH, expand=True)

        # 标题
        title_label = ttk.Label(card, text="班级分数统计", style="Title.TLabel")
        title_label.pack(anchor="center", pady=(0, 10))

        # ===== 上方输入区域=====
        frame_top = ttk.Frame(card, style="Card.TFrame")
        frame_top.pack(pady=(6, 4))  

        inner_top = ttk.Frame(frame_top, style="Card.TFrame")
        inner_top.pack(anchor="center")  # 整块输入区域居中

        ttk.Label(inner_top, text="姓名：").grid(row=0, column=0, sticky="", padx=(0, 4))
        self.name_var = tk.StringVar()
        self.entry_name = ttk.Entry(inner_top, textvariable=self.name_var, width=18)
        self.entry_name.grid(row=0, column=1, padx=(0, 10))

        ttk.Label(inner_top, text="分数：").grid(row=0, column=2, sticky="", padx=(0, 4))
        self.score_var = tk.StringVar()
        self.entry_score = ttk.Entry(inner_top, textvariable=self.score_var, width=10)
        self.entry_score.grid(row=0, column=3)

        # 回车键也可以添加
        self.entry_score.bind("<Return>", lambda event: self.add_student())

        # ===== 按钮区域 =====
        frame_btn = ttk.Frame(card, style="Card.TFrame")
        frame_btn.pack(pady=(8, 4))  # 不再 fill=X

        btn_add = ttk.Button(frame_btn, text="添加（自动降序）", style="Accent.TButton", command=self.add_student)
        btn_add.pack(side=tk.LEFT, padx=(0, 8))

        btn_delete = ttk.Button(frame_btn, text="删除选中成绩", style="Secondary.TButton", command=self.delete_selected)
        btn_delete.pack(side=tk.LEFT, padx=(0, 8))

        btn_clear = ttk.Button(frame_btn, text="清空列表", style="Secondary.TButton", command=self.clear_students)
        btn_clear.pack(side=tk.LEFT)

        # ===== 表格显示区域 =====
        frame_table = ttk.Frame(card, style="Card.TFrame")
        frame_table.pack(fill=tk.BOTH, expand=True, pady=(8, 4))

        columns = ("index", "name", "score")
        self.tree = ttk.Treeview(
            frame_table,
            columns=columns,
            show="headings",
            height=9,
            style="Custom.Treeview"
        )

        self.tree.heading("index", text="序号")
        self.tree.heading("name", text="姓名")
        self.tree.heading("score", text="分数")

        self.tree.column("index", width=60, anchor="center")
        self.tree.column("name", width=210, anchor="center")
        self.tree.column("score", width=80, anchor="center")

        # 允许多选
        self.tree["selectmode"] = "extended"

        # 加滚动条
        scroll_y = ttk.Scrollbar(frame_table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")

        frame_table.rowconfigure(0, weight=1)
        frame_table.columnconfigure(0, weight=1)

        # 奇偶行不同底色
        self.tree.tag_configure("oddrow", background="#ffffff")
        self.tree.tag_configure("evenrow", background="#f9fafb")

        # 底部提示
        hint = ttk.Label(
            card,
            text="说明：输入姓名和分数后点击“添加（自动降序）”；用鼠标选中要删除的行点击“删除选中成绩”。",
            style="TLabel",
            foreground="#6b7280",
            wraplength=480,
            justify="center"   # 文本多行居中
        )
        hint.pack(anchor="center", pady=(6, 0))

        # 存储学生数据：[{name: '张三', score: 95}, ...]
        self.students = []

        # 默认让光标在姓名输入框
        self.entry_name.focus()

    def add_student(self):
        """添加一个学生到列表，并自动按分数降序排序"""
        name = self.name_var.get().strip()
        score_str = self.score_var.get().strip()

        if not name:
            messagebox.showwarning("提示", "姓名不能为空！")
            return
        if not score_str:
            messagebox.showwarning("提示", "分数不能为空！")
            return

        # 分数合法性检查
        try:
            score = float(score_str)
        except ValueError:
            messagebox.showwarning("提示", "分数必须是数字！")
            return

        if score < 0 :
            messagebox.showwarning("提示", "分数应为正数！")
            return

        # 添加到列表
        self.students.append({"name": name, "score": score})

        # 自动按分数降序排序
        self.students.sort(key=lambda x: x["score"], reverse=True)

        # 刷新表格显示
        self.refresh_table()

        # 清空输入框，光标回到姓名
        self.name_var.set("")
        self.score_var.set("")
        self.entry_name.focus()

    def delete_selected(self):
        """删除选中的成绩记录"""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showinfo("提示", "请先在表格中选中要删除的记录。")
            return

        if not messagebox.askyesno("确认", "确定要删除选中的记录吗？"):
            return

        for item in selected_items:
            values = self.tree.item(item, "values")
            # values: (序号, 姓名, 分数)
            _, name, score_str = values
            score = float(score_str)

            # 删除第一条匹配到的记录
            for i, stu in enumerate(self.students):
                if stu["name"] == name and stu["score"] == score:
                    del self.students[i]
                    break

        # 删除后保持降序
        self.students.sort(key=lambda x: x["score"], reverse=True)
        self.refresh_table()

    def clear_students(self):
        """清空所有学生数据"""
        if messagebox.askyesno("确认", "确定要清空所有记录吗？"):
            self.students.clear()
            self.refresh_table()

    def refresh_table(self):
        """根据 self.students 刷新表格内容"""
        # 清空表格
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 重新插入，顺便加上奇偶行底色
        for idx, stu in enumerate(self.students, start=1):
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.tree.insert("", tk.END, values=(idx, stu["name"], stu["score"]), tags=(tag,))


if __name__ == "__main__":
    root = tk.Tk()
    app = ScoreApp(root)
    root.mainloop()
