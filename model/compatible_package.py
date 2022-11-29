import re

from model.database_pool import DatabasePool
from packaging.specifiers import SpecifierSet
from packaging.version import Version


class CompatiblePkg:
    def __init__(self, pkg_name, pkg_version_range, compatible_pkg, compatible_pkg_version_range):
        self.pkg_name = pkg_name
        self.pkg_version_range = pkg_version_range
        self.compatible_pkg = compatible_pkg
        self.compatible_pkg_version_range = compatible_pkg_version_range

    @staticmethod
    def compatibility_check(packages_info: dict) -> bool:
        """
        :param packages_info:
          package info is dict type
        such as:
          {
            "keras":"2.4.1",
            "tensorflow":"2.7.0",
            "scikit-learn:"1.0.1"
          }

        :return: if these packages and them versions is compatible return True,otherwise return False
        """
        packages = list(packages_info.keys())
        versions = list(packages_info.values())
        if len(packages) <= 1:
            return True
        for i in range(len(packages)-1):
            j = i+1
            while j < len(packages):
                if not CompatiblePkg.is_package_compatible(packages[i], versions[i], packages[j], versions[j]):
                    return False
                j += 1
        return True

    @staticmethod
    def is_package_compatible(pkg_name1, pkg_version1, pkg_name2, pkg_version2):
        result1 = CompatiblePkg.filter(pkg_name1, pkg_name2)
        result2 = CompatiblePkg.filter(pkg_name2, pkg_name1)
        if not result1 and not result2:
            return True
        if result1 and result2:
            print("TO DO: The two packages have constraints on each other!")
            return True
        pkg_name = pkg_name1 if result1 else pkg_name2
        pkg_version = pkg_version1 if pkg_name1 == pkg_name else pkg_version2
        compatible_pkg = pkg_name2 if pkg_name == pkg_name1 else pkg_name1
        compatible_version = pkg_version1 if compatible_pkg == pkg_name1 else pkg_version2
        result = result1 if result1 else result2
        for item in result:
            pkg_ver_range = item["pkg_version_range"]
            com_pkg_ver_range = item['compatible_pkg_version_range']
            state1 = CompatiblePkg.is_version_meet_constrict(pkg_version, pkg_ver_range)
            state2 = CompatiblePkg.is_version_meet_constrict(compatible_version, com_pkg_ver_range)
            if state1 and state2: return True
        return False

    @staticmethod
    def is_version_meet_constrict(version, constrict):
        if Version(version) in SpecifierSet("".join(constrict)):
            return True
        else:
            return False

    @staticmethod
    def filter(pkg_name=None, compatible_pkg=None, columns: list = None):
        sel_columns = ",".join(columns) if columns else "*"
        sql = "select " + sel_columns + " from compatible_package"
        filter_state = False
        if pkg_name:
            sql += " where pkg_name = '%s'" % pkg_name
            filter_state = True

        if compatible_pkg and filter_state:
            sql += " and compatible_pkg = '%s'" % compatible_pkg

        if compatible_pkg and not filter_state:
            sql += " where application = '%s'" % compatible_pkg

        database = DatabasePool()
        return database.fetchall(sql)


if __name__ == "__main__":
    CompatiblePkg.is_package_compatible("tensorflow", "2.6.1", "keras", "2.4.1")
