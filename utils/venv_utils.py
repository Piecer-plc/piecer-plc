import os
import re
import subprocess
import timeit
from utils import files_utils
from utils import pypi_utils


# 运行cmd命令
def external_cmd(cmd, timeout=300):
    global proc
    try:
        proc = subprocess.Popen(cmd, shell=True, close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
        print('pid:' + str(proc.pid))
        stdout_value, stdout_error = proc.communicate(timeout=timeout)

        if stdout_value != '' and stdout_error != '':
            if 'running develop' in stdout_value:
                return handle_generate_egg_info_cmd_out_put(stdout_value)

        if stdout_error != '':
            if "==> WARNING: A newer version of conda exists. <==" in stdout_error:
                return True, stdout_value
            if 'WARNING: Running pip as the \'root\' user' in stdout_error:
                return True, stdout_value
            if '[NbConvertApp]' in stdout_error:
                return handle_ipynb_tp_py_cmd_output(stdout_error)
            else:
                print(stdout_error)

            return False, stdout_error + "####$$$$$$#####" + stdout_value
        else:
            return True,stdout_value
    except Exception as e:
        print('external_cmd error: ' + str(e))
        if 'time out after' in str(e):
            return False, 'timeout'
        return False, 'error'
    finally:
        proc.kill()


# 处理生成eeg-info目录的输出
def handle_generate_egg_info_cmd_out_put(info):
    success_format = "writing (.*?)PKG-INFO"
    success_search = re.search(success_format, info)
    if success_search:
        print('generate success!')
        return True
    else:
        print('generate error!')
        return False


# 处理运行ipynb转py文件命令的输出
def handle_ipynb_tp_py_cmd_output(info):
    success_format = '\[NbConvertApp\] Writing (.*?) to (.*?).py'
    error_format = 'nbformat.reader.NotJSONError:'
    success_search = re.search(success_format, info)
    type_error_search = re.search(error_format, info)
    if success_search:
        print(info)
        return True
    elif type_error_search:
        print('NotJSONError')
        return 'NotJSONError'


# 根据库的名字获取最新的版本，并返回安装名
def get_packages_last_install_name(package_names):
    install_names = []
    for package_name in package_names:
        pypi_util = pypi_utils.PYPIUtils()
        versions = pypi_util.get_package_versions(package_name)
        install_name = package_name + '=' + versions[0]
        install_names.append(install_name)
    return install_names


# 创建虚拟环境
# 参数：
#    venv_path 建立的虚拟环境的地址，地址的最后一级是venv的名
#    python_version 创建的虚拟环境的python版本
#    dependencies  项目的依赖包
def create_initial_virtual_environment(venv_path, python_version):
    create_venv_cmd = 'echo yes | conda create --prefix="' + venv_path + '" python=' + str(python_version)
    activate_cmd = 'conda activate "' + venv_path + '"'
    pip_update_cmd = 'python -m pip install --upgrade pip'
    os.system(create_venv_cmd)
    os.system(activate_cmd + ' && ' + pip_update_cmd)


def install_local_packages_in_venv(venv_path, download_file_path):
    activate_cmd = 'conda activate "' + venv_path + '"'
    install_cmd = 'pip install "' + download_file_path + '"'
    cmd = activate_cmd + " && " + install_cmd
    print(cmd)
    result, info = external_cmd(cmd)
    return result


def uninstall_package(venv_path, package_name):
    package_path = os.path.join(venv_path, 'Lib\\site-packages\\' + package_name)
    files_utils.delete_dir(package_path)


def get_venv_install_packages(venv_name):
    activate_cmd = 'conda activate ' + venv_name
    pip_list_cmd = 'pip list'
    packages_list = external_cmd(activate_cmd + ' && ' + pip_list_cmd)
    print(packages_list)


def run_python_file_venv(venv_path, file_path):
    begin_time = timeit.default_timer()
    activate_cmd = 'conda activate "' + venv_path + '"'
    run_cmd = 'python "' + file_path + '"'
    cmd = activate_cmd + ' && ' + run_cmd
    result, false_info = external_cmd(cmd)
    end_time = timeit.default_timer()
    run_time = end_time - begin_time
    if result == 'timeout':
        return 'timeout'
    return run_time, false_info


# 对不同的库的版本间进行组合排列
# 参数：
#     dicts 库的版本的dicts例{'name1':['0.1','0.2'],'name2':['0.1','0.2']}
def get_dependency_version_combination(dicts):
    version_combinations = []
    combinations = []
    if not dicts:
        return combinations
    version_list = [dicts[pkg_name] for pkg_name in dicts]
    if len(dicts) == 1:
        pkg_name = list(dicts.keys())[0]
        return [{pkg_name:ver} for ver in list(dicts.values())[0]]
    get_combinations(version_list, version_combinations)
    keys = list(dicts.keys())
    for version_combine in version_combinations:
        combination = {}
        for i in range(len(keys)):
            combination.update({keys[i]: version_combine[i]})
        combinations.append(combination)
    return combinations


def get_combinations(lis, combinations, jude=True):
    if jude:
        lis = [[[i] for i in lis[0]]] + lis[1:]

    if len(lis) > 2:
        for i in lis[0]:
            for j in lis[1]:
                get_combinations([[i + [j]]] + lis[2:], combinations, False)
    elif len(lis) == 2:
        for i in lis[0]:
            for j in lis[1]:
                combination = i + [j]
                combinations.append(combination)


# 批量删除虚拟环境
def batch_delete_venv(pipeline_id):
    venv_pipeline_path = "F:\\pipeline_venvs\\" + str(pipeline_id)
    num = len(os.listdir(venv_pipeline_path))
    for i in range(num):
        venv_num = str(i+1)
        venv_path = venv_pipeline_path + "\\_" + venv_num
        cmd = "conda remove -name \"" + venv_path + "\" --all"
        os.system(cmd)


def is_continue_run(project_folder, output_sign=None):
    out_put_file_path = os.path.join(project_folder, 'outputFiles')
    out_put_file_num = len(os.listdir(out_put_file_path))
    if out_put_file_num == 0:
        out_put_file_num = 1
    if output_sign is None:
        output_result_path = os.path.join(project_folder, 'result_output')
    else:
        output_result_path = os.path.join(project_folder, 'result_output_' + output_sign)
    result_num = len(os.listdir(output_result_path))
    if result_num == 0:
        return False
    elif out_put_file_num != 1 and result_num % out_put_file_num != 0:
        return False
    else:
        return True