from datetime import date
from os import path as os_path, chdir
from sys import path as sys_path


def main(args: dict):
    p = os_path.dirname(os_path.dirname(os_path.abspath(__file__)))
    sys_path.insert(0, p)
    chdir(p)
    from relax.util_biz import start_common

    file_name = f"{os_path.basename(__file__)}".replace(".py", "")
    package_name = f"relax.{file_name}"

    root_folder = "data1"
    pic_folder = "pic"

    params = {
        "create_start": None,
        "create_end": None,
        "log_start": date(2024, 1, 2),
        "log_end": date(2024, 1, 7),
        "sprint_date": None,
        "project_keys": [],
        "exclude_project_keys": ["TEST", "TEST2"],
        "catelogs": [],
    }
    if args:
        params.update(args)
    params = params.values()
    start_common(
        package_name,
        file_name,
        root_folder,
        pic_folder,
        *params,
    )


if __name__ == "__main__":
    main()
