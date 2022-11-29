class PipelineInstallDeps:
    """
       pipeline 运行时的直接依赖的详细信息
       pipeline_dependency 中只是pipeline的直接依赖的包名
    """

    def __init__(self, pipeline_id=None, venv_num=None, python_version="3.7.10", fixed_packages=None,
                 non_fixed_packages=None, non_ml_packages=None):
        self.pipeline_id = pipeline_id
        self.venv_num = venv_num
        self.python_version = python_version
        self.fixed_packages = fixed_packages
        self.non_fixed_package = non_fixed_packages
        self.non_ml_packages = non_ml_packages


