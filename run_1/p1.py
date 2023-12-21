from datetime import date
from os import path as os_path, chdir
from sys import path as sys_path
import matplotlib.pyplot as plt


if __name__ == "__main__":
    p = os_path.dirname(os_path.dirname(os_path.abspath(__file__)))
    sys_path.insert(0, p)
    chdir(p)
    from relax.util import gen_dir
    from relax.util import getFont
    from relax.p1 import start

    root_folder = "data1"
    pic_folder = "pic"
    in_file = os_path.join(root_folder, "task", "d1.xlsx")
    # 根据项目查询
    project_keys = ["POC8"]

    out_folder = os_path.join(root_folder, pic_folder)
    gen_dir(out_folder)
    file_name = f"{'_'.join(project_keys)}_{os_path.basename(__file__)}".replace(
        ".py", ".png"
    )
    out_file = os_path.join(out_folder, file_name)
    font = getFont()
    plt.rcParams["font.family"] = font

    # 根据日志记录工时，提交时间查出
    log_start = date(2023, 12, 1)
    log_end = date.today()

    # 根据迭代期间查询
    sprint_start = date(2023, 12, 1)
    sprint_end = date.today()

    params = (log_start, log_end, sprint_start, sprint_end)

    try:
        start(in_file, out_file, project_keys, params)
    except Exception as e:
        pass
        print(e)
