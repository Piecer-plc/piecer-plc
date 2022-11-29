import pandas as pd
from sklearn.model_selection import train_test_split
import os


def split_train_test_file(old_folder, save_folder):
    old_train_drug_csv = os.path.join(old_folder, "train_drug.csv")
    old_train_features_csv = os.path.join(old_folder,"train_features.csv")
    old_train_targets_nonscored_csv = os.path.join(old_folder, "train_targets_nonscored.csv")
    old_train_targets_scored_csv = os.path.join(old_folder, "train_targets_scored.csv")
    old_train_drug_df = pd.read_csv(old_train_drug_csv)
    old_train_features_df = pd.read_csv(old_train_features_csv)
    old_train_targets_nonscored_df = pd.read_csv(old_train_targets_nonscored_csv)
    old_train_targets_scored_df = pd.read_csv(old_train_targets_scored_csv)

    X = old_train_targets_scored_df.loc[:, ['sig_id']]
    Y = old_train_targets_scored_df.drop("sig_id", axis=1)

    X_train, X_valid, Y_train, Y_valid = train_test_split(X, Y, test_size=0.2, random_state=0)

    new_train_target_scored_df = pd.concat([X_train,Y_train], axis=1)
    new_sample_df = pd.concat([X_valid, Y_valid], axis=1)

    target_df = Y_valid

    new_train_sig_id = set([])
    for row in new_train_target_scored_df.itertuples():
        new_train_sig_id.add(row.sig_id)

    new_train_drug_df = []
    for row in old_train_drug_df.itertuples():
        if row.sig_id in new_train_sig_id:
            new_train_drug_df.append(row)
    new_train_drug_df = pd.DataFrame(new_train_drug_df)
    new_train_drug_df = new_train_drug_df.drop("Index", axis=1)

    new_train_features_df = []
    new_test_features_df = []
    for row in old_train_features_df.itertuples():
        if row.sig_id in new_train_sig_id:
            new_train_features_df.append(row)
        else:
            new_test_features_df.append(row)
    new_train_features_df = pd.DataFrame(new_train_features_df)
    new_train_features_df = new_train_features_df.drop("Index", axis=1)
    new_test_features_df = pd.DataFrame(new_test_features_df)
    new_test_features_df = new_test_features_df.drop("Index", axis=1)

    new_train_targets_nonscored_df = []
    for row in old_train_targets_nonscored_df.itertuples():
        if row.sig_id in new_train_sig_id:
            new_train_targets_nonscored_df.append(row)
    new_train_targets_nonscored_df = pd.DataFrame(new_train_targets_nonscored_df)
    new_train_targets_nonscored_df = new_train_targets_nonscored_df.drop("Index", axis=1)

    new_sample_df.to_csv(os.path.join(save_folder, "sample_submission.csv"), index=False)
    new_train_drug_df.to_csv(os.path.join(save_folder, "train_drug.csv"), index=False)
    new_train_features_df.to_csv(os.path.join(save_folder, "train_features.csv"),index=False)
    new_train_targets_nonscored_df.to_csv(os.path.join(save_folder,"train_targets_nonscored.csv"),index=False)
    new_train_target_scored_df.to_csv(os.path.join(save_folder, 'train_targets_scored.csv'),index=False)
    new_test_features_df.to_csv(os.path.join(save_folder, "test_features.csv"), index=False)
    target_df.to_csv(os.path.join(save_folder,"target.csv"), index=False)


if __name__ == "__main__":
    # 多次分割的结果是相同的

    old_folder_p = r"E:\RQ2_compete_input\Mechanisms of Action (MoA) Prediction\lish-moa"
    save_folder_p = r"E:\RQ2_compete_input\Mechanisms of Action (MoA) Prediction"
    split_train_test_file(old_folder_p,save_folder_p)

