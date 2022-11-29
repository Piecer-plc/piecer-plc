import os
import time
from model.pipeline import Pipeline
from model.run_pipeline_state import RunPipelineState
from model.venv_install_info import VenvInstallInfo
from model.experiemnt_record import ExperimentRecord
from run_experiment.build_run_venv import BuildRunVenv
from utils import venv_utils
import re
import json


class RunExperiment:
    def __init__(self, compete_root, venv_root, package_root, output_folder, computer_num, python_version, input_root,
                 concerned_stages, experiment_No, support_os, timeout=14400):
        self.compete_root = compete_root
        self.venv_root = venv_root
        self.package_root = package_root
        self.output_folder = output_folder
        self.computer_num = computer_num
        self.python_version = python_version
        self.input_root = input_root
        self.concerned_stages = concerned_stages
        self.concerned_stages.sort()
        self.concerned_stages_str = ','.join(self.concerned_stages)
        self.experiment_No = experiment_No
        self.support_os = support_os
        # 4个小时
        self.timeout = timeout

    def __get_venv_path(self, pipeline_id):
        return os.path.join(self.venv_root, str(pipeline_id))

    def __get_run_file_folder(self, pipeline_id):
        save_folder = ""
        if self.experiment_No == '1-1':
            save_folder = "run_files_experiment1" + '-'.join( self.concerned_stages)
        if self.experiment_No == '1-2':
            save_folder = "run_files_experiment2" + '-'.join( self.concerned_stages)
        if self.experiment_No == '1-3':
            save_folder = "run_files_experiment3" + '-'.join( self.concerned_stages)

        project_folder = Pipeline.get_pipeline_save_path(pipeline_id, self.compete_root)
        run_file_folder = os.path.join(project_folder, save_folder)
        return run_file_folder

    def __get_output_save_path(self, pipeline_id):
        project_folder = Pipeline.get_pipeline_save_path(pipeline_id, self.compete_root)
        result_save_path = os.path.join(project_folder,  self.output_folder)
        if not os.path.exists(result_save_path):
            os.makedirs(result_save_path)
        return result_save_path

    def __run_python_file_venv(self, venv_path, file_path):
        activate_cmd = 'conda activate "' + venv_path + '"'
        run_cmd = 'python "' + file_path + '"'
        cmd = activate_cmd + ' && ' + run_cmd
        result, run_info = venv_utils.external_cmd(cmd, timeout=self.timeout)
        run_time = ""
        memory = ""
        false_info = ""
        if "####$$$$$$#####" in run_info:
            false_info = run_info.split("####$$$$$$#####")[0]
        if run_info == 'timeout':
            run_time = "14400"
            memory = ""
            return run_time, memory, 'timeout'

        memory_pattern = "###%%%Peak memory was :(.*?)MB"
        time_pattern = "###%%%run time:(.*?)s"
        memory_find = re.findall(memory_pattern, run_info)
        run_time_find = re.findall(time_pattern, run_info)
        if memory_find:
            memory = memory_find[0]
        if run_time_find:
            run_time = run_time_find[0]

        return run_time, memory, false_info

    def __is_stop_run(self, pipeline_id):
        false_info_list = ExperimentRecord.filter(pipeline_id,computer_num=self.computer_num,
                                                  concerned_stages=self.concerned_stages_str,
                                                  experiment_No=self.experiment_No, columns=['false_info'])
        stop_error_format = "FileNotFoundError: (.*?) No such file or directory:"
        false_num =0
        for false_info in false_info_list:
            false_info = false_info['false_info']
            if re.search(stop_error_format, false_info):
                false_num += 1
            if false_num == 2:
                return True
        return False

    def run_pipeline(self, pipeline_id):
        pipeline_info = Pipeline.filter(pipeline_id=pipeline_id, sel_one=True, columns=['compete_name'])
        compete_name = pipeline_info['compete_name']

        if RunPipelineState.is_exist(pipeline_id, self.concerned_stages_str, self.experiment_No):
            return

        RunPipelineState.insert_start_record(pipeline_id, compete_name, self.concerned_stages_str, self.experiment_No, self.computer_num)
        max_venv_num = VenvInstallInfo.get_venv_max_num(pipeline_id, self.concerned_stages_str, self.experiment_No)
        for i in range(max_venv_num):
            venv_num = i+1
            if ExperimentRecord.is_exist(pipeline_id, venv_num, self.concerned_stages_str, self.experiment_No):
                continue
            self.run_pipeline_file_with_independent_venv(venv_num, pipeline_id)
            if self.__is_stop_run(pipeline_id):
                print("File Not Found Error Stop Run!  %d %s %s" % (pipeline_id, self.concerned_stages_str, self.experiment_No))
                return

        pipeline_run_state = ExperimentRecord.is_run_pipeline_success(pipeline_id,self.concerned_stages_str, self.experiment_No)
        RunPipelineState.update_run_pipeline_state(pipeline_id, pipeline_run_state, compete_name, self.concerned_stages_str)

    def run_pipeline_file_with_independent_venv(self, venv_num, pipeline_id):
        result_path = self.__get_output_save_path(pipeline_id)
        begin_time = time.time()
        start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(begin_time))
        ExperimentRecord.insert_start_record(pipeline_id, self.concerned_stages_str, venv_num, self.computer_num, self.experiment_No)
        ExperimentRecord.update_experiment_record_start_time(pipeline_id, self.concerned_stages_str, venv_num,  start_time, self.experiment_No)
        install_info_list = VenvInstallInfo.filter(pipeline_id, self.concerned_stages_str, self.experiment_No, venv_num, order_by="install_order")
        run_venv_builder = BuildRunVenv(self.venv_root, self.package_root, self.support_os, self.concerned_stages)
        run_venv_builder.build_run_venv(pipeline_id, venv_num, install_info_list)
        run_file_path = os.path.join(self.__get_run_file_folder(pipeline_id), "pipeline_run" + str(venv_num) + ".py")
        print('run path :' + run_file_path)
        venv_path = os.path.join(self.__get_venv_path(pipeline_id), str(venv_num) + '-'.join(self.concerned_stages))
        run_time, memory, false_info = self.__run_python_file_venv(venv_path, run_file_path)
        end_time = time.time()
        print('run a dependencies combine need time: ', end_time - begin_time)
        run_state = is_folder_file_recent_change(result_path, end_time, run_time)
        end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))
        ExperimentRecord.update_experiment_record_run_time(pipeline_id, self.concerned_stages_str, venv_num, run_time, self.experiment_No)
        ExperimentRecord.update_experiment_record_end_time(pipeline_id, self.concerned_stages_str, venv_num, end_time, self.experiment_No)
        ExperimentRecord.update_experiment_record_memory(pipeline_id, self.concerned_stages_str, venv_num, memory, self.experiment_No)
        ExperimentRecord.update_experiment_record_run_state(pipeline_id, self.concerned_stages_str, venv_num,  str(run_state), self.experiment_No)
        if not run_state and false_info:
            ExperimentRecord.update_experimental_record_false_info(pipeline_id, self.concerned_stages_str,venv_num,false_info, self.experiment_No)


