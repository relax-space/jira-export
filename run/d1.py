"""
将所有项目合并成一个
"""
from pandas import read_excel, concat, ExcelWriter
from multiprocessing import Pool
from traceback import format_exc

from os import chdir, path as os_path, listdir
from sys import path as sys_path


def process_file(filename):
    try:
        # usecols = [
        #     "项目名称",
        #     "经办人",
        #     "类型",
        #     "摘要",
        #     "预估工时",
        #     "实际工时",
        #     "迭代名称",
        #     "迭代开始时间",
        #     "迭代结束时间",
        # ]
        df1 = read_excel(filename, sheet_name="sheet1")
        return df1
    except Exception as e:
        print(filename, format_exc())
        pass


def main(root_folder):
    raw_folder = os_path.join(root_folder, "raw")
    f_list = [os_path.join(raw_folder, f) for f in listdir(raw_folder) if f != "init"]

    with Pool(processes=4) as pool:  # 可以根据需要调整进程数
        df_list = pool.map(process_file, f_list)

    task_folder = os_path.join(root_folder, "task")
    gen_dir(task_folder)
    df = concat(df_list)
    with ExcelWriter(os_path.join(task_folder, "d1.xlsx")) as writer:
        df.to_excel(writer, index=False)


if __name__ == "__main__":
    p = os_path.dirname(os_path.dirname(os_path.abspath(__file__)))
    sys_path.insert(0, p)
    chdir(p)
    from relax.util import gen_dir

    main("data1")
