"""
原始需求：期间内事务类型是“生产问题”创建数量和状态是关闭的数量，用柱状图
AI对话：根据创建日期，分析每天创建和解决的数量在不同项目中的分布情况
"""

from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator
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
    value = "生产问题"
    df.query("类型 == @value", inplace=True)

    if df.empty:
        print(f"{filename} 查询条件没有数据。")
        return

    # 计算每个项目的创建日期和解决日期数量
    created = df.groupby(["创建日期", "项目名称"]).size().unstack(fill_value=0)
    resolved = df.groupby(["解决日期", "项目名称"]).size().unstack(fill_value=0)

    index_all = set(created.index.to_list()).union(set(resolved.index.to_list()))
    index_all = sorted(index_all)
    # 使用created的索引，将resolved重新索引，并填充缺失值为0
    created = created.reindex(index=index_all, fill_value=0)
    resolved = resolved.reindex(index=index_all, fill_value=0)

    # 创建堆积柱状图
    fig, ax1 = plt.subplots(figsize=(12, 12))

    # 绘制主坐标轴的堆积柱状图
    created.plot(kind="bar", stacked=True, ax=ax1, position=1, width=0.4, label="创建日期")
    # 绘制次坐标轴的堆积柱状图并使用相同颜色
    ax2 = ax1.twinx()
    color_map = {
        col: container.get_children()[0].get_facecolor()
        for col, container in zip(created.columns, ax1.containers)
    }
    resolved_mapped_colors = resolved.columns.map(
        lambda x: color_map[x] if x in color_map else "r"
    )
    resolved.plot(
        kind="bar",
        stacked=True,
        ax=ax2,
        position=0,
        width=0.4,
        color=resolved_mapped_colors,
        label="解决日期",
    )

    # 添加标签
    ax1.set_xlabel("日期")
    ax1.set_ylabel("创建数量")
    ax1.yaxis.set_major_locator(MultipleLocator(1))
    ax1.set_title(f'事务类型是"生产问题"时，不同项目每天创建和解决的数量 \n查询条件：{cond}"')

    ax1.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    # Set the x-axis ticks to match the dates in the DataFrame
    ax1.set_xticks(range(len(created.index)))
    ax1.set_xticklabels([date.strftime("%Y-%m-%d") for date in created.index])
    # 显示图例
    ax1.legend()
    for container in ax1.containers:
        ax1.bar_label(
            container,
            label_type="center",
            labels=[f"{v}" if v != 0 else "" for v in container.datavalues],
        )

    # 设置次坐标的x轴刻度和标签
    ax2.set_xticks(range(len(resolved.index)))
    ax2.set_xticklabels([date.strftime("%Y-%m-%d") for date in resolved.index])

    ax2.set_ylabel("解决数量")

    # 隐藏次坐标轴的图例
    ax2.get_legend().remove()
    for container in ax2.containers:
        ax2.bar_label(
            container,
            label_type="center",
            labels=[f"{v}" if v != 0 else "" for v in container.datavalues],
        )

    # 保存图表
    plt.savefig(f"{outfile}.png", bbox_inches="tight")
