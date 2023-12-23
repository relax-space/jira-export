"""
根据日志创建日期，分析每天日志记录工时在不同"日志创建人"下的分布情况
"""

from matplotlib import pyplot as plt
from pandas import read_excel, to_datetime
from datetime import date
from os import path as os_path


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

    if sprint_date:
        df.dropna(subset=["迭代开始日期", "迭代结束日期"], inplace=True)
        df.query("@sprint_date >= 迭代开始日期 and @sprint_date <= 迭代结束日期", inplace=True)
        cond += f"迭代{sprint_date}\n"
        outfile += f'_sprint{sprint_date.strftime("%Y%m%d")}'
    if catelogs:
        df.query("项目类别 in @catelogs", inplace=True)
        cond += f"项目类别{','.join(catelogs)}\n"
        outfile += f"_项目类别{'_'.join(catelogs)}"

    if df.empty:
        print(f"{filename} 查询条件没有数据。")
        return

    # df.query("日志创建日期 >= @date1 and 日志创建日期 <= @date2", inplace=True)
    # Group by 创建日期 and 工作日志创建者, and calculate the sum of 日志记录工时 for each day and creator
    # hour_number = get_workday_count(date1, date2)
    hour_number = df.groupby(["日志创建人"]).ngroups
    work_hour = round(hour_number * 8 * 0.8, 1)
    daily_time_spent_by_creator = (
        df.groupby([df["日志创建日期"], "日志创建人"])["日志记录工时"].sum().unstack()
    )

    # Plotting the data
    daily_time_spent_by_creator.plot(kind="bar", stacked=True, figsize=(12, 8))
    x_start = 0.5
    x_end = len(daily_time_spent_by_creator) - 0.5

    # Add the horizontal line with specified start and end points, color, and linestyle
    plt.axhline(
        y=work_hour,
        color="g",
        linestyle="-",
        label="Average Work Hours",
        xmin=x_start / len(daily_time_spent_by_creator),
        xmax=x_end / len(daily_time_spent_by_creator),
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
