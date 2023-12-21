from os import chdir, path as os_path
from sys import path as sys_path


if __name__ == "__main__":
    p = os_path.dirname(os_path.dirname(os_path.abspath(__file__)))
    sys_path.insert(0, p)
    chdir(p)
    from relax.util import gen_dir
    from relax.d2 import start

    root_folder = "data1"
    in_folder = os_path.join(root_folder, "raw")
    out_folder = os_path.join(root_folder, "task")
    gen_dir(out_folder)
    out_file = os_path.join(out_folder, "d2.xlsx")

    start(in_folder, out_file)
