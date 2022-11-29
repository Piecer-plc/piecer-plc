import json
import linecache
import os
import re
import shutil
import codecs

import numpy as np

from model.pipeline import Pipeline
from utils import venv_utils


# 判断两个集合是否有相同元素
def is_contain_same_elements(array_a, array_b):
    for item_a in array_a:
        if item_a in array_b:
            return True, item_a
    for item_a in array_a:
        if item_a in array_b:
            return True, item_a
    return False, ''


# 创建一个txt文件，文件名为name ,并向文件写入msg,保存在path内
def txt_write_into(file_path, msg, clear=False):
    # desktop_path = "C:\\Users\\Administrator\\Desktop\\"  # 新创建的txt文件的存放路径
    try:
        if clear:
            file = codecs.open(file_path, 'w', 'utf-8')
        else:
            file = codecs.open(file_path, 'a', 'utf-8')
        file.write(msg)
    except Exception as e:
        print('txt_write_into error :' + str(e))
        print(msg)
        print('\n' + file_path)
        print('-' * 50)


def get_file_content(txt_path):
    with open(txt_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
        f.close()

    success_list = content.split('\n')
    return success_list

# 创建一个txt文件，文件名为name ,并向文件写入msg,保存在path内
def txt_write_into_in_head(file_path, msg):
    # desktop_path = "C:\\Users\\Administrator\\Desktop\\"  # 新创建的txt文件的存放路径
    try:
        file = codecs.open(file_path, 'r+', 'utf-8')
        content = file.read()
        content = msg + content
        file.seek(0)
        file.write(content)
        file.close()
    except Exception as e:
        print('txt_write_into error :' + str(e))
        print(msg)
        print('\n' + file_path)
        print('-' * 50)


# 查找某一个字符在字符串中的所有位置
def find_all_character_index_in_string(character, string):
    index_list = [i.start() for i in re.finditer(character, string)]
    return index_list


# 获取文件夹下面的所有文件的路径
# folder_path 文件夹路径
def get_files_path_in_folder(folder_path):
    results = []
    for dir_path, sub_paths, files in os.walk(folder_path, True):
        results.extend([dir_path + '\\' + file for file in files])
    return results


# 获取ipynb文件所在的文件夹，将ipynb文件转为.py文件
# compete_path：下载的project的竞赛文件夹
def ipynb_to_py(compete_path):
    i=0
    for project_name in os.listdir(compete_path):
        project_path = os.path.join(compete_path, project_name)
        file_name = str(project_name.split('#id#')[0])
        ipynb_file_name = file_name + '.ipynb'
        py_file_name = file_name + '.py'
        py_file_path = os.path.join(project_path, py_file_name)
        ipynb_file_path = os.path.join(project_path, ipynb_file_name)
        if os.path.exists(py_file_path):
            print('have exist')
            continue
        i +=1
        print(i)
        os.chdir(project_path)
        cmd = 'jupyter nbconvert --to script {}'.format(ipynb_file_name)
        # os.system(cmd)
        result = venv_utils.external_cmd(cmd)
        print(project_path + "   " + ipynb_file_name)
        if result == 'NotJSONError':
            shutil.copy(ipynb_file_path, py_file_path)
        print('-' * 60)


def ipynb_file_to_py_file(file_path, support_os):
    if "\\" in file_path:
        file_path = file_path.replace("\\", "/")
    file_name = file_path.split("/")[-1]
    work_path = os.getcwd()
    project_path = file_path.replace(file_name, "")
    py_file_path = file_path.replace(".ipynb", ".py")
    os.chdir(project_path)
    if support_os == "win_amd64":
       cmd = 'jupyter nbconvert --to script {}'.format(file_name)
    else:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "run_experiment\\run_experiment_config.json")
        with open(config_path) as f:
            conda_path = json.load(f)["linux_conda_bin"]
        cmd = conda_path + 'jupyter nbconvert --to script {}'.format(file_name)
    result = venv_utils.external_cmd(cmd)
    print(project_path + "   " + file_name)
    if result == 'NotJSONError':
        shutil.copy(file_path, py_file_path)
    os.chdir(work_path)



# 删除目录
def delete_dir(dir_path):
    cmd = "rd /s /q \"" + dir_path + "\""
    print("delete " + dir_path)
    venv_utils.external_cmd(cmd)


# 打开pipeline project文件夹位置
# root file = r'D:\A_run\kaggle_compete
def open_pipeline_folder(pipeline_id, root_path):
    project_path = Pipeline.get_pipeline_save_path(pipeline_id, root_path)
    # cmd ="C:\Windows\explorer.exe \"%s\"" % project_path
    # print(cmd)
    # os.startfile(project_path)
    print(pipeline_id)
    print(project_path)
   # os.system(cmd)


def get_pipeline_file_path_linux(pipeline_id, root_path):
    file_path = Pipeline.get_pipeline_py_file_save_path(pipeline_id, root_path)
    project_path = Pipeline.get_pipeline_save_path(pipeline_id, root_path)
    print("File Path: %s" % file_path)
    print("Proj Path: %s" % project_path)


def open_pipeline_file_win(pipeline_id, root_path, file_type):
    file_path = None
    if file_type == "origin":
        file_path = Pipeline.get_pipeline_py_file_save_path(pipeline_id, root_path)
    if file_type == "clean":
        file_path = Pipeline.get_pipeline_save_path(pipeline_id, root_path)
        file_path = os.path.join(file_path, "clean_file.py")
    if file_type == "run":
        "run_files_experiment"
        project_path = Pipeline.get_pipeline_save_path(pipeline_id, root_path)
        for folder in os.listdir(project_path):
            if "run_files_experiment" in folder:
                file_path = os.path.join(project_path, folder, "pipeline_run1.py")
                break
    if file_path is None or not os.path.exists(file_path):
        print("FileNotFindError")
        return
    cmd = 'D:/Software/Notepad++/notepad++.exe "%s"' % file_path
    venv_utils.external_cmd(cmd)


if __name__ == '__main__':
    # root_path = r"G:\RQ2_compete_valid"
    # 37620,34068,32383,36907,38126
    root_path = r"E:\rq2_fix"
    # new 31787 36511 35724
    # old 35720 36483 34020  36490  34334
    for i in [20679


]:
        a = np.mean([1,2,3])
        print(a)
        open_pipeline_folder(i, root_path)
    # root_path = r"D:\A_run\kaggle_compete"
    # # move_machine_learning_file(root_path, 'D:/new_kaggle_compete')
    # open_pipeline_folder(25815, root_path)
    # i = 0
    # for compete_name in business_utils.get_RQ1_comppetes()[:5]:
    #     print(i+1)
    #     i = i+1
    #     compete_path = os.path.join(root_path, compete_name)
    #     ipynb_to_py(compete_path)
    # ipynb_to_py("E:\RQ2_compete_valid\GitHub")
