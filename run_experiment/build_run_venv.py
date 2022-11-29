import os
from utils import venv_utils
from build_envirement import deal_package_reqs
from spider_data.spider_pypi_data import packages_spider


class BuildRunVenv:
    def __init__(self, venv_root, pkg_root, support_os, concerned_stages: list, py_version="3.7.10"):
        self.venv_root = venv_root
        self.py_version = py_version
        self.pkg_root = pkg_root
        self.support_os = support_os
        self.concerned_stages = concerned_stages
        self.concerned_stages.sort()
        self.concerned_stages_str = ','.join(self.concerned_stages)

    # 创建虚拟环境
    # 参数：
    #    venv_path 建立的虚拟环境的地址，地址的最后一级是venv的名
    #    python_version 创建的虚拟环境的python版本
    #    dependencies  项目的依赖包
    def __create_initial_virtual_environment(self, venv_path):
        create_venv_cmd = 'echo yes | conda create --prefix="' + venv_path + '" python=' + self.py_version
        activate_cmd = 'conda activate "' + venv_path + '"'
        pip_update_cmd = 'python -m pip install --upgrade pip'
        result, value = venv_utils.external_cmd(create_venv_cmd)
        if result:
            print(value)
        result, value = venv_utils.external_cmd(activate_cmd + ' && ' + pip_update_cmd)
        if result:
            print(value)

    def __batch_install_pkgs_local(self, install_info_list, venv_path):
        for item in install_info_list:
            download_files = item["package_files"].split(',')
            print(download_files)
            download_files = download_files_sort(download_files)
            print(download_files)
            for download_file in download_files:
                os_name = deal_package_reqs.get_whl_package_file_support_os(download_file)
                if os_name and os_name != self.support_os and os_name!="any":
                    continue
                print(download_file)
                download_file_path = os.path.join(self.pkg_root, download_file)
                download_file_path = download_file_path.replace('\\', '/')
                if not os.path.exists(download_file_path):
                    packages_spider.spider_packages_by_download_name_list([download_file], self.pkg_root)
                result = self.__install_local_packages_in_venv(download_file_path, venv_path)
                if result:
                    print(result)
                    break
                else:
                    print('install error try install another')

    def __batch_install_pkgs_pypi(self, install_info_list, venv_path):
        for item in install_info_list:
            pkg_name = item['install_package']
            pkg_version = item['install_version']
            self.__install_pypi_packages_in_venv(pkg_name, pkg_version, venv_path)

    def __get_venv_path(self, pipeline_id, venv_num):
        venv_path = os.path.join(self.venv_root, str(pipeline_id))
        venv_name = str(venv_num) + '-'.join(self.concerned_stages)
        return os.path.join(venv_path, venv_name)

    def __install_local_packages_in_venv(self, download_file_path, venv_path):
        activate_cmd = 'conda activate "' + venv_path + '"'
        install_cmd = 'pip install "' + download_file_path + '"'
        cmd = activate_cmd + " && " + install_cmd
        print(cmd)
        result, info = venv_utils.external_cmd(cmd)
        return result

    def __install_pypi_packages_in_venv(self, pkg_name, pkg_version, venv_path):
        activate_cmd = 'conda activate "' + venv_path + '"'
        install_cmd = 'pip install "' + pkg_name + '==' + pkg_version
        cmd = activate_cmd + " && " + install_cmd
        print(cmd)
        result, info = venv_utils.external_cmd(cmd)
        return result

    def build_run_venv(self, pipeline_id, venv_num, venv_install_list):
        venv_path = self.__get_venv_path(pipeline_id, venv_num)
        if not os.path.exists(venv_path) or not os.listdir(venv_path):
            self.__create_initial_virtual_environment(venv_path)
        if self.support_os == "win_amd64":
            self.__batch_install_pkgs_local(venv_install_list, venv_path)
        else:
            self.__batch_install_pkgs_pypi(venv_install_list, venv_path)


# 对download_file的文件排序，
def download_files_sort(download_files):
    right = len(download_files)
    left = 0
    while left < right and right > 0:
        download_file = download_files[left]
        os_name = deal_package_reqs.get_whl_package_file_support_os(download_file)
        if '.tar.gz' in download_file or '.zip' in download_file or not (os_name == "win_amd64" or os_name == "any"):
            right -= 1
            temp = download_files[right]
            download_files[right] = download_files[left]
            download_files[left] = temp
        else:
            left += 1
    return download_files
