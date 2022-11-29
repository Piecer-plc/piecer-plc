from model.database_pool import DatabasePool


class ValidRecord:
    def __init__(self, pipeline_id, valid_No, kn_id, computer_num=None, valid_result=None):
        self.pipeline_id = pipeline_id
        self.valid_No = valid_No
        self.kn_id = kn_id
        self.computer_num = computer_num
        self.valid_result = valid_result

    @staticmethod
    def insert(pipeline_id, valid_no, kn_id, computer_num=None,valid_result=None):
        elements = ["pipeline_id", "valid_No", "kn_id"]
        value_sign = ["%d", '%d', "%d"]
        if computer_num:
            elements.append("computer_num")
            value_sign.append("%d")
        if valid_result:
            elements.append("valid_result")
            value_sign.append("'%s'")

        sql = "insert into valid_record(" + ','.join(elements) +") VALUES (" + ",".join(value_sign) +")"

        if len(value_sign) == 3:
            sql = sql % (pipeline_id, valid_no,  kn_id)
        elif len(value_sign) == 5:
            sql = sql % (pipeline_id,valid_no,kn_id,computer_num,valid_result)
        elif computer_num:
            sql = sql % (pipeline_id, valid_no,  kn_id,computer_num)
        else:
            sql = sql % (pipeline_id, valid_no, kn_id,valid_result)
        database = DatabasePool()
        database.insert(sql)

    @staticmethod
    def filter(pipeline_id=None,valid_No=None,kn_id=None,valid_result=None,columns: list = None, distinct=False):
        select = "select distinct " if distinct else "select "
        select_columns = "*" if not columns else ','.join(columns)
        sql = select + select_columns + " from valid_record"
        filter_state = False
        if pipeline_id:
            sql += " where pipeline_id = %d" % pipeline_id
            filter_state = True

        if valid_No is not None and filter_state:
            sql += " and valid_No = %d" % valid_No
        if valid_No is not None and not filter_state:
            sql += " where valid_No = %d" % valid_No
            filter_state = True

        if kn_id and filter_state:
            sql += " and kn_id = %d" % kn_id
        if kn_id and not filter_state:
            sql += " where kn_id = %d" % kn_id
            filter_state = True

        if valid_result and filter_state:
            sql += " and valid_result = '%s'" % valid_result
        if valid_result and not filter_state:
            sql += " where valid_result = '%s'" % valid_result

        database = DatabasePool()
        return database.fetchall(sql)


if __name__ == "__main__":
    # 36:  36174,36188,36265

    # 38:  33224,33259,33303,33341,31753,31751,31770,37359,37400

    # 13:  32292,32347,32532,33147,33185,33288,37298,37356

    #  8:  33468,33603,11119,11169,36734,37107,37125

    # 40:  33744,33805,33959,36728,36157,36198,36253,36722

    #  7:  33193,33217,33307,33335,33346,37244

    # 29 : 35699,36829

    # 39 : 33302,34245,34249,34299,34300

    # 41 : 33329,37079

    # 31 : 33853,33939,33956,36306

    #  5 : 33789,33948,37112

    # 15 : 33981

    # 30 : 32490

    # 12 : 32564,32574

    # 38 : 33342,34177,34226,36487

    # 16:  37056,33514

    # 52: 31799,32053,32056,32401,32434,32560,32607

    # 12 : 37403,34215,34207,34197,34186,34185,34159,34154,34150

    # 43,35: 34658,34723,

    # 4,43:31920,31975,37246,37261,37321,37410,37426
    # 31950,32253,37258,37335,36502,36488,36486,36676

    # 37646,37360,37489,37514,37517,37521,37543,37544,37548,37551,37552,37559,37599,37284,37343,37764,37768,37776,37742,
    # 37059,36877,37264,37251,37100,36893,36886,36859,36848,




    for pipeline_id in [34116,34048,33913,33910,33883,33868,33850,33812,33796,33790,33776,33771,33770,33754,33742,33729,32928,32923,32613,32566,32552,32551,32547,32522,32518,33915,33906,33901,33896,33878,33857,33811,33775,33735,33724,33946,32511,32475,32429,32392,32377,32372,32371,32343,31941,31927,31807
                        ]:
        # pipeline_id = 37800
        valid_No = 1
        kn_id = 246
        ValidRecord.insert(pipeline_id, valid_No, kn_id)
        print(str(pipeline_id) + "  " + str(valid_No) + "  " + str(kn_id))
