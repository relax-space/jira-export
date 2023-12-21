"""
经办人预估工时与实际工时对比
"""

import matplotlib.pyplot as plt
import pandas as pd


def start(in_file, out_file, project_keys, params):
    log_start, log_end, sprint_start, sprint_end = params
    df = pd.read_excel(in_file)
    if df.empty:
        return
    project_names = []
    unique_project_key = set()
    if project_keys:
        df.query("项目秘钥 in @project_keys", inplace=True)
        for key in project_keys:
            for i, row in df.iterrows():
                if key not in unique_project_key:
                    if row["项目秘钥"] == key:
                        project_names.append(row["项目名称"])
                        unique_project_key.add(key)
    project_name = "||".join(project_names)
    if sprint_start:
        df.query("迭代开始时间 >= @sprint_start and 迭代结束时间 <= @sprint_end", inplace=True)

    if log_start:
        pass

    # 按 '经办人' 分组，并计算预估工时和实际工时的总和
    grouped = df.groupby("经办人")[["预估工时", "实际工时"]].sum()

    # 创建柱状图
    grouped.plot(kind="bar")
    for container in plt.gca().containers:
        plt.bar_label(container, label_type="edge")

    plt.xlabel("经办人")
    plt.ylabel("工时(小时)")
    plt.title(f"{project_name} 经办人预估工时与实际工时对比")
    # 显示图表
    plt.savefig(out_file)
