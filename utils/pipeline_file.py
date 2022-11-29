import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
from model.pipeline import Pipeline
from utils import venv_utils


def open_pipeline_file_linux(pipeline_id, root_path, file_type="origin"):
    file_path = None
    if file_type == "origin":
        file_path = Pipeline.get_pipeline_py_file_save_path(pipeline_id, root_path)
    if file_type == "clean":
        file_path = Pipeline.get_pipeline_save_path(pipeline_id, root_path)
        file_path = os.path.join(file_path, "clean_file.py")
    if file_type == "run":
        "run_files_experiment"
        project_path = Pipeline.get_pipeline_save_path(pipeline_id, root_path)
        for folder in os.listdir(project_path):
            if "run_files_experiment" in folder:
                file_path = os.path.join(project_path, folder, "pipeline_run1.py")
                break
    if file_path is None or not os.path.exists(file_path):
        print("FileNotFindError")
        return
    cmd = 'notepadqq --allow-root "%s"' % file_path
    venv_utils.external_cmd(cmd)


if __name__ == '__main__':
    import sys
    pipeline_id = sys.argv[1]
    type = sys.argv[2]
    print(type)
    if not type:
        type = "origin"
    root_path = r"/media/root/463f6ed8-032d-42e1-9e7c-d4abfc295fdb1/RQ2_compete"
    # move_machine_learning_file(root_path, 'D:/new_kaggle_compete')
    open_pipeline_file_linux(int(pipeline_id), root_path, file_type=type)