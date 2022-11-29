from model.database_pool import DatabasePool


class PipelineApiLabel:
    @staticmethod
    def filter(pipeline_id=None,lib =None, api=None, label=None, columns:list=None, distinct=False):
        select = "select distinct " if distinct else "select "
        select_columns = "*" if not columns else ','.join(columns)
        sql = select + select_columns + " from pipeline_api_label"
        filter_state = False
        if pipeline_id:
            sql += " where pipeline_id = %d" % pipeline_id
            filter_state = True

        if lib and filter_state:
            sql += " and lib= '%s'" % lib

        if lib and not filter_state:
            sql += " where lib = '%s'" % lib
            filter_state = True

        if api is not None and filter_state:
            sql += " and api = '%s'" % api

        if api is not None and not filter_state:
            sql += " where api = '%s'" % api
            filter_state = True

        if label and filter_state:
            sql += " and label = '%s'" % label

        if label and not filter_state:
            sql += " where label = '%s'" % label

        database = DatabasePool()
        return database.fetchall(sql)