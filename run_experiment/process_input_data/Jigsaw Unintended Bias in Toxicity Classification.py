import pandas as pd
import os
import shutil


def split_train_test_file(old_folder, save_folder):
    old_all_data_csv = os.path.join(old_folder, "all_data.csv")
    old_identity_individual_annotations_csv = os.path.join(old_folder, "identity_individual_annotations.csv")
    old_sample_submission_csv = os.path.join(old_folder, "sample_submission.csv")
    old_test_csv = os.path.join(old_folder, "test.csv")
    old_test_private_expanded_csv = os.path.join(old_folder, "test_private_expanded.csv")
    old_test_public_expanded_csv = os.path.join(old_folder, "test_public_expanded.csv")
    old_toxicity_individual_annotations_csv = os.path.join(old_folder, "toxicity_individual_annotations.csv")
    old_train_csv = os.path.join(old_folder, "train.csv")

    old_test_private_expanded_df = pd.read_csv(old_test_private_expanded_csv)
    target = old_test_private_expanded_df.loc[:, ["toxicity"]]
    target.columns = ['prediction']
    target.to_csv(os.path.join(save_folder,"target.csv"), index= False)
    shutil.copy(old_all_data_csv, save_folder)
    shutil.copy(old_identity_individual_annotations_csv, save_folder)
    shutil.copy(old_sample_submission_csv, save_folder)
    shutil.copy(old_test_csv, save_folder)
    shutil.copy(old_test_public_expanded_csv, save_folder)
    shutil.copy(old_test_private_expanded_csv, save_folder)
    shutil.copy(old_toxicity_individual_annotations_csv, save_folder)
    shutil.copy(old_train_csv, save_folder)


if __name__ == "__main__":
    # 数据集与竞赛公开数据集吻合

    old_folder_p = r"E:\RQ2_compete_input\Jigsaw Unintended Bias in Toxicity Classification\jigsaw-unintended-bias-in-toxicity-classification"
    save_folder_p = r"E:\RQ2_compete_input\Jigsaw Unintended Bias in Toxicity Classification"
    split_train_test_file(old_folder_p, save_folder_p)
