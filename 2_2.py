# -*- coding: utf-8 -*-
"""
模拟电信计费系统（Python + Tkinter + JSON）

页面 1：用户信息查询
    - 通过姓名查询名下手机号（支持模糊匹配）
    - 支持选中结果行后 Ctrl + C 复制
页面 2：话费与话单查询
    - 根据通话记录和费率计算话费，结果保存到 fees.json
    - 话费查询：按电话号码汇总本地费、长途费、总费用
    - 话单查询：按电话号码显示所有通话记录

改动点：
1. 去掉了“重新计算全部费用”按钮
2. 增加：程序启动后自动每 5 秒轮询一次 compute_all_fees()
3. 增加：用户查询表格支持 Ctrl + C 复制选中行内容
"""

import json
import os
import math
import tkinter as tk
from tkinter import ttk, messagebox

# -------------------- 文件路径设置 --------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE_DIR, "users.json")
RATES_FILE = os.path.join(BASE_DIR, "rates.json")
CALLS_FILE = os.path.join(BASE_DIR, "calls.json")
FEES_FILE = os.path.join(BASE_DIR, "fees.json")


# -------------------- 初始化示例数据 --------------------

def init_sample_data():
    """如果 JSON 文件不存在，则创建一些示例数据，方便测试。"""
    if not os.path.exists(USERS_FILE):
        users = {
            "users": [
                {"userId": "U001", "userName": "张三", "phoneNumber": "13800000001"},
                {"userId": "U002", "userName": "李四", "phoneNumber": "13800000002"},
                {"userId": "U003", "userName": "王五", "phoneNumber": "01088880000"},
                {"userId": "U004", "userName": "张三丰", "phoneNumber": "13900000003"}
            ]
        }
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=4)

    if not os.path.exists(RATES_FILE):
        rates = {
            "longDistanceRates": [
                {"areaCode": "010", "areaName": "北京", "ratePerMinute": 0.60},
                {"areaCode": "021", "areaName": "上海", "ratePerMinute": 0.65},
                {"areaCode": "020", "areaName": "广州", "ratePerMinute": 0.70}
            ]
        }
        with open(RATES_FILE, "w", encoding="utf-8") as f:
            json.dump(rates, f, ensure_ascii=False, indent=4)

    if not os.path.exists(CALLS_FILE):
        calls = {
            "callRecords": [
                {
                    "callId": "C001",
                    "callerNumber": "13800000001",
                    "calleeNumber": "01088880000",
                    "startTime": "2025-11-18 09:00:10",
                    "durationSeconds": 125,  # 2分5秒 -> 3分钟
                    "callType": "long-distance",
                    "longDistanceAreaCode": "010"
                },
                {
                    "callId": "C002",
                    "callerNumber": "13800000001",
                    "calleeNumber": "13800000002",
                    "startTime": "2025-11-18 10:15:05",
                    "durationSeconds": 170,  # 2分50秒 -> 3分钟
                    "callType": "local",
                    "longDistanceAreaCode": None
                },
                {
                    "callId": "C003",
                    "callerNumber": "13800000002",
                    "calleeNumber": "02166668888",
                    "startTime": "2025-11-18 11:20:30",
                    "durationSeconds": 59,   # 0分59秒 -> 1分钟
                    "callType": "long-distance",
                    "longDistanceAreaCode": "021"
                }
            ]
        }
        with open(CALLS_FILE, "w", encoding="utf-8") as f:
            json.dump(calls, f, ensure_ascii=False, indent=4)


# -------------------- 计费核心逻辑 --------------------

def calc_local_fee(minutes: int) -> float:
    """
    本地电话费计算：
    - 3 分钟以内 0.5 元
    - 超过 3 分钟以后，每 3 分钟递增 0.2 元（不足 3 分钟按 3 分钟算）
    """
    if minutes <= 3:
        return 0.5
    else:
        extra_minutes = minutes - 3
        extra_blocks = math.ceil(extra_minutes / 3)
        return 0.5 + extra_blocks * 0.2


