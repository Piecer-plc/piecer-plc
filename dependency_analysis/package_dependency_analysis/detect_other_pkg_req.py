import os
import re
import subprocess

from pkg_resources import Requirement
from astroid import Call, AssignName,MANAGER, Name, Assign
from astroid import Keyword, List, Tuple, Const, Attribute
from astroid.builder import AstroidBuilder
from uncompress_package import PackageUncompress


# urlparse模块主要是用于解析url中的参数  对url按照一定格式进行 拆分或拼接
from utils import files_utils, venv_utils

try:
    import urlparse
except ImportError:
    # python3
    from urllib import parse as urlparse


def _is_filepath(req):
    # this is (probably) a file
    return os.path.sep in req or req.startswith('.')


def _parse_egg_name(url_fragment):
    """
    >>> _parse_egg_name('egg=fish&cake=lala')
    fish
    >>> _parse_egg_name('something_spurious')
    None
    """
    if '=' not in url_fragment:
        return None
    parts = urlparse.parse_qs(url_fragment)
    if 'egg' not in parts:
        return None
    return parts['egg'][0]  # taking the first value mimics pip's behaviour


# 逆urlparse的过程，返回是一个url
def _strip_fragment(urlparts):
    new_urlparts = (
        urlparts.scheme,
        urlparts.netloc,
        urlparts.path,
        urlparts.params,
        urlparts.query,
        None
    )
    return urlparse.urlunparse(new_urlparts)


# 获取python文件的运行结果
def external_cmd(cmd):
    try:
        proc = subprocess.Popen(cmd,
                                shell=True,
                                stdout=subprocess.PIPE,
                                close_fds=True,
                                stderr=subprocess.PIPE,
                                encoding="utf8")
        print("pid:" + str(proc.pid))
        proc.wait(timeout=60)
        stdout_value, stdout_error = proc.communicate()
        return stdout_value, stdout_error
    except Exception:
        raise Exception


