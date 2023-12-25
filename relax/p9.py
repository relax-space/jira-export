"""
期间内类型-状态分布
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

    group = df.groupby(["类型", "状态"]).size().unstack(fill_value=0)

    # Plotting the data
    group.plot(kind="bar", stacked=True, figsize=(12, 8))

    plt.legend()
    for container in plt.gca().containers:
        plt.bar_label(
            container,
            label_type="center",
            labels=[f"{v}" if v != 0 else "" for v in container.datavalues],
        )
    plt.title(f"期间内类型-状态分布 \n查询条件：{cond}")
    plt.xlabel("类型")
    plt.ylabel("状态数量")
    # 显示图表
    plt.savefig(f"{outfile}.png", bbox_inches="tight")
