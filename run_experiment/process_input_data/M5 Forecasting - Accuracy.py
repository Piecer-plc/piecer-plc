import pandas as pd
import os
import datacompy


def compare_sale_validation_evaluation(old_folder):
    old_sales_train_evaluation_df = pd.read_csv(os.path.join(old_folder, "sales_train_evaluation.csv"))
    old_sales_train_validation_df = pd.read_csv(os.path.join(old_folder, "sales_train_validation.csv"))
    old_sales_train_validation_df["Index"] = old_sales_train_validation_df.index
    old_sales_train_evaluation_df["Index"] = old_sales_train_evaluation_df.index
    compare = datacompy.Compare(old_sales_train_evaluation_df, old_sales_train_validation_df, join_columns="Index")
    # Compare 参数：
    #   df1: 数据框1
    #   df2: 数据框2
    #   join_columns: 指定索引的列名，默认“None”，可以传入数组，比如：['key', 'AdID']
    #   on_index: 是否要开启索引，开启之后不需要指定 join_columns，默认“False”
    #   abs_tol: 绝对公差，默认“0”
    #   rel_tal: 相对公差，默认“0”
    #   df1_name: 报告中数据框1的名字，默认“df1”
    #   df2_name: 报告中数据框2的名字，默认“df2”
    #   ignore_spaces: 是否忽略空格，默认“False”
    #   ignore_case: 是否忽略大小写，默认“False”

    print(compare.matches())  # 最后判断是否相等，返回 bool
    print(compare.report())  # 打印报告详情，返回 string


def split_train_test_file(old_folder, save_folder):
    old_sales_train_evaluation_df = pd.read_csv(os.path.join(old_folder, "sales_train_evaluation.csv"))
    evaluation_columns = old_sales_train_evaluation_df.columns.values
    target_columns = evaluation_columns[-28:]
    new_target_columns = ["F" + str(i+1) for i in range(28)]
    target = old_sales_train_evaluation_df.loc[:, target_columns]
    target.columns = new_target_columns
    target.to_csv(os.path.join(save_folder, "target.csv"), index=False)
    print("gg")


if __name__ == "__main__":
    # 数据集与竞赛公开数据集吻合
    old_folder_p = r"E:\RQ2_compete_input\M5 Forecasting - Accuracy\m5-forecasting-accuracy"
    save_folder_p = r"E:\RQ2_compete_input\M5 Forecasting - Accuracy"
    split_train_test_file(old_folder_p, save_folder_p)
