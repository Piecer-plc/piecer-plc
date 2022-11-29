import os
import platform
import re
import sys

from packaging.specifiers import SpecifierSet
from packaging.version import parse, Version


# 处理dependency_ann:
def deal_req_ann(req_ann, py_version):
    if "(" in req_ann and ")" in req_ann:
        return False
    elif '#or#' in req_ann:
        req_ann_list = req_ann.split('#or#')
        for or_item in req_ann_list:
            if '#and#' in or_item:
                state = True
                and_item_list = or_item.split('#and#')
                for and_item in and_item_list:
                    result = __is_the_restrict_met(and_item, py_version)
                    if not result:
                        state = False
                        break
                if state:
                    return True
            else:
                result = __is_the_restrict_met(or_item, py_version)
                if result:
                    return True

    elif '#and#' in req_ann:
        state = True
        and_item_list = req_ann.split('#and#')
        for and_item in and_item_list:
            result = __is_the_restrict_met(and_item, py_version)
            if not result:
                state = False
                break
        if state:
            return True
    elif '#in#' in req_ann:
        versions = req_ann.split('#in#')[-1].split(',')
        if py_version in versions:
            return True
        else:
            return False
    else:
        return __is_the_restrict_met(req_ann, py_version)
    return False


def __is_the_restrict_met(req_ann, py_version):
    python_version_format1 = "python_version[<=>!]"
    python_version_format1_search = re.search(python_version_format1, req_ann)
    python_version_format2 = "python[<=>!]"
    python_version_format2_search = re.search(python_version_format2, req_ann)
    platform_release_name_format = 'platform_release[><=]'
    platform_release_name_format_search = re.search(platform_release_name_format, req_ann)
    platform_system_format = "platform_system[!=]"
    platform_system_format_search = re.search(platform_system_format, req_ann)
    sys_platform_format = "sys[._]platform[!=]"
    sys_platform_format_search = re.search(sys_platform_format, req_ann)
    platform_python_implementation_format = "platform[._]python_implementation[=!]"
    platform_python_implementation_format_search = re.search(platform_python_implementation_format, req_ann)
    implementation_name_format = 'implementation_name[!=]'
    implementation_name_format_search = re.search(implementation_name_format, req_ann)
    python_implementation_format = "python_implementation[!=]"
    python_implementation_format_search = re.search(python_implementation_format, req_ann)
    python_full_version_format = 'python_full_version[><=!]'
    python_full_version_format_search = re.search(python_full_version_format, req_ann)
    os_name_format = "os_name[!=]"
    os_name_format_search = re.search(os_name_format, req_ann)
    if python_version_format1_search or python_version_format2_search or python_full_version_format_search:
        return __deal_python_version_ann(req_ann, py_version)
    if platform_system_format_search:
        return __deal_platform_system_ann(req_ann)
    if sys_platform_format_search:
        return __deal_sys_platform_ann(req_ann)
    if platform_python_implementation_format_search:
        return __deal_platform_python_imp_ann(req_ann)
    if implementation_name_format_search:
        return __deal_imp_name_ann(req_ann)
    if python_implementation_format_search:
        return __deal_python_imp_ann(req_ann)
    if os_name_format_search:
        return __deal_os_name(req_ann)
    if platform_release_name_format_search:
        return __deal_platform_release_ann(req_ann)


def __deal_imp_name_ann(dependency_ann):
    implementation_name_format = 'implementation_name[!=]'
    ann_format = re.findall(implementation_name_format, dependency_ann)[0]
    implementation_name_info = dependency_ann.replace(ann_format + '=', '').lower()
    if '!=' in dependency_ann and platform.python_implementation().lower() != implementation_name_info:
        return True
    if '==' in dependency_ann and platform.python_implementation().lower() == implementation_name_info:
        return True
    return False


def __deal_platform_release_ann(dependency_ann):
    release = platform.release()
    if '>=' in dependency_ann:
        ann_release = dependency_ann.split('>=')[1]
        if parse(release) >= parse(ann_release):
            return True
        else:
            return False
    if '<=' in dependency_ann:
        ann_release = dependency_ann.split('<=')[1]
        if parse(release) <= parse(ann_release):
            return True
        else:
            return False
    if '>' in dependency_ann:
        ann_release = dependency_ann.split('>')[1]
        if parse(release) > parse(ann_release):
            return True
        else:
            return False
    if '<' in dependency_ann:
        ann_release = dependency_ann.split('<')[1]
        if parse(release) < parse(ann_release):
            return True
        else:
            return False
    return False


def __deal_sys_platform_ann(dependency_ann):
    sys_platform_format = "sys[._]platform[!=]"
    ann_format = re.findall(sys_platform_format, dependency_ann)[0]
    sys_info = dependency_ann.replace(ann_format + '=', '').lower()
    if '!=' in dependency_ann and sys.platform != sys_info:
        return True
    if '==' in dependency_ann and sys.platform == sys_info:
        return True
    return False


def __deal_platform_python_imp_ann(dependency_ann):
    platform_python_implementation_format = "platform[._]python_implementation[=!]"
    ann_format = re.findall(platform_python_implementation_format, dependency_ann)[0]
    platform_python_implementation_info = dependency_ann.replace(ann_format + '=', '')
    if '!=' in dependency_ann and platform.python_implementation() != platform_python_implementation_info:
        return True
    if '==' in dependency_ann and platform.python_implementation() == platform_python_implementation_info:
        return True
    return False


def __deal_python_imp_ann(dependency_ann):
    python_imp_format = "python_implementation[!=]"
    ann_format = re.findall(python_imp_format, dependency_ann)[0]
    platform_python_imp_info = dependency_ann.replace(ann_format + '=', '')
    if '!=' in dependency_ann and platform.python_implementation() != platform_python_imp_info:
        return True
    if '==' in dependency_ann and platform.python_implementation() == platform_python_imp_info:
        return True
    return False


def __deal_os_name(dependency_ann):
    os_name_format = "os_name[!=]"
    ann_format = re.findall(os_name_format, dependency_ann)[0]
    os_name_info = dependency_ann.replace(ann_format + '=', '')
    if '!=' in dependency_ann and os.name != os_name_info:
        return True
    if '==' in dependency_ann and os_name_format == os_name_info:
        return True
    return False


def __deal_platform_system_ann(dependency_ann):
    platform_system_format = "platform_system[!=]"
    ann_format = re.findall(platform_system_format, dependency_ann)[0]
    platform_sys_info = dependency_ann.replace(ann_format + '=', '')
    if '!=' in dependency_ann and platform.system() != platform_sys_info:
        return True
    if '==' in dependency_ann and platform.system() == platform_sys_info:
        return True
    return False


def __deal_python_version_ann(dependency_ann, python_version):
    python_version_format1 = "python_version[<=>!]"
    python_version_format2 = "python[<=>!]"
    python_full_version_format = 'python_full_version[><=!]'
    search1 = re.search(python_version_format1, dependency_ann)
    search2 = re.search(python_version_format2, dependency_ann)
    search3 = re.search(python_full_version_format, dependency_ann)
    python_constrict = None
    if search1:
        python_constrict = dependency_ann.replace('python_version', '')
    if search2:
        python_constrict = dependency_ann.replace('python', '')
    if search3:
        python_constrict = dependency_ann.replace('python_full_version', '')
    if python_constrict is None:
        return True
    return __is_version_meet_constrict(python_version, python_constrict)


def __is_version_meet_constrict(version, constrict):
    if Version(version) in SpecifierSet("".join(constrict)):
        return True
    else:
        return False
