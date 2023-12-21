"""
根据日志创建时间，分析每天日志记录工时在不同"日志创建人"下的分布情况
"""

import matplotlib.pyplot as plt
import pandas as pd
from pandas import DataFrame
from datetime import date

from chinese_calendar import is_workday, is_holiday


def start(in_file, out_file, project_keys):
    df = pd.read_excel(in_file)
    if df.empty:
        return
    project_names = []
    unique_project_key = set()
    if project_keys:
        df.query("项目秘钥 in @project_keys", inplace=True)
        for key in project_keys:
            for i, row in df.iterrows():
                if key not in unique_project_key:
                    if row["项目秘钥"] == key:
                        project_names.append(row["项目名称"])
                        unique_project_key.add(key)
    project_name = "||".join(project_names)
    # Convert 创建时间 to datetime type
    df["日志创建时间"] = pd.to_datetime(df["日志创建时间"])
    rows = []
    for i, row in df.iterrows():
        if is_workday(row["日志创建时间"]):
            rows.append(row)
    df = DataFrame(rows)

    # df.query("日志创建时间 >= @date1 and 日志创建时间 <= @date2", inplace=True)
    # Group by 创建时间 and 工作日志创建者, and calculate the sum of 日志记录工时 for each day and creator
    # hour_number = get_workday_count(date1, date2)
    hour_number = df.groupby(["日志创建人"]).ngroups
    print(hour_number)
    work_hour = round(hour_number * 8 * 0.8, 1)
    daily_time_spent_by_creator = (
        df.groupby([df["日志创建时间"].dt.date, "日志创建人"])["日志记录工时"].sum().unstack()
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
    plt.title(f"{project_name} 每天的实际工时")
    plt.xlabel("日期")
    plt.ylabel("实际工时(小时)")
    # 显示图表
    plt.savefig(out_file)
