"""
经办人预估工时与实际工时对比
"""

from matplotlib import pyplot as plt
from pandas import read_excel, to_datetime
from datetime import date
from os import path as os_path


def start(out_folder, in_file, filename, project_keys, params: tuple[date, date, date]):
    log_start, log_end, sprint_date = params
    df = read_excel(
        in_file,
        converters={
            "迭代开始时间": to_datetime,
            "迭代结束时间": to_datetime,
            "日志创建时间": to_datetime,
        },
    )
    if df.empty:
        return
    project_names = []
    unique_project_key = set()
    cond = ""
    if project_keys:
        df.query("项目秘钥 in @project_keys", inplace=True)
        cond += f"项目[{','.join(project_keys)}]\n"
        for key in project_keys:
            for i, row in df.iterrows():
                if key not in unique_project_key:
                    if row["项目秘钥"] == key:
                        project_names.append(row["项目名称"])
                        unique_project_key.add(key)
    project_name = "||".join(project_names)

    outfile = os_path.join(out_folder, f"{'_'.join(project_keys)}_{filename}")
    if sprint_date:
        df.dropna(subset=["迭代开始时间", "迭代结束时间"], inplace=True)
        df.query("@sprint_date >= 迭代开始时间 and @sprint_date <= 迭代结束时间", inplace=True)
        cond += f"迭代{sprint_date}\n"
        outfile += f'_sprint{sprint_date.strftime("%Y%m%d")}'

    if log_start:
        df.query("日志创建时间 >= @log_start and 日志创建时间 <= @log_end", inplace=True)
        cond += f"日志期间[{log_start}~{log_end}]"
        outfile += (
            f'_worklog{log_start.strftime("%Y%m%d")}_{log_end.strftime("%Y%m%d")}'
        )

    df.drop_duplicates(subset=["编号"], keep="first", inplace=True)

    # 按 '经办人' 分组，并计算预估工时和实际工时的总和
    grouped = df.groupby("经办人")[["预估工时", "实际工时"]].sum()

    # 创建柱状图
    grouped.plot(kind="bar", figsize=(12, 8))
    for container in plt.gca().containers:
        plt.bar_label(container, label_type="edge")

    plt.xlabel("经办人")
    plt.ylabel("工时(小时)")
    plt.title(f"{project_name} 经办人预估工时与实际工时对比 \n查询条件：{cond}")
    # 显示图表
    plt.savefig(f"{outfile}.png")
