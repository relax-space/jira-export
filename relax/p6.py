"""
根据日志创建日期，分析每天日志记录工时在不同"日志创建人"下的分布情况
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
    if df.empty:
        print(f"{filename} 查询条件没有数据。")
        return
    hour_number = df.groupby(["日志创建人"]).ngroups
    work_hour = round(hour_number * 8 * 0.8, 1)
    group = df.groupby([df["日志创建日期"], "日志创建人"])["日志记录工时"].sum().unstack()

    # Plotting the data
    group.plot(kind="bar", stacked=True, figsize=(12, 8))

    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1))
    plt.gca().set_xticks(range(len(group.index)))
    plt.gca().set_xticklabels([date.strftime("%Y-%m-%d") for date in group.index])

    x_start = 0.5
    x_end = len(group) - 0.5

    # Add the horizontal line with specified start and end points, color, and linestyle
    plt.axhline(
        y=work_hour,
        color="g",
        linestyle="-",
        label="Average Work Hours",
        xmin=x_start / len(group),
        xmax=x_end / len(group),
    )
    plt.text(
        x_end,
        work_hour,
        f"{work_hour}",
        va="center",
        ha="right",
        backgroundcolor="w",
    )

    plt.legend()
    for container in plt.gca().containers:
        plt.bar_label(
            container,
            label_type="center",
            labels=[f"{v}" if v != 0 else "" for v in container.datavalues],
        )
    # [{date1.strftime('%Y-%m-%d')}~{date2.strftime('%Y-%m-%d')}]
    plt.title(f"成员工时每日分布 \n查询条件：{cond}")
    plt.xlabel("日期")
    plt.ylabel("实际工时(小时)")
    # 显示图表
    plt.savefig(f"{outfile}.png", bbox_inches="tight")
