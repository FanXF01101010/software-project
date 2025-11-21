# -*- coding: utf-8 -*-
"""
实时通话记录生成器：每隔随机时间生成一条通话记录，追加到 calls.json 中。

与计费 GUI 搭配使用：
- 计费 GUI 每 5 秒自动重算话费
- 本脚本负责源数据 calls.json 的“实时”增长
- 【修改】：所有号码（主叫 & 被叫）都来自 users.json，不再生成未知用户
"""

import json
import os
import random
import time
from datetime import datetime

# ===== 基本路径设置 =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE_DIR, "users.json")
RATES_FILE = os.path.join(BASE_DIR, "rates.json")
CALLS_FILE = os.path.join(BASE_DIR, "calls.json")

# ===== 生成间隔（秒）范围，可以根据需要修改 =====
MIN_INTERVAL = 2    # 每条通话之间最短间隔（秒）
MAX_INTERVAL = 10   # 每条通话之间最长间隔（秒）


# ===== 一些初始化工具 =====

def init_sample_users_and_rates():
    """如果 users.json 或 rates.json 不存在，就自动生成一些示例数据。"""
    if not os.path.exists(USERS_FILE):
        users = {
            "users": [
                {"userId": "U001", "userName": "张三", "phoneNumber": "13800000001"},
                {"userId": "U002", "userName": "李四", "phoneNumber": "13800000002"},
                {"userId": "U003", "userName": "王五", "phoneNumber": "01088880000"},
                {"userId": "U004", "userName": "赵六", "phoneNumber": "13900000003"}
            ]
        }
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=4)
        print("[init] 未找到 users.json，已自动生成示例用户文件。")

    if not os.path.exists(RATES_FILE):
        rates = {
            "longDistanceRates": [
                {"areaCode": "010", "areaName": "北京", "ratePerMinute": 0.60},
                {"areaCode": "021", "areaName": "上海", "ratePerMinute": 0.65},
                {"areaCode": "020", "areaName": "广州", "ratePerMinute": 0.70},
                {"areaCode": "025", "areaName": "南京", "ratePerMinute": 0.55}
            ]
        }
        with open(RATES_FILE, "w", encoding="utf-8") as f:
            json.dump(rates, f, ensure_ascii=False, indent=4)
        print("[init] 未找到 rates.json，已自动生成示例长途费率文件。")


def load_json(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# ===== 随机生成通话相关的工具 =====

def random_duration_seconds():
    """
    生成“正常”的通话时长（秒）：
    - 最少 10 秒，最多 600 秒
    - 使用偏短的分布：随机取 0~1 的浮点数做平方
    """
    r = random.random()  # 0~1
    x = r * r            # 平方后更偏向小值
    return int(10 + x * (600 - 10))


def current_time_str():
    """
    使用当前时间作为通话开始时间。
    返回格式：YYYY-MM-DD HH:MM:SS
    """
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


def random_other_user_phone(users, caller_number):
    """
    从已知用户中随机选一个“被叫”号码：
    - 优先选“不是自己”的手机号
    - 如果只有一个用户（极端情况），就允许自己给自己打（至少不会生成未知用户）
    """
    others = [u for u in users if u.get("phoneNumber") != caller_number]
    if others:
        return random.choice(others).get("phoneNumber")
    # 没有别人，只能自己
    return caller_number


# ===== 主逻辑：实时生成通话记录 =====

def prepare_environment():
    """确保用户、费率文件存在，并加载数据；同时加载/初始化 calls.json。"""
    init_sample_users_and_rates()

    users_data = load_json(USERS_FILE, default={"users": []})
    rates_data = load_json(RATES_FILE, default={"longDistanceRates": []})
    calls_data = load_json(CALLS_FILE, default={"callRecords": []})

    users = users_data.get("users", [])
    rate_items = rates_data.get("longDistanceRates", [])
    area_codes = [r["areaCode"] for r in rate_items] if rate_items else ["010"]
    call_records = calls_data.get("callRecords", [])

    # 根据现有记录确定下一个 callId 序号
    next_index = 1
    if call_records:
        last_id = call_records[-1].get("callId", "")
        try:
            num_part = int(last_id.strip("C"))
            next_index = num_part + 1
        except Exception:
            next_index = len(call_records) + 1

    print(f"[init] 当前已有通话记录 {len(call_records)} 条，下一个 callId 将从 C{next_index:04d} 开始。")

    return users, area_codes, call_records, next_index


def realtime_generate_calls():
    """
    无限循环，每隔随机时间生成一条新通话记录，写入 calls.json。
    按 Ctrl + C 可以终止。
    所有号码（主叫 & 被叫）均来自 users.json。
    """
    users, area_codes, call_records, next_index = prepare_environment()

    if not users:
        print("users.json 中没有用户信息，无法生成通话记录。")
        return

    print("===== 实时通话模拟开始 =====")
    print(f"每条通话之间的随机间隔：{MIN_INTERVAL} ~ {MAX_INTERVAL} 秒")
    print("所有主叫 / 被叫号码均来自 users.json，不会出现未知用户。")
    print("按 Ctrl + C 可以停止。")
    print("----------------------------------------")

    try:
        while True:
            # 1. 随机等待一段时间
            interval = random.uniform(MIN_INTERVAL, MAX_INTERVAL)
            time.sleep(interval)

            # 2. 随机生成一条通话记录
            call_id = f"C{next_index:04d}"
            next_index += 1

            caller = random.choice(users)
            caller_number = caller.get("phoneNumber")

            # 70% 本地通话，30% 长途通话
            if random.random() < 0.7:
                call_type = "local"
                callee_number = random_other_user_phone(users, caller_number)
                area_code = None
            else:
                call_type = "long-distance"
                callee_number = random_other_user_phone(users, caller_number)
                # 这里 area_code 与号码本身不强绑定，只是为了给计费用费率
                area_code = random.choice(area_codes)

            duration_seconds = random_duration_seconds()
            start_time = current_time_str()

            new_record = {
                "callId": call_id,
                "callerNumber": caller_number,
                "calleeNumber": callee_number,
                "startTime": start_time,
                "durationSeconds": duration_seconds,
                "callType": call_type,
                "longDistanceAreaCode": area_code
            }

            # 3. 加入内存列表，并写回 calls.json
            call_records.append(new_record)
            save_json(CALLS_FILE, {"callRecords": call_records})

            # 4. 在终端打印一行日志
            print(f"[新增通话] {call_id} | 主叫: {caller_number} | 被叫: {callee_number} | "
                  f"类型: {'长途' if call_type == 'long-distance' else '本地'} | "
                  f"时长: {duration_seconds}s | 时间: {start_time} | "
                  f"下次生成约 {interval:.1f}s 后")

    except KeyboardInterrupt:
        print("\n===== 已停止实时通话模拟 =====")
        print(f"最终总通话记录条数：{len(call_records)}")
        print(f"数据保存在：{CALLS_FILE}")


if __name__ == "__main__":
    realtime_generate_calls()
