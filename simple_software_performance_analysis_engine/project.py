import streamlit as st
import os
import sys
import subprocess
from hardware import SystemValidation
from data_handler import Maximums, FileHandling, DataHandling
import signal
import pandas
import datetime, time

# prints badges based on gpu validation from SystemValidation
def is_gpu():
    is_gpu = SystemValidation().checker()
    
    if is_gpu and SystemValidation().one_gpu():
        st.badge("Success! We've found an Nvidia GPU", color="green", icon=":material/check_circle:")
        return True
    else:
        if not SystemValidation().one_gpu():
            st.badge("Failed! We can't process multiple Nvidia GPUs", color="red", icon=":material/cancel:")
        else:
            st.badge("Failed! We couldn't find Nvidia GPU", color="red", icon=":material/cancel:")
        
        return False
    
# ensure everything clears up from the first slide when button is clicked   
if "monitor_btn_clicked" not in st.session_state:
    st.session_state.monitor_btn_clicked = False
    st.session_state.second_window_clear = False
    st.session_state.engine_start = False

if "record_pid" not in st.session_state:
    st.session_state.record_pid = None

def monitor_btn_clicked():  # initiates the monitoring
    st.session_state.monitor_btn_clicked = True
def second_window_clear():  # clears out the second window
    st.session_state.second_window_clear = True 

# validate requirements in the first slide
def begining():
    # generate texts on the page
    st.title("Performance Analysis Application")
    st.write("by Tahsin Tasnim Talha (tahsinttalha)")

    st.write("Feel free to tap the start button when you want to start monitoring. We suggest you tap the following button. If you want to measure some other application, switch to the desired application after you press the button. We would analyse your data and provide a result.")

    # just some fancy UX
    with st.status("Please wait while we test your system's eligibility...", width="stretch", state="running") as status:
        time.sleep(1)
        status.update(label="Done", state="complete")

    if is_gpu():   
        st.button(
            label="Start Monitoring", 
            icon=":material/folder_eye:", 
            type="primary", 
            width="stretch", 
            on_click=monitor_btn_clicked
            )
        st.caption("We don't collect your data. The temporary analysis files are stored on your device or deleted upon your concern.")
    else:
        st.error("Please retry when you've an Nvidia GPU", icon=":material/cancel:")

# initiate terminating protocols
def terminate(string):
    st.button(
        label="End Monitoring",
        icon=":material/cancel:",
        type="primary",
        width="stretch",
        on_click=termination,
        args=(string,)
    )    

# terminates the monitoring
def termination(string):
    if string == "monitor_btn_clicked":
        st.session_state.monitor_btn_clicked = False
        st.session_state.second_window_clear = True
        st.session_state.engine_start = True
    else:
        st.session_state.second_window_clear = False
        st.session_state.engine_start = False

def delete_data():
    try:
        FileHandling().delete_file()
        st.session_state.second_window_clear = False
    except FileNotFoundError:
        st.text("Umm...You've already deleted the file!")

# start monitoring the system and record data on record.py
def run_monitoring():
    process = subprocess.Popen([sys.executable, "record.py"])
    st.session_state.record_pid = process.pid

def main():
    # this is the main executing block
    if st.session_state.monitor_btn_clicked:
        run_monitoring()

        #   <------ first termination happens here ------->

        st.status(label="monitoring your performance... Please switch to your desired application. Kindly tap the following button when you want to stop.", state="running", width="stretch")        
        terminate("monitor_btn_clicked")

        #   <--------------------------------------------->

    elif st.session_state.second_window_clear:
        # kills the external data recorder file
        try:
            if st.session_state.record_pid is not None:
                os.kill(st.session_state.record_pid, signal.SIGTERM)
        except OSError:
            pass
        
        # display maximum data on each section
        col1, col2, col3, col4, col5 = st.columns(5)

        cpu_metric = DataHandling().cpu_bottleneck()
        gpu_metric = DataHandling().gpu_bottleneck()
        thermal_metric = DataHandling().thermal_throttling()
        ram_metric = DataHandling().ram_bottleneck()

        col1.metric("Total Runtime", f"{Maximums().max_time()}s")

        col2.metric("Max CPU Usage", f"{Maximums().max_cpu()}%", delta=cpu_metric, delta_color="normal" if cpu_metric == "CPU's calm!" else "inverse", delta_arrow="up" if cpu_metric == "CPU's calm!" else "down")

        col3.metric("Max GPU Usage", f"{Maximums().max_gpu()}%", delta=gpu_metric,  delta_color="normal" if gpu_metric == "GPU's thriving!" else "inverse", delta_arrow="up" if gpu_metric == "GPU's thriving!" else "down")

        col4.metric("Max GPU Temperature", f"{Maximums().max_temp()}°C", delta=thermal_metric,  delta_color="normal" if thermal_metric == "GPU's chilling!" else "inverse", delta_arrow="up" if thermal_metric == "GPU's chilling!" else "down")

        col5.metric("Max RAM Usage", f"{Maximums().max_ram()}%", delta=ram_metric,  delta_color="normal" if ram_metric == "RAM's healthy!" else "inverse", delta_arrow="up" if ram_metric == "RAM's healthy!" else "down")

        # display the graph
        chart_data = pandas.read_csv("data.csv")
        csv_file = chart_data   # initialize csv_file for downlaod
        chart_data = chart_data.set_index("Time")

        # add toggle functionality
        option = st.radio("View Mode: ", ["All", "CPU Usage", "GPU Usage", "RAM Usage", "GPU Temperature"], horizontal=True)

        if option == "All":
            radio_option = chart_data
            unit = ""
        elif option == "CPU Usage":
            radio_option = chart_data[["CPU"]]
            unit = "%"
        elif option == "GPU Usage":
            radio_option = chart_data[["GPU"]]
            unit = "%"
        elif option == "GPU Temperature":
            radio_option = chart_data[["GPU Temp"]]
            unit = "°C"
        else:
            radio_option = chart_data[["RAM"]]
            unit = "%"

        st.line_chart(radio_option, x_label="Time (seconds)", y_label=f"{option} ({unit if unit != "" else "Designated Units"})")

        # downloadable data file
        csv_file = csv_file.to_csv().encode("utf-8")

        current_time = datetime.datetime.now()

        with st.container(horizontal=True):
            st.download_button(
                label="Download CSV", 
                data=csv_file,
                file_name=f"data_{current_time}.csv",
                icon=":material/download:",
                type="primary"
                )
            
            st.button(
                label="Delete Record & End Program",
                on_click=delete_data
            )

    # this block will only run in the first time
    else:
        begining()

if __name__ == "__main__":
    main()