class AnalysisRequirementOther:

    PIP_OPTIONS = (
        '-i', '--index-url',
        '--extra-index-url',
        '--no-index',
        '-f', '--find-links',
        '-r'
    )

    printRequireFunction = """
    def setup(**atrrs):
        name = ""
        version = ""
        for k, v in atrrs.items():
            if k.__eq__("name"):
                name = v
                break
        for k, v in atrrs.items():
            if k.__eq__("version"):
                version = v
                break
        for k, v in atrrs.items():
            if k.__eq__("install_requires") or k.__eq__("setup_requires"):
                for req in v:
                    print(req)
                break\n\n"""

    def __init__(self, build_in_lib):
        self.build_in_lib = build_in_lib

    # 通过语法分析树从setup.py文件中提取依赖
    def get_requirements_from_setup_py(self, setup_file_path):
        try:
            from astroid import AstroidBuildingException  # base exception class for all astroid related exceptions
        except ImportError:
            syntax_exceptions = (SyntaxError,)
        else:
            syntax_exceptions = (SyntaxError, AstroidBuildingException)

        try:
            with open(setup_file_path, encoding='UTF-8') as f:
                contents = f.read()
            # 获取抽象语法树 Build astroid from source code string.
            ast = AstroidBuilder(MANAGER).string_build(contents)
        except syntax_exceptions:
            # if the setup file is broken, we can't do much about that...
            # raise CouldNotParseRequirements
            print('语法树获取失败！')
            return []

        walker = SetupWalker(ast)
        requirements = []
        for req in walker.get_requires():
            requirement = DetectedRequirement.parse(req, setup_file_path)
            if requirement is not None and str(requirement) not in self.build_in_lib:
                requirements.append(str(requirement))

        return requirements

    # 通过requires.txt文件获取文件的依赖
    def __get_requirements_from_requires_txt(self, requirements_file, package_info_path):
        # see http://www.pip-installer.org/en/latest/logic.html
        requirements = []
        label = ''
        require_ann = []
        for item in self.get_require_extra_label(package_info_path):
            item = item.strip()
            require_ann.append(item)
        status = False
        with open(requirements_file) as f:
            for req in f.readlines():
                if req.strip() == '' and not status:
                    continue
                if req.strip() == '' and status:
                    status = False
                    label = ''
                    continue

                if req.strip().startswith('#'):
                    # this is a comment
                    continue
                if req.strip().split()[0] in self.PIP_OPTIONS:
                    # this is a pip option
                    continue

                if req.strip().startswith('['):
                    pattern = "[[](.*?)[]]"
                    pattern_compile = re.compile(pattern, re.S)
                    if status:
                        status = False
                        label = ''
                    ann = req.strip()
                    result = re.findall(pattern_compile, ann)
                    if result and self.is_extra_label(require_ann, result[0]):
                        status = True
                        continue
                    else:
                        print(ann)
                        label = result[0]
                        continue
                if status:
                    continue
                detected = DetectedRequirement.parse(req, requirements_file)
                if detected is None:
                    continue
                if label != '':
                    if ':' in label:
                        label.replace(':', '')
                    if '\"' in label:
                        label.replace('\"', '')
                    detected = str(detected) + ';' + label
                if str(detected) not in self.build_in_lib:
                    requirements.append(str(detected))
        if not requirements:
            return 'no dependencies'
        else:
            return requirements

    # 缺少PKG-INFO文件的时候分析获取依赖
    # uncompress_package_name 临时文件夹内解压缩后的package路径
    # package_name
    def get_requirements_from_requires_txt(self, requirements_file, uncompress_package_path, pkg_info_path):
        extra_label = self.get_require_extra_label(pkg_info_path)
        if pkg_info_path and os.path.exists(pkg_info_path) and extra_label and requirements_file:
            return self.__get_requirements_from_requires_txt(requirements_file, pkg_info_path)
        result = self.generate_egg_info_folder(uncompress_package_path)
        generate_folder_path = self.get_generate_folder_path(uncompress_package_path)
        if result and generate_folder_path is not None:
            print('generate success')
            requires_txt_path = os.path.join(generate_folder_path, 'requires.txt')
            pkg_info_path = os.path.join(generate_folder_path, 'PKG-INFO')
            if not os.path.exists(requires_txt_path):
                requires = 'no dependencies'
                files_utils.delete_dir(uncompress_package_path)
            else:
                requires = self.__get_requirements_from_requires_txt(requires_txt_path, pkg_info_path)
                print(os.getcwd())
                files_utils.delete_dir(uncompress_package_path)
            return requires
        else:
            print('generate false! 直接进行分析')
            return self.__get_requirements_from_requires_txt(requirements_file, pkg_info_path)

    # 获取generate后requires的文件夹
    def get_generate_folder_path(self, uncompress_package_path):
        for dir_path, sub_paths, files in os.walk(uncompress_package_path, True):
            for item in sub_paths:
                if '.egg-info' in item:
                    print(os.path.join(dir_path, item))
                    return os.path.join(dir_path, item)
        print("未找到egg 路径")
        return None

    # 生成egg-info目录
    # 生成文件 requires.txt PKG-INFO
    # uncompress_folder_path: 解压缩后的文件夹的存放位置
    def generate_egg_info_folder(self, uncompress_package_path):
        package_files = files_utils.get_files_path_in_folder(uncompress_package_path)
        min_setup_deep = self.get_file_min_deep(package_files, 'setup.py')
        cmd = 'python -W ignore setup.py develop'
        for path in package_files:
            file_name = path.split('\\')[-1]
            deep = len(path.split('\\'))
            if 'setup.py' == file_name and min_setup_deep == deep:
                work_path = path.replace('setup.py', '')
                os.chdir(work_path)
                result = venv_utils.external_cmd(cmd)
                if result:
                    os.chdir(r'D:')
                    return True
                else:
                    break
        os.chdir(r'D:')
        return False

    # 在setup.py文件中插入打印方法，然后运行setup.py文件，输出requirements
    def get_requirements_by_run_setup_py(self, package_path, temp_uncompress_path, file_type):
        uncompress = PackageUncompress()
        uncompress.uncompress_package(package_path, temp_uncompress_path, is_filter=False)
        folder_name = package_path.split('\\')[-1].replace(file_type, '')
        folder_path = temp_uncompress_path + "\\" + folder_name
        setup_path = self.get_setup_file_path(folder_path)
        if setup_path is None:
            return 'no idea'
        result = self.run_my_setup_py(setup_path)
        try:
            print(os.getcwd())
            files_utils.delete_dir(folder_path)
        except Exception as e:
            print(str(e))
            pass
        return result

    # 判断是否是extra标签
    def is_extra_label(self, extra_label, label):
        for item in extra_label:
            extra_form = item + ':'
            if label == item or extra_form in label:
                return True
        return False

    # 获取文件的extra标签：
    def get_require_extra_label(self, package_info_path):
        pattern = 'Provides-Extra:(.*)\n'
        with open(package_info_path, encoding='utf-8') as f:
            content = f.read()
            labels = re.findall(pattern, content)
            if labels:
                print("PKG-INFO   : " + str(labels))
                return labels
            else:
                print('no extra labels')
                return []

    # 获取临时解压缩文件中的setup文件
    def get_setup_file_path(self, folder_path):
        files_path = files_utils.get_files_path_in_folder(folder_path)
        min_deep = self.get_file_min_deep(files_path, 'setup.py')
        for f in files_path:
            deep = len(f.split('\\'))
            if 'setup.py' in f and deep == min_deep:
                return f

    # 获取指定文件名的最小文件夹深度
    def get_file_min_deep(self, files_path, file_name):
        min_deep = -1
        for file in files_path:
            name = file.split('\\')[-1]
            if file_name == name:
                deep = len(file.split('\\'))
                if min_deep == -1:
                    min_deep = deep
                elif deep < min_deep:
                    min_deep = deep
        return min_deep

    # 运行MySetup.py文件并获取依赖
    def run_my_setup_py(self, setup_file_path):
        try:
            setup_file = open(os.path.realpath(setup_file_path), "r+", encoding='UTF-8')
            content = setup_file.read()
            setup_file.close()
            parent_folder = setup_file_path.replace('\\setup.py', '')
            pos = content.find("setup(")
            def_pos = content.find("def ")
            main_pos = content.find("if __name__ == '__main__':")
            if pos == -1:
                pos = content.find("setuptools.setup(")
            # 当文件中存在setup()方法的时候建立新的文件MySetup.py
            if pos != -1:
                if def_pos != -1:
                    print("匹配到setup()方法  匹配到def")
                    content = "# -*- coding:utf-8 -*-\n" + content[:def_pos].strip() + \
                              self.printRequireFunction + content[def_pos:]
                elif main_pos != -1:
                    print("匹配到setup()方法  匹配到main")
                    content = "# -*- coding:utf-8 -*-\n" + content[:main_pos].strip() +\
                              self.printRequireFunction + content[main_pos:]
                else:
                    print("匹配到setup()方法")
                    content = "# -*- coding:utf-8 -*-\n" + content[:pos].strip() + \
                              self.printRequireFunction + content[pos:]

                new_file = parent_folder + "\\" + "MySetup.py"
                setup_file = open(new_file, "w+", encoding='utf-8')
                setup_file.write(content)
                setup_file.close()
                # 执行文件
                results, error = external_cmd("python -W ignore \"" + new_file + "\"")
                if results and not error:
                    print("运行python MySetup.py的结果")
                    requirements = []
                    for item in str(results).split("\n"):
                        item = item.replace(' ', '')
                        if item != '' and item not in self.build_in_lib:
                            requirements.append(item)
                    print(requirements)
                    return requirements
                elif not results and not error:
                    print("run 无结果 ， 确定无依赖")
                    return 'no dependencies'
                else:
                    print("运行出错")
                    return "no idea"
                    # raise Exception
            else:
                print("未找到setup方法")
                return 'no setup'

        except Exception as e:
            print("run_my_setup_py error" + str(e))
            return "no idea"


