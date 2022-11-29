import time
import numpy as np
import pandas as pd
from model.compete import Compete
from model.pipeline import Pipeline
from model.evaluate_algorithm import EvaluateAlgorithm
from model.output_evaluate import OutputEvaluate
from model.run_pipeline_state import RunPipelineState
from utils import files_utils
import json
import os
import re


def rename_csv_file_column(column_index, alter_name, csv_path):
    dataset = pd.read_csv(csv_path, header=0, encoding='utf-8', dtype=str)
    headers = dataset.columns.values
    headers[column_index] = alter_name
    dataset.to_csv(csv_path, header=headers, index=False)
    print(headers)


def rename_csv(csv_folder, old_name_sign, new_name_sign):
    for item in os.listdir(csv_folder):
        if old_name_sign in item:
            pattern = old_name_sign + '(.*).csv'
            search = re.search(pattern, item)
            venv_num = search.group(1)
            os.rename(os.path.join(csv_folder, item), os.path.join(csv_folder, new_name_sign +'.csv' + venv_num + '.csv'))


def get_venv_num_from_output_file(file_name):
    pattern = ".csv(.*?).csv"
    try:
        search = re.search(pattern, file_name)
        venv_num = int(search.group(1))
    except Exception as e:
        print(str(e))
        print(file_name)
        venv_num = None
    return venv_num


class Evaluate:
    def __init__(self,  pipeline_id, concerned_stages, experiment_No, deploy_os, deploy_computer_num):
        with open("./run_experiment_config.json") as f:
            content = json.load(f)
        concerned_stages.sort()
        self.deploy_os = deploy_os
        self.deploy_computer = deploy_computer_num
        self.experiment_No = experiment_No
        self.con_stg_str = ",".join(concerned_stages)
        output_folder = "result_output_experiment" + experiment_No.split('-')[-1]+ '-'.join(concerned_stages)
        self.pipeline_id = pipeline_id
        self.output_folder = output_folder
        self.compete_root = content['compete_root']
        self.input_root = content['input_data_root']
        compete_name = Pipeline.filter(pipeline_id,columns=['compete_name'],sel_one=True)['compete_name']
        self.true_file_path = os.path.join(self.input_root, compete_name + '\\' + 'target.csv')
        self.compete_info = Compete.filter(compete_name, sel_one=True)
        self.result_folder = os.path.join(Pipeline.get_pipeline_save_path(pipeline_id, self.compete_root), self.output_folder)
        if self.compete_info:
            self.label_columns = self.compete_info["target_columns"].split(',')
            self.ground_truth = self.get_output(self.true_file_path)
        else:
            self.label_columns = None
            self.ground_truth = None

    def get_output(self, file_path):
        data = pd.read_csv(file_path)
        data = data.loc[:, self.label_columns]
        data = np.array(data)
        return data

    def evaluate_pipeline(self):
        for file in os.listdir(self.result_folder):
            path = os.path.join(self.result_folder, file)
            times = os.path.getctime(path)
            times = time.strftime('%Y%m%d%H%M%S', time.localtime(times))
            if times < "20211228":
                continue
            y_pred = None
            try:
                y_pred = self.get_output(path)
                venv_num = get_venv_num_from_output_file(file)
            except Exception as e:
                venv_num = None
                files_utils.txt_write_into("./evaluate_false.txt", path)
                print(str(e))
            if y_pred is None:
                return
            if  y_pred.shape != self.ground_truth.shape:
                print("Shape don't match")
                files_utils.txt_write_into("./evaluate_false.txt", path + "\n\n")
                continue
            evaluate_algorithm = self.compete_info["evaluate_algorithm"]
            is_exist = OutputEvaluate.is_exist(self.pipeline_id,self.con_stg_str,venv_num,file,self.experiment_No,
                                               evaluate_algorithm,self.deploy_os,self.deploy_computer)
            if is_exist:
                print("have evaluate %d %s %d" % (self.pipeline_id, self.con_stg_str, venv_num))
                continue
            try:
                score = EvaluateAlgorithm.evaluate(self.ground_truth, y_pred, evaluate_algorithm)
            except Exception as e:
                print(str(e))
                files_utils.txt_write_into("./evaluate_false.txt", path + "  ERROR" + str(e) + "\n\n")
                continue
            if score is None:
                print("EvaluateError: get score error")
                return
            OutputEvaluate.insert(self.pipeline_id, self.con_stg_str, venv_num, "3.7.10", file, self.experiment_No,
                                  score, evaluate_algorithm, self.deploy_os, self.deploy_computer)
            print("insert evaluate %d %s %d %s" % (self.pipeline_id, self.con_stg_str, venv_num, score))


def batch_evaluate_experiment(experiment_No, deploy_os, deploy_computer):
    pipeline_ids = RunPipelineState.filter(experiment_No=experiment_No,run_state="True", computer_num=deploy_computer,
                                           columns=['pipeline_id', "concerned_stages"])
    for pipeline in pipeline_ids:
        pipeline_id = pipeline['pipeline_id']
        concerned_stages = pipeline['concerned_stages'].split(',')
        evaluator = Evaluate(pipeline_id, concerned_stages, experiment_No,deploy_os, deploy_computer)
        evaluator.evaluate_pipeline()


if __name__ == '__main__':
    batch_evaluate_experiment("1-1", "win_amd64", 171)




