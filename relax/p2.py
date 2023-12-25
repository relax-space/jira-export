"""
期间内团队成员饱和度 成员期间内登记的工时总和/（8小时*期间天数） 期间天数不含周末及休假 
"""

from matplotlib import pyplot as plt
from matplotlib.ticker import PercentFormatter
from pandas import read_excel, to_datetime
from datetime import date
from os import path as os_path
from relax.util import get_workday_count
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

    if df.empty:
        print(f"{filename} 查询条件没有数据。")
        return

    # 按 '项目' 分组，并计算预估工时和实际工时的总和
    grouped = df.groupby("日志创建人")[["日志记录工时"]].sum()

    (_, _, log_start, log_end, _, _, _, _) = params
    standard_hour = get_workday_count(log_start, log_end) * 8

    # 计算每个日志创建人的日志记录工时总和除以standard_hour
    grouped["饱和度"] = grouped["日志记录工时"] / standard_hour

    grouped.drop(columns=["日志记录工时"], inplace=True)

    grouped.plot(kind="bar", figsize=(12, 8))
    # 将纵坐标格式转换为百分比
    plt.gca().yaxis.set_major_formatter(PercentFormatter(1))

    for container in plt.gca().containers:
        plt.bar_label(
            container,
            label_type="edge",
            labels=[f"{v*100:.2f}%" if v != 0 else "" for v in container.datavalues],
        )

    # 设置图表标题和坐标轴标签
    plt.title(f"期间内团队成员饱和度 \n查询条件：{cond}")
    plt.xlabel("成员")
    plt.ylabel("饱和度")

    plt.legend()

    plt.savefig(f"{outfile}.png", bbox_inches="tight")
