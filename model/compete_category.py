from model.dependency_pool import DatabasePool


class CompeteCategory:
    def __init__(self, compete_name=None, pipeline_num=None, application=None, tasks=None, data_type=None):
        self.compete_name = compete_name
        self.pipeline_num = pipeline_num
        self.application = application
        self.tasks = tasks
        self.data_type = data_type

    @staticmethod
    def get_compete_category(compete_name):
        sql = "select application, tasks, data_type from compete_rq1_classify where compete_name='%s'" % compete_name
        database = DatabasePool()
        result = database.fetchone(sql)
        return result

    @staticmethod
    def filter(compete_name=None, application=None, tasks=None, data_type=None, distinct=False, sel_one=False, columns:list=None):
        select = "select distinct " if distinct else "select "
        select_columns = "*" if not columns else ','.join(columns)
        sql = select + select_columns + " from compete_rq1_classify"
        filter_state = False
        if compete_name:
            sql += " where compete_name = '%s'" % compete_name
            filter_state = True

        if application and filter_state:
            sql += " and application = '%s'" % application

        if application and not filter_state:
            sql += " where application = '%s'" % application
            filter_state = True

        if tasks is not None and filter_state:
            sql += " and tasks = '%s'" % tasks

        if tasks is not None and not filter_state:
            sql += " where tasks = '%s'" % tasks
            filter_state = True

        if data_type and filter_state:
            sql += " and data_type = '%s'" % data_type

        if data_type and not filter_state:
            sql += " where data_type = '%s'" % data_type

        database = DatabasePool()
        if sel_one:
            return database.fetchone(sql)
        return database.fetchall(sql)