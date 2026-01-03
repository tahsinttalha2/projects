import csv
import os
import pandas

class FileHandling:   
    def __init__(self):
        self._filename = "data.csv" 

    def create_file(self):
        with open(self._filename, "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["Time", "CPU", "GPU Temp", "GPU", "RAM"])
            writer.writeheader()
    
    def add_data(self, cpu_u, gpu_u, ram_u, time_u):
        with open(self._filename, "a", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["Time", "CPU", "GPU Temp", "GPU", "RAM"])
            writer.writerow({
                "Time": time_u,
                "CPU": cpu_u,
                "GPU Temp": gpu_u["temp"],
                "GPU": gpu_u["mem"],
                "RAM": ram_u
                })
            
    def delete_file(self):
        if os.path.exists(self._filename):
            os.remove(self._filename)

class DataCleaning:
    def __init__(self, filename="data.csv"):
        self._data = pandas.read_csv(filename)

        self.min_cpu_rate = self._data["CPU"].quantile(0.10)
        self.min_gpu_rate = self._data["GPU"].quantile(0.10)

    def low_cpu_rate(self):
        cpu_mode = self._data["CPU"].mode()[0]
        if self.min_cpu_rate < 20:
            if cpu_mode > 80:
                return self._data["CPU"] > -1
            
            cpu_cutoff = self._data["CPU"].mode()[0] + 15
            return self._data["CPU"] > cpu_cutoff
        else:
            return self._data["CPU"] > -1
        
    def low_gpu_rate(self):
        gpu_mode = self._data["GPU"].mode()[0]
        if self.min_gpu_rate < 20:
            if gpu_mode > 80:
                return self._data["GPU"] > -1
            
            gpu_cutoff = self._data["GPU"].mode()[0] + 15
            return self._data["GPU"] > gpu_cutoff
        else:
            return self._data["GPU"] > -1
        
    def remove_noise(self):
        return self._data[
            self.low_cpu_rate() | self.low_gpu_rate()
            ]   
        

class DataHandling:
    def __init__(self, file=DataCleaning().remove_noise()):
        self.cleaned_data = file

        self.cpu95 = self.cleaned_data["CPU"].quantile(0.95)
        self.gpu95 = self.cleaned_data["GPU"].quantile(0.95)

    # measure if CPU P95 is near 100% and GPU P95 is less than 90%
    def cpu_bottleneck(self):
        if self.cpu95 > 90 and self.gpu95 < 85:
            comment = "CPU bottleneck!!"
        else:
            comment = "CPU's calm!"
        return comment
    
    # measure if GPU P95 is near 100% and CPU P95 is less than 90%
    def gpu_bottleneck(self):
        if self.cpu95 < 85 and self.gpu95 > 90:
            comment = "GPU bottleneck!!"
        else:
            comment = "GPU's thriving!"
        return comment

    # measure if ram usage is crossing 90%
    def ram_bottleneck(self):
        if self.cleaned_data["RAM"].max() > 90:
            comment = "RAM bottleneck!!"
        else:
            comment = "RAM's healthy!"
        return comment
    
    # measure if gpu temperature is moving beyond 83,
    # standard temp limit for NVIDIA GPUs
    def thermal_throttling(self):
        if self.cleaned_data["GPU Temp"].max() > 83:
            comment = "GPU exploding!"
        else:
            comment = "GPU's chilling!"
        return comment
    
class Maximums:
    def __init__(self, filename="data.csv"):
        self.data = pandas.read_csv(filename)

    def max_time(self):
        return self.data["Time"].max()

    def max_cpu(self):
        return self.data["CPU"].max()
    
    def max_gpu(self):
        return self.data["GPU"].max()
    
    def max_temp(self):
        return self.data["GPU Temp"].max()
    
    def max_ram(self):
        return self.data["RAM"].max()


