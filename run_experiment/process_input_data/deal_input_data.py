# coding=gb2312
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import shutil
import os
import re

true_output_label = {
    'Santander Value Prediction Challenge': 'target',
    'Elo Merchant Category Recommendation': 'target',
    'House Prices - Advanced Regression Techniques': 'SalePrice',
    'Santander Customer Transaction Prediction': 'target',
    'Home Credit Default Risk': 'TARGET',
    'Santander Customer Satisfaction': 'TARGET',
    'Toxic Comment Classification Challenge': ['toxic','severe_toxic','obscene','threat','insult','identity_hate'],
    'Porto Seguro’s Safe Driver Prediction': 'target',
    'Titanic - Machine Learning from Disaster': 'Survived',
    'Quora Insincere Questions Classification': 'prediction',
    'Digit Recognizer': 'Label',
    'University of Liverpool - Ion Switching': 'open_channels',
    'Mercedes-Benz Greener Manufacturing': 'y',
    'Sberbank Russian Housing Market': 'price_doc',
    'CommonLit Readability Prize': 'target',
    "Natural Language Processing with Disaster Tweets": 'target',
    "Tabular Playground Series - Jul 2021": ['target_carbon_monoxide','target_benzene','target_nitrogen_oxides'],
    "Tabular Playground Series - Apr 2021":"Survived",
    "Tabular Playground Series - Feb 2021":"target",
    "Categorical Feature Encoding Challenge II":"target",
    "Categorical Feature Encoding Challenge":"target",
    "Tabular Playground Series - May 2021":"target",
    "Tabular Playground Series - Jan 2021":"target",
    "Tabular Playground Series - Mar 2021":"target",
    "Tweet Sentiment Extraction": "selected_text",
    "Instant Gratification":"target",
    "Tabular Playground Series - Jun 2021":"target",
    "Aerial Cactus Identification" : "has_cactus",
    "APTOS 2019 Blindness Detection": "diagnosis",
    "Coleridge Initiative - Show US the Data":"cleaned_label",
    "Humpback Whale Identification":"Id",
    "Kannada MNIST":"label",
    "Optiver Realized Volatility Prediction":"target",
    "Plant Pathology 2020 - FGVC7": ['healthy','multiple_diseases','rust','scab'],
    "chaii - Hindi and Tamil Question Answering" :"answer_text",
    "Tabular Playground Series - Aug 2021" : "loss",
    "Tabular Playground Series - Sep 2021" : "claim",
    "Tabular Playground Series - Oct 2021":"target",
    "Tabular Playground Series - Nov 2021":"target",
    "Tabular Playground Series - Dec 2021":"Cover_Type",
    "Feedback Prize - Evaluating Student Writing" : "predictionstring",
    "Store Sales - Time Series Forecasting":"sales",
    "Spaceship Titanic":"Transported",
    "Tabular Playground Series - Feb 2022":"target",
    "Tabular Playground Series - May 2022":"target",
    "Tabular Playground Series - Mar 2022":"congestion",
    "Tabular Playground Series - Aug 2022":"failure",
    "Feedback Prize - Predicting Effective Arguments":"discourse_effectiveness",
    "Google Brain - Ventilator Pressure Prediction":""
}


# 生成新的test.csv 文件
# , new_test_save_path
def split_new_train_test_tabulation(train_path, new_save_path, compete_name, id_name, is_order_split=False, test_size=0.2):
    df_train = pd.read_csv(train_path)
    var_columns = df_train.columns
    print(var_columns)
    X = df_train.loc[:, var_columns]
    y = df_train.loc[:, true_output_label[compete_name]]
    if isinstance(true_output_label[compete_name], list):
        sample_columns = [id_name]
        sample_columns.extend(true_output_label[compete_name])
    else:
        sample_columns = [id_name, true_output_label[compete_name]]
    if is_order_split:
        l = int((1-test_size) * X.shape[0])
        X_train = X.loc[:l]
        X_test = X.loc[l:]
        Y_test = y.loc[l:]
        sample = X_test.loc[:, sample_columns]
        X_test = X_test.drop(true_output_label[compete_name], axis=1)
        X_train.to_csv(os.path.join(new_save_path,"train.csv"), index =False)
        X_test.to_csv(os.path.join(new_save_path,"test.csv"), index =False)
        Y_test.to_csv(os.path.join(new_save_path,"target.csv"), index = False)
        sample.to_csv(os.path.join(new_save_path,"sample_submission.csv"),index=False)
        return

    try:
        X_train, X_valid, y_train, y_valid = train_test_split(X, y, test_size=0.2, random_state=0, stratify=y)
    except:
        X_train, X_valid, y_train, y_valid = train_test_split(X, y, test_size=0.2, random_state=0)
    X_train.to_csv(os.path.join(new_save_path, 'train.csv'), index=False)

    sample_submission = X_valid.loc[:,sample_columns]
    sample_submission.to_csv(os.path.join(new_save_path, 'sample_submission.csv'), index=False)
    b = X_valid.drop(true_output_label[compete_name], axis=1)
    b.to_csv(os.path.join(new_save_path, 'test.csv'), index=False)
    y_valid.to_csv(os.path.join(new_save_path, 'target.csv'), index=False)
    print(X_train.shape)
    print(X_valid.shape)
    print(y_train.shape)
    print(y_valid.shape)


