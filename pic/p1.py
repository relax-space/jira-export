"""
计算任务的平均创建时间和解决时间，以便评估任务处理效率
"""

import matplotlib.pyplot as plt
from os import listdir, path as os_path, makedirs
import pandas as pd
from traceback import format_exc
import platform


def getFont():
    if platform.system().lower() == "windows":
        return "Microsoft YaHei"
    elif platform.system().lower() == "darwin":
        print("Songti")


def print_one(pic, folder, filename, font):
    filepath = os_path.join(folder, filename)
    df = pd.read_csv(filepath)
    if df.empty:
        return

    # 假设df是包含任务创建时间和解决时间的数据框
    # 将时间字段转换为日期时间类型
    df["创建时间"] = pd.to_datetime(df["创建时间"])
    df["解决时间"] = pd.to_datetime(df["解决时间"])

    # 计算任务处理时间
    df["处理时间"] = (df["解决时间"] - df["创建时间"]).dt.days
    # 设置中文字体为"Microsoft YaHei"
    plt.rcParams["font.family"] = font
    # 创建图表
    fig, ax = plt.subplots()
    ax.hist(df["处理时间"], bins=20, edgecolor="black")

    # 设置图表标题和标签
    ax.set_title("任务处理时间分布")
    ax.set_xlabel("处理时间（天）")
    ax.set_ylabel("任务数量")

    # 显示图表
    pic_name = filename.replace(".csv", ".png")
    plt.savefig(os_path.join(pic, pic_name))


def loop_all():
    if not os_path.isdir("pic1"):
        makedirs("pic1")
    if not os_path.isdir("pic2"):
        makedirs("pic2")
    font = getFont()
    pic = "pic1"
    folder = "new1"
    for i in listdir(folder):
        if i == "init":
            continue
        # if i != "POC8.csv":
        #     continue
        try:
            print_one(pic, folder, i, font)
        except Exception as e:
            pass
            # print(i)
            # print(format_exc())
    pass


if __name__ == "__main__":
    loop_all()
