from run_experiment import run_experiments
from model.pipeline import Pipeline
from run_experiment import deal_run_file
import os
from model.venv_install_info import VenvInstallInfo
from utils import files_utils

if __name__ == "__main__":
    concerned_stages = ["FE"]
    concerned_stages.sort()
    concerned_stages_str = ','.join(concerned_stages)
    os.chdir("../")
    pipelines = Pipeline.filter(RQ2=1,is_gpu="True",columns=['pipeline_id', 'compete_name'], pipeline_type="machine-learning")
    new_pipelines = []
    for pipeline in pipelines:
        if pipeline['compete_name'] in files_utils.get_file_content(r"E:\software2.0\RQ2_compete_input\invalid_compete.txt"):
            continue
        if not os.path.exists("E:\\software2.0\\RQ2_compete_input\\" + pipeline['compete_name']):
            continue
        max_num = VenvInstallInfo.get_venv_max_num(pipeline['pipeline_id'], concerned_stages_str, '1-1')
        if max_num <3 or max_num > 300:
            continue
        new_pipelines.append(pipeline)
    deal_run_file.batch_create_run_py_file(new_pipelines[100:200],concerned_stages, "1-1")
    run_experiments.batch_run(concerned_stages, "win_amd64", "1-1", new_pipelines[100:200], 62)