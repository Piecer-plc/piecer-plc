from model.database_pool import DatabasePool
from pymysql.converters import escape_string
import os


class Pipeline:
    def __init__(self, pipeline_id=None, project_name=None, compete_name=None, author=None, project_url=None,
                 output_file_urls=None, script_version_id=None, last_time=None, score=None, code_download_url=None,
                 runtime=None, is_gpu_enable=None, pipeline_type=None, table=None, RQ1=None,RQ2=None):
        self.pipeline_id = pipeline_id
        self.project_name = project_name
        self.compete_name = compete_name
        self.author = author
        self.project_url = project_url
        self.output_file_urls = output_file_urls
        self.script_version_id = script_version_id
        self.last_time = last_time
        self.score = score
        self.code_download_url = code_download_url
        self.runtime = runtime
        self.is_gpu_enable = is_gpu_enable
        self.pipeline_type = pipeline_type
        self.table = table
        self.RQ1 = RQ1
        self.RQ2 = RQ2

    def is_exist_in_pipelines(self):
        sql = "SELECT * FROM pipeline WHERE project_name = '%s' and script_version_id='%s' limit 1" % (
            self.project_name, self.script_version_id)
        database = DatabasePool()
        nums = database.fetchone(sql)
        if nums is not None:
            return True
        else:
            return False

    def update_pipeline_type(self):
        sql = "update pipeline set pipeline_type = '%s' where pipeline_id=%d" % (self.pipeline_type, self.pipeline_id)
        database = DatabasePool()
        database.update(sql)

    def update_runtime_in_pipelines(self):
        sql = "update pipeline set runtime=%d where project_name='%s' and script_version_id='%s'" % (
            self.runtime, self.project_name, self.script_version_id)
        database = DatabasePool()
        database.update(sql)

    def update_is_gpu_enable_in_pipelines(self):
        sql = "update pipeline set is_gpu_enable='%s'  where project_name='%s' and script_version_id='%s'" % (
            self.is_gpu_enable, self.project_name, self.script_version_id)
        database = DatabasePool()
        database.update(sql)

    def update_score_in_pipelines(self):
        sql = "update pipeline set score='%s' where project_name='%s' and script_version_id='%s'" % (
            self.score, self.project_name, self.script_version_id)
        database = DatabasePool()
        database.update(sql)

    def insert_into_pipelines(self):
        # if self.is_exist_in_pipelines():
        #     print("pipeline have exist")
        #     return
        urls = ''
        for url in self.output_file_urls:
            urls += url + ';'
        # sql = "insert into pipeline (pipeline_id,project_name, compete_name, project_url, output_file_urls, last_time, " \
        #       "script_version_id,score, runtime, is_gpu_enable, author, code_download_url) values ('%s', %d, '%s', '%s', " \
        #       "'%s', '%s', '%s', '%s', %d, '%s', '%s', '%s')" % (int(self.pipeline_id),
        #           self.project_name, self.compete_name, self.project_url, urls, self.last_time, self.script_version_id,
        #           self.score, int(self.runtime),
        #           self.is_gpu_enable,
        #           self.author, self.code_download_url)
        sql = "insert into %s (pipeline_id, project_name, compete_name, author, project_url, output_file_urls, script_version_id, last_time, score, code_download_url, runtime, is_gpu_enable, RQ1, RQ2, pipeline_type) VALUES (%d,'%s','%s','%s','%s','%s','%s','%s','%s','%s',%d,'%s',%d,%d,'%s')" %(self.table,int(self.pipeline_id), self.project_name,self.compete_name,self.author,escape_string(self.project_url),escape_string(self.output_file_urls),self.script_version_id,self.last_time,self.score,self.code_download_url,int(self.runtime),self.is_gpu_enable,int(self.RQ1),int(self.RQ2),self.pipeline_type)
        database = DatabasePool()
        database.insert(sql)

    # 获取pipeline 表中的pipeline_id
    def get_pipeline_id(self):
        sql = "select pipeline_id from pipeline where project_name = '%s' and script_version_id = '%s'" % (
            self.project_name, self.script_version_id)
        database = DatabasePool()
        result = database.fetchone(sql)
        if result:
            return result['pipeline_id']
        else:
            print('get pipeline id None')
            return None

    @staticmethod
    def get_all_pipeline_ids():
        sql = "select distinct pipeline_id from pipeline"
        database = DatabasePool()
        result = database.fetchall(sql)
        return result

    @staticmethod
    def get_rq1_pipelines():
        sql = "select distinct pipeline_id from pipeline where RQ1=1"
        database = DatabasePool()
        result = database.fetchall(sql)
        return result

    @staticmethod
    def get_rq2_pipelines():
        sql = "select distinct pipeline_id from pipeline where RQ2=1"
        database = DatabasePool()
        result = database.fetchall(sql)
        return result

    @staticmethod
    def get_all_able_deploy_compete():
        sql = "select distinct compete_name from pipeline where pipeline_id in (select distinct pipeline_id from dependencies_pool)"
        database = DatabasePool()
        result = database.fetchall(sql)
        return result

    @staticmethod
    def get_all_able_deploy_pipeline(pipeline_type):
        sql = "select distinct pipeline_id from pipeline where pipeline_id in (select distinct pipeline_id from dependencies_pool) and pipeline_type='%s'" % pipeline_type
        database = DatabasePool()
        result = database.fetchall(sql)
        return result

    @staticmethod
    def get_RQ2_pipeline_num_in_compete(able_deploy: bool = False):
        if able_deploy:
            sql = "select compete_name, count(distinct pipeline_id) as num from pipeline where pipeline_id in (select distinct pipeline_id from dependencies_pool) GROUP BY compete_name"
        else:
            sql = "select compete_name, count(distinct pipeline_id) as num from pipeline where RQ2=1 GROUP BY compete_name"

        database = DatabasePool()
        result = database.fetchall(sql)
        return result

    @staticmethod
    # 获取pipeline 存放的路径
    # root path 表示存放的根目录
    def get_pipeline_save_path(pipeline_id, root_path):
        pipeline_info = Pipeline.filter(pipeline_id=pipeline_id, sel_one=True)
        project_name = pipeline_info['project_name']
        compete_name = pipeline_info['compete_name']
        script_version_id = pipeline_info['script_version_id']
        if script_version_id is None:
            folder_name = project_name
        else:
            folder_name = project_name + '#id#' + str(script_version_id)
        path = os.path.join(root_path, compete_name, folder_name)
        return path.replace('\\', '/')

    @staticmethod
    def update_private_dataset(pipeline_id, private_dataset):
        sql = "update pipeline set private_dataset='%s' where pipeline_id=%d" % (private_dataset, pipeline_id)
        database = DatabasePool()
        database.update(sql)

    @staticmethod
    def update_dataset_urls(pipeline_id, private_dataset):
        sql = "update pipeline set dataset_urls='%s' where pipeline_id=%d" % (private_dataset, pipeline_id)
        database = DatabasePool()
        database.update(sql)

    @staticmethod
    def update_extra_dataset(pipeline_id, extra_dataset):
        sql = "update pipeline set extra_dataset='%s' where pipeline_id = %d" % (extra_dataset,pipeline_id)
        database = DatabasePool()
        database.update(sql)

    @staticmethod
    # 获取pipeline 存放的路径
    # root path 表示存放的根目录
    def get_pipeline_py_file_save_path(pipeline_id, root_path):
        pipeline_info = Pipeline.filter(pipeline_id=pipeline_id, sel_one=True)
        project_name = pipeline_info['project_name']
        compete_name = pipeline_info['compete_name']
        script_version_id = pipeline_info['script_version_id']
        if script_version_id is None:
            folder_name = project_name
        else:
            folder_name = project_name + '#id#' + str(script_version_id)
        path = os.path.join(root_path, compete_name, folder_name)
        path = os.path.join(path, project_name + ".py")
        return path.replace('\\', '/')

    @staticmethod
    def get_pipeline_compete_name(pipeline_id):
        compete_name = Pipeline.filter(pipeline_id,columns=['compete_name'],sel_one=True)
        compete_name = compete_name['compete_name']
        return compete_name

    @staticmethod
    def filter(pipeline_id=None, compete_name=None, RQ1=None, RQ2=None, pipeline_type=None, is_gpu=None,
               columns: list = None, distinct: bool = False, sel_one=False, order_by=None):
        select = "select distinct " if distinct else "select "
        select_columns = "*" if not columns else ','.join(columns)
        sql = select + select_columns + " from pipeline"
        filter_state = False
        if pipeline_id:
            sql += " where pipeline_id = %d" % pipeline_id
            filter_state = True

        if compete_name and filter_state:
            sql += " and compete_name = '%s'" % compete_name

        if compete_name and not filter_state:
            sql += " where compete_name = '%s'" % compete_name
            filter_state = True

        if RQ1 is not None and filter_state:
            sql += " and RQ1 = %d" % RQ1

        if RQ1 is not None and not filter_state:
            sql += " where RQ1 = %d" % RQ1
            filter_state = True

        if RQ2 is not None and filter_state:
            sql += " and RQ2 = %d" % RQ2

        if RQ2 is not None and not filter_state:
            sql += " where RQ2 = %d" % RQ2
            filter_state = True

        if is_gpu is not None and filter_state:
            sql += " and is_gpu_enable = '%s'" % is_gpu

        if is_gpu is not None and not filter_state:
            sql += " where is_gpu_enable = '%s'" % is_gpu
            filter_state = True

        if pipeline_type and filter_state:
            sql += " and pipeline_type = '%s'" % pipeline_type

        if pipeline_type and not filter_state:
            sql += " where pipeline_type = '%s'" % pipeline_type

        if order_by is not None:
            sql += " order by " + order_by
        database = DatabasePool()
        if sel_one:
            return database.fetchone(sql)
        return database.fetchall(sql)

    @staticmethod
    def insert_github_pipeline(github_url, repo_name):
        sql = "insert into pipeline (project_name,compete_name,project_url) values ('%s','%s','%s')" % (repo_name, "GitHub", github_url)
        database = DatabasePool()
        database.insert(sql)


if __name__ == "__main__":
    Pipeline.insert_github_pipeline("https://github.com/dgovor/Housing-Price-Prediction-Python","Housing-Price-Prediction-Python")
    # sql = "select * from project_info"
    # database = database_pool.DatabasePool()
    # result = database.fetchall(sql)
    # for item in result:
    #     pipeline_id = item['pipeline_id']
    #     pipeline_type = item['project_type']
    #     Pipeline(pipeline_id=pipeline_id, pipeline_type=pipeline_type).update_pipeline_type()
    print('hh')
