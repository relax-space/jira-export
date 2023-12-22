"""
期间内团队成员饱和度 成员期间内登记的工时总和/（8小时*期间天数） 期间天数不含周末及休假 
"""

from matplotlib import pyplot as plt
from matplotlib.ticker import PercentFormatter
from pandas import read_excel, to_datetime
from datetime import date
from os import path as os_path
from relax.util import get_workday_count


def start(
    out_folder,
    in_file,
    filename,
    project_keys,
    params: tuple[date, date, date, list, list],
):
    log_start, log_end, sprint_date, exclude_project_keys, catelogs = params
    df = read_excel(
        in_file,
        converters={
            "迭代开始日期": to_datetime,
            "迭代结束日期": to_datetime,
            "日志创建日期": to_datetime,
        },
    )
    if df.empty:
        return
    unique_project_key = set()
    cond = ""
    if project_keys:
        df.query("项目秘钥 in @project_keys", inplace=True)
        cond += f"项目[{','.join(project_keys)}]\n"
        for key in project_keys:
            for i, row in df.iterrows():
                if key not in unique_project_key:
                    if row["项目秘钥"] == key:
                        unique_project_key.add(key)

    if exclude_project_keys:
        df.query("项目秘钥 not in @exclude_project_keys", inplace=True)

    outfile = os_path.join(out_folder, f"{'_'.join(project_keys)}_{filename}")
    if log_start:
        df.query("日志创建日期 >= @log_start and 日志创建日期 <= @log_end", inplace=True)
        cond += f"日志期间[{log_start}~{log_end}]\n"
        outfile += (
            f'_worklog{log_start.strftime("%Y%m%d")}_{log_end.strftime("%Y%m%d")}'
        )

    df.drop_duplicates(subset=["编号"], keep="first", inplace=True)

    if sprint_date:
        df.dropna(subset=["迭代开始日期", "迭代结束日期"], inplace=True)
        df.query("@sprint_date >= 迭代开始日期 and @sprint_date <= 迭代结束日期", inplace=True)
        cond += f"迭代{sprint_date}\n"
        outfile += f'_sprint{sprint_date.strftime("%Y%m%d")}'
    if catelogs:
        df.query("项目类别 in @catelogs", inplace=True)
        cond += f"项目类别{','.join(catelogs)}\n"
        outfile += f"_项目类别{'_'.join(catelogs)}"

    # 按 '项目' 分组，并计算预估工时和实际工时的总和
    grouped = df.groupby("日志创建人")[["日志记录工时"]].sum()

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

    plt.legend(loc="upper left")

    plt.savefig(f"{outfile}.png", bbox_inches="tight")
