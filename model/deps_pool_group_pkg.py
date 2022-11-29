from model.database_pool import DatabasePool
from pymysql.converters import escape_string


class DepsPoolGroupPkg:
    def __init__(self, pipeline_id=None, group_No=None, pkg_name=None, pkg_versions=None):
        self.pipeline_id = pipeline_id
        self.group_No = group_No
        self.pkg_name = pkg_name
        self.pkg_versions = pkg_versions

    def insert_into_deps_pool_group_pkg(self):
        sql = "insert into deps_pool_group_pkg (pipeline_id,group_No,pkg_name,pkg_versions) values (%d,%d,'%s','%s')"
        sql = sql % (self.pipeline_id, self.group_No, self.pkg_name, escape_string(self.pkg_versions))
        database = DatabasePool()
        database.insert(sql)


if __name__ == "__main__":
   print('hhhh')