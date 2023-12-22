from os import path as os_path, chdir
import matplotlib.pyplot as plt

from sys import path as sys_path
from datetime import date


if __name__ == "__main__":
    p = os_path.dirname(os_path.dirname(os_path.abspath(__file__)))
    sys_path.insert(0, p)
    chdir(p)
    from relax.util import gen_dir
    from relax.util import getFont
    from relax.p2 import start

    root_folder = "data1"
    pic_folder = "pic"
    in_file = os_path.join(root_folder, "raw", "raw.xlsx")
    project_keys = ["POC8"]

    out_folder = os_path.join(root_folder, pic_folder)
    gen_dir(out_folder)
    file_name = f"{'_'.join(project_keys)}_{os_path.basename(__file__)}".replace(
        ".py", ".png"
    )
    out_file = os_path.join(out_folder, file_name)
    font = getFont()
    plt.rcParams["font.family"] = font

    date1 = date(2023, 12, 1)
    date2 = date.today()

    try:
        start(in_file, out_file, project_keys)
    except Exception as e:
        pass
        print(e)