def split_new_train_test_folder(train_folder_path, test_file, train_file, id_name,save_train_folder, save_test_folder, file_format=None):
    df_train = pd.read_csv(train_file)
    df_test = pd.read_csv(test_file)
    train_id = df_train.loc[:, [id_name]]
    test_id = df_test.loc[:, [id_name]]
    __batch_copy_files(train_id.values, train_folder_path, save_train_folder, file_format=file_format)
    __batch_copy_files(test_id.values, train_folder_path, save_test_folder, file_format=file_format)


def __batch_copy_files(file_names, file_folder_path, save_folder_path, file_format=None):
    if not os.path.exists(save_folder_path):
        os.makedirs(save_folder_path)
    for name in file_names:
        if file_format is not None:
            file_name = name[0] + file_format
        else:
            file_name = name[0]
        file_path = os.path.join(file_folder_path, file_name)
        target_f_path = os.path.join(save_folder_path, file_name)
        if os.path.exists(target_f_path):
            continue
        try:
            shutil.copy(file_path, save_folder_path)
        except Exception as e:
            print(str(e))


# 多分类标签转换
def multi_class_convert(file_path, save_path):
    df = pd.read_csv(file_path)

    df = pd.get_dummies(df,prefix='', prefix_sep='')
    df.to_csv(save_path, index=False)

# # 为图片类型的数据集划分成新的训练集以及测试集
# def split_new_train_test_imagine():


def get_output(file_path, compete_name):
    data = pd.read_csv(file_path)
    data = data.loc[:, true_output_label[compete_name]]
    if isinstance(true_output_label[compete_name], list):
        data = np.array(data)
    else:
        data = data.values
    return data


def get_venv_num_from_output_file(file_name):
    pattern = ".csv(.*?).csv"
    try:
        search = re.search(pattern, file_name)
        venv_num = int(search.group(1))
    except Exception as e:
        print(str(e))
        print(file_name)
        venv_num = None
    return venv_num


def split_Optiver_Realized_Volatility_Prediction_train_csv(train_csv_path, new_save_dir):
    df_train = pd.read_csv(train_csv_path)
    var_columns = df_train.columns
    print(var_columns)
    compete_name = "Optiver Realized Volatility Prediction"
    X = df_train.loc[:, var_columns]
    y = df_train.loc[:, true_output_label["Optiver Realized Volatility Prediction"]]
    X_train = X.loc[38300:, :]
    y_train = y.loc[38300:]
    X_valid = X.loc[:38299, :]
    y_valid = y.loc[:38299]
    X_train.to_csv(os.path.join(new_save_dir, 'train.csv'), index=False)
    X_valid['row_id'] = X_valid['stock_id'].astype(str) + "-" + X_valid['time_id'].astype(str)
    b = X_valid.drop(true_output_label[compete_name], axis=1)
    b.to_csv(os.path.join(new_save_dir, 'test.csv'), index=False)
    sample_submission = X_valid.loc[:, ['row_id', true_output_label[compete_name]]]
    sample_submission.to_csv(os.path.join(new_save_dir, 'sample_submission.csv'), index=False)
    y_valid.to_csv(os.path.join(new_save_dir, 'target.csv'), index=False)
    print(X_train.shape)
    print(X_valid.shape)
    print(y_train.shape)
    print(y_valid.shape)


def batch_rename_files(folder_path,save_train_folder,save_test_folder, train_csv, test_csv, id_name):
    df_train = pd.read_csv(train_csv)
    df_test = pd.read_csv(test_csv)
    train_ids = df_train.loc[:, id_name]
    test_ids = df_test.loc[:, id_name]
    i = 0
    train_rename_info = {}
    test_rename_info = {}
    trains = []
    tests = []
    for train_id in train_ids:
        if train_id == id_name: continue
        trains.append("Train_" + str(i))
        train_rename_info.update({train_id: "Train_" + str(i)})
        i+=1
    i=0
    for test_id in test_ids:
        if test_id == id_name: continue
        tests.append("Test_" + str(i))
        test_rename_info.update({test_id: "Test_" + str(i)})
        i+=1

    for k, v in train_rename_info.items():
        old_file = os.path.join(folder_path, k + ".jpg")
        new_file = os.path.join(save_train_folder, v + ".jpg")
        shutil.copy(old_file, new_file)

    for k, v in test_rename_info.items():
        old_file = os.path.join(folder_path, k + ".jpg")
        new_file = os.path.join(save_test_folder, v + ".jpg")
        shutil.copy(old_file, new_file)
    df_train[id_name] = trains
    df_test[id_name] = tests
    df_sample = pd.read_csv(r"E:\RQ2_compete_input\Plant Pathology 2020 - FGVC7\sample_submission.csv")
    df_sample[id_name] = tests
    df_train.to_csv(r"E:\RQ2_compete_input\Plant Pathology 2020 - FGVC7\new_train.csv",index=False)
    df_test.to_csv(r"E:\RQ2_compete_input\Plant Pathology 2020 - FGVC7\new_test.csv",index=False)
    df_sample.to_csv(r"E:\RQ2_compete_input\Plant Pathology 2020 - FGVC7\new_sample_submission.csv",index=False)


