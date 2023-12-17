"""
一周内，团队每个人每天处理的事务功的工时
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
        return "Arial Unicode MS"


def print_one(pic, folder, filename, font):
    filepath = os_path.join(folder, filename)
    df = pd.read_csv(filepath)
    if df.empty:
        return
    plt.rcParams["font.family"] = font
    # Convert 创建时间 to datetime type
    df["创建时间"] = pd.to_datetime(df["创建时间"])

    # Group by 创建时间 and 工作日志创建者, and calculate the sum of 花费时间 for each day and creator
    daily_time_spent_by_creator = (
        df.groupby([df["创建时间"].dt.date, "工作日志创建者"])["花费时间"].sum().unstack()
    )

    # Plotting the data
    daily_time_spent_by_creator.plot(kind="bar", stacked=True, figsize=(12, 8))
    plt.title("Time Spent Each Day by Work Log Creator")
    plt.xlabel("Date")
    plt.ylabel("Total Time Spent")
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
        if i != "POC8.csv":
            continue
        try:
            print_one(pic, folder, i, font)
        except Exception as e:
            pass
            print(i, e)
            # print(format_exc())
    pass


if __name__ == "__main__":
    loop_all()