class DetectedRequirement(object):

    def __init__(self, name=None, url=None, requirement=None, location_defined=None):
        if requirement is not None:
            self.name = requirement.key
            self.requirement = requirement
            self.version_specs = requirement.specs
            self.url = None
        else:
            self.name = name
            self.version_specs = []
            self.url = url
            self.requirement = None
        self.location_defined = location_defined

    def _format_specs(self):
        return ','.join(['%s%s' % (comp, version) for comp, version in self.version_specs])

    def pip_format(self):
        if self.url:
            if self.name:
                return '%s#egg=%s' % (self.url, self.name)
            return self.url
        if self.name:
            if self.version_specs:
                return "%s%s" % (self.name, self._format_specs())
            return self.name

    def __str__(self):
        rep = self.name or 'Unknown'
        if self.version_specs:
            specs = ','.join(['%s%s' % (comp, version) for comp, version in self.version_specs])
            rep = '%s%s' % (rep, specs)
        if self.url:
            rep = '%s (%s)' % (rep, self.url)
        return rep

    def __hash__(self):
        return hash(str(self.name) + str(self.url) + str(self.version_specs))

    def __repr__(self):
        return '%s' % str(self)

    def __eq__(self, other):
        return self.name == other.name and self.url == other.url and self.version_specs == other.version_specs

    def __gt__(self, other):
        return (self.name or "") > (other.name or "")

    @staticmethod
    def parse(line, location_defined=None):
        # the options for a Pip requirements file are:
        #
        # 1) <dependency_name>
        # 2) <dependency_name><version_spec>
        # 3) <vcs_url>(#egg=<dependency_name>)?
        # 4) <url_to_archive>(#egg=<dependency_name>)?
        # 5) <path_to_dir>
        # 6) (-e|--editable) <path_to_dir>(#egg=<dependency_name)?
        # 7) (-e|--editable) <vcs_url>#egg=<dependency_name>
        line = line.strip()

        # strip the editable flag
        line = re.sub('^(-e|--editable) ', '', line)

        url = urlparse.urlparse(line)

        # if it is a VCS URL, then we want to strip off the protocol as urlparse
        # might not handle it correctly
        vcs_scheme = None
        if '+' in url.scheme or url.scheme in ('git',):
            if url.scheme == 'git':
                vcs_scheme = 'git+git'
            else:
                vcs_scheme = url.scheme
            url = urlparse.urlparse(re.sub(r'^%s://' % re.escape(url.scheme), '', line))

        if vcs_scheme is None and url.scheme == '' and not _is_filepath(line):
            # if we are here, it is a simple dependency
            try:
                req = Requirement.parse(line)
            except ValueError:
                # this happens if the line is invalid
                return None
            else:
                return DetectedRequirement(requirement=req, location_defined=location_defined)

        # otherwise, this is some kind of URL
        name = _parse_egg_name(url.fragment)
        url = _strip_fragment(url)

        if vcs_scheme:
            url = '%s://%s' % (vcs_scheme, url)

        return DetectedRequirement(name=name, url=url, location_defined=location_defined)


