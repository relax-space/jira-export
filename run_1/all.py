from concurrent.futures import ProcessPoolExecutor


def main():
    with ProcessPoolExecutor() as executor:
        executor.submit(main1)
        executor.submit(main2)
        executor.submit(main3)
        executor.submit(main4)
        executor.submit(main5)
        executor.submit(main6)
        executor.submit(main7)
        executor.submit(main8)
        executor.submit(main9)
        executor.submit(main10)


if __name__ == "__main__":
    from os import path as os_path, chdir
    from sys import path as sys_path

    p = os_path.dirname(os_path.dirname(os_path.abspath(__file__)))
    sys_path.insert(0, p)
    chdir(p)
    from run_1.p1 import main as main1
    from run_1.p2 import main as main2
    from run_1.p3 import main as main3
    from run_1.p4 import main as main4
    from run_1.p5 import main as main5
    from run_1.p6 import main as main6
    from run_1.p7 import main as main7
    from run_1.p8 import main as main8
    from run_1.p9 import main as main9
    from run_1.p10 import main as main10

    main()
