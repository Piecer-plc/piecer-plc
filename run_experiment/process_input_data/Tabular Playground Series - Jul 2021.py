import pandas as pd
import os


def split_train_test_file(old_folder, save_folder):
    old_train_csv = os.path.join(old_folder, "train.csv")
    old_test_csv = os.path.join(old_folder, "test.csv")
    old_sample_submission_csv = os.path.join(old_folder, "sample_submission.csv")

    old_train_df = pd.read_csv(old_train_csv)
    old_test_df = pd.read_csv(old_test_csv)
    old_sample_submission_df = pd.read_csv(old_sample_submission_csv)

    new_train_df = old_train_df.loc[:int(7111 * 0.8), :]
    target_columns = ["target_carbon_monoxide", "target_benzene", "target_nitrogen_oxides"]
    test_columns = list(old_test_df.columns.values)
    new_test_df = old_train_df.loc[int(7111 * 0.8):, test_columns]
    sample_submission_columns = list(old_sample_submission_df.columns.values)
    new_sample_submission_df = old_train_df.loc[int(7111 * 0.8):, sample_submission_columns]
    target_df = new_sample_submission_df.loc[:, target_columns]

    new_train_df.to_csv(os.path.join(save_folder, "train.csv"), index= False)
    new_test_df.to_csv(os.path.join(save_folder, "test.csv"), index= False)
    new_sample_submission_df.to_csv(os.path.join(save_folder, "sample_submission.csv"), index=False)
    target_df.to_csv(os.path.join(save_folder, "target.csv"), index=False)

    print("p")


if __name__ == "__main__":
    old_folder_p = r"E:\RQ2_compete_input\Tabular Playground Series - Jul 2021\tabular-playground-series-jul-2021"
    save_folder_p = r"E:\RQ2_compete_input\Tabular Playground Series - Jul 2021"
    split_train_test_file(old_folder_p, save_folder_p)