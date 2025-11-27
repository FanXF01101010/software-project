import tkinter as tk
from tkinter import ttk, messagebox


class BaseConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("进制转换器")

        # 窗口尺寸  尝试最大化
        self.root.geometry("1000x550")
        try:
            self.root.state("zoomed")
        except tk.TclError:
            pass
        self.root.minsize(800, 480)

        # ========== 样式  ==========
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        bg_main = "#f3f4f6"     # 背景浅灰
        bg_card = "#ffffff"     # 中间卡片白色
        accent = "#2563eb"      # 主色：蓝
        text_main = "#111827"
        text_sub = "#4b5563"

        self.root.configure(bg=bg_main)
        style.configure("Main.TFrame", background=bg_main)
        style.configure("Card.TFrame", background=bg_card)

        style.configure(
            "Title.TLabel",
            background=bg_card,
            foreground=text_main,
            font=("Segoe UI", 20, "bold")
        )
        style.configure(
            "SubTitle.TLabel",
            background=bg_card,
            foreground=text_sub,
            font=("Segoe UI", 11)
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
            padding=8,
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
            padding=8,
            relief="flat"
        )
        style.map(
            "Secondary.TButton",
            background=[("!disabled", "#e5e7eb"), ("active", "#d1d5db")],
            foreground=[("!disabled", text_main)]
        )

        style.configure(
            "TRadiobutton",
            background=bg_card,
            foreground=text_sub,
            font=("Segoe UI", 10)
        )

        # ========== 外层布局 ==========
        outer = ttk.Frame(self.root, style="Main.TFrame", padding=20)
        outer.pack(fill=tk.BOTH, expand=True)

        card = ttk.Frame(outer, style="Card.TFrame", padding=(22, 18, 22, 18))
        card.pack(fill=tk.BOTH, expand=True)

        # 标题
        header = ttk.Frame(card, style="Card.TFrame")
        header.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(header, text="进制转换器", style="Title.TLabel").pack(anchor="center")
        ttk.Label(
            header,
            text="支持二进制、八进制、十进制、十六进制之间的互相转换",
            style="SubTitle.TLabel"
        ).pack(anchor="center", pady=(4, 0))

        # ========== 上方：输入区域 ==========
        top = ttk.Frame(card, style="Card.TFrame")
        top.pack(fill=tk.X, pady=(10, 6))

        # 左：输入框
        input_frame = ttk.Frame(top, style="Card.TFrame")
        input_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Label(input_frame, text="输入数字：", style="TLabel").pack(anchor="w")

        self.input_var = tk.StringVar()
        self.entry_input = ttk.Entry(
            input_frame,
            textvariable=self.input_var,
            font=("Consolas", 14)
        )
        self.entry_input.pack(fill=tk.X, pady=(4, 0))

        # 右：进制选择 + 按钮
        right_frame = ttk.Frame(top, style="Card.TFrame")
        right_frame.pack(side=tk.LEFT, padx=(20, 0))

        ttk.Label(right_frame, text="当前输入的进制：", style="TLabel").pack(anchor="w")

        self.base_var = tk.StringVar(value="10")
        ttk.Radiobutton(
            right_frame, text="二进制 (2)", variable=self.base_var, value="2"
        ).pack(anchor="w")
        ttk.Radiobutton(
            right_frame, text="八进制 (8)", variable=self.base_var, value="8"
        ).pack(anchor="w")
        ttk.Radiobutton(
            right_frame, text="十进制 (10)", variable=self.base_var, value="10"
        ).pack(anchor="w")
        ttk.Radiobutton(
            right_frame, text="十六进制 (16)", variable=self.base_var, value="16"
        ).pack(anchor="w")

        ttk.Button(
            right_frame,
            text="转 换",
            style="Accent.TButton",
            command=self.convert
        ).pack(fill=tk.X, pady=(12, 4))

        ttk.Button(
            right_frame,
            text="清 空",
            style="Secondary.TButton",
            command=self.clear
        ).pack(fill=tk.X)

        # ========== 下方：结果显示 ==========
        bottom = ttk.Frame(card, style="Card.TFrame")
        bottom.pack(fill=tk.BOTH, expand=True, pady=(14, 0))

        ttk.Label(bottom, text="转换结果：", style="TLabel").pack(anchor="w")

        # 每一种进制一行：标签 + 只读输入框，方便复制
        result_frame = ttk.Frame(bottom, style="Card.TFrame")
        result_frame.pack(fill=tk.X, pady=(6, 0))

        self.result_vars = {
            2: tk.StringVar(),
            8: tk.StringVar(),
            10: tk.StringVar(),
            16: tk.StringVar(),
        }

        # 二进制
        row1 = ttk.Frame(result_frame, style="Card.TFrame")
        row1.pack(fill=tk.X, pady=2)
        ttk.Label(row1, text="二进制 (2)：", style="TLabel", width=12).pack(side=tk.LEFT)
        e_bin = ttk.Entry(row1, textvariable=self.result_vars[2], font=("Consolas", 12), state="readonly")
        e_bin.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 八进制
        row2 = ttk.Frame(result_frame, style="Card.TFrame")
        row2.pack(fill=tk.X, pady=2)
        ttk.Label(row2, text="八进制 (8)：", style="TLabel", width=12).pack(side=tk.LEFT)
        e_oct = ttk.Entry(row2, textvariable=self.result_vars[8], font=("Consolas", 12), state="readonly")
        e_oct.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 十进制
        row3 = ttk.Frame(result_frame, style="Card.TFrame")
        row3.pack(fill=tk.X, pady=2)
        ttk.Label(row3, text="十进制 (10)：", style="TLabel", width=12).pack(side=tk.LEFT)
        e_dec = ttk.Entry(row3, textvariable=self.result_vars[10], font=("Consolas", 12), state="readonly")
        e_dec.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 十六进制
        row4 = ttk.Frame(result_frame, style="Card.TFrame")
        row4.pack(fill=tk.X, pady=2)
        ttk.Label(row4, text="十六进制 (16)：", style="TLabel", width=12).pack(side=tk.LEFT)
        e_hex = ttk.Entry(row4, textvariable=self.result_vars[16], font=("Consolas", 12), state="readonly")
        e_hex.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 说明
        ttk.Label(
            card,
            text="提示：\n"
                 "• 二进制只允许 0 和 1；八进制使用 0–7；十进制使用 0–9；十六进制使用 0–9 和 A–F / a–f。\n"
                 "• 输入负数也可以（例如 -10），程序会保留负号并对绝对值进行进制转换。",
            style="SubTitle.TLabel",
            wraplength=960,
            justify="left"
        ).pack(anchor="w", pady=(10, 0))

    # ========== 功能部分 ==========
    def clear(self):
        self.input_var.set("")
        for v in self.result_vars.values():
            v.set("")
        self.entry_input.focus()

    def convert(self):
        s = self.input_var.get().strip()
        if not s:
            messagebox.showwarning("提示", "请输入一个数字。")
            return

        base = int(self.base_var.get())

        # 处理负号
        negative = False
        if s.startswith("-"):
            negative = True
            s_body = s[1:]
        else:
            s_body = s

        # 尝试按所选进制解析
        try:
            value = int(s_body, base)
        except ValueError:
            messagebox.showerror("错误", f"输入的数字与所选进制不匹配（当前进制：{base}）。")
            return

        if negative:
            value = -value

        # 生成四种进制表示
        if value < 0:
            sign = "-"
            abs_val = -value
        else:
            sign = ""
            abs_val = value

        bin_str = sign + bin(abs_val)[2:]
        oct_str = sign + oct(abs_val)[2:]
        dec_str = str(value)
        hex_str = sign + hex(abs_val)[2:].upper()

        self.result_vars[2].set(bin_str)
        self.result_vars[8].set(oct_str)
        self.result_vars[10].set(dec_str)
        self.result_vars[16].set(hex_str)



# 主程序入口
if __name__ == "__main__":
    root = tk.Tk()
    app = BaseConverterApp(root)
    root.mainloop()
