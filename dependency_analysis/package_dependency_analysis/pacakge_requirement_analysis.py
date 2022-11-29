import os
from utils import files_utils
from model.package import Package
from uncompress_package import PackageUncompress
from detect_other_pkg_req import AnalysisRequirementOther
from detect_whl_pkg_req import AnalysisRequirementWhl
from buid_in_libraries import PYTHON_STANDARD_LIBRARIES
from dependency_analysis.dependency_analysis_config import pkg_dep_analysis_config


# 分析一个包的依赖
def analysis_package_dependency(package_name, package_version, package_path):
    file_name = os.path.basename(package_path)
    file_format = get_package_file_format(file_name)
    if file_format is None:
        return
    if file_format == '.whl':
        dependencies = analysis_whl_package_dependency(package_path)
    else:
        dependencies = analysis_other_package_dependency(package_path)
    try:
        if not isinstance(dependencies, str):
            dependencies = '||'.join(dependencies)
            dependencies = dependencies.replace('\'', '').replace('\"', '').replace(':', '').replace(' ', '')
        print(dependencies)
        if dependencies == '':
            print('dd')
        Package.update_package_requirements(dependencies,package_name,package_version,file_name)
        print('\n' + '-' * 50 + '\n\n')
    except Exception as e:
        print(str(e))
        print(str(dependencies))
    return dependencies


def analysis_whl_package_dependency(package_path):
    pkg_uncompress = PackageUncompress()
    whl_analysis = AnalysisRequirementWhl(PYTHON_STANDARD_LIBRARIES)
    pkg_uncompress.uncompress_package(package_path, pkg_dep_analysis_config.WHL_UNCOMPRESS_PATH, True)
    folder_name = os.path.basename(package_path).replace('.whl', '')
    folder_path = os.path.join(pkg_dep_analysis_config.WHL_UNCOMPRESS_PATH, folder_name)
    files_path = files_utils.get_files_path_in_folder(folder_path)
    print('metadata 文件分析')
    for path in files_path:
        if 'METADATA' in path:
            dependencies = whl_analysis.analysis_requirements_from_metadata(path)
            return dependencies
    for path in files_path:
        if '.json' in path:
            dependencies = whl_analysis.analysis_requirements_from_metadata(path)
            return dependencies
    files_utils.delete_dir(folder_path)


# 分析除.whl文件以外的文件的依赖
# uncompress_package_path : 解压缩并且处理过后的包的的存放位置
# package_path：未解压的文件的存放位置
# temp_path: 存放临时解压缩文件的位置
def analysis_other_package_dependency(package_path):
    filename = os.path.basename(package_path)
    pkg_uncompress = PackageUncompress()
    other_analysis = AnalysisRequirementOther(PYTHON_STANDARD_LIBRARIES)
    file_format = get_package_file_format(filename)

    if ".tar.gz" == file_format:
        uncompress_path = pkg_dep_analysis_config.GZ_UNCOMPRESS_PATH
        tmp_path = pkg_dep_analysis_config.GZ_TMP_UNCOMPRESS_PATH
    elif ".zip" == filename:
        uncompress_path = pkg_dep_analysis_config.ZIP_UNCOMPRESS_PATH
        tmp_path = pkg_dep_analysis_config.ZIP_TMP_UNCOMPRESS_PATH
    else:
        return

    folder_name = os.path.basename(package_path).replace(file_format, '')
    pkg_uncompress.uncompress_package(package_path, uncompress_path, True)
    folder_path = os.path.join(pkg_dep_analysis_config.GZ_UNCOMPRESS_PATH, folder_name)

    files = files_utils.get_files_path_in_folder(folder_path)
    requires = []
    requires_txt_exist_status = False
    uncompress_folder_path = os.path.join(tmp_path, folder_name)
    for file_path in files:
        file_name = file_path.split('\\')[-1]
        if 'setup' in file_name:
            print('setup 文件分析')
            requires = other_analysis.get_requirements_from_setup_py(file_path)
        elif 'require' in file_name:
            print('requires 文件分析')
            requires_txt_exist_status = True
            pkg_info_path = file_path.replace(file_name, 'PKG-INFO')
            pkg_uncompress.uncompress_package(package_path, tmp_path, False)
            requires = other_analysis.get_requirements_from_requires_txt(file_path, uncompress_folder_path,
                                                                         pkg_info_path)

        if (not isinstance(requires, str) and requires != []) or requires == 'no dependencies':
            return requires

    if not requires_txt_exist_status:
        other_analysis.get_requirements_from_requires_txt(None, uncompress_folder_path, None)

    if not isinstance(requires, str) or requires == 'no dependencies':
        return requires

    return other_analysis.get_requirements_by_run_setup_py(package_path, tmp_path, file_format)


def get_package_file_format(package_file_name):
    if ".zip" in package_file_name:
        return ".zip"
    if ".tar.gz" in package_file_name:
        return ".tar.gz"
    if ".whl" in package_file_name:
        return ".whl"
    return None


if __name__ == "__main__":
    # 使用
    pkg_name = ""
    pkg_version = ""
    pkg_path = ""
    analysis_package_dependency(pkg_name, pkg_version, pkg_path)
