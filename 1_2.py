import tkinter as tk
from tkinter import ttk, messagebox
import random
import string


class TypingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("打字练习程序")
        # 窗口加大一点
        self.root.geometry("780x520")
        self.root.resizable(False, False)

        # 当前目标字符串
        self.target_text = ""

        # ===== 样式简单美化 =====
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        bg_main = "#f5f7fb"
        bg_card = "#ffffff"
        accent = "#4f46e5"

        self.root.configure(bg=bg_main)
        style.configure("Main.TFrame", background=bg_main)
        style.configure("Card.TFrame", background=bg_card)

        style.configure(
            "Title.TLabel",
            background=bg_card,
            foreground="#111827",
            font=("Microsoft YaHei", 16, "bold")
        )
        style.configure(
            "TLabel",
            background=bg_card,
            foreground="#4b5563",
            font=("Microsoft YaHei", 11)
        )

        style.configure("Accent.TButton", font=("Microsoft YaHei", 11), padding=8)
        style.map(
            "Accent.TButton",
            background=[("!disabled", accent), ("active", "#4338ca"), ("pressed", "#4338ca")],
            foreground=[("!disabled", "#ffffff")]
        )

        style.configure("Secondary.TButton", font=("Microsoft YaHei", 11), padding=8)
        style.map(
            "Secondary.TButton",
            background=[("!disabled", "#e5e7eb"), ("active", "#d1d5db"), ("pressed", "#d1d5db")]
        )

        # ===== 外层框架 =====
        main_frame = ttk.Frame(self.root, style="Main.TFrame", padding=18)
        main_frame.pack(fill=tk.BOTH, expand=True)

        card = ttk.Frame(main_frame, style="Card.TFrame", padding=(20, 18, 20, 18))
        card.pack(fill=tk.BOTH, expand=True)

        # 标题
        title_label = ttk.Label(card, text="打字练习程序", style="Title.TLabel")
        title_label.pack(anchor="center", pady=(0, 12))

        # ===== 显示随机字符串 =====
        target_frame = ttk.Frame(card, style="Card.TFrame")
        target_frame.pack(pady=(6, 6))

        ttk.Label(target_frame, text="目标字符串：", style="TLabel").pack(side=tk.TOP, pady=(0, 6))

        self.target_label = ttk.Label(
            target_frame,
            text="请点击下方按钮生成字符串",
            style="TLabel",
            font=("Consolas", 14)
        )
        self.target_label.pack()

        # 生成按钮
        btn_frame = ttk.Frame(card, style="Card.TFrame")
        btn_frame.pack(pady=(10, 10))

        btn_generate = ttk.Button(
            btn_frame,
            text="随机生成字符串",
            style="Accent.TButton",
            command=self.generate_string
        )
        btn_generate.pack()

        # ===== 用户输入区 =====
        input_frame = ttk.Frame(card, style="Card.TFrame")
        input_frame.pack(pady=(10, 6), fill=tk.X)

        ttk.Label(input_frame, text="请在下方输入你看到的字符串：", style="TLabel").pack(anchor="center", pady=(0, 6))

        self.input_var = tk.StringVar()
        self.entry_input = ttk.Entry(
            input_frame,
            textvariable=self.input_var,
            font=("Consolas", 13),
            width=60
        )
        self.entry_input.pack(anchor="center")

        # 回车键直接判定
        self.entry_input.bind("<Return>", lambda event: self.check_input())

        # ===== 判定按钮 & 清空按钮 =====
        action_frame = ttk.Frame(card, style="Card.TFrame")
        action_frame.pack(pady=(10, 8))

        btn_check = ttk.Button(
            action_frame,
            text="判 定 正 确 率",
            style="Accent.TButton",
            command=self.check_input
        )
        btn_check.pack(side=tk.LEFT, padx=(0, 10))

        btn_clear = ttk.Button(
            action_frame,
            text="清空输入",
            style="Secondary.TButton",
            command=self.clear_input
        )
        btn_clear.pack(side=tk.LEFT)

        # ===== 结果显示区（加大 + 可滚动文本框）=====
        result_frame = ttk.Frame(card, style="Card.TFrame")
        result_frame.pack(pady=(10, 6), fill=tk.BOTH, expand=True)

        ttk.Label(result_frame, text="结果：", style="TLabel").pack(anchor="w")

        # 文本框 + 滚动条
        text_container = ttk.Frame(result_frame, style="Card.TFrame")
        text_container.pack(fill=tk.BOTH, expand=True, pady=(4, 0))

        self.result_text = tk.Text(
            text_container,
            height=8,
            width=80,
            font=("Consolas", 12),
            wrap="word",
            bg="#f9fafb",
            relief="solid",
            bd=1
        )
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scroll_y = ttk.Scrollbar(text_container, orient="vertical", command=self.result_text.yview)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.configure(yscrollcommand=scroll_y.set)

        # 默认提示
        self.set_result_text("尚未进行判定。")

        # 底部提示
        hint = ttk.Label(
            card,
            text="说明：每次点击“随机生成字符串”都会生成一个不同的字符串和长度；\n"
                 "在下面输入框中输入后，按“判定正确率”或回车键查看结果。",
            style="TLabel",
            foreground="#6b7280",
            wraplength=720,
            justify="center"
        )
        hint.pack(anchor="center", pady=(8, 0))

    def set_result_text(self, text, color="#111827"):
        """设置结果文本框内容和颜色"""
        self.result_text.config(state="normal")
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, text)
        self.result_text.tag_configure("color", foreground=color)
        self.result_text.tag_add("color", "1.0", tk.END)
        self.result_text.config(state="disabled")

    def generate_string(self):
        """随机产生目标字符串：内容、长度都随机"""
        # 随机长度 5~20
        length = random.randint(5, 20)
        # 随机内容：大小写字母 + 数字
        chars = string.ascii_letters + string.digits
        self.target_text = "".join(random.choices(chars, k=length))

        self.target_label.config(text=self.target_text)
        self.input_var.set("")
        self.entry_input.focus()
        self.set_result_text("已生成新字符串，请输入后判定。", color="#6b7280")

    def check_input(self):
        """比较输入与目标，计算正确率"""
        if not self.target_text:
            messagebox.showinfo("提示", "请先点击“随机生成字符串”生成一个目标字符串。")
            return

        user_input = self.input_var.get()

        if not user_input:
            messagebox.showwarning("提示", "输入不能为空！")
            return

        target = self.target_text

        # 按“位置对齐”来计算正确字符数量
        total_len = len(target)
        compare_len = min(len(user_input), len(target))

        correct_count = 0
        for i in range(compare_len):
            if user_input[i] == target[i]:
                correct_count += 1

        # 总长度按目标长度计算
        accuracy = correct_count / total_len * 100

        result_text = (
            f"目标字符串：{target}\n"
            f"你的输入：  {user_input}\n\n"
            f"目标长度：{total_len}\n"
            f"按位置逐字比较正确字符数：{correct_count}\n"
            f"正确率：{accuracy:.2f}%"
        )

        if accuracy == 100:
            color = "#16a34a"   # 绿色
        elif accuracy >= 60:
            color = "#ea580c"   # 橙色
        else:
            color = "#dc2626"   # 红色

        self.set_result_text(result_text, color=color)

    def clear_input(self):
        """清空输入"""
        self.input_var.set("")
        self.entry_input.focus()
        self.set_result_text("输入已清空。", color="#6b7280")


if __name__ == "__main__":
    root = tk.Tk()
    app = TypingApp(root)
    root.mainloop()
