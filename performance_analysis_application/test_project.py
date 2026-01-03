import os
import pandas
from data_handler import FileHandling, DataHandling, DataCleaning
from hardware import DataCollection
import psutil
import pytest

@pytest.fixture
def setup_test_file():

    filename = "testfile.csv"

    # test data with CPU bottleneck
    data = pandas.DataFrame ({
        "Time": [1, 2, 3, 4, 5],
        "CPU": [95, 95, 95, 95, 95],
        "GPU Temp": [40, 41, 40, 42, 40],
        "GPU": [10, 10, 10, 10, 10],
        "RAM": [50, 50, 50, 50, 50]
    })

    data.to_csv(filename)
    
    return filename

def test_file_creation():
    file = FileHandling()
    file._filename = "test.csv" 
    file.create_file()

    assert os.path.exists("test.csv") == True
    
def test_cpu_bottleneck_detection(setup_test_file):
    data = pandas.read_csv(setup_test_file)
    bottleneck_file = DataHandling(file=data)
    
    assert bottleneck_file.cpu_bottleneck() == "CPU bottleneck!!"
    assert bottleneck_file.gpu_bottleneck() == "GPU's thriving!"

def test_cpu_usage():
    usage = DataCollection().get_cpu_usage()
    assert (isinstance(usage, (float, int)) and 0 <= usage <= 100)
