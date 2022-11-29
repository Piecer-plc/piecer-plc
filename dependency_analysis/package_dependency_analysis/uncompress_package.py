import os
import shutil
from utils import venv_utils


class PackageUncompress:

    def __init__(self, exe_7z_path=None, exe_winRar_path=None):
        self.exe_7z_path = exe_7z_path
        self.exe_winRar_path = exe_winRar_path
        # cmd命令的参数，只解压符合格式的文件
        self.remain_files = " require*.txt setup*.py PKG-INFO.* "

    # is_filter : True 只提取remain_files中的文件
    def uncompress_tar_gz_package(self, package_path, target_path, is_filter: bool):
        package_name = os.path.basename(package_path)
        file_name = package_name.replace('.tar.gz', '')
        save_path = os.path.join(target_path, file_name)
        if os.path.exists(save_path):
            print("Have uncompress " + package_name + " to " + target_path)
            return
        else:
            os.makedirs(save_path)
        if is_filter:
            cmd = self.exe_winRar_path + " -ibck -y x " + package_path + " " + save_path + self.remain_files
        else:
            cmd = self.exe_winRar_path + " -ibck -y x " + package_path + " " + save_path
        venv_utils.external_cmd(cmd)

    def uncompress_zip_package(self, package_path, target_path, is_filter:bool):
        package_name = os.path.basename(package_path)
        file_name = package_name.replace('.zip', '')
        save_path = os.path.join(target_path, file_name)
        if os.path.exists(save_path):
            print("Have uncompress " + package_name + " to " + target_path)
            return
        else:
            os.makedirs(save_path)
        if is_filter:
            cmd = self.exe_winRar_path + " -ibck -y x " + package_path + " " + save_path + self.remain_files
        else:
            cmd = self.exe_winRar_path + " -ibck -y x " + package_path + " " + save_path
        venv_utils.external_cmd(cmd)

    def uncompress_whl_package(self, package_path, target_path, is_filter: bool):
        package_name = os.path.basename(package_path)
        file_name = package_name.replace('.zip', '')
        save_path = os.path.join(target_path, file_name)
        if os.path.exists(save_path):
            print("Have uncompress " + package_name + " to " + target_path)
            return
        else:
            os.makedirs(save_path)
        shutil.copy(package_path, target_path)
        copy_pkg_path = os.path.join(target_path, package_path)
        if is_filter:
            delete_cmd = self.exe_7z_path + " d \"" + copy_pkg_path + "\" -x!METADATA -x!METADATA.json -r"
            venv_utils.external_cmd(delete_cmd)
        uncompress_cmd = self.exe_7z_path + "x \"" + copy_pkg_path + ".whl\" -o\"" + save_path + "\""
        venv_utils.external_cmd(uncompress_cmd)
        os.remove(copy_pkg_path)

    def uncompress_package(self, package_path, target_path, is_filter: bool):
        package_name = os.path.basename(package_path)
        if '.tar.gz' in package_name:
            self.uncompress_tar_gz_package(package_path, target_path, is_filter)
        elif '.zip' in package_name:
            self.uncompress_zip_package(package_path, target_path, is_filter)
        elif '.whl' in package_name:
            self.uncompress_whl_package(package_path, target_path, is_filter)
        else:
            print("Can't uncompress " + package_name + " False format")
