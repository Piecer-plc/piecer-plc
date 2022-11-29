import pandas as pd
import os
import shutil
import re
import random


def __get_test_site_id_from_txt(txt_path):
    with open(txt_path, "r", encoding='UTF-8') as f:
        content = f.read()
    site_id_format = "SiteID:(.*)\t"
    result = re.findall(site_id_format, content)[0]
    return result


def __get_targets_info_from_txt(txt_path):
    with open(txt_path, "r", encoding='UTF-8') as f:
        content = f.read()
    site_id_format = "\n(.*?)\tTYPE_WAYPOINT\t(.*?)\t(.*?)\n"
    result = re.findall(site_id_format, content)
    return result


def __random_choice_test_txt(old_folder):
    old_test_files = os.listdir(os.path.join(old_folder, "test"))
    old_test_sites = []
    old_test_sites_info = {}

    for item in old_test_files:
        file_path = os.path.join(old_folder, "test", item)
        old_test_site = __get_test_site_id_from_txt(file_path)
        if old_test_site not in old_test_sites:
            old_test_sites.append(old_test_site)
        if old_test_site in old_test_sites_info:
            old_test_sites_info[old_test_site]["num"] += 1
        else:
            old_test_sites_info.update({old_test_site: {"num":1}})

    for old_test_site in old_test_sites:
        site_all_train_files = []
        old_test_site_path = os.path.join(old_folder, 'train', old_test_site)
        for floor in os.listdir(old_test_site_path):
            floor_path = os.path.join(old_test_site_path, floor)
            files = os.listdir(floor_path)
            files = [floor + "-" + file for file in files]
            site_all_train_files.extend(files)
        old_test_sites_info[old_test_site].update({"files": site_all_train_files})
        new_test_choice = random.sample(site_all_train_files, old_test_sites_info[old_test_site]["num"])
        old_test_sites_info[old_test_site].update({"new_test": new_test_choice})

    return old_test_sites_info


def __get_floor_sign(floor):
    if "F" in floor:
        num = int(floor.replace("F", ""))-1
    elif "B" in floor:
        num = -int(floor.replace("B", ""))
    else:
        print("Get floor sign ERROR!")
        return None
    return num


def split_train_test_files(old_folder, save_folder):
    choice_info = __random_choice_test_txt(old_folder)
    sample_submission = []
    target = []
    test_file_path_list = []
    for k, v in choice_info.items():
        for file in v["new_test"]:
            floor = file.split("-")[0]
            floor_sign = __get_floor_sign(floor)
            txt_name = file.split("-")[1]
            path_name = txt_name.replace(".txt", "")
            file_path = os.path.join(old_folder, "train", k, floor, txt_name)
            test_file_path = os.path.join(save_folder, "train", k, floor, txt_name)
            test_file_path_list.append(test_file_path)
            target_items = __get_targets_info_from_txt(file_path)
            for item in target_items:
                timestamp = item[0]
                x = item[1]
                y = item[2]
                site_path_timestamp = "_".join([k, path_name, timestamp])
                sample_submission.append([site_path_timestamp, floor_sign, x, y])
                target.append([x, y])

    shutil.copytree(os.path.join(old_folder, "train"), os.path.join(save_folder, "train"))
    for test_path in test_file_path_list:
        shutil.move(test_path, os.path.join(save_folder, "test"))
    target_df = pd.DataFrame(target, columns=["x", "y"])
    sample_submission_df = pd.DataFrame(sample_submission, columns=['site_path_timestamp', 'floor', 'x', 'y'])
    target_df.to_csv(os.path.join(save_folder, "target.csv"), index=False)
    sample_submission_df.to_csv(os.path.join(save_folder, "sample_submission.csv"), index=False)


if __name__ == "__main__":
    old_folder_p = r"E:\RQ2_compete_input\Indoor Location & Navigation\indoor-location-navigation"
    save_folder_p = r"E:\RQ2_compete_input\Indoor Location & Navigation"
    split_train_test_files(old_folder_p, save_folder_p)