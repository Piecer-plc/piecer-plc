import pynvml
import psutil
import re
import time


class GPUUtil:

    def __init__(self):
        pynvml.nvmlInit()
        self.handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        total_memory_info = pynvml.nvmlDeviceGetMemoryInfo(self.handle)
        self.total_memory = total_memory_info.total / (1024 ** 2)

    def get_peek_gpu_used_memory(self, info):
        peek_memory = 0
        while psutil.pid_exists(info['pid_id']):
            cur_memory = self.get_current_pid_used_gpu_memory(info['pid_id'])
            print("cur memory : " + str(cur_memory))
            peek_memory = cur_memory if cur_memory>peek_memory else peek_memory
            time.sleep(2)
        return peek_memory

    def get_current_pid_used_gpu_memory(self, pid):
        process_info = pynvml.nvmlDeviceGetComputeRunningProcesses(self.handle)
        for item in process_info:
            if item.pid == pid:
                return item.usedGpuMemory / (1024 ** 2)

    def get_watch_info(self):
        proc_name_format = "/run_pipeline_venv_experiment(.*?)/(.*?)/(.*?)/bin/python"
        process_info = pynvml.nvmlDeviceGetComputeRunningProcesses(self.handle)
        search = None
        info = {}
        pid_id = None
        for item in process_info:
            proc_info = psutil.Process(item.pid)
            proc_name = proc_info.cmdline()[0]
            search = re.search(proc_name_format, proc_name)
            if search:
                pid_id = item.pid
                break
        if search:
            ot = search.group(3)
            venv_num = re.sub("\D", "", ot)
            con_stags = ot.replace(ot, venv_num)
            info.update({"experiment_No": search.group(1)})
            info.update({"pipeline_id": int(search.group(2))})
            info.update({"venv_num": int(venv_num)})
            info.update({"concerned_stages": con_stags})
            info.update({"pid_id": pid_id})
        return info

    def watch_gpu_memory(self):
        info = {}
        while True:
            while not info: info = self.get_watch_info()
            peek_memory = self.get_peek_gpu_used_memory(info)
            print("peek memory : " + str(peek_memory))
            print("peek usage  : " + str(peek_memory/self.total_memory))


if __name__ == "__main__":
    gpu_util = GPUUtil()
    gpu_util.watch_gpu_memory()
