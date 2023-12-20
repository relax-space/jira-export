"""
根据创建时间，分析每天实际工时在不同"经办人"下的分布情况
"""

import matplotlib.pyplot as plt
from os import path as os_path, chdir
import pandas as pd

from sys import path as sys_path


def print_one(in_file, out_file, font, project_keys):
    df = pd.read_excel(in_file)
    if df.empty:
        return
    project_name = ""
    if project_keys:
        df.query("项目秘钥 in @project_keys", inplace=True)
        if not df["项目名称"].empty:
            project_name = df["项目名称"].iloc[0]
    plt.rcParams["font.family"] = font
    # Convert 创建时间 to datetime type
    df["创建时间"] = pd.to_datetime(df["创建时间"])

    # Group by 创建时间 and 工作日志创建者, and calculate the sum of 实际工时 for each day and creator
    daily_time_spent_by_creator = (
        df.groupby([df["创建时间"].dt.date, "经办人"])["实际工时"].sum().unstack()
    )

    # Plotting the data
    daily_time_spent_by_creator.plot(kind="bar", stacked=True, figsize=(12, 8))
    for container in plt.gca().containers:
        plt.bar_label(container, label_type="center")

    plt.title(f"{project_name} 每天的实际工时")
    plt.xlabel("日期")
    plt.ylabel("实际工时(小时)")
    # 显示图表
    plt.savefig(out_file)


if __name__ == "__main__":
    p = os_path.dirname(os_path.dirname(os_path.abspath(__file__)))
    sys_path.insert(0, p)
    chdir(p)
    from relax.util import gen_dir
    from relax.util import getFont

    root_folder = "data1"
    pic_folder = "pic"
    in_file = os_path.join(root_folder, "task", "d1.xlsx")
    project_keys = ["BSNDDC", "POC8"]

    out_folder = os_path.join(root_folder, pic_folder)
    gen_dir(out_folder)
    file_name = f"{'_'.join(project_keys)}_{os_path.basename(__file__)}".replace(
        ".py", ".png"
    )
    out_file = os_path.join(out_folder, file_name)
    font = getFont()

    try:
        print_one(in_file, out_file, font, project_keys)
    except Exception as e:
        pass
        print(e)
