import pytz
from datetime import datetime, date, timedelta
from os import path as os_path, makedirs
import platform
from chinese_calendar import is_workday, is_holiday


def to_hour(second) -> float:
    if not isinstance(second, (int, float)):
        return 0
    h = round(second / 3600, 1)
    return h


def f_date(original_time: str, format: str = "%Y-%m-%d %H:%M:%S") -> str:
    # original_time = "2023-12-13T17:33:46.976+0800"
    try:
        if not original_time:
            return ""
        parsed_time = datetime.strptime(original_time, "%Y-%m-%dT%H:%M:%S.%f%z")
        china_tz = pytz.timezone("Asia/Shanghai")
        china_time = parsed_time.astimezone(china_tz)
        return china_time.strftime(format)
    except Exception as e:
        print(4, e)
        return ""


def gen_dir(folder):
    if not os_path.isdir(folder):
        makedirs(folder)


def getFont():
    if platform.system().lower() == "windows":
        return "Microsoft YaHei"
    elif platform.system().lower() == "darwin":
        return "Arial Unicode MS"


def get_workday_count(start: date, end: date) -> int:
    count = 0
    while start <= end:
        start += timedelta(days=1)
        if is_holiday(start):
            continue
        count += 1
    return count
