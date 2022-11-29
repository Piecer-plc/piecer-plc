from model.database_pool import DatabasePool


class ValidInfo:
    def __init__(self, pipeline_id, valid_No, valid_pkg, valid_api):
        self.pipeline_id = pipeline_id
        self.valid_No = valid_No
        self.valid_pkg = valid_pkg
        self.valid_api = valid_api

    @staticmethod
    def insert(pipeline_id, valid_no, valid_pkg, valid_api,computer_num):
        sql = "insert into valid_info(valid_No, pipeline_id, valid_pkg, valid_api,computer_num) VALUES (%d,%d,'%s','%s',%d)"
        sql = sql % (valid_no, pipeline_id, valid_pkg, valid_api,computer_num)
        database = DatabasePool()
        database.insert(sql)

    @staticmethod
    def filter(pipeline_id=None,valid_No=None,valid_pkg=None,valid_api=None,columns: list = None, distinct=False):
        select = "select distinct " if distinct else "select "
        select_columns = "*" if not columns else ','.join(columns)
        sql = select + select_columns + " from valid_info"
        filter_state = False
        if pipeline_id:
            sql += " where pipeline_id = %d" % pipeline_id
            filter_state = True

        if valid_No is not None and filter_state:
            sql += " and valid_No = %d" % valid_No
        if valid_No is not None and not filter_state:
            sql += " where valid_No = %d" % valid_No
            filter_state = True

        if valid_pkg and filter_state:
            sql += " and valid_pkg = '%s'" % valid_pkg
        if valid_pkg and not filter_state:
            sql += " where valid_pkg = '%s'" % valid_pkg
            filter_state = True

        if valid_api and filter_state:
            sql += " and valid_api = '%s'" % valid_api
        if valid_api and not filter_state:
            sql += " where valid_api = '%s'" % valid_api

        database = DatabasePool()
        return database.fetchall(sql)

    @staticmethod
    def get_valid_evaluate_infos(pipeline_id, valid_No):
        sql = "select distinct run_time,memory,gpu_memory,score,venv_num from valid_run_info where pipeline_id = %d and valid_No = %d" % (pipeline_id, valid_No)
        database = DatabasePool()
        res = database.fetchall(sql)
        return res


if __name__ == "__main__":
    # 36623,37049
    pipeline_id = 36623
    valid_no=1
    valid_pkg="catboost"
    valid_api="catboost.CatBoostRegressor"
    computer_num = 171
    print(pipeline_id)
    ValidInfo.insert(pipeline_id,valid_no,valid_pkg,valid_api,computer_num)
