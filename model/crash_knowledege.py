from model.database_pool import DatabasePool


class CrashKnowledge:

    def __init__(self,crash_id=None,pkg=None,API=None,crash_detect=None,type=None,version_range=None):
        self.crash_id = crash_id
        self.package = pkg
        self.API = API
        self.crash_detect=crash_detect
        self.type = type
        self.version_range = version_range

    @staticmethod
    def filter(crash_id=None,pkg=None,API=None,type=None,distinct=False,columns: list=None):
        select = "select distinct " if distinct else "select "
        select_columns = "*" if not columns else ','.join(columns)
        sql = select + select_columns + " from crash_knowledge"
        filter_state = False
        if crash_id:
            sql += " where crash_id = %d" % crash_id
            filter_state = True

        if pkg and filter_state:
            sql += " and package = '%s'" % pkg

        if API and not filter_state:
            sql += " where API = '%s'" % API
            filter_state = True

        if type and filter_state:
            sql += " and type = '%s'" % type

        database = DatabasePool()
        return database.fetchall(sql)