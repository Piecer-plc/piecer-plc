from model.database_pool import DatabasePool


class Compete:
    def __init__(self, compete_id=None, compete_name=None, total_teams=None, total_competitors=None, create_date=None,
                 evaluate_algorithm=None, evaluate_description=None, evaluate_id=None, evaluate_is_max=None,
                 data_types=None, category_technique=None, category_others=None, compete_url=None,
                 dataset_size_str=None, pipeline_num=None):
        self.compete_id = compete_id
        self.compete_name = compete_name
        self.total_teams = total_teams
        self.total_competitors = total_competitors
        self.create_date = create_date
        self.evaluate_algorithm = evaluate_algorithm
        self.evaluate_description = evaluate_description
        self.evaluate_id = evaluate_id
        self.evaluate_is_max = evaluate_is_max
        self.data_types = data_types
        self.category_technique = category_technique
        self.category_others = category_others
        self.compete_url = compete_url
        self.dataset_size_str = dataset_size_str
        self.pipeline_num = pipeline_num

    def insert_into_compete(self):
        sql = "insert into compete(compete_id, compete_name, total_teams, total_competitors, create_date, " \
              "evaluate_algorithm, evaluate_description, evaluate_id, evaluate_is_max, data_types," \
              " category_technique, category_others, compete_url) values " \
              "(%d,'%s',%d,%d,'%s','%s','%s',%d,'%s','%s','%s','%s','%s')"
        sql = sql % (self.compete_id, self.compete_name, self.total_teams, self.total_competitors, self.create_date,
                     self.evaluate_algorithm, self.evaluate_description, self.evaluate_id, self.evaluate_is_max,
                     self.data_types, self.category_technique, self.category_others, self.compete_url)
        database = DatabasePool()
        database.insert(sql)
        print("insert ", self.compete_url)

    def update_pipeline_num(self):
        sql = "update compete set pipeline_num=%d where compete_name='%s'" % (self.pipeline_num, self.compete_name)
        database = DatabasePool()
        database.update(sql)

    @staticmethod
    def get_compete_info_by_min_create_date(min_create_data):
        sql = "select * from compete where create_date >='%s' and RQ1=1" % min_create_data
        database = DatabasePool()
        result = database.fetchall(sql)
        return result

    @staticmethod
    def get_compete_info_compete_name(compete_name):
        sql = "select * from compete where compete_name='%s'" % compete_name
        database = DatabasePool()
        result = database.fetchall(sql)
        return result

    @staticmethod
    def get_compete_info_by_valid(is_valid):
        sql = "select * from compete where is_valid=%d" % is_valid
        database = DatabasePool()
        result = database.fetchall(sql)
        return result

    @staticmethod
    def get_compete_rank_score(compete_name):
        sql = "select evaluate_algorithm from compete_evaluate_algorithm where compete_name='%s'" % compete_name
        database = DatabasePool()
        result = database.fetchone(sql)
        if result:
            return result["evaluate_algorithm"]
        return None

    @staticmethod
    def filter(compete_name=None, evaluate_algorithm=None, target_columns=None, columns:list=None, sel_one=False, distinct=False):
        select = "select distinct " if distinct else "select "
        if columns is not None:
            columns_str = ",".join(columns)
        else:
            columns_str = "*"
        filter_num = 0
        sql = select + columns_str + " from compete_evaluate_algorithm"
        if compete_name is not None:
            if filter_num == 0:sql += " where "
            sql += "compete_name = '%s'" % compete_name
            filter_num += 1
        if evaluate_algorithm is not None:
            if filter_num == 0: sql += " where "
            if filter_num > 0: sql += " and "
            sql += "evaluate_algorithm = '%s'" % evaluate_algorithm
            filter_num += 1
        if target_columns is not None:
            if filter_num == 0: sql += " where "
            if filter_num > 0: sql += " and "
            sql += "target_columns = '%s'" % target_columns
            filter_num += 1
        database = DatabasePool()
        if sel_one:
            return database.fetchone(sql)
        else:
            return database.fetchall(sql)