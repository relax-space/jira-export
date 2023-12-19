"""
项目名称，经办人，类型，摘要，预估工时，实际工时，迭代

如果迭代有多个，则取id最大的一个迭代
"""
import os
from pandas import read_excel, concat, ExcelWriter
from multiprocessing import Pool
from traceback import format_exc


def get_max_name(group):
    max_id = group["编号"].idxmax()
    return group.loc[max_id, "名称"]


def process_file(filename):
    try:
        usecols = ["项目名称", "经办人", "类型", "摘要", "预估工时", "实际工时", "编号"]
        usecols_2 = ["名称", "任务编号", "编号"]
        df1 = read_excel(filename, usecols=usecols, sheet_name="sheet1")
        df2 = read_excel(
            filename, usecols=usecols_2, sheet_name="sheet2", dtype={"名称": str}
        )
        max_ids = df2.groupby("任务编号")["编号"].transform("max")
        max_names = df2[df2["编号"] == max_ids][["任务编号", "名称"]].rename(
            columns={"名称": "迭代"}
        )
        df_merged = df1.merge(max_names, how="left", left_on="编号", right_on="任务编号")
        return df_merged
    except Exception as e:
        print(filename, format_exc())
        pass


def main(folder):
    f_list = [os.path.join(folder, f) for f in os.listdir(folder) if f != "init"]

    with Pool(processes=4) as pool:  # 可以根据需要调整进程数
        df_list = pool.map(process_file, f_list)

    df = concat(df_list)
    with ExcelWriter(os.path.join("task", "d1.xlsx")) as writer:
        df.to_excel(writer, index=False)


if __name__ == "__main__":
    main("new1")