# 用来分析setup.py文件中的install_info
class SetupWalker(object):

    def __init__(self, ast):
        self._ast = ast
        self._setup_call = None
        self._top_level_assigns = {}
        self.walk()

    # 找到调用setup()方法的节点
    def walk(self, node=None):
        # node 为空说明在队头
        top = node is None
        # node 不为空 则 node=node node为空则node=ast
        node = node or self._ast

        # test to see if this is a call to setup()
        # 判断节点是不是Call 类型
        if isinstance(node, Call):
            for child_node in node.get_children():
                if isinstance(child_node, Name) and child_node.name == 'setup':
                    # TODO: what if this isn't actually the distutils setup?
                    self._setup_call = node
                elif isinstance(child_node, Attribute) and child_node.attrname == 'setup':
                    self._setup_call = node

        for child_node in node.get_children():
            if top and isinstance(child_node, Assign):
                for target in child_node.targets:
                    if isinstance(target, AssignName):
                        self._top_level_assigns[target.name] = child_node.value
            self.walk(child_node)

    # 获取AST中的常数值
    def _get_list_value(self, list_node):
        values = []
        for child_node in list_node.get_children():
            if not isinstance(child_node, Const):
                # we can't handle anything fancy, only constant values
                # raise CouldNotParseRequirements
                return []
            values.append(child_node.value)
        return values

    # 通过setup.py 文件分析Call(setup)节点
    def get_requires(self):
        # first, if we have a call to setup, then we can see what its "install_requires" argument is
        if not self._setup_call:
            print("无setup 调用")
            return []

        found_requirements = []

        for child_node in self._setup_call.get_children():
            if not isinstance(child_node, Keyword):
                # do we want to try to handle positional arguments?
                continue

            if child_node.arg not in ('install_requires', 'requires'):
                continue

            if isinstance(child_node.value, (List, Tuple)):
                # joy! this is a simple list or tuple of requirements
                # this is a Keyword -> List or Keyword -> Tuple
                found_requirements += self._get_list_value(child_node.value)
                continue

            if isinstance(child_node.value, Name):
                # otherwise, it's referencing a value defined elsewhere
                # this will be a Keyword -> Name
                try:
                    reqs = self._top_level_assigns[child_node.value.name]
                except KeyError:
                    print('KeyError')
                    return []
                    # raise CouldNotParseRequirements
                else:
                    if isinstance(reqs, (List, Tuple)):
                        found_requirements += self._get_list_value(reqs)
                        continue

            # otherwise it's something funky and we can't handle it
            # raise CouldNotParseRequirements
            return []

        # if we've fallen off the bottom with nothing in our list of requirements,
        #  we simply didn't find anything useful
        if len(found_requirements) > 0:
            return found_requirements
        else:
            return []
        # raise CouldNotParseRequirements

