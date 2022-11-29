import statistics
from model.database_pool import DatabasePool


class PipelineDeps:
    def __init__(self, pipeline_id=None, pipeline_deps_list: list = None):
        self.pipeline_id = pipeline_id
        self.pipeline_deps = pipeline_deps_list

    def insert_into_pipeline_dependencies(self):
        for dependency in self.pipeline_deps:
            sql = "INSERT INTO pipeline_dependencies (pipeline_dep,  pipeline_id) VALUES ('%s', '%s')" % (
                dependency, self.pipeline_id)
            database = DatabasePool()
            if not self.is_exit_in_project_dependency(dependency):
                database.insert(sql)
                print('pipeline_id : ' + str(self.pipeline_id) + '  project_dependency : ' + dependency + '  INSERT')
            else:
                print('pipeline_id : ' + str(self.pipeline_id) + '  project_dependency : ' + dependency + '  EXIST')

    # 查找当前库是否存在于表package_info中，不存在则无法检查
    def is_exit_in_project_dependency(self, project_dependency):
        sql = "SELECT * FROM pipeline_dependencies WHERE pipeline_dep = '%s' and pipeline_id = '%s' limit 1" % (
            project_dependency, self.pipeline_id)
        database = DatabasePool()
        nums = database.fetchone(sql)
        if nums is not None:
            return True
        else:
            return False

    # 获取项目的依赖
    def get_pipeline_deps(self) -> list:
        sql = "select pipeline_dep from pipeline_dependencies where pipeline_id = '%s'" % self.pipeline_id
        database = DatabasePool()
        results = database.fetchall(sql)
        dependencies = []
        for result in results:
            dependencies.append(result['pipeline_dep'])
        return dependencies

    @staticmethod
    def delete_pipeline_dep(pipeline_id, dep):
        sql = "delete from pipeline_dependencies where pipeline_id=%d and pipeline_dep = '%s'" %(pipeline_id, dep)
        database = DatabasePool()
        database.update(sql)

    @staticmethod
    def update_pipeline_dep(pipeline_id, old_dep, new_dep):
        sql = "update pipeline_dependencies set pipeline_dep='%s' where pipeline_id=%d and pipeline_dep = '%s'"
        sql = sql % (new_dep, pipeline_id, old_dep)
        database = DatabasePool()
        database.update(sql)

    @staticmethod
    def get_pipeline_ids_by_dep(dependency):
        sql = "select distinct pipeline_id from pipeline_dependencies where pipeline_dep='%s' " % dependency
        database = DatabasePool()
        result = database.fetchall(sql)
        return result

    @staticmethod
    def filter(pipeline_id=None, pipeline_dep=None, is_extra=None, related_extra_dep=None, columns: list = None,
               distinct=False):
        select = "select distinct " if distinct else "select "
        select_columns = "*" if not columns else ','.join(columns)
        sql = select + select_columns + " from pipeline_dependencies"
        filter_state = False
        if pipeline_id:
            sql += " where pipeline_id = %d" % pipeline_id
            filter_state = True

        if pipeline_dep and filter_state:
            sql += " and pipeline_dep = '%s'" % pipeline_dep
        if pipeline_dep and not filter_state:
            sql += " where pipeline_dep = '%s'" % pipeline_dep
            filter_state = True

        if pipeline_dep and filter_state:
            sql += " and pipeline_dep = '%s'" % pipeline_dep
        if pipeline_dep and not filter_state:
            sql += " where pipeline_dep = '%s'" % pipeline_dep
            filter_state = True

        if is_extra is not None and filter_state:
            sql += " and is_extra = %d" % is_extra
        if is_extra is not None and not filter_state:
            sql += " where is_extra = %d" % is_extra
            filter_state = True

        if related_extra_dep and filter_state:
            sql += " and related_extra_dep = '%s'" % related_extra_dep
        if related_extra_dep and not filter_state:
            sql += " where related_extra_dep = '%s'" % related_extra_dep

        database = DatabasePool()
        return database.fetchall(sql)

    @staticmethod
    def insert(pipeline_id: int, pipeline_dep: str, is_extra: int = None, related_extra_dep: str = None):
        sql = "INSERT INTO pipeline_dependencies "
        insert_columns = ["pipeline_id", "pipeline_dep"]
        replace = ['%d', '\'%s\'']
        grant = [pipeline_id, pipeline_dep]
        if is_extra is not None:
            insert_columns.append("is_extra")
            replace.append('%d')
            grant.append(is_extra)
        if related_extra_dep is not None:
            insert_columns.append("related_extra_dep")
            replace.append('\'%s\'')
            grant.append(related_extra_dep)
        sql += "(" + ','.join(insert_columns) + ") VALUES"
        sql += "(" + ','.join(replace) + ")"
        sql = sql % tuple(grant)
        database = DatabasePool()
        database.insert(sql)
