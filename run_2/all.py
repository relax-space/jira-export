from concurrent.futures import ProcessPoolExecutor
from datetime import date


def main():
    args = {
        "log_start": date(2023, 12, 18),
        "log_end": date(2024, 12, 19),
    }
    with ProcessPoolExecutor() as executor:
        executor.submit(main1, args)
        executor.submit(main2, args)
        executor.submit(main3, args)
        executor.submit(main4, args)
        executor.submit(main5, args)
        executor.submit(main6, args)
        executor.submit(main7, args)
        executor.submit(main8, args)
        executor.submit(main9, args)
        executor.submit(main10, args)


if __name__ == "__main__":
    from os import path as os_path, chdir
    from sys import path as sys_path

    p = os_path.dirname(os_path.dirname(os_path.abspath(__file__)))
    sys_path.insert(0, p)
    chdir(p)
    from run_2.p1 import main as main1
    from run_2.p2 import main as main2
    from run_2.p3 import main as main3
    from run_2.p4 import main as main4
    from run_2.p5 import main as main5
    from run_2.p6 import main as main6
    from run_2.p7 import main as main7
    from run_2.p8 import main as main8
    from run_2.p9 import main as main9
    from run_2.p10 import main as main10

    main()
