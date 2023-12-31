"""
项目预估工时与实际工时对比
"""

from matplotlib import pyplot as plt
from pandas import read_excel, to_datetime
from datetime import date
from os import path as os_path
import matplotlib.ticker as mtick

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

    df.drop_duplicates(subset=["编号"], keep="first", inplace=True)

    status = "完成"
    df.query("解决方案 == @status", inplace=True)

    if df.empty:
        print(f"{filename} 查询条件没有数据。")
        return

    # 按 '项目' 分组，并计算预估工时和实际工时的总和
    grouped = df.groupby("项目名称")[["预估工时", "实际工时"]].sum()

    # 去除所有预估工时为0的数据
    grouped = grouped[grouped["预估工时"] != 0]

    # 计算预估偏差率
    grouped["预估偏差率"] = (grouped["实际工时"] - grouped["预估工时"]) / grouped["预估工时"]
    # 计算预估偏差率的平均值
    avg_deviation = grouped["预估偏差率"].mean()

    # 创建一个新的图表，显示柱状图和折线图
    fig, ax1 = plt.subplots(figsize=(12, 8))
    # 绘制柱状图
    grouped[["预估工时", "实际工时"]].plot(kind="bar", ax=ax1, color=["skyblue", "lightgreen"])
    ax1.set_xlabel("项目名称")
    ax1.set_ylabel("工时(小时)")
    # ax1.set_ylim(bottom=-15, top=15)  # 设置y轴范围
    plt.title(f"项目预估工时与实际工时对比，并且计算预估偏差率 \n查询条件：{cond}")

    for i in ax1.patches:
        # get_x pulls left or right; get_height pushes up or down
        ax1.text(
            i.get_x() + i.get_width() / 2,
            i.get_height() + 0.5,
            str(round(i.get_height(), 2)),
            ha="center",
            va="bottom",
        )

    # 创建第二个y轴
    ax2 = ax1.twinx()
    # 绘制折线图表示偏差率
    line = ax2.plot(
        grouped.index, grouped["预估偏差率"], color="r", marker="o", label="预估偏差率"
    )
    ax2.axhline(y=avg_deviation, color="b", linestyle="--", label="平均偏差率")
    ax2.axhline(y=0, color="g", linestyle="--", label="无偏差")
    ax2.set_ylabel("偏差率 (%)", color="r")
    ax2.yaxis.set_label_coords(1.05, 0)  # 将y轴标签和y轴重合
    # ax2.set_ylim(bottom=-1.5, top=1.5)  # 设置y轴范围
    ax2.set_ylim(
        bottom=grouped["预估偏差率"].min() - 0.4, top=grouped["预估偏差率"].max() + 0.4
    )  # 设置y轴范围，增加5%的余量
    ax2.yaxis.set_major_locator(plt.MaxNLocator(10))  # 设置y轴刻度间距

    fmt = "{x:,.0%}"
    tick = mtick.StrMethodFormatter(fmt)
    ax2.yaxis.set_major_formatter(tick)  # 格式化y轴标签为百分比形式

    for i in range(len(grouped["预估偏差率"])):
        v = grouped["预估偏差率"][i]
        ax2.text(
            i,
            v,
            f"{v*100:.2f}%",
            ha="center",
            va="bottom",
        )

    plt.legend()

    plt.savefig(f"{outfile}.png", bbox_inches="tight")
