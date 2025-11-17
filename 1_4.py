import tkinter as tk
from tkinter import ttk, messagebox


class EncryptApp:
    def __init__(self, root):
        self.root = root
        self.root.title("加密 / 解密 工具（Ci = mi + K）")
        self.root.geometry("800x520")
        self.root.minsize(700, 420)

        # ===== 样式 =====
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

        # ===== 外层框架 =====
        main_frame = ttk.Frame(self.root, style="Main.TFrame", padding=14)
        main_frame.pack(fill=tk.BOTH, expand=True)

        card = ttk.Frame(main_frame, style="Card.TFrame", padding=14)
        card.pack(fill=tk.BOTH, expand=True)

        ttk.Label(card, text="加密 / 解密 工具", style="Title.TLabel").pack(anchor="center", pady=(0, 10))

        # ===== 中间：输入框 + 右侧控制区 =====
        middle_frame = ttk.Frame(card, style="Card.TFrame")
        middle_frame.pack(fill=tk.BOTH, expand=True)

        # 左侧输入框
        left_frame = ttk.Frame(middle_frame, style="Card.TFrame")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Label(left_frame, text="输入内容：", style="TLabel").pack(anchor="w")

        self.text_input = tk.Text(
            left_frame,
            wrap="word",
            font=("Consolas", 12),
            height=8,
            relief="solid",
            bd=1,
            padx=4,
            pady=4
        )
        self.text_input.pack(fill=tk.BOTH, expand=True, pady=(4, 0))

        # 右侧控制区
        right_frame = ttk.Frame(middle_frame, style="Card.TFrame")
        right_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 0))

        ttk.Label(right_frame, text="输入类型：", style="TLabel").pack(anchor="w")

        # 选择输入的是 明文 or 密文
        self.input_type = tk.StringVar(value="plain")  # "plain" 或 "cipher"
        rb_plain = ttk.Radiobutton(
            right_frame, text="明文（要加密）",
            variable=self.input_type, value="plain"
        )
        rb_cipher = ttk.Radiobutton(
            right_frame, text="密文（要解密）",
            variable=self.input_type, value="cipher"
        )
        rb_plain.pack(anchor="w", pady=(4, 0))
        rb_cipher.pack(anchor="w")

        ttk.Label(right_frame, text="密钥 K（整数）：", style="TLabel").pack(anchor="w", pady=(10, 0))

        self.key_var = tk.StringVar(value="3")
        self.entry_key = ttk.Entry(right_frame, textvariable=self.key_var, width=10)
        self.entry_key.pack(anchor="w", pady=(4, 8))

        # 转换按钮
        self.btn_convert = ttk.Button(
            right_frame,
            text="开始转换",
            style="Accent.TButton",
            command=self.convert
        )
        self.btn_convert.pack(fill=tk.X, pady=(6, 4))

        # 清空按钮
        self.btn_clear = ttk.Button(
            right_frame,
            text="清空",
            command=self.clear
        )
        self.btn_clear.pack(fill=tk.X, pady=(2, 0))

        # ===== 底部：结果输出 =====
        bottom_frame = ttk.Frame(card, style="Card.TFrame")
        bottom_frame.pack(fill=tk.BOTH, expand=True, pady=(12, 0))

        ttk.Label(bottom_frame, text="结果：", style="TLabel").pack(anchor="w")

        self.text_output = tk.Text(
            bottom_frame,
            wrap="word",
            font=("Consolas", 12),
            height=8,
            relief="solid",
            bd=1,
            padx=4,
            pady=4
        )
        self.text_output.pack(fill=tk.BOTH, expand=True, pady=(4, 0))

        hint = ttk.Label(
            card,
            text="说明：对每个字符 mi，按 Ci = mi + K （或 mi = Ci - K）进行转换。\n"
                 "程序使用字符编码值加/减密钥 K 后对 256 取模，再转回字符。",
            style="TLabel",
            foreground="#6b7280",
            wraplength=760,
            justify="left"
        )
        hint.pack(anchor="w", pady=(6, 0))

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

        # ⭐ 关键修改：去掉 Text 自动附加的最后一个换行符
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


if __name__ == "__main__":
    root = tk.Tk()
    app = EncryptApp(root)
    root.mainloop()
