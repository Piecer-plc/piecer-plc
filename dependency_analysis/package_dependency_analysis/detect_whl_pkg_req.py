import json
import os
import re


class AnalysisRequirementWhl:
    def __init__(self, build_in_lib):
        self.build_in_lib = build_in_lib

    # 从.whl文件中提取依赖
    def analysis_requirements_from_metadata(self, file_path):
        file_name = os.path.split(file_path)[-1]
        if file_name == "METADATA" or file_name == "metadata":
            dependencies = self.get_requires_from_metadata(file_path)
        else:
            dependencies = self.get_requires_from_metadata_json(file_path)
        if not dependencies:
            return 'no dependencies'
        else:
            return dependencies

    def get_requires_from_metadata(self, file_path):
        pattern = 'Requires-Dist:(.*)\n'
        with open(file_path, encoding='utf-8') as f:
            content = f.read()
        all_dependencies = re.findall(pattern, content)
        dependencies = []
        for dependency in all_dependencies:
            dependency = dependency.replace("\"", '').replace(" ", '')
            dependency = dependency.replace('(', '').replace(')', '')
            if (';' in dependency and 'extra' in dependency) or (
                    dependency in self.build_in_lib):
                continue
            dependencies.append(dependency)
        if not dependencies:
            return 'no dependencies'
        else:
            return dependencies

    def get_requires_from_metadata_json(self, json_file_path):
        with open(json_file_path, encoding='utf-8') as f:
            content = f.read()
            content = json.loads(content)
        dependencies = []
        result = self.get_all_json_key(content)
        for item in result:
            item = item.replace("\"", '').replace(" ", '')
            item = item.replace('(', '').replace(')', '')
            if item in self.build_in_lib:
                continue
            dependencies.append(item)
        return dependencies

    # 获取json格式的所有关键字：
    # json_content :json 内容
    # result ：返回结果，用于递归
    def get_all_json_key(self, dict_a, result=None):
        # res为传入的json数据，循序找出每一个key
        if result is None:
            result = []
        if isinstance(dict_a, dict):  # 使用isinstance检测数据类型
            # 如果为字典类型，则提取key存放到key_list中
            for x in range(len(dict_a)):
                temp_key = list(dict_a.keys())[x]
                temp_value = dict_a[temp_key]
                if temp_key == 'requires':
                    result.extend(temp_value)
                self.get_all_json_key(temp_value, result)
        elif isinstance(dict_a, list):
            # 如果为列表类型，则遍历列表里的元素，将字典类型的按照上面的方法提取key
            for k in dict_a:
                if isinstance(k, dict):
                    for x in range(len(k)):
                        temp_key = list(k.keys())[x]
                        temp_value = k[temp_key]
                        if temp_key == 'requires':
                            result.extend(temp_value)
                        self.get_all_json_key(temp_value, result)
        return result
