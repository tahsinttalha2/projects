import pynvml
import psutil
import time

class SystemValidation:
    def __init__(self):
        self._isgpu = self.checker()

    # validates nvidia gpu
    def checker(self):
        try:
            pynvml.nvmlInit()
            return True
        except:
            return False

    # validates only one gpu    
    def one_gpu(self):
        device_count = pynvml.nvmlDeviceGetCount()
        if device_count > 1:
            return False
        return True

    # terminates nvml initialization
    def terminator(self):
        pynvml.nvmlShutdown()

class DataCollection:
    def get_cpu_usage(self):
        return psutil.cpu_percent()
    
    def get_ram_usage(self):
        return round(psutil.virtual_memory().percent, 1)
    
    def get_gpu_usage(self):
        if SystemValidation().checker() and SystemValidation().one_gpu():
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
            mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
            mem_percent = round((mem.used / mem.total) * 100, 1)

            return {
                "temp": temp,
                "mem": mem_percent
            }
    
    def get_time(self, strt):
        crnt = time.time()
        passed = crnt - strt
        return round(passed)

        