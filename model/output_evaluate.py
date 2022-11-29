import decimal

from model.database_pool import DatabasePool
from model.pipeline import Pipeline
from model.compete import Compete
from model.evaluate_algorithm import EvaluateAlgorithm


EVALUATE_ALGORITHM = {
    "binary_classification" : ['recall','f1_score','accuracy','precision','AUC'],

    "multi_classification": ['precision_micro','precision_macro','recall_macro','recall_micro','f1_score_macro','f1_score_micro'],

    "regression":['RMSE', 'RMSLE', 'r2_score', 'MAPE'],

    "other": ["normalized_gini_coefficient"]
}


class OutputEvaluate:
    def __init__(self, pipeline_id=None, concerned_stages=None, venv_num=None, python_version=None, valid_file=None,
                 experiment_No=None, score=None, evaluate_id=None):
        self.pipeline_id = pipeline_id
        self.concerned_stages = concerned_stages
        self.venv_num = venv_num
        self.python_version = python_version
        self.evaluate_id = evaluate_id
        self.valid_file = valid_file
        self.score = score
        self.experiment_No = experiment_No

    @staticmethod
    def insert(pipeline_id, concerned_stages, venv_num, python_version, valid_file, experiment_No, score,
               evaluate_algorithm, deploy_os, computer_num):
        sql = "insert into output_evaluate(pipeline_id, concerned_stages, venv_num, python_version, valid_file, " \
              "experiment_No, score, evaluate_algorithm, support_os, computer_num) values (%d, '%s', %d, '%s','%s', " \
              "'%s','%s','%s','%s',%d)" % (pipeline_id, concerned_stages, venv_num, python_version, valid_file,
                                           experiment_No, score, evaluate_algorithm, deploy_os, computer_num)

        database = DatabasePool()
        database.insert(sql)

    @staticmethod
    def is_exist(pipeline_id, concerned_stages, venv_num, valid_file, experiment_No, evaluate_algorithm, deploy_os,
                 computer_num):
        sql = "select distinct pipeline_id from output_evaluate where pipeline_id=%d and concerned_stages='%s' " \
              "and venv_num=%d and valid_file='%s' and experiment_No='%s' and evaluate_algorithm='%s' " \
              "and support_os='%s' and computer_num=%d limit 1" % (pipeline_id, concerned_stages, venv_num, valid_file,
                                                           experiment_No, evaluate_algorithm, deploy_os,computer_num)
        database = DatabasePool()
        result = database.fetchone(sql)
        if result:
            return True
        else:
            return False

    @staticmethod
    def filter(pipeline_id=None, concerned_stages=None, venv_num=None, experiment_No=None, evaluate_algorithm=None,
               columns: list = None, distinct: bool = False):
        select = "select distinct " if distinct else "select "
        select_columns = "*" if not columns else ','.join(columns)
        sql = select + select_columns + " from output_evaluate"
        filter_state = False

        if pipeline_id:
            sql += " where pipeline_id = %d" % pipeline_id
            filter_state = True

        if venv_num and filter_state:
            sql += " and venv_num = %d" % venv_num

        if venv_num and not filter_state:
            sql += " where venv_num= %d" % venv_num
            filter_state = True

        if experiment_No and filter_state:
            sql += " and experiment_No = '%s'" % experiment_No

        if experiment_No and not filter_state:
            sql += " where experiment_No = '%s'" % experiment_No
            filter_state = True

        if evaluate_algorithm and filter_state:
            sql += " and evaluate_algorithm = '%s'" % evaluate_algorithm

        if evaluate_algorithm and not filter_state:
            sql += " where evaluate_algorithm = '%s'" % evaluate_algorithm
            filter_state = True

        if concerned_stages and filter_state:
            sql += " and concerned_stages = '%s'" % concerned_stages

        if concerned_stages and not filter_state:
            sql += " where concerned_stages = '%s'" % concerned_stages
        database = DatabasePool()
        return database.fetchall(sql)

    @staticmethod
    def get_output_info_by_compete_name(compete_name):
        sql = "select * from output_evaluate where pipeline_id in (select distinct pipeline_id from pipeline " \
              "where compete_name='%s')" % compete_name
        database = DatabasePool()
        result = database.fetchall(sql)
        return result

    @staticmethod
    def get_evaluated_pipelines_by_compete_name(compete_name):
        sql = "select distinct pipeline_id from output_evaluate where pipeline_id in (select distinct pipeline_id " \
              "from pipeline where compete_name='%s')" % compete_name
        database = DatabasePool()
        result = database.fetchall(sql)
        return result

    @staticmethod
    def get_evaluated_competitions():
        sql = "select distinct compete_name from pipeline where pipeline_id in (select distinct pipeline_id " \
              "from output_evaluate )"
        database = DatabasePool()
        result = database.fetchall(sql)
        return result

    @staticmethod
    def get_best_score_info(pipeline_id, shift_percent=0.1):
        compete_name = Pipeline.filter(pipeline_id,columns=['compete_name'], sel_one=True)['compete_name']
        evaluate_algorithm = Compete.get_compete_rank_score(compete_name)
        if not evaluate_algorithm: return None
        all_infos = OutputEvaluate.filter(pipeline_id, evaluate_algorithm=evaluate_algorithm)
        is_max = EvaluateAlgorithm.score_is_max(evaluate_algorithm)
        if is_max is None:return None
        is_max = True if is_max=="Y" else False
        if not all_infos: return None
        max_score = float('-inf')
        min_score = float('inf')
        min_info = None
        max_info = None
        for item in all_infos:
            score = float(item['score'])
            if score < min_score:
                min_score = score
                min_info = item
            if score > max_score:
                max_score = score
                max_info = item
        best_info = max_info if is_max else min_info
        if min_info and max_info and (max_score-min_score)/min_score < shift_percent:
            return None
        if best_info:
            best_info.update({'compete_name':compete_name})
            return best_info
        return None


if __name__ == "__main__":
    OutputEvaluate.get_best_score_info(10655)
    # all_al = ['RMSE', "RMSLE", "normalized_gini_coefficient", "precision_macro", "precision_micro", "recall_macro", "recall_micro", "f1_score_macro", "f1_score_micro", "accuracy", "AUC", "r2_score", "precision", "f1_score", "recall", "MAPE"]
    # result = OutputEvaluate.filter()
    # for item in result:
    #     p_id = item['pipeline_id']
    #     concerned_stages = item['concerned_stages']
    #     py_version = item['python_version']
    #     valid_file = item['valid_file']
    #     venv_num = item['venv_num']
    #     experiment_No = item['experiment_No']
    #     support_os = "win_amd64"
    #     sql = "select computer_num from run_pipeline_state where pipeline_id=%d and concerned_stages='%s' and experiment_No='%s'" % (p_id,concerned_stages, experiment_No)
    #     da = DatabasePool()
    #     t = da.fetchone(sql)
    #     computer_num = t ['computer_num']
    #     for al in all_al:
    #         if item[al] != "None":
    #             score = item[al]
    #             score = decimal.Decimal(score)
    #             OutputEvaluate.insert(p_id,concerned_stages,venv_num,py_version,valid_file,experiment_No,score,al,support_os,computer_num)

