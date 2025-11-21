import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


class GradeSystemApp:
    def __init__(self, root):
        self.root = root
        self.root.title("学生成绩核算系统")
        self.root.geometry("1100x650")
        self.root.minsize(900, 550)

        # 所有记录
        self.all_records = []
        # 当前筛选后的记录
        self.current_records = []

        # ===== 样式设置 =====
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        bg_main = "#f3f4f6"
        bg_card = "#ffffff"
        accent = "#2563eb"
        text_main = "#111827"
        text_sub = "#4b5563"

        self.root.configure(bg=bg_main)
        style.configure("Main.TFrame", background=bg_main)
        style.configure("Card.TFrame", background=bg_card)

        style.configure(
            "Title.TLabel",
            background=bg_main,
            foreground=text_main,
            font=("Segoe UI", 18, "bold")
        )
        style.configure(
            "TLabel",
            background=bg_card,
            foreground=text_sub,
            font=("Segoe UI", 10)
        )

        style.configure(
            "Accent.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=6,
            relief="flat"
        )
        style.map(
            "Accent.TButton",
            background=[("!disabled", accent), ("active", "#1d4ed8")],
            foreground=[("!disabled", "#ffffff")]
        )
        style.configure(
            "Secondary.TButton",
            font=("Segoe UI", 10),
            padding=6,
            relief="flat"
        )
        style.map(
            "Secondary.TButton",
            background=[("!disabled", "#e5e7eb"), ("active", "#d1d5db")],
            foreground=[("!disabled", text_main)]
        )

        # ===== 外层框架 =====
        outer = ttk.Frame(self.root, style="Main.TFrame", padding=16)
        outer.pack(fill=tk.BOTH, expand=True)

        # 顶部标题
        ttk.Label(
            outer,
            text="学生成绩核算系统",
            style="Title.TLabel"
        ).pack(anchor="center", pady=(0, 10))

        # 白色卡片区域
        card = ttk.Frame(outer, style="Card.TFrame", padding=12)
        card.pack(fill=tk.BOTH, expand=True)

        # ===== 上方：文件与筛选区 =====
        top_frame = ttk.Frame(card, style="Card.TFrame")
        top_frame.pack(fill=tk.X, pady=(0, 6))

        btn_open = ttk.Button(
            top_frame,
            text="打开 JSON 成绩文件",
            style="Accent.TButton",
            command=self.open_json
        )
        btn_open.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(top_frame, text="班级：", style="TLabel").pack(side=tk.LEFT)
        self.class_var = tk.StringVar()
        self.class_combo = ttk.Combobox(
            top_frame, textvariable=self.class_var,
            state="readonly", width=15
        )
        self.class_combo.pack(side=tk.LEFT, padx=(4, 10))

        ttk.Label(top_frame, text="课程：", style="TLabel").pack(side=tk.LEFT)
        self.course_var = tk.StringVar()
        self.course_combo = ttk.Combobox(
            top_frame, textvariable=self.course_var,
            state="readonly", width=20
        )
        self.course_combo.pack(side=tk.LEFT, padx=(4, 10))

        ttk.Button(
            top_frame,
            text="计算成绩",
            style="Accent.TButton",
            command=self.calculate
        ).pack(side=tk.LEFT, padx=(10, 0))

        ttk.Button(
            top_frame,
            text="清空结果",
            style="Secondary.TButton",
            command=self.clear_results
        ).pack(side=tk.LEFT, padx=(6, 0))

        # ===== 中间：左表格 + 右统计 =====
        middle_frame = ttk.Frame(card, style="Card.TFrame")
        middle_frame.pack(fill=tk.BOTH, expand=True, pady=(6, 4))

        # --- 左边：学生成绩表 ---
        table_frame = ttk.Frame(middle_frame, style="Card.TFrame")
        table_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        columns = ("id", "name", "daily", "mid", "final", "total", "level")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=15
        )

        self.tree.heading("id", text="学号")
        self.tree.heading("name", text="姓名")
        self.tree.heading("daily", text="平时")
        self.tree.heading("mid", text="期中")
        self.tree.heading("final", text="期末")
        self.tree.heading("total", text="总评")
        self.tree.heading("level", text="等级")

        self.tree.column("id", width=100, anchor="center")
        self.tree.column("name", width=80, anchor="center")
        self.tree.column("daily", width=60, anchor="center")
        self.tree.column("mid", width=60, anchor="center")
        self.tree.column("final", width=60, anchor="center")
        self.tree.column("total", width=70, anchor="center")
        self.tree.column("level", width=60, anchor="center")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # --- 右边：统计信息 ---
        stat_frame = ttk.Frame(middle_frame, style="Card.TFrame")
        stat_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 0))
        stat_frame.configure(width=260)
        stat_frame.pack_propagate(False)

        ttk.Label(stat_frame, text="统计信息", style="TLabel").pack(anchor="w", pady=(0, 6))

        self.avg_label = ttk.Label(stat_frame, text="平均分：--", style="TLabel")
        self.avg_label.pack(anchor="w", pady=(0, 6))

        # 各等级统计
        self.stat_labels = {}
        level_names = ["优(100-90)", "良(89-80)", "中(79-70)", "及格(69-60)", "不及格(<60)"]
        for name in level_names:
            lbl = ttk.Label(stat_frame, text=f"{name}：0 人，占 0.0%", style="TLabel")
            lbl.pack(anchor="w", pady=1)
            self.stat_labels[name] = lbl

        # ===== 下方：按等级输出学生学号和成绩 =====
        bottom_frame = ttk.Frame(card, style="Card.TFrame")
        bottom_frame.pack(fill=tk.BOTH, expand=True, pady=(6, 0))

        ttk.Label(bottom_frame, text="各等级学生学号及总评成绩：", style="TLabel").pack(anchor="w")

        self.text_output = tk.Text(
            bottom_frame,
            wrap="word",
            font=("Consolas", 11),
            height=8,
            relief="solid",
            bd=1,
            padx=6,
            pady=4
        )
        self.text_output.pack(fill=tk.BOTH, expand=True, pady=(4, 0))

    # ===== 打开 JSON 文件 =====
    def open_json(self):
        path = filedialog.askopenfilename(
            title="选择 JSON 成绩文件",
            filetypes=[("JSON 文件", "*.json"), ("所有文件", "*.*")]
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            messagebox.showerror("错误", f"读取 JSON 文件失败：\n{e}")
            return

        if not isinstance(data, list):
            messagebox.showerror("错误", "JSON 格式错误：根节点应为列表（list）。")
            return

        self.all_records = data
        # 提取所有班级、课程
        classes = sorted({rec.get("class", "") for rec in self.all_records if "class" in rec})
        courses = sorted({rec.get("course", "") for rec in self.all_records if "course" in rec})

        self.class_combo["values"] = classes
        self.course_combo["values"] = courses

        if classes:
            self.class_combo.current(0)
        if courses:
            self.course_combo.current(0)

        messagebox.showinfo("成功", f"已成功加载 {len(self.all_records)} 条成绩记录。")

    # ===== 计算成绩与统计 =====
    def calculate(self):
        if not self.all_records:
            messagebox.showwarning("提示", "请先打开 JSON 成绩文件。")
            return

        cls = self.class_var.get().strip()
        cour = self.course_var.get().strip()
        if not cls or not cour:
            messagebox.showwarning("提示", "请选择班级和课程。")
            return

        # 按班级+课程筛选记录
        self.current_records = [
            rec for rec in self.all_records
            if rec.get("class") == cls and rec.get("course") == cour
        ]

        if not self.current_records:
            messagebox.showwarning("提示", f"没有找到 {cls} 班 {cour} 课程的成绩记录。")
            self.clear_results()
            return

        # 计算总评、等级
        for rec in self.current_records:
            try:
                daily = float(rec.get("daily", 0))
                mid = float(rec.get("mid", 0))
                final = float(rec.get("final", 0))
            except ValueError:
                daily = mid = final = 0.0

            total = 0.3 * daily + 0.3 * mid + 0.4 * final
            total = round(total, 2)
            rec["total"] = total
            rec["level"] = self.get_level(total)

        # 更新表格
        for item in self.tree.get_children():
            self.tree.delete(item)

        for rec in self.current_records:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    rec.get("id", ""),
                    rec.get("name", ""),
                    rec.get("daily", ""),
                    rec.get("mid", ""),
                    rec.get("final", ""),
                    rec.get("total", ""),
                    rec.get("level", ""),
                )
            )

        # 平均分
        totals = [rec["total"] for rec in self.current_records]
        avg = sum(totals) / len(totals)
        self.avg_label.config(text=f"平均分：{avg:.2f}")

        # 各等级统计
        count = len(self.current_records)
        level_ranges = {
            "优(100-90)": lambda x: x >= 90,
            "良(89-80)": lambda x: 80 <= x <= 89.9999,
            "中(79-70)": lambda x: 70 <= x <= 79.9999,
            "及格(69-60)": lambda x: 60 <= x <= 69.9999,
            "不及格(<60)": lambda x: x < 60,
        }

        level_students = {key: [] for key in level_ranges}

        for rec in self.current_records:
            total = rec["total"]
            for key, cond in level_ranges.items():
                if cond(total):
                    level_students[key].append(rec)
                    break

        for key, lbl in self.stat_labels.items():
            num = len(level_students[key])
            pct = num / count * 100
            lbl.config(text=f"{key}：{num} 人，占 {pct:.1f}%")

        # 下方文本区：按等级输出学号和成绩
        self.text_output.delete("1.0", tk.END)
        for key in ["优(100-90)", "良(89-80)", "中(79-70)", "及格(69-60)", "不及格(<60)"]:
            self.text_output.insert(tk.END, f"{key}：\n")
            students = level_students[key]
            if not students:
                self.text_output.insert(tk.END, "  无学生\n\n")
                continue
            for rec in students:
                sid = rec.get("id", "")
                name = rec.get("name", "")
                total = rec.get("total", 0)
                self.text_output.insert(
                    tk.END,
                    f"  学号：{sid:<12} 姓名：{name:<6} 总评：{total:.2f}\n"
                )
            self.text_output.insert(tk.END, "\n")

    # ===== 根据总评返回等级 =====
    @staticmethod
    def get_level(total: float) -> str:
        if total >= 90:
            return "优"
        elif total >= 80:
            return "良"
        elif total >= 70:
            return "中"
        elif total >= 60:
            return "及格"
        else:
            return "不及格"

    # ===== 清空结果显示 =====
    def clear_results(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.avg_label.config(text="平均分：--")
        for key, lbl in self.stat_labels.items():
            lbl.config(text=f"{key}：0 人，占 0.0%")
        self.text_output.delete("1.0", tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = GradeSystemApp(root)
    root.mainloop()
