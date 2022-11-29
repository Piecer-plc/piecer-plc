from model.database_pool import DatabasePool
from packaging.version import parse


class PkgVersionUsage:
    def __init__(self, package_name=None, package_version=None, version_usage=None):
        self.package_name = package_name
        self.package_version = package_version
        self.version_usage = version_usage

    def get_pkg_popular_versions(self, top_num=None):
        sql = "select version,version_usage from package_version_usage where package_name='%s' and version_usage!='' " \
              "ORDER BY version_usage DESC " % self.package_name
        database = DatabasePool()
        result = database.fetchall(sql)
        popular_versions = []
        if not result:
            return []
        for item in result:
            popular_versions.append(item['version'])
        if top_num:
            return popular_versions[: top_num]
        else:
            return popular_versions

    # 判断是否爬取了version_usage
    @staticmethod
    def is_spider(package_name):
        sql = "select version_usage from package_version_usage where package_name='%s' and version_usage!=''" % package_name
        database = DatabasePool()
        result = database.fetchall(sql)
        if result:
            return True
        else:
            return False

    @staticmethod
    def is_exist(pkg_name, pkg_version):
        sql = "select * from package_version_usage where package_name = '%s' and version = '%s' limit 1" % (
            pkg_name, pkg_version)
        database = DatabasePool()
        result = database.fetchone(sql)
        if result:
            return True
        else:
            return False

    @staticmethod
    # 更新dependency_version表里面的version_usage
    def update_version_usage(package_name, package_version, version_usage):
        sql = "update package_version_usage set version_usage = '%s' where package_name = '%s' and version='%s'" % (
            version_usage, package_name, package_version)
        database = DatabasePool()
        database.update(sql)
        print("update " + package_name + ' ' + package_version + ' ' + version_usage)

    @staticmethod
    # 向dependency_version中插入数据
    def insert(package_name, version, version_usage):
        sql = "insert into package_version_usage (package_name, version, version_usage) values ('%s', '%s', '%s')" % (
            package_name, version, version_usage)
        database = DatabasePool()
        if not PkgVersionUsage.is_exist(package_name, version):
            database.insert(sql)
            print('insert ' + package_name + ' ' + version + '  ' + version_usage)


