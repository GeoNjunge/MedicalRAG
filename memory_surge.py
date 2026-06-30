import psutil
import time
import logging

# Configure logging
logging.basicConfig(filename='memory_surge.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# List of processes to monitor for memory and CPU surges
MONITORED_PROCESSES = ['embeddings', 'python3', "python", 'ollama']

def get_process_memory_usage(process: psutil.Process):
    try:
        memory_info = process.memory_info()
        return memory_info.rss  # Resident Set Size, which is a measure of how much memory the process is using
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return None

def get_process_cpu_usage(process: psutil.Process):
    try:
        cpu_percent = process.cpu_percent(interval=1)
        return cpu_percent
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return None

process_info = {}
def monitor_memory_usage():
    while True:
        for pid in psutil.pids():
            try:
                process = psutil.Process(pid)
                if pid not in process_info:
                    process_info[pid] = {
                        'name': process.name(),
                        'start_time': time.time()
                    }
                
                memory_usage = get_process_memory_usage(process)
                cpu_usage = get_process_cpu_usage(process)
                
                # Check if the process name is in the list of monitored processes
                if any(process_info[pid]['name'].lower().startswith(proc.lower()) for proc in MONITORED_PROCESSES):
                    if memory_usage is not None and memory_usage > 0:
                        logging.info(f"Memory Surge Detected: {process.name()} - PID: {pid}")
                        logging.info(f"CPU Usage: {cpu_usage}")
                        logging.info(f"Memory Usage (RSS): {memory_usage / 1024 / 1024:.2f} MB")
                    
                    # if cpu_usage is not None and cpu_usage > 5:
                        logging.info(f"CPU Surge Detected: {process.name()} - PID: {pid}")
                        logging.info(f"CPU Usage: {cpu_usage:.2f}%")
                
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                if pid in process_info:
                    del process_info[pid]
        
        time.sleep(2)  # Check every 2 seconds

if __name__ == "__main__":
    print("Started logging system metrics")
    monitor_memory_usage()
