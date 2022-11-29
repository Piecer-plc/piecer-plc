from model.pipeline_dependency import PipelineDeps
from utils import extrct_api_utils


# 分析pipeline的直接依赖，通过语法树
def analysis_pipeline_direct_dependencies(pipeline_file_path, pipeline_id):
        dependencies = extrct_api_utils.get_all_import_packages_name(pipeline_file_path)
        pipeline_dependency = PipelineDeps(pipeline_id, dependencies)
        pipeline_dependency.insert_into_pipeline_dependencies()


if __name__ == "__main__":
    # python文件的路径
    file_path = ""
    # 项目的编号
    pipeline_id = ""
    analysis_pipeline_direct_dependencies(file_path,pipeline_id)
