from model.database_pool import DatabasePool


class Incompatibility:
    @staticmethod
    def filter(trigger_API=None,trigger_package=None,API=None,package=None,distinct=False,columns:list=None):
        select = "select distinct " if distinct else "select "
        select_columns = "*" if not columns else ','.join(columns)
        sql = select + select_columns + " from distinct_incompatibility_api"
        filter_state = False
        if trigger_API:
            sql += " where trigger_API = '%s'" % trigger_API
            filter_state = True

        if trigger_package and filter_state:
            sql += " and trigger_package = '%s'" % trigger_package

        if API and not filter_state:
            sql += " where API = '%s'" % API
            filter_state = True

        if package and filter_state:
            sql += " and package = '%s'" % package

        database = DatabasePool()
        return database.fetchall(sql)
