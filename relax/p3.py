"""
期间内缺陷创建量与解决量趋势
"""

from matplotlib import pyplot as plt
from pandas import read_excel, to_datetime
from datetime import date
from os import path as os_path
import matplotlib.dates as mdates

from relax.util_biz import df_filter


def start(
    out_folder,
    root_folder,
    in_file,
    filename,
    params: tuple[date, date, date, date, date, list, list, list],
):
    df = read_excel(
        in_file,
        converters={
            "迭代开始日期": to_datetime,
            "迭代结束日期": to_datetime,
            "创建日期": to_datetime,
            "解决日期": to_datetime,
            "日志创建日期": to_datetime,
        },
    )
    if df.empty:
        return
    cond, outfile = df_filter(out_folder, filename, df, params)
    df.drop_duplicates(subset=["编号"], keep="first", inplace=True)
    if df.empty:
        print(f"{filename} 查询条件没有数据。")
        return

    # 计算每天的BUG创建数量和关闭数量
    daily_bug_created = df["创建日期"].value_counts().sort_index()
    daily_bug_closed = df["解决日期"].value_counts().sort_index()
    # 创建折线图
    plt.figure()
    plt.plot(
        daily_bug_created.index, daily_bug_created.values, label="BUG创建数量", marker="o"
    )
    plt.plot(daily_bug_closed.index, daily_bug_closed.values, label="关闭数量", marker="x")

    # 设置横坐标文字竖着显示
    plt.xticks(rotation="vertical")
    # plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1))

    # 设置日期格式
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))

    # 显示每个节点的数据
    for a, b in zip(daily_bug_created.index, daily_bug_created.values):
        plt.text(a, b, str(b))

    for a, b in zip(daily_bug_closed.index, daily_bug_closed.values):
        plt.text(a, b, str(b))

    # 添加网格线
    plt.grid(True)

    # 设置图表标题和坐标轴标签
    plt.title(f"期间内缺陷创建量与解决量趋势 \n查询条件：{cond}")
    plt.xlabel("日期")
    plt.ylabel("数量")

    # 显示图例
    plt.legend()

    plt.savefig(f"{outfile}.png", bbox_inches="tight")
