"""
期间查询所有项目的工时分布占比
"""

from matplotlib import pyplot as plt
from pandas import read_excel, to_datetime
from datetime import date
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

    group = df.groupby(["项目名称"])[["日志记录工时"]].sum()

    def calc(pct):
        work_hours = round(pct / 100.0 * sum(group.sum(axis=1)), 1)
        return f"{pct:.2f}%\n{work_hours}h"

    # Plotting the data
    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(
        group.sum(axis=1),
        labels=group.index,
        autopct=lambda pct: calc(pct),
        startangle=140,
    )

    for container in plt.gca().containers:
        plt.bar_label(
            container,
            label_type="center",
            labels=[f"{v}" if v != 0 else "" for v in container.datavalues],
        )

    plt.title(f"期间内所有项目的工时分布占比 \n查询条件：{cond}")
    # 显示图表
    plt.savefig(f"{outfile}.png", bbox_inches="tight")
