from model.database_pool import DatabasePool
from model.api_label import ApiLabel


class PipelineApi:
    def __init__(self, pipeline_id=None, api=None, lib=None):
        self.pipeline_id = pipeline_id
        self.api = api
        self.lib = lib

    def get_pipeline_apis(self):
        sql = "select api,lib from pipeline_api where pipeline_id=%d" % self.pipeline_id
        database = DatabasePool()
        result = database.fetchall(sql)
        return result

    # 获取pipeline在指定的阶段所使用的包
    def get_pipeline_ml_stage_dependencies(self, stage):
        result = self.get_pipeline_apis()
        packages = []
        for item in result:
            label = ApiLabel(api=item['api']).get_api_stage_label()
            if label == stage and item['lib'] not in packages:
                packages.append(item['lib'])
        return packages

    @staticmethod
    def update_pipeline_api_lib(old_lib, new_lib):
        sql = "update pipeline_api set lib = '%s' where lib='%s'" % (new_lib, old_lib)
        database = DatabasePool()
        database.update(sql)

    @staticmethod
    def is_exist(pipeline_id, api):
        sql = "select pipeline_id from pipeline_api where pipeline_id = %d and api='%s' limit 1" % (pipeline_id, api)
        database = DatabasePool()
        result = database.fetchone(sql)
        if result:
            return True
        else:
            return False

    @staticmethod
    def insert(pipeline_id, api, lib):
        sql = "insert into pipeline_api(pipeline_id, api, lib) values(%d, '%s', '%s')" % (pipeline_id, api, lib)
        database = DatabasePool()
        database.insert(sql)
        print("insert api  %d,  %s,  %s" % (pipeline_id, api, lib))

    @staticmethod
    def filter(pipeline_id=None, api=None, lib=None, columns: list = None):
        select_columns = "*" if not columns else ','.join(columns)
        sql = "select " + select_columns + " from pipeline_api"
        filter_state = False
        if api:
            sql += " where api = '%s'" % api
            filter_state = True

        if lib and filter_state:
            sql += " and lib = '%s'" % lib

        if lib and not filter_state:
            sql += " where lib = '%s'" % lib
            filter_state = True

        if pipeline_id and filter_state:
            sql += " and pipeline_id = %d" % pipeline_id

        if pipeline_id and not filter_state:
            sql += " where pipeline_id = %d" % pipeline_id

        database = DatabasePool()
        return database.fetchall(sql)

    @staticmethod
    def is_use_apis(pipeline_id, api_list):
        apis = PipelineApi.filter(pipeline_id)
        apis = [item['api']for item in apis]
        if set(apis) & set(api_list):
            return True
        else:
            return False

if __name__ == "__main__":
    result = []
    api_list = ["sklearn.decomposition.PCA", "sklearn.preprocessing.MinMaxScaler"]
    from model.database_pool import DatabasePool
    sql = "select distinct pipeline_id from pipeline where compete_name in (select distinct compete_name from compete where compete_name in ('Tabular Playground Series - Aug 2021','Tabular Playground Series - Sep 2021','Tabular Playground Series - Oct 2021','Tabular Playground Series - Nov 2021','Tabular Playground Series - Dec 2021'))"
    database = DatabasePool()
    pipelines = database.fetchall(sql)
    for pipe in pipelines:
        pipeline_id = pipe['pipeline_id']
        if PipelineApi.is_use_apis(pipeline_id, api_list):
            result.append(pipeline_id)
    print(result)



