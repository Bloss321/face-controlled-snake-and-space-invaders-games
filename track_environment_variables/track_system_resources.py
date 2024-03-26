import psutil
import time


# Track system resources
def track_system_resources(initial_time):
    if time.time() > initial_time + 5:  # show system resources after 5 seconds
        display_system_resources()
        initial_time = time.time()


def print_gpu_info():
    import subprocess as sp
    # raw strings avoid unicode encoding errors
    gpu_mem_cmd = r'(((Get-Counter "\GPU Process Memory(*)\Local Usage").CounterSamples | where ' \
                  r'CookedValue).CookedValue | measure -sum).sum'
    gpu_usage_cmd = r'(((Get-Counter "\GPU Engine(*engtype_3D)\Utilization Percentage").CounterSamples | where ' \
                    r'CookedValue).CookedValue | measure -sum).sum'

    def run_command(command):
        val = sp.run(['powershell', '-Command', command], capture_output=True).stdout.decode("ascii")
        return float(val.strip().replace(',', '.'))

    print()
    print(" GPU Info ".center(80, '='))
    print(f"GPU Memory Usage: {round(run_command(gpu_mem_cmd) / 1e6, 1):<6} MB")
    print(f"GPU Load :        {round(run_command(gpu_usage_cmd), 2):<6} %")


def display_system_resources():
    cpu_percent = psutil.cpu_percent()
    memory_info = psutil.virtual_memory()
    disk_info = psutil.disk_usage('/')

    print(f"CPU Usage: {cpu_percent}%")
    print(f"Memory Usage: {memory_info.percent}%")
    print(f"Disk Usage: {disk_info.percent}%")
    print("-" * 30)
