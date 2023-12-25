"""
经办人预估工时与实际工时对比
"""

from matplotlib import pyplot as plt
from pandas import read_excel, to_datetime
from datetime import date
from os import path as os_path

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

    # 按 '经办人' 分组，并计算预估工时和实际工时的总和
    grouped = df.groupby("经办人")[["预估工时", "实际工时"]].sum()

    # 创建柱状图
    grouped.plot(kind="bar", figsize=(12, 8))
    for container in plt.gca().containers:
        plt.bar_label(container, label_type="edge")

    plt.xlabel("经办人")
    plt.ylabel("工时(小时)")
    plt.title(f"经办人预估工时与实际工时对比 \n查询条件：{cond}")
    # 显示图表
    plt.savefig(f"{outfile}.png")