class BillingSystem:
    def __init__(self):
        init_sample_data()
        self.users = self._load_json(USERS_FILE)
        self.rates = self._load_json(RATES_FILE)
        self.calls = self._load_json(CALLS_FILE)

        if os.path.exists(FEES_FILE):
            self.fees = self._load_json(FEES_FILE)
        else:
            self.fees = {"fees": []}
            self.compute_all_fees()

    @staticmethod
    def _load_json(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _save_json(path, data):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    # ---------- 用户相关 ----------

    def get_user_name(self, phone_number: str) -> str:
        for u in self.users.get("users", []):
            if u.get("phoneNumber") == phone_number:
                return u.get("userName", "未知用户")
        return "未知用户"

    def find_users_by_name(self, name: str):
        """
        根据姓名（支持模糊匹配）查询所有用户。
        返回列表，每项为用户字典。
        """
        result = []
        name = name.strip()
        if not name:
            return result
        for u in self.users.get("users", []):
            if name in u.get("userName", ""):
                result.append(u)
        return result

    # ---------- 费率 & 计费 ----------

    def get_rate(self, area_code: str) -> float:
        if not area_code:
            return 0.0
        for r in self.rates.get("longDistanceRates", []):
            if r.get("areaCode") == area_code:
                return float(r.get("ratePerMinute", 0.0))
        return 0.0

    def compute_all_fees(self):
        """根据通话记录和长途费率计算所有通话费用，并保存到 fees.json。"""
        fees_list = []
        for call in self.calls.get("callRecords", []):
            call_id = call.get("callId")
            caller_number = call.get("callerNumber")
            callee_number = call.get("calleeNumber")
            duration_seconds = int(call.get("durationSeconds", 0))
            call_type = call.get("callType", "local")
            area_code = call.get("longDistanceAreaCode")

            # 通话时长（分钟），不满 1 分钟按 1 分钟算
            minutes = math.ceil(duration_seconds / 60.0)
            # 本地话费
            local_fee = calc_local_fee(minutes)
            # 长途话费
            long_fee = 0.0
            if call_type == "long-distance":
                rate = self.get_rate(area_code)
                long_fee = rate * minutes

            local_fee = round(local_fee, 2)
            long_fee = round(long_fee, 2)
            total_fee = round(local_fee + long_fee, 2)

            user_name = self.get_user_name(caller_number)

            fees_list.append({
                "callId": call_id,
                "callerNumber": caller_number,
                "calleeNumber": callee_number,
                "userName": user_name,
                "localFee": local_fee,
                "longDistanceFee": long_fee,
                "totalFee": total_fee
            })

        self.fees = {"fees": fees_list}
        self._save_json(FEES_FILE, self.fees)

    # ---------- 查询接口 ----------

    def query_fee_summary(self, phone_number: str):
        """
        话费查询：返回 userName, local_sum, long_sum, total_sum
        """
        user_name = self.get_user_name(phone_number)
        local_sum = 0.0
        long_sum = 0.0

        for fee in self.fees.get("fees", []):
            if fee.get("callerNumber") == phone_number:
                local_sum += float(fee.get("localFee", 0.0))
                long_sum += float(fee.get("longDistanceFee", 0.0))

        local_sum = round(local_sum, 2)
        long_sum = round(long_sum, 2)
        total_sum = round(local_sum + long_sum, 2)

        return user_name, local_sum, long_sum, total_sum

    def query_call_records(self, phone_number: str):
        """
        话单查询：返回记录列表
        """
        user_name = self.get_user_name(phone_number)
        records = []
        for call in self.calls.get("callRecords", []):
            if call.get("callerNumber") == phone_number:
                records.append({
                    "userName": user_name,
                    "callerNumber": call.get("callerNumber"),
                    "calleeNumber": call.get("calleeNumber"),
                    "durationSeconds": call.get("durationSeconds"),
                    "callType": call.get("callType", "local")
                })
        return records


# -------------------- 图形界面 --------------------

class BillingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("模拟电信计费系统")
        self.geometry("950x620")
        self.resizable(False, False)

        self.billing = BillingSystem()

        self._create_widgets()

        # 启动时就开启 5 秒一次的自动计费轮询
        self.start_auto_recompute()

    def _create_widgets(self):
        # 使用 Notebook 创建多页面
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)

        # 页面 1：用户信息查询
        self.page_user = ttk.Frame(notebook)
        notebook.add(self.page_user, text="用户信息查询")

        # 页面 2：话费与话单查询
        self.page_billing = ttk.Frame(notebook)
        notebook.add(self.page_billing, text="话费与话单查询")

        self._build_page_user()
        self._build_page_billing()

    # ---------- 自动轮询计费 ----------

    def start_auto_recompute(self):
        """
        每 5 秒自动重新计算一次费用。
        使用 Tkinter 的 after，不阻塞界面。
        """
        try:
            self.billing.compute_all_fees()
        except Exception as e:
            # 不弹框打扰用户，只简单打印
            print("自动计算费用出错：", e)
        # 5000 毫秒后再次调用自己
        self.after(5000, self.start_auto_recompute)

    # ---------- 页面 1：用户信息查询 ----------

    def _build_page_user(self):
        frame_top = ttk.LabelFrame(self.page_user, text="按姓名查询用户", padding=10)
        frame_top.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        ttk.Label(frame_top, text="姓名：").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.name_entry = ttk.Entry(frame_top, width=25)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        btn_search_name = ttk.Button(frame_top, text="查询用户", command=self.on_search_user_by_name)
        btn_search_name.grid(row=0, column=2, padx=10, pady=5)

        btn_clear_users = ttk.Button(frame_top, text="清空结果", command=self.on_clear_user_table)
        btn_clear_users.grid(row=0, column=3, padx=10, pady=5)

        frame_table = ttk.LabelFrame(self.page_user, text="查询结果（用户及名下手机号）", padding=10)
        frame_table.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        columns = ("userId", "userName", "phoneNumber")
        self.user_tree = ttk.Treeview(frame_table, columns=columns, show="headings", height=15)
        self.user_tree.heading("userId", text="用户ID")
        self.user_tree.heading("userName", text="用户名")
        self.user_tree.heading("phoneNumber", text="手机号")

        self.user_tree.column("userId", width=100, anchor=tk.CENTER)
        self.user_tree.column("userName", width=150, anchor=tk.CENTER)
        self.user_tree.column("phoneNumber", width=200, anchor=tk.CENTER)

        self.user_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(frame_table, orient=tk.VERTICAL, command=self.user_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.user_tree.configure(yscrollcommand=scrollbar.set)

        # 绑定 Ctrl + C 复制选中行内容
        self.user_tree.bind("<Control-c>", self.on_copy_user_row)

        # 底部提示
        self.user_hint_label = ttk.Label(
            self.page_user,
            text="提示：支持模糊查询，例如输入“张”可列出所有姓名中包含“张”的用户；"
                 "选中一行后按 Ctrl + C 可复制该行信息。",
            foreground="gray"
        )
        self.user_hint_label.pack(side=tk.BOTTOM, anchor=tk.W, padx=15, pady=5)

    def on_search_user_by_name(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("提示", "请先输入姓名！")
            return

        try:
            users = self.billing.find_users_by_name(name)
            # 清空表格
            for item in self.user_tree.get_children():
                self.user_tree.delete(item)

            if not users:
                messagebox.showinfo("提示", f"未找到姓名包含“{name}”的用户。")
                return

            for u in users:
                self.user_tree.insert(
                    "",
                    tk.END,
                    values=(u.get("userId"), u.get("userName"), u.get("phoneNumber"))
                )
        except Exception as e:
            messagebox.showerror("错误", f"查询用户时发生错误：{e}")

    def on_clear_user_table(self):
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)

    def on_copy_user_row(self, event):
        """
        当按下 Ctrl + C 时，将当前选中的行复制到剪贴板。
        格式：用户ID\t用户名\t手机号
        """
        selected = self.user_tree.selection()
        if not selected:
            return
        lines = []
        for item in selected:
            values = self.user_tree.item(item, "values")
            # 用制表符拼接，方便粘贴到 Excel / 文本
            line = "\t".join(str(v) for v in values)
            lines.append(line)
        text = "\n".join(lines)
        try:
            self.clipboard_clear()
            self.clipboard_append(text)
            # 轻微提示（不弹框，避免打扰）
            self.user_hint_label.config(
                text=f"已复制到剪贴板：{text}    （可以在其他地方 Ctrl + V 粘贴）",
                foreground="green"
            )
        except Exception as e:
            print("复制到剪贴板失败：", e)

    # ---------- 页面 2：话费与话单查询 ----------

    def _build_page_billing(self):
        # 顶部输入区域
        top_frame = ttk.Frame(self.page_billing, padding=10)
        top_frame.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(top_frame, text="电话号码：").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.phone_entry = ttk.Entry(top_frame, width=25)
        self.phone_entry.grid(row=0, column=1, padx=5, pady=5)

        # 不再需要“重新计算全部费用”按钮
        btn_query_fee = ttk.Button(top_frame, text="话费查询", command=self.on_query_fee)
        btn_query_fee.grid(row=0, column=2, padx=10, pady=5)

        btn_query_calls = ttk.Button(top_frame, text="话单查询", command=self.on_query_calls)
        btn_query_calls.grid(row=0, column=3, padx=10, pady=5)

        # 中间：话费查询结果（文本显示）
        summary_frame = ttk.LabelFrame(self.page_billing, text="话费查询结果", padding=10)
        summary_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        self.summary_label = ttk.Label(
            summary_frame,
            text="在上方输入电话号码，然后点击“话费查询”或“话单查询”。\n"
                 "提示：系统每 5 秒自动刷新一次费用文件。",
            font=("微软雅黑", 11)
        )
        self.summary_label.pack(anchor=tk.W)

        # 底部：话单查询结果（表格）
        records_frame = ttk.LabelFrame(self.page_billing, text="话单查询结果", padding=10)
        records_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        columns = ("userName", "callerNumber", "calleeNumber", "durationSeconds", "callType")
        self.tree = ttk.Treeview(records_frame, columns=columns, show="headings", height=15)
        self.tree.heading("userName", text="用户名")
        self.tree.heading("callerNumber", text="主叫号码")
        self.tree.heading("calleeNumber", text="被叫号码")
        self.tree.heading("durationSeconds", text="通话时长(秒)")
        self.tree.heading("callType", text="通话类型")

        self.tree.column("userName", width=100, anchor=tk.CENTER)
        self.tree.column("callerNumber", width=150, anchor=tk.CENTER)
        self.tree.column("calleeNumber", width=150, anchor=tk.CENTER)
        self.tree.column("durationSeconds", width=120, anchor=tk.CENTER)
        self.tree.column("callType", width=100, anchor=tk.CENTER)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(records_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

    # ---------- 页面 2 按钮事件 ----------

    def on_query_fee(self):
        """话费查询：汇总本地费、长途费与总计。"""
        phone = self.phone_entry.get().strip()
        if not phone:
            messagebox.showwarning("提示", "请先输入电话号码！")
            return

        try:
            user_name, local_sum, long_sum, total_sum = self.billing.query_fee_summary(phone)
            if local_sum == 0.0 and long_sum == 0.0:
                msg = f"用户名：{user_name}    电话号码：{phone}\n该号码没有通话记录。"
            else:
                msg = (
                    f"用户名：{user_name}    电话号码：{phone}\n"
                    f"本地话费合计：{local_sum:.2f} 元    "
                    f"长途话费合计：{long_sum:.2f} 元    "
                    f"话费总计：{total_sum:.2f} 元\n"
                    f"（费用文件会每 5 秒自动刷新一次）"
                )
            self.summary_label.config(text=msg)
        except Exception as e:
            messagebox.showerror("错误", f"查询话费时发生错误：{e}")

    def on_query_calls(self):
        """话单查询：在表格中显示通话记录。"""
        phone = self.phone_entry.get().strip()
        if not phone:
            messagebox.showwarning("提示", "请先输入电话号码！")
            return

        try:
            records = self.billing.query_call_records(phone)
            # 清空表格
            for item in self.tree.get_children():
                self.tree.delete(item)

            if not records:
                messagebox.showinfo("提示", "该号码没有通话记录。")
                return

            for rec in records:
                self.tree.insert(
                    "",
                    tk.END,
                    values=(
                        rec["userName"],
                        rec["callerNumber"],
                        rec["calleeNumber"],
                        rec["durationSeconds"],
                        "长途" if rec["callType"] == "long-distance" else "本地"
                    )
                )
        except Exception as e:
            messagebox.showerror("错误", f"查询话单时发生错误：{e}")


# -------------------- 主程序入口 --------------------

if __name__ == "__main__":
    app = BillingApp()
    app.mainloop()
