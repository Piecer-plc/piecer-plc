from model.database_pool import DatabasePool


class ApiLabel:
    def __init__(self, api=None, lib=None, label=None, num=None):
        self.api = api
        self.lib = lib
        self.label = label
        self.num = num

    # 获取api所标记的阶段
    def get_api_stage_label(self):
        sql = "select label from api_label where api='%s'" % self.api
        database = DatabasePool()
        result = database.fetchone(sql)
        if result:
            label = result['label']
            if label == "DCO":
                label = "DC"
            return label
        else:
            return None

    @staticmethod
    def update_api_label_lib( old_lib, new_lib):
        sql = "update api_label set lib = '%s' where lib='%s'" % (new_lib, old_lib)
        database = DatabasePool()
        database.update(sql)

    @staticmethod
    def filter(api=None, lib=None, label=None, num=None, columns: list = None):
        select_columns = "*" if not columns else ','.join(columns)
        sql = "select " + select_columns + " from api_label"
        filter_state = False
        if api:
            sql += " where api = '%s'" % api
            filter_state = True

        if lib and filter_state:
            sql += " and lib = '%s'" % lib

        if lib and not filter_state:
            sql += " where lib = '%s'" % lib
            filter_state = True

        if label and filter_state:
            sql += " and label = '%s'" % label

        if label and not filter_state:
            sql += " where label = '%s'" % label
            filter_state = True

        if num and filter_state:
            sql += " and num = %d" % num

        if num and not filter_state:
            sql += " where num = %d" % num

        database = DatabasePool()
        return database.fetchall(sql)
