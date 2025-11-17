import tkinter as tk
from tkinter import ttk, messagebox


class ScoreApp:
    def __init__(self, root):
        self.root = root
        self.root.title("班级分数统计")
        self.root.geometry("500x380")

        # 存储学生数据：[{name: '张三', score: 95}, ...]
        self.students = []

        # ===== 上方输入区域 =====
        frame_top = tk.Frame(root, padx=10, pady=10)
        frame_top.pack(fill=tk.X)

        tk.Label(frame_top, text="姓名：").grid(row=0, column=0, sticky="w")
        self.name_var = tk.StringVar()
        self.entry_name = tk.Entry(frame_top, textvariable=self.name_var, width=15)
        self.entry_name.grid(row=0, column=1, padx=5)

        tk.Label(frame_top, text="分数：").grid(row=0, column=2, sticky="w")
        self.score_var = tk.StringVar()
        self.entry_score = tk.Entry(frame_top, textvariable=self.score_var, width=10)
        self.entry_score.grid(row=0, column=3, padx=5)

        # 回车键也可以添加
        self.entry_score.bind("<Return>", lambda event: self.add_student())

        # ===== 按钮区域 =====
        frame_btn = tk.Frame(root, padx=10, pady=5)
        frame_btn.pack(fill=tk.X)

        btn_add = tk.Button(frame_btn, text="添加（自动降序）", command=self.add_student)
        btn_add.pack(side=tk.LEFT, padx=5)

        btn_delete = tk.Button(frame_btn, text="删除选中成绩", command=self.delete_selected)
        btn_delete.pack(side=tk.LEFT, padx=5)

        btn_clear = tk.Button(frame_btn, text="清空列表", command=self.clear_students)
        btn_clear.pack(side=tk.LEFT, padx=5)

        # ===== 表格显示区域 =====
        frame_table = tk.Frame(root, padx=10, pady=10)
        frame_table.pack(fill=tk.BOTH, expand=True)

        columns = ("index", "name", "score")
        self.tree = ttk.Treeview(frame_table, columns=columns, show="headings", height=10)
        self.tree.heading("index", text="序号")
        self.tree.heading("name", text="姓名")
        self.tree.heading("score", text="分数")

        self.tree.column("index", width=60, anchor="center")
        self.tree.column("name", width=180, anchor="center")
        self.tree.column("score", width=80, anchor="center")

        # 允许多选：按 Ctrl/Shift 可以选中多行
        self.tree["selectmode"] = "extended"

        self.tree.pack(fill=tk.BOTH, expand=True)

        # 底部提示
        label_hint = tk.Label(
            root,
            text="说明：输入姓名和分数后点击“添加（自动降序）”；\n"
                 "用鼠标选中要删除的行，点击“删除选中成绩”。",
            fg="#555"
        )
        label_hint.pack(pady=3)

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

        if score < 0 or score > 100:
            messagebox.showwarning("提示", "分数应在 0~100 之间！")
            return

        # 添加到列表
        self.students.append({"name": name, "score": score})

        # ★ 自动按分数降序排序
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

        # 从 students 中删除对应数据
        for item in selected_items:
            values = self.tree.item(item, "values")
            # values: (序号, 姓名, 分数)
            _, name, score_str = values
            score = float(score_str)

            # 删除第一条匹配到的记录（考虑可能重名且同分）
            for i, stu in enumerate(self.students):
                if stu["name"] == name and stu["score"] == score:
                    del self.students[i]
                    break

        # 删除后保持降序（原则上顺序仍然是降序，但稳妥起见再排一次）
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

        # 重新插入
        for idx, stu in enumerate(self.students, start=1):
            self.tree.insert("", tk.END, values=(idx, stu["name"], stu["score"]))


if __name__ == "__main__":
    root = tk.Tk()
    app = ScoreApp(root)
    root.mainloop()
