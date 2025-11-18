import json
import random

# 固定随机种子，保证每次生成的内容一致（方便你调试）
random.seed(42)

# 班级 & 课程列表
classes = ["电科2301", "电科2302", "电科2303"]
courses = ["高等数学", "半导体物理", "大学物理"]

# 随机姓名用到的一些字
family_names = list("赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜戚谢邹喻柏水窦章苏潘葛范彭郎鲁韦马苗")
given_1 = list("一二三四五六七八九子文明国思志佳婷雪超玲军磊艳静凯杰欣雨蕾浩川宁宇晨")
given_2 = list("一二三四五六七八九子文明国思志佳婷雪超玲军磊艳静凯杰欣雨蕾浩川宁宇晨")

def rand_name():
    return random.choice(family_names) + random.choice(given_1) + random.choice(given_2)

records = []
base_id = 20230001

for i in range(150):
    rec = {
        "class": random.choice(classes),
        "course": random.choice(courses),
        "id": str(base_id + i),
        "name": rand_name(),
        "daily": random.randint(50, 100),   # 平时成绩
        "mid": random.randint(40, 100),     # 期中成绩
        "final": random.randint(30, 100)    # 期末成绩
    }
    records.append(rec)

# 写入 JSON 文件
output_file = "sample_data.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(records, f, ensure_ascii=False, indent=2)

print(f"已生成 {len(records)} 条样本数据，保存为 {output_file}")
