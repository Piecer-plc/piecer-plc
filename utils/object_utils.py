def dict_to_obj(dict_data: dict, obj: object):
    if not isinstance(dict_data, dict):
        print("dict_data type error!")
        return
    obj_key = set(obj.__dict__.keys())
    dict_key = set(dict_data.keys())
    if not obj_key & dict_key:
        print("无效的转换")
        return None
    for key, value in dict_data.items():
        if key in obj.__dict__:
            obj.__dict__.update({key: value})
    return obj
