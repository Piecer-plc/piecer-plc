from model.database_pool import DatabasePool
import datetime


class RunPipelineState:
    def __init__(self, pipeline_id=None, run_state=None, compete_name=None, finish_time=None, computer_num=None,
                 concerned_stages=None, experiment_No=None):
        self.pipeline_id = pipeline_id
        self.run_state = run_state
        self.compete_name = compete_name
        self.finish_time = finish_time
        self.computer_num = computer_num
        self.concerned_stages = concerned_stages
        self.experiment_No = experiment_No

    @staticmethod
    def insert_start_record(pipeline_id, compete_name, concerned_stages_str, experiment_No, computer_num):
        sql = "insert into run_pipeline_state (pipeline_id, compete_name, concerned_stages, experiment_No, computer_num) values (%d, '%s', '%s', '%s', %d)"
        sql = sql % (pipeline_id, compete_name, concerned_stages_str, experiment_No, computer_num)
        database = DatabasePool()
        database.insert(sql)

    @staticmethod
    def is_exist(pipeline_id, concerned_stages, experiment_No):
        sql = "select distinct pipeline_id from run_pipeline_state where pipeline_id=%d and concerned_stages='%s'" \
              " and experiment_No='%s' and run_state is not null"
        sql = sql % (pipeline_id, concerned_stages, experiment_No)
        database = DatabasePool()
        result = database.fetchall(sql)
        if result:
            return True
        else:
            return False

    @staticmethod
    def update_run_pipeline_state(pipeline_id, state, compete_name, concerned_stages):
        curr_time = datetime.datetime.now()
        time_str = datetime.datetime.strftime(curr_time, '%Y-%m-%d %H:%M:%S')
        sql = "update run_pipeline_state set run_state ='%s',finish_time = '%s' where pipeline_id = %d and compete_name = '%s' and concerned_stages='%s' " % (
            str(state), time_str, pipeline_id, compete_name, concerned_stages)
        database = DatabasePool()
        database.update(sql)

    @staticmethod
    def filter(pipeline_id=None, run_state=None, compete_name=None, computer_num=None, concerned_stages=None,
               experiment_No=None, columns: list = None, distinct: bool = False):
        select = "select distinct " if distinct else "select "
        select_columns = "*" if not columns else ','.join(columns)
        sql = select + select_columns + " from run_pipeline_state"
        filter_state = False

        if pipeline_id:
            sql += " where pipeline_id = %d" % pipeline_id
            filter_state = True

        if run_state and filter_state:
            sql += " and run_state = '%s" % run_state

        if run_state and not filter_state:
            sql += " where run_state= '%s'" % run_state
            filter_state = True

        if compete_name and filter_state:
            sql += " and compete_name = '%s'" % compete_name

        if compete_name and not filter_state:
            sql += " where compete_name = '%s'" % compete_name
            filter_state = True

        if computer_num and filter_state:
            sql += " and computer_num = %d" % computer_num

        if computer_num and not filter_state:
            sql += " where computer_num = %d" % computer_num

        if concerned_stages and filter_state:
            sql += " and concerned_stages = '%s'" % concerned_stages

        if concerned_stages and not filter_state:
            sql += " where concerned_stages = '%s'" % concerned_stages

        if experiment_No and filter_state:
            sql += " and experiment_No = '%s'" % experiment_No

        if experiment_No and not filter_state:
            sql += " where experiment_No = '%s'" % experiment_No
        database = DatabasePool()
        return database.fetchall(sql)
