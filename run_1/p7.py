from datetime import date
from os import path as os_path, chdir
from sys import path as sys_path
import matplotlib.pyplot as plt


def main():
    p = os_path.dirname(os_path.dirname(os_path.abspath(__file__)))
    sys_path.insert(0, p)
    chdir(p)
    from relax.util import gen_dir, getFont
    from relax.p7 import start

    root_folder = "data1"
    pic_folder = "pic"
    in_file = os_path.join(root_folder, "raw", "raw.xlsx")
    # 根据项目查询
    project_keys = []
    exclude_project_keys = ["TEST", "TEST2"]

    out_folder = os_path.join(root_folder, pic_folder)
    gen_dir(out_folder)
    file_name = f"{os_path.basename(__file__)}".replace(".py", "")
    font = getFont()
    plt.rcParams["font.family"] = font

    # 根据创建时间
    log_start = date(2023, 12, 18)
    log_end = date.today()

    # log_start = None
    # log_end = date.today()

    # 根据迭代期间查询
    # sprint_date = date(2023, 12, 1)
    sprint_date = None

    # 根据项目类别查询
    catelogs = []

    params = (log_start, log_end, sprint_date, exclude_project_keys, catelogs)

    try:
        start(out_folder, in_file, file_name, project_keys, params)
    except Exception as e:
        pass
        print(e)


if __name__ == "__main__":
    main()
