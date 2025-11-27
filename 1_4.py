import tkinter as tk
from tkinter import ttk, messagebox


class EncryptApp:
    def __init__(self, root):
        self.root = root
        self.root.title("加密 / 解密 工具（Ci = mi + K）")

        self.root.geometry("1100x650")
        try:
            self.root.state("zoomed")
        except tk.TclError:
            pass

        self.root.minsize(900, 550)

        # ===== 样式 =====
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        bg_main = "#f3f4f6"   # 整体背景：浅灰
        bg_card = "#ffffff"   # 中央卡片：纯白
        accent = "#2563eb"    # 主色：蓝色
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
            foreground=[("!disabled", "#ffffff")],
            relief=[("pressed", "sunken")]
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

        # ===== 外层：居中卡片 =====
        outer = ttk.Frame(self.root, style="Main.TFrame", padding=20)
        outer.pack(fill=tk.BOTH, expand=True)

        card = ttk.Frame(outer, style="Card.TFrame", padding=(22, 18, 22, 18))
        card.pack(fill=tk.BOTH, expand=True)

        # 顶部标题
        header = ttk.Frame(card, style="Card.TFrame")
        header.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(header, text="加密 / 解密 工具", style="Title.TLabel").pack(anchor="center")
        ttk.Label(
            header,
            text="基于 Ci = mi + K / mi = Ci - K 的简单移位加密示例",
            style="SubTitle.TLabel"
        ).pack(anchor="center", pady=(4, 0))

        # ===== 中间：输入框 + 右侧控制区 =====
        middle_frame = ttk.Frame(card, style="Card.TFrame")
        middle_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 4))

        # 左侧输入框
        left_frame = ttk.Frame(middle_frame, style="Card.TFrame")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Label(left_frame, text="输入内容：", style="TLabel").pack(anchor="w")

        input_container = ttk.Frame(left_frame, style="Card.TFrame")
        input_container.pack(fill=tk.BOTH, expand=True, pady=(4, 0))

        self.text_input = tk.Text(
            input_container,
            wrap="word",
            font=("Consolas", 12),
            height=10,
            relief="flat",
            bd=0,
            padx=8,
            pady=6,
        )
        self.text_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        input_scroll = ttk.Scrollbar(
            input_container, orient=tk.VERTICAL, command=self.text_input.yview
        )
        input_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_input.configure(yscrollcommand=input_scroll.set)

        # 右侧控制区：固定宽度，不会被挤掉
        right_frame = ttk.Frame(middle_frame, style="Card.TFrame")
        right_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(16, 0))
        right_frame.configure(width=260)
        right_frame.pack_propagate(False)

        ttk.Label(right_frame, text="输入类型", style="TLabel").pack(anchor="w")

        self.input_type = tk.StringVar(value="plain")  # "plain" 或 "cipher"
        ttk.Radiobutton(
            right_frame, text="明文（需要加密）",
            variable=self.input_type, value="plain"
        ).pack(anchor="w", pady=(4, 0))
        ttk.Radiobutton(
            right_frame, text="密文（需要解密）",
            variable=self.input_type, value="cipher"
        ).pack(anchor="w")

        ttk.Label(right_frame, text="密钥 K（整数）：", style="TLabel").pack(anchor="w", pady=(14, 0))

        self.key_var = tk.StringVar(value="3")
        self.entry_key = ttk.Entry(right_frame, textvariable=self.key_var, width=12)
        self.entry_key.pack(anchor="w", pady=(4, 10))

        self.btn_convert = ttk.Button(
            right_frame,
            text="开始转换",
            style="Accent.TButton",
            command=self.convert
        )
        self.btn_convert.pack(fill=tk.X, pady=(6, 4))

        self.btn_clear = ttk.Button(
            right_frame,
            text="清空",
            style="Secondary.TButton",
            command=self.clear
        )
        self.btn_clear.pack(fill=tk.X, pady=(2, 0))

        # ===== 底部：结果输出 =====
        bottom_frame = ttk.Frame(card, style="Card.TFrame")
        bottom_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        ttk.Label(bottom_frame, text="结果：", style="TLabel").pack(anchor="w")

        output_container = ttk.Frame(bottom_frame, style="Card.TFrame")
        output_container.pack(fill=tk.BOTH, expand=True, pady=(4, 0))

        self.text_output = tk.Text(
            output_container,
            wrap="word",
            font=("Consolas", 12),
            height=8,
            relief="flat",
            bd=0,
            padx=8,
            pady=6,
        )
        self.text_output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        output_scroll = ttk.Scrollbar(
            output_container, orient=tk.VERTICAL, command=self.text_output.yview
        )
        output_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_output.configure(yscrollcommand=output_scroll.set)

        # 说明文字
        ttk.Label(
            card,
            text="说明：对每个字符 mi，按 Ci = mi + K（或 mi = Ci - K）处理，使用字符编码值加/减密钥 K 后对 256 取模再转回字符。",
            style="SubTitle.TLabel",
            wraplength=1000,
            justify="left"
        ).pack(anchor="w", pady=(8, 0))

    # ===== 加解密核心 =====
    def get_key(self):
        key_str = self.key_var.get().strip()
        if not key_str:
            messagebox.showwarning("提示", "请先输入密钥 K（整数）。")
            return None
        try:
            k = int(key_str)
        except ValueError:
            messagebox.showwarning("提示", "密钥 K 必须是整数！")
            return None
        return k

    def encrypt(self, text, k):
        return "".join(chr((ord(ch) + k) % 256) for ch in text)

    def decrypt(self, text, k):
        return "".join(chr((ord(ch) - k) % 256) for ch in text)

    def convert(self):
        """根据选择的类型进行加密或解密"""
        k = self.get_key()
        if k is None:
            return

        # 去掉 Text 自动附加的最后一个换行符
        src = self.text_input.get("1.0", "end-1c")
        if not src:
            messagebox.showwarning("提示", "请先在上方输入内容。")
            return

        mode = self.input_type.get()
        if mode == "plain":
            result = self.encrypt(src, k)
        else:
            result = self.decrypt(src, k)

        self.text_output.delete("1.0", tk.END)
        self.text_output.insert(tk.END, result)

    def clear(self):
        self.text_input.delete("1.0", tk.END)
        self.text_output.delete("1.0", tk.END)
        self.entry_key.focus()

#主程序入口
if __name__ == "__main__":
    root = tk.Tk()
    app = EncryptApp(root)
    root.mainloop()
