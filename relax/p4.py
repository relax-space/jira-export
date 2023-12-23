"""
期间内缺陷创建量与解决量趋势
"""

from matplotlib import pyplot as plt
from pandas import read_excel, to_datetime
from datetime import date
from os import path as os_path
import matplotlib.dates as mdates


def start(
    out_folder,
    in_file,
    filename,
    project_keys,
    params: tuple[date, date, date, list, list],
):
    create_start, create_end, sprint_date, exclude_project_keys, catelogs = params
    if not create_start:
        print("必须指定期间，create_start不能为空")
        return
    df = read_excel(
        in_file,
        converters={
            "迭代开始日期": to_datetime,
            "迭代结束日期": to_datetime,
            "创建日期": to_datetime,
            "解决日期": to_datetime,
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

    df.drop_duplicates(subset=["编号"], keep="first", inplace=True)
    status = ["缺陷", "缺陷子任务"]
    df.query("类型 in @status", inplace=True)

    outfile = os_path.join(out_folder, f"{'_'.join(project_keys)}_{filename}")
    df.query("创建日期 >= @create_start and 创建日期 <= @create_end", inplace=True)
    cond += f"创建期间[{create_start}~{create_end}]\n"
    outfile += f'_创建日期{create_start.strftime("%Y%m%d")}_{create_end.strftime("%Y%m%d")}'

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

    # 计算每天的BUG创建数量和关闭数量
    daily_bug_created = df["创建日期"].value_counts().sort_index()
    daily_bug_closed = df["解决日期"].value_counts().sort_index()
    # 创建折线图
    plt.figure(figsize=(10, 6))
    plt.plot(
        daily_bug_created.index, daily_bug_created.values, label="BUG创建数量", marker="o"
    )
    plt.plot(daily_bug_closed.index, daily_bug_closed.values, label="关闭数量", marker="x")

    # 设置横坐标文字竖着显示
    plt.xticks(rotation="vertical")
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1))

    # 设置日期格式
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))

    # 显示每个节点的数据
    for a, b in zip(daily_bug_created.index, daily_bug_created.values):
        plt.text(a, b, str(b))

    for a, b in zip(daily_bug_closed.index, daily_bug_closed.values):
        plt.text(a, b, str(b))

    # 添加网格线
    plt.grid(True)

    # 设置图表标题和坐标轴标签
    plt.title(f"期间内缺陷创建量与解决量趋势 \n查询条件：{cond}")
    plt.xlabel("日期")
    plt.ylabel("数量")

    # 显示图例
    plt.legend()

    plt.savefig(f"{outfile}.png", bbox_inches="tight")
