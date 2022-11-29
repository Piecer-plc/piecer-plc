import pandas as pd
import shutil
import os


def split_train_test_file(old_folder, save_folder):
    old_jigsaw_toxic_comment_train_csv = os.path.join(old_folder, "jigsaw-toxic-comment-train.csv")
    old_jigsaw_toxic_comment_train_processed_seqlen128_csv = os.path.join(old_folder, "jigsaw-toxic-comment-train-processed-seqlen128.csv")
    old_jigsaw_unintended_bias_train_csv = os.path.join(old_folder, "jigsaw-unintended-bias-train.csv")
    old_jigsaw_unintended_bias_train_processed_seqlen128_csv = os.path.join(old_folder, "jigsaw-unintended-bias-train-processed-seqlen128.csv")
    old_sample_submission_csv = os.path.join(old_folder, "sample_submission.csv")
    old_test_csv = os.path.join(old_folder, "test.csv")
    old_test_labels_csv = os.path.join(old_folder, "test_labels.csv")
    old_test_processed_seqlen128_csv = os.path.join(old_folder, "test-processed-seqlen128.csv")
    old_validation_csv = os.path.join(old_folder, "validation.csv")
    old_validation_processed_seqlen128_csv = os.path.join(old_folder, "validation-processed-seqlen128.csv")


    old_test_labels_df = pd.read_csv(old_test_labels_csv)
    target = old_test_labels_df.loc[:, ["toxic"]]
    target.to_csv(os.path.join(save_folder, "target.csv"), index=False)
    shutil.copy(old_jigsaw_unintended_bias_train_csv, save_folder)
    shutil.copy(old_test_processed_seqlen128_csv, save_folder)
    shutil.copy(old_test_labels_csv, save_folder)
    shutil.copy(old_jigsaw_unintended_bias_train_processed_seqlen128_csv, save_folder)
    shutil.copy(old_jigsaw_toxic_comment_train_csv, save_folder)
    shutil.copy(old_jigsaw_toxic_comment_train_processed_seqlen128_csv, save_folder)
    shutil.copy(old_sample_submission_csv, save_folder)
    shutil.copy(old_test_csv, save_folder)
    shutil.copy(old_validation_processed_seqlen128_csv, save_folder)
    shutil.copy(old_validation_csv, save_folder)
    print("hh")


if __name__ == "__main__":
    save_folder_p = r"E:\RQ2_compete_input\Jigsaw Multilingual Toxic Comment Classification"
    old_folder_p = r"E:\RQ2_compete_input\Jigsaw Multilingual Toxic Comment Classification\jigsaw-multilingual-toxic-comment-classification"
    split_train_test_file(old_folder_p, save_folder_p)


