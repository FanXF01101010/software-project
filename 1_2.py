import tkinter as tk
from tkinter import ttk, messagebox
import random
import string


class TypingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("打字练习程序")

        # 为 1366×768 之类的屏幕优化的尺寸
        self.root.geometry("900x600")
        self.root.configure(bg="#f5f7fb")
        self.root.resizable(True, True)

        self.target_text = ""

        # ==== 样式 ====
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        bg_main = "#f5f7fb"
        bg_card = "#ffffff"
        accent = "#4f46e5"

        style.configure("Main.TFrame", background=bg_main)
        style.configure("Card.TFrame", background=bg_card)

        style.configure(
            "Title.TLabel",
            background=bg_card,
            foreground="#111827",
            font=("Microsoft YaHei", 18, "bold")
        )
        style.configure(
            "TLabel",
            background=bg_card,
            foreground="#4b5563",
            font=("Microsoft YaHei", 11)
        )

        style.configure("Accent.TButton", font=("Microsoft YaHei", 11), padding=6)
        style.map(
            "Accent.TButton",
            background=[("!disabled", accent), ("active", "#4338ca"), ("pressed", "#4338ca")],
            foreground=[("!disabled", "#ffffff")]
        )

        style.configure("Secondary.TButton", font=("Microsoft YaHei", 11), padding=6)
        style.map(
            "Secondary.TButton",
            background=[("!disabled", "#e5e7eb"), ("active", "#d1d5db"), ("pressed", "#d1d5db")]
        )

        # ==== 外层框架 ====
        main_frame = ttk.Frame(self.root, style="Main.TFrame", padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        card = ttk.Frame(main_frame, style="Card.TFrame", padding=15)
        card.pack(fill=tk.BOTH, expand=True)

        # 标题
        ttk.Label(card, text="打字练习程序", style="Title.TLabel").pack(anchor="center", pady=(0, 10))

        # ==== 目标字符串 ====
        target_frame = ttk.Frame(card, style="Card.TFrame")
        target_frame.pack(pady=(4, 4))

        ttk.Label(target_frame, text="目标字符串：", style="TLabel").pack(side=tk.TOP, pady=(0, 4))

        self.target_label = ttk.Label(
            target_frame,
            text="请点击下方按钮生成字符串",
            style="TLabel",
            font=("Consolas", 14)
        )
        self.target_label.pack()

        # 生成按钮
        btn_frame = ttk.Frame(card, style="Card.TFrame")
        btn_frame.pack(pady=(6, 6))

        ttk.Button(
            btn_frame,
            text="随机生成字符串",
            style="Accent.TButton",
            command=self.generate_string
        ).pack()

        # ==== 输入区 ====
        input_frame = ttk.Frame(card, style="Card.TFrame")
        input_frame.pack(pady=(8, 4), fill=tk.X)

        ttk.Label(
            input_frame,
            text="请在下方输入你看到的字符串：",
            style="TLabel"
        ).pack(anchor="center", pady=(0, 4))

        self.input_var = tk.StringVar()
        self.entry_input = ttk.Entry(
            input_frame,
            textvariable=self.input_var,
            font=("Consolas", 14),
            width=40
        )
        self.entry_input.pack(anchor="center")

        self.entry_input.bind("<Return>", lambda e: self.check_input())

        # ==== 按钮区 ====
        action_frame = ttk.Frame(card, style="Card.TFrame")
        action_frame.pack(pady=(8, 6))

        ttk.Button(
            action_frame,
            text="判 定 正 确 率",
            style="Accent.TButton",
            command=self.check_input
        ).pack(side=tk.LEFT, padx=(0, 8))

        ttk.Button(
            action_frame,
            text="清空输入",
            style="Secondary.TButton",
            command=self.clear_input
        ).pack(side=tk.LEFT)

        # ==== 正确率显示：左边圆盘 + 右边评价文字 ====
        icon_frame = ttk.Frame(card, style="Card.TFrame")
        icon_frame.pack(pady=(10, 4), fill=tk.BOTH, expand=False)

        ttk.Label(icon_frame, text="正确率：", style="TLabel").pack(anchor="center")

        display_frame = ttk.Frame(icon_frame, style="Card.TFrame")
        display_frame.pack(anchor="center", pady=(0, 0))

        # 左侧圆盘
        self.icon_canvas = tk.Canvas(
            display_frame,
            width=170,
            height=170,
            bg=bg_card,
            highlightthickness=0
        )
        self.icon_canvas.pack(side=tk.LEFT, padx=(0, 12))

        self.circle = self.icon_canvas.create_oval(
            15, 15, 155, 155,
            fill="#e5e7eb",
            outline="#d1d5db",
            width=6
        )
        self.percent_text = self.icon_canvas.create_text(
            85, 85,
            text="--%",
            font=("Microsoft YaHei", 20, "bold"),
            fill="#4b5563"
        )

        # 右侧评价文字
        right_frame = ttk.Frame(display_frame, style="Card.TFrame")
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.accuracy_label = ttk.Label(
            right_frame,
            text="请先生成字符串并完成一次输入判定。",
            style="TLabel",
            foreground="#6b7280",
            wraplength=350,
            justify="left"
        )
        self.accuracy_label.pack(anchor="w")

        # 底部提示
        ttk.Label(
            card,
            text="说明：点击“随机生成字符串”获得练习内容；输入后按“判定正确率”或回车键即可。",
            style="TLabel",
            foreground="#6b7280",
            wraplength=860,
            justify="center"
        ).pack(anchor="center", pady=(8, 0))

    # ===== 更新圆盘和评价 =====
    def update_accuracy_icon(self, accuracy):
        if accuracy is None:
            color = "#e5e7eb"
            outline = "#d1d5db"
            text = "--%"
            text_color = "#4b5563"
            desc = "请先生成字符串并完成一次输入判定。"
        else:
            text = f"{accuracy:.1f}%"
            if accuracy >= 99.9:
                color, outline, text_color = "#16a34a", "#15803d", "#ffffff"
                desc = f"太强了！正确率 {text}，可以尝试提高打字速度。"
            elif accuracy >= 60:
                color, outline, text_color = "#f59e0b", "#d97706", "#111827"
                desc = f"不错哦，正确率 {text}，多练习可以向 100% 冲刺。"
            else:
                color, outline, text_color = "#dc2626", "#b91c1c", "#ffffff"
                desc = f"继续加油，正确率 {text}，建议慢一点认真对照。"

        self.icon_canvas.itemconfig(self.circle, fill=color, outline=outline)
        self.icon_canvas.itemconfig(self.percent_text, text=text, fill=text_color)
        self.accuracy_label.config(text=desc)

    # ===== 逻辑 =====
    def generate_string(self):
        length = random.randint(5, 20)
        chars = string.ascii_letters + string.digits
        self.target_text = "".join(random.choices(chars, k=length))

        self.target_label.config(text=self.target_text)
        self.input_var.set("")
        self.entry_input.focus()
        self.update_accuracy_icon(None)

    def check_input(self):
        if not self.target_text:
            messagebox.showinfo("提示", "请先点击“随机生成字符串”。")
            return

        user_input = self.input_var.get()
        if not user_input:
            messagebox.showwarning("提示", "输入不能为空！")
            return

        target = self.target_text
        total_len = len(target)
        compare_len = min(len(user_input), len(target))

        correct_count = sum(
            1 for i in range(compare_len) if user_input[i] == target[i]
        )
        accuracy = correct_count / total_len * 100
        self.update_accuracy_icon(accuracy)

    def clear_input(self):
        self.input_var.set("")
        self.entry_input.focus()
        self.update_accuracy_icon(None)


if __name__ == "__main__":
    root = tk.Tk()
    app = TypingApp(root)
    root.mainloop()
