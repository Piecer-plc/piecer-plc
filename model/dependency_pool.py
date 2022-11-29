import ast
from typing import List
from model.database_pool import DatabasePool
from pymysql.converters import escape_string
from utils import object_utils


class DepsPoolItem:
    def __init__(self, pkg_name=None, deepest_level=None, rule_based_versions: List = None, pkg_dep_info: dict = None,
                 pkg_files_info: dict = None, reqs_group: dict = None, analysis_state=None):
        self.pkg_name = pkg_name
        self.deepest_level = deepest_level
        self.rule_based_versions = rule_based_versions
        self.reqs_group = reqs_group
        self.pkg_dep_info = pkg_dep_info
        self.pkg_files_info = pkg_files_info
        self.analysis_state = analysis_state

    def param_type_convert(self):
        if not isinstance(self.pkg_dep_info, dict):
            self.pkg_dep_info = ast.literal_eval(self.pkg_dep_info)
        if not isinstance(self.pkg_files_info, dict):
            self.pkg_files_info = ast.literal_eval(self.pkg_files_info)
        if not isinstance(self.reqs_group, dict):
            self.reqs_group = ast.literal_eval(self.reqs_group)
        if not isinstance(self.rule_based_versions, List):
            self.rule_based_versions = self.rule_based_versions.replace('[', '').replace(']', '').replace('\'',
                                                                                                          '').replace(
                ' ', '')
            self.rule_based_versions = self.rule_based_versions.split(',')

    # 判断pool_item在dependencies_pool表中是否存在pool item
    def is_item_exist_in_deps_pool(self, pipeline_id, python_version, group_No):
        sql = "select pkg_name from dependencies_pool where pipeline_id=%d and pkg_name='%s' and python_version=" \
              "'%s' and group_No = %d limit  1" % (pipeline_id, self.pkg_name, python_version, group_No)
        database = DatabasePool()
        result = database.fetchone(sql)
        if result:
            return True
        else:
            return False

    def update_dep_pool_item_rule_based_ver(self, pipeline_id, python_version):
        sql = "update dependencies_pool set rule_based_versions='%s' where pipeline_id=%d and python_version='%s' " \
              "and pkg_name='%s'" % (self.rule_based_versions, pipeline_id, python_version, self.pkg_name)
        database = DatabasePool()
        database.update(sql)


class DepsPool:
    def __init__(self, pipeline_id=None, python_version=None, support_os=None, dep_item_list: List[DepsPoolItem] = None,
                 group_No=None):
        self.pipeline_id = pipeline_id
        self.python_version = python_version
        self.dep_item_list = dep_item_list
        self.support_os = support_os
        self.group_No = group_No

    def insert_into_deps_pool(self):
        database = DatabasePool()
        base_sql = "insert into dependencies_pool(pipeline_id, python_version, pkg_name, deepest_level, " \
                   " rule_based_versions, pkg_dep_info, pkg_files_info, reqs_group, analysis_state, support_os, " \
                   "group_No) values (%d, '%s', '%s', %d, '%s', '%s', '%s', '%s', '%s', '%s', '%d') "
        for item in self.dep_item_list:
            sql = base_sql % (self.pipeline_id, self.python_version, item.pkg_name, item.deepest_level,
                              escape_string(str(item.rule_based_versions)), escape_string(str(item.pkg_dep_info)),
                              escape_string(str(item.pkg_files_info)), escape_string(str(item.reqs_group)),
                              str(item.analysis_state), self.support_os, self.group_No)
            if item.is_item_exist_in_deps_pool(self.pipeline_id, self.python_version, self.group_No):
                print("item have exist in pool ", self.pipeline_id, " group No:", self.group_No)
                continue
            else:
                database.insert(sql)
                print('insert id:', self.pipeline_id, ' pkg: ' + item.pkg_name + " group No:", self.group_No)

    @staticmethod
    def get_deps_pool(pipeline_id, py_version, group_No):
        sql = "select * from dependencies_pool where pipeline_id=%d  and python_version='%s' and group_No=%d"
        sql = sql % (pipeline_id, py_version, group_No)
        database = DatabasePool()
        result = database.fetchall(sql)
        item_list = []
        for item in result:
            dep_pool_item = object_utils.dict_to_obj(item, DepsPoolItem())
            dep_pool_item.param_type_convert()
            item_list.append(dep_pool_item)
        return DepsPool(pipeline_id=pipeline_id, python_version=py_version, dep_item_list=item_list)

    @staticmethod
    def get_deps_pool_info(pipeline_id, py_version, group_No):
        sql = "select * from dependencies_pool where pipeline_id=%d  and python_version='%s' and group_No=%d"
        sql = sql % (pipeline_id, py_version, group_No)
        database = DatabasePool()
        result = database.fetchall(sql)
        pool_info = {}
        for item in result:
            dep_pool_item = object_utils.dict_to_obj(item, DepsPoolItem())
            dep_pool_item.param_type_convert()
            pool_info.update({item['pkg_name']: dep_pool_item})
        return pool_info

    @staticmethod
    def is_exist_dep_pool(pipeline_id, python_version):
        sql = "select pipeline_id from dependencies_pool where pipeline_id=%d and python_version='%s'" % (
        pipeline_id, python_version)
        database = DatabasePool()
        result = database.fetchone(sql)
        if result:
            return True
        else:
            return False

    @staticmethod
    def delete_dependencies_pool(pipeline_id):
        sql = "delete from dependencies_pool where pipeline_id = %d" % pipeline_id
        database = DatabasePool()
        print("delete dependencies pool pipeline_id %d" % pipeline_id)
        database.update(sql)

    @staticmethod
    def max_deps_pool_group_num(pipeline_id, python_version):
        sql = "select max(group_No) from dependencies_pool where pipeline_id = %d and python_version='%s'"
        sql = sql % (pipeline_id, python_version)
        result = DatabasePool().fetchone(sql)
        if not result:
            return result['group_No']
        else:
            return None

    @staticmethod
    def get_group_nums(pipeline_id, python_version):
        sql = "select distinct group_No from dependencies_pool where pipeline_id = %d and python_version='%s'"
        sql = sql % (pipeline_id, python_version)
        result = DatabasePool().fetchall(sql)
        if not result:
            return []
        return [item['group_No'] for item in result]

    @staticmethod
    def filter(pipeline_id=None, support_os=None, python_version=None, group_No=None, columns: list = None,
               distinct: bool = False):
        select = "select distinct " if distinct else "select "
        select_columns = "*" if not columns else ','.join(columns)
        sql = select + select_columns + " from dependencies_pool"
        filter_state = False
        if pipeline_id:
            sql += " where pipeline_id = %d" % pipeline_id
            filter_state = True

        if support_os and filter_state:
            sql += " and support_os = '%s'" % support_os

        if support_os and not filter_state:
            sql += " where support_os = '%s'" % support_os
            filter_state = True

        if python_version and filter_state:
            sql += " and python_version = '%s'" % python_version

        if python_version and not filter_state:
            sql += " where python_version = '%s'" % python_version
            filter_state = True

        if group_No and filter_state:
            sql += " and group_No = %d" % group_No

        if group_No and not filter_state:
            sql += " where group_No = %d" % group_No

        database = DatabasePool()
        return database.fetchall(sql)


if __name__ == "__main__":
    dep_pool = DepsPool.get_deps_pool(1079, '3.7.10', 1)
    print("ddd")
