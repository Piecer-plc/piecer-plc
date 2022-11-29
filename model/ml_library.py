from model import database_pool


class MlLibrary:
    def __init__(self, package_name=None, category=None):
        self.package_name = package_name
        self.category = category

    def get_package_category(self):
        package_name = self.package_name.lower()
        sql = "select category from ml_libraries where package_name = '%s'" % package_name
        database = database_pool.DatabasePool()
        result = database.fetchone(sql)
        if result:
            return result['category']
        else:
            return None
