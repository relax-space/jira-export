"""
统计各个项目生产问题的响应时长和生存时长
"""

from matplotlib import pyplot as plt
from pandas import read_excel, to_datetime
from datetime import date
from os import path as os_path
import matplotlib.dates as mdates
from numpy import timedelta64

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
            "创建时间": to_datetime,
            "解决时间": to_datetime,
            "日志创建日期": to_datetime,
        },
    )
    df_log = read_excel(
        os_path.join(root_folder, "raw", "raw_log.xlsx"),
        converters={
            "进行中时间": to_datetime,
        },
    )
    if df.empty:
        print("数据为空！")
        return
    if df_log.empty:
        print("历史数据为空！")
        return
    cond, outfile = df_filter(out_folder, filename, df, params)

    df.drop_duplicates(subset=["编号"], keep="first", inplace=True)

    df = df.loc[:, ["编号", "类型", "项目名称", "创建时间", "解决时间"]]
    df_log = df_log.loc[:, ["事务编号", "进行中时间"]]
    df_log.dropna(subset=["进行中时间"], inplace=True)

    df = df.merge(df_log, how="inner", left_on="编号", right_on="事务编号")

    df["生产问题响应时长"] = (
        ((df["进行中时间"] - df["创建时间"]).map(lambda x: x / timedelta64(1, "h")))
        .fillna(0)
        .astype(int)
    )
    df["生产问题生存时长"] = (
        ((df["解决时间"] - df["创建时间"]).map(lambda x: x / timedelta64(1, "h")))
        .fillna(0)
        .astype(int)
    )

    grouped = df.groupby("项目名称")[["生产问题响应时长", "生产问题生存时长"]].sum()

    # 创建一个新的图表，显示柱状图和折线图
    fig, ax1 = plt.subplots(figsize=(12, 8))
    # 绘制柱状图
    grouped[["生产问题响应时长", "生产问题生存时长"]].plot(
        kind="bar", ax=ax1, color=["skyblue", "lightgreen"]
    )
    ax1.set_xlabel("项目名称")
    ax1.set_ylabel("时长(小时)")
    # ax1.set_ylim(bottom=-15, top=15)  # 设置y轴范围
    plt.title(f"统计项目生产问题的响应时长和生存时长 \n查询条件：{cond}")

    for container in plt.gca().containers:
        plt.bar_label(
            container,
            label_type="center",
            labels=[f"{v}" if v != 0 else "" for v in container.datavalues],
        )
    # 显示图表
    plt.savefig(f"{outfile}.png", bbox_inches="tight")