# 判断文件夹内容最近是否发生改变
def is_folder_file_recent_change(folder_path, end_time, recent_range):
    if recent_range == 'timeout':
        return False
    if recent_range == "":
        recent_range =0
    if isinstance(recent_range,str):
        recent_range = float(recent_range)
    newest_time = 0
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        mtime = os.stat(file_path).st_mtime
        if mtime > newest_time:
            newest_time = mtime

    r_time = end_time - newest_time
    print('newest  time ' + str(r_time))
    if end_time - newest_time <= recent_range:
        return True
    else:
        return False


def batch_run(concerned_stages:list, support_os, experiment_No, pipeline_ids, computer_num):
    concerned_stages.sort()
    with open("./run_experiment_config.json", 'r') as load_f:
        config_dict = json.load(load_f)
    output_folder = ""
    if experiment_No == '1-1':
        output_folder = "result_output_experiment1" + '-'.join(concerned_stages)
    if experiment_No == '1-2':
        output_folder = "result_output_experiment2" + '-'.join(concerned_stages)
    if experiment_No == '1-3':
        output_folder = "result_output_experiment3" + '-'.join(concerned_stages)
    if output_folder == "":
        print("experiment_no error")
        return
    run_ex = RunExperiment(config_dict['compete_root'], config_dict['venv_root'], config_dict['pkg_root'],
                           output_folder, computer_num, '3.7.10',config_dict['input_data_root'],
                           concerned_stages, experiment_No,support_os)

    for pipeline_id in pipeline_ids:
        if isinstance(pipeline_id, dict):
            pipeline_id = pipeline_id['pipeline_id']
        run_ex.run_pipeline(pipeline_id)


if __name__ == "__main__":
    #root 项目路径的上级目录名
    root = ""
    # venv_root 虚拟环境创建的根目录
    venv_root = ""
    # package_root 下载的第三方库存放路径
    package_root= ""
    # output_folder 项目输出的存放路径
    output_folder = ""
    # computer_num 使用的电脑的编号
    computer_num = ""
    # python_version python版本
    python_version = ""
    # input_root 输入文件的路径
    input_root = ""
    # concerned_stages 变更的阶段
    concerned_stages = []
    # experiment_No 实验编号
    experiment_No = ""
    # support_os 操作系统
    support_os = ""
    run_ex = RunExperiment(root,venv_root,package_root,output_folder,computer_num,python_version,input_root,concerned_stages,experiment_No,support_os)
    pipeline_id = 1
    run_ex.run_pipeline(pipeline_id)
