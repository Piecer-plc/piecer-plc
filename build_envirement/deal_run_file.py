from model.pipeline import Pipeline
from utils import files_utils
from model.venv_install_info import VenvInstallInfo
import os
import re
import codecs


class DealRunFile:
    """
       input_root : 运行项目的输入文件所保存的根目录
         输入数据路径： input_root/竞赛名/文件名

       file_root : 保存项目代码的根目录
         项目代码路径： file_root/竞赛名/项目名##id##script_version_id/new_file_folder/run_py+venv_num.py
       save_folder : 新的运行代码的存放的文件夹名称
    """

    # 在.ipynb 文件中适用， 不适用于.py的代码
    INVALID_LINE = {
        "get_ipython().run_line_magic('matplotlib','inline')",
        "init_notebook_mode",
        "print(check_output",
        'print((subprocess.check_output("lscpu",shell=True).strip()).decode())'
        "get_ipython().system",
    }

    # 必须在第一行的引入
    HEAD_LINE = {
        "from __future__ import division",
    }

    # 将原来的进行替换
    REPLACE = {
        "sklearn.cross_validation": "sklearn.model_selection",
        "StratifiedKFold(n_splits=5, shuffle=False, random_state=10)": "StratifiedKFold(n_splits=5, shuffle=True, random_state=10)"

    }

    TIME_START_CODE = "\nimport timeit\nstart = timeit.default_timer()\n"
    TIME_END_CODE = "\nend = timeit.default_timer()\nprint(\"###%%%run time:\" + str(end-start) + \"s\")\n"

    MEMORY_START_CODE = "\n\nimport tracemalloc\ntracemalloc.start()\n"
    MEMORY_END_CODE = "\ncurrent, peak = tracemalloc.get_traced_memory()\nprint(f\"Current memory usage is {current /1024/1024}MB; ###%%%Peak memory was :{peak / 1024/1024}MB\")\ntracemalloc.stop()\n"

    def __init__(self, pipeline_id, input_root, file_root, save_folder):
        self.pipeline_id = pipeline_id
        self.input_root = input_root
        self.file_root = file_root
        self.save_folder = save_folder
        self.pipeline_info = Pipeline.filter(pipeline_id=pipeline_id, sel_one=True)
        self.__init_file_path()
        self.__init_save_path()

    def __init_file_path(self):
        project_name = self.pipeline_info['project_name']
        script_version_id = self.pipeline_info['script_version_id']
        folder_name = project_name + '#id#' + str(script_version_id)
        file_name = project_name + '.py'
        file_path = os.path.join(self.file_root, self.pipeline_info['compete_name'], folder_name, file_name)
        self.file_path = file_path.replace('\\', '/')

    def __init_save_path(self):
        project_name = self.pipeline_info['project_name']
        script_version_id = self.pipeline_info['script_version_id']
        folder_name = project_name + '#id#' + str(script_version_id)
        save_path = os.path.join(self.file_root, self.pipeline_info['compete_name'], folder_name, self.save_folder)
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        self.save_path = save_path.replace('\\', '/')

    def __init_input_data_folder_path(self):
        compete_name = self.pipeline_info['compete_name']
        self.input_data_folder = os.path.join(self.input_root, compete_name).replace('\\', '/')

    def __is_invalid_line(self, line):
        for item in self.INVALID_LINE:
            if item in line: return True
        return False

    def __replace_line(self, line):
        for item in self.REPLACE:
            if item in line:
                new_line = line.replace(item, self.REPLACE[item])
                return new_line
        return None

    def __replace_sample_submission(self, file_path, line):
        results = re.findall(r"['\"](.*?)['\"]", line)
        for result in results:
            if '/' not in result:
                continue
            try:
                path = self.input_data_folder + '/sample_submission.csv'
                line = line.replace(result, path)
            except Exception as e:
                print('replace_sample error :' + str(e))
                print(line)
                print('-' * 40)
        files_utils.txt_write_into(file_path, line)

    # 替换文件的输入格式并写入到新的文件夹中
    def __replace_input(self, file_path, line, input_files):
        results = re.findall(r"['\"](.*?)['\"]", line)
        for result in results:
            if '/' not in result:
                continue
            try:
                file = result.split('/')[-1]
                if file == '':
                    file = result.split('/')[-2]
                if is_compete_name(self.pipeline_info['compete_name'], file) or file == 'input':
                    line = line.replace(result, self.input_data_folder + "/")
                if file in input_files:
                    line = line.replace(result, self.input_data_folder + '/' + file)
            except Exception as e:
                print('replace_input error :' + str(e))
                print(line)
                print('-' * 40)
                break
        files_utils.txt_write_into(file_path, line)

    def __replace_output(self, file_path, line, num):
        results = re.findall(r".to_csv\((.*?)\)", line)
        path_result = re.findall(r"['\"](.*?)['\"]", line)
        for result in results:
            if '.csv' not in result:
                continue
            try:
                submission_file_name = path_result[0].split('/')[-1]
                file_name = submission_file_name + str(num) + '.csv'
                path = os.path.join(self.save_path, file_name).replace('\\', '/')
                line = line.replace(result, '"' + path + '", index=False')
            except Exception as e:
                print('replace_input error :' + str(e))
                print(line)
                print('-' * 40)
            num = num + 1
        files_utils.txt_write_into(file_path, line)

    def create_run_py_file(self, venv_num):
        py_path = os.path.join(self.save_path, 'pipeline_run%d.py' % venv_num)
        codecs.open(py_path, 'w', 'utf-8').close()
        # 插入内存计算模块
        files_utils.txt_write_into(py_path, self.MEMORY_START_CODE)
        # 插入时间计算模块
        files_utils.txt_write_into(py_path, self.TIME_START_CODE)
        with codecs.open(self.file_path, 'rb', encoding='utf-8') as f:
            for line in f.readlines():
                judge_line = line.replace('\r', '').replace('\n', '').replace(" ", '')
                result = self.__is_invalid_line(judge_line)
                if result: continue

                re_line = self.__replace_line(line)
                if re_line is not None:
                    new_line = re_line

                if 'sample_submission.csv' in judge_line:
                    self.__replace_sample_submission(py_path, new_line)
                elif '/input' in judge_line:
                    input_files = os.listdir(self.input_data_folder)
                    self.__replace_input(py_path, judge_line, input_files)
                elif '.to_csv' in judge_line:
                    self.__replace_output(py_path, judge_line, venv_num)

                elif 'with open' in judge_line and 'submission.csv' in judge_line:
                    judge_line = judge_line.replace('submission.csv', 'submission.csv' + str(venv_num) + '.csv')
                    files_utils.txt_write_into(py_path, judge_line)
                elif not judge_line.startswith('#'):
                    files_utils.txt_write_into(py_path, judge_line)

        # 插入时间结束模块
        files_utils.txt_write_into(py_path, self.TIME_END_CODE)
        # 插入计算内存结束模块
        files_utils.txt_write_into(py_path, self.MEMORY_END_CODE)


def is_compete_name(compete_name, file_name):
    cop = re.compile("[^\u4e00-\u9fa5^a-z^A-Z^0-9]")  # 匹配不是中文、大小写、数字的其他字符
    if cop.sub('', compete_name).lower() == cop.sub('', file_name).lower():
        return True
    else:
        return False


def batch_create_run_py_file(pipeline_ids, input_root, file_root, save_folder, concerned_stages_str, experiment_No):
    for pipeline_id in pipeline_ids:
        if isinstance(pipeline_id, dict):
            pipeline_id = pipeline_id['pipeline_id']
        deal_run_file = DealRunFile(pipeline_id, input_root, file_root, save_folder)
        max_venv_num = VenvInstallInfo.get_venv_max_num(pipeline_id, concerned_stages_str, experiment_No)
        for i in range(max_venv_num):
            venv_num = i + 1
            deal_run_file.create_run_py_file(venv_num)



