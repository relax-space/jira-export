from datetime import date
from os import path as os_path, chdir
from sys import path as sys_path


def main():
    p = os_path.dirname(os_path.dirname(os_path.abspath(__file__)))
    sys_path.insert(0, p)
    chdir(p)
    from relax.util_biz import start_common

    file_name = f"{os_path.basename(__file__)}".replace(".py", "")
    package_name = f"relax.{file_name}"

    root_folder = "data2"
    pic_folder = "pic"

    params = {
        "create_start": date(2023, 12, 18),
        "create_end": date.today(),
        "log_start": None,
        "log_end": None,
        "sprint_date": None,
        "project_keys": [],
        "exclude_project_keys": ["TEST", "TEST2"],
        "catelogs": [],
    }
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
