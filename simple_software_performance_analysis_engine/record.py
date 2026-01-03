from hardware import DataCollection, SystemValidation
from data_handler import FileHandling
import time

def main():
    SystemValidation().checker()
    FileHandling().create_file()
    strt_time = time.time()

    while True:
        time.sleep(1)

        collect = DataCollection()

        FileHandling().add_data(collect.get_cpu_usage(), collect.get_gpu_usage(), collect.get_ram_usage(), collect.get_time(strt_time))


if __name__ == "__main__":
    main()

