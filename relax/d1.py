"""
将所有项目合并成一个
"""
from pandas import read_excel, concat, ExcelWriter
from multiprocessing import Pool
from traceback import format_exc

from os import path as os_path, listdir


def process_file(filename):
    try:
        df1 = read_excel(filename, sheet_name="sheet1")
        return df1
    except Exception as e:
        print(filename, format_exc())
        pass


def start(in_folder, out_file):
    f_list = [os_path.join(in_folder, f) for f in listdir(in_folder) if f != "init"]
    with Pool(processes=4) as pool:  # 可以根据需要调整进程数
        df_list = pool.map(process_file, f_list)
    df = concat(df_list)
    with ExcelWriter(out_file) as writer:
        df.to_excel(writer, index=False)
