from model.database_pool import DatabasePool


class Knowledge:

    def __init__(self,kn_id=None,pkg_name=None,api=None,effect_type=None,context=None,better_vers=None,worse_vers=None):
        self.kn_id = kn_id
        self.pkg_name = pkg_name
        self.api = api
        self.effect_type = effect_type
        self.context = context
        self.better_vers = better_vers
        self.worse_vers = worse_vers

    @staticmethod
    def filter(kn_id=None,pkg_name=None,api=None,effect_type=None,context=None,distinct=False,columns: list=None):
        select = "select distinct " if distinct else "select "
        select_columns = "*" if not columns else ','.join(columns)
        sql = select + select_columns + " from knowledge"
        filter_state = False
        if kn_id:
            sql += " where kn_id = %d" % kn_id
            filter_state = True

        if pkg_name and filter_state:
            sql += " and package_name = '%s'" % pkg_name

        if api and not filter_state:
            sql += " where api = '%s'" % api
            filter_state = True

        if effect_type and filter_state:
            sql += " and effect_type = '%s'" % effect_type

        if context and not filter_state:
            sql += " where context = '%s'" % context

        database = DatabasePool()
        return database.fetchall(sql)