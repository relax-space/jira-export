from datetime import date
from os import path as os_path, chdir
from sys import path as sys_path, argv as sys_argv
from matplotlib.pyplot import rcParams
from importlib import import_module


def start_common(
    package_name,
    file_name,
    root_folder="data1",
    pic_folder="pic",
    *params,
):
    p = os_path.dirname(os_path.dirname(os_path.abspath(__file__)))
    sys_path.insert(0, p)
    chdir(p)
    from relax.util import gen_dir, getFont

    module = import_module(package_name)
    start = getattr(module, "start")

    in_file = os_path.join(root_folder, "raw", "raw.xlsx")

    out_folder = os_path.join(root_folder, pic_folder)
    gen_dir(out_folder)
    rcParams["font.family"] = getFont()

    try:
        start(out_folder, root_folder, in_file, file_name, params)
    except Exception as e:
        pass
        print(e)
    pass


def df_filter(out_folder, filename, df, params):
    (
        create_start,
        create_end,
        log_start,
        log_end,
        sprint_date,
        project_keys,
        exclude_project_keys,
        catelogs,
    ) = params

    cond = ""
    outfile = os_path.join(out_folder, filename)
    if catelogs:
        df.query("项目类别 in @catelogs", inplace=True)
        cond += f"项目类别{','.join(catelogs)}\n"
        outfile += f"_项目类别{'_'.join(catelogs)}"
    if project_keys:
        df.query("项目秘钥 in @project_keys", inplace=True)
        cond += f"项目[{','.join(project_keys)}]\n"
        outfile += f"_项目秘钥{'_'.join(project_keys)}"

    if exclude_project_keys:
        df.query("项目秘钥 not in @exclude_project_keys", inplace=True)

    if create_start:
        df.query("创建日期 >= @create_start and 创建日期 <= @create_end", inplace=True)
        cond += f"创建期间[{create_start}~{create_end}]\n"
        outfile += (
            f'_创建期间{create_start.strftime("%Y%m%d")}_{create_end.strftime("%Y%m%d")}'
        )

    if log_start:
        df.query("日志创建日期 >= @log_start and 日志创建日期 <= @log_end", inplace=True)
        cond += f"日志期间[{log_start}~{log_end}]\n"
        outfile += f'_日志期间{log_start.strftime("%Y%m%d")}_{log_end.strftime("%Y%m%d")}'

    if sprint_date:
        df.dropna(subset=["迭代开始日期", "迭代结束日期"], inplace=True)
        df.query("@sprint_date >= 迭代开始日期 and @sprint_date <= 迭代结束日期", inplace=True)
        cond += f"迭代{sprint_date}\n"
        outfile += f'_迭代{sprint_date.strftime("%Y%m%d")}'

    return cond,outfile