def convert_Shopee_Price_Match_Guarantee_target(csv_path):
    df = pd.read_csv(csv_path)
    df2 = df
    df3 = pd.merge(df, df2, on="label_group")
    df3 = df3.drop("label_group", axis=1)
    print(df3.duplicated())
    print("hhhhh")


if __name__ == '__main__':
    # csv_path = r"E:\RQ2_compete_input\Shopee - Price Match Guarantee\sample_submission.csv"
    # convert_Shopee_Price_Match_Guarantee_target(csv_path)

    # f_path = r"D:\pipeline\kaggle compete input\Tabular Playground Series - May 2021\sample_submission.csv"
    # s_path = r"D:\pipeline\kaggle compete input\Tabular Playground Series - May 2021\sample_submission1.csv"
    # multi_class_convert(f_path, s_path)

    # foldr_p = r"E:\RQ2_compete_input\Plant Pathology 2020 - FGVC7\plant-pathology-2020-fgvc7\tmp_train"
    # s_train_f = r"E:\RQ2_compete_input\Plant Pathology 2020 - FGVC7\train"
    # s_test_p = r"E:\RQ2_compete_input\Plant Pathology 2020 - FGVC7\test"
    # train_csv=r"E:\RQ2_compete_input\Plant Pathology 2020 - FGVC7\train.csv"
    # test_csv = r"E:\RQ2_compete_input\Plant Pathology 2020 - FGVC7\test.csv"
    # id_name = "image_id"
    # batch_rename_files(foldr_p,s_train_f,s_test_p,train_csv,test_csv, id_name)

    # split_Optiver_Realized_Volatility_Prediction_train_csv(r"E:\RQ2_compete_input\Optiver Realized Volatility Prediction\optiver-realized-volatility-prediction\train.csv", r"E:\RQ2_compete_input\Optiver Realized Volatility Prediction")
    #
    # competes = {"Tabular Playground Series - Jun 2021": r"D:\pipeline\kaggle compete input\Tabular Playground Series - Jun 2021\tabular-playground-series-jun-2021\train.csv",
    #            }
    # id_name = {
    #     "Tabular Playground Series - Jun 2021": "id",
    # }
    # for compete in competes:
    #     train_path =competes[compete]
    #     save_path = r"D:\pipeline\kaggle compete input\%s" % compete
    #     split_new_train_test_tabulation(train_path, save_path, compete,  id_name[compete])

    train_path = r"E:\RQ2_compete_valid_input\Feedback Prize - Predicting Effective Arguments\feedback-prize-effectiveness\train.csv"
    test_path = r"E:\RQ2_compete_valid_input\Feedback Prize - Predicting Effective Arguments\feedback-prize-effectiveness\test.csv"
    save_path = r"E:\RQ2_compete_valid_input\Feedback Prize - Predicting Effective Arguments"
    compete = "Feedback Prize - Predicting Effective Arguments"
    # ,
    id_name = "discourse_id"
    tr = pd.read_csv(train_path)
    t = pd.read_csv(test_path)
    test_size = t.shape[0]/tr.shape[0]
    split_new_train_test_tabulation(train_path, save_path, compete, id_name,test_size=0.1)
    #
    train_folder_p = r"E:\RQ2_compete_valid_input\Feedback Prize - Predicting Effective Arguments\feedback-prize-effectiveness\train"
    train_f = r"E:\RQ2_compete_valid_input\Feedback Prize - Predicting Effective Arguments\train.csv"
    test_f = r"E:\RQ2_compete_valid_input\Feedback Prize - Predicting Effective Arguments\test.csv"
    save_train_fo = r"E:\RQ2_compete_valid_input\Feedback Prize - Predicting Effective Arguments\train"
    save_test_fo = r"E:\RQ2_compete_valid_input\Feedback Prize - Predicting Effective Arguments\test"
    split_new_train_test_folder(train_folder_p, test_f, train_f, "discourse_id", save_train_fo, save_test_fo, file_format='.txt')
