import pandas as pd
import os
import shutil
from sklearn.model_selection import train_test_split


def split_train_test_file(old_folder, save_folder):
    old_sample_submission_csv = os.path.join(old_folder, "sample_submission.csv")
    old_test_identity_csv = os.path.join(old_folder, "test_identity.csv")
    old_test_transaction_csv = os.path.join(old_folder, "test_transaction.csv")
    old_train_identity_csv = os.path.join(old_folder, "train_identity.csv")
    old_train_transaction_csv = os.path.join(old_folder, "train_transaction.csv")

    # old_sample_submission_df = pd.read_csv(old_sample_submission_csv)
    # old_test_identity_df = pd.read_csv(old_test_identity_csv)
    # old_test_transaction_df = pd.read_csv(old_test_transaction_csv)
    old_train_identity_df = pd.read_csv(old_train_identity_csv)
    old_train_transaction_df = pd.read_csv(old_train_transaction_csv)
    test_size = 0.46

    old_train_identity_ID = set(old_train_identity_df["TransactionID"].values)
    old_train_transaction_ID = set(old_train_transaction_df["TransactionID"].values)

    old_train_transaction_none_identity = []
    old_train_transaction_identity = []
    for item in old_train_transaction_df.itertuples():
        if len(old_train_transaction_identity) == 1000:
            break
        if item.TransactionID in old_train_identity_ID:
            old_train_transaction_identity.append(item)
        else:
            old_train_transaction_none_identity.append(item)
    old_train_transaction_none_identity = pd.DataFrame(old_train_transaction_none_identity)
    old_train_transaction_none_identity = old_train_transaction_none_identity.drop("Index", axis=1)
    old_train_transaction_identity = pd.DataFrame(old_train_transaction_identity)
    old_train_transaction_identity = old_train_transaction_identity.drop("Index", axis=1)

    X_columns = list(old_train_transaction_df.columns.values)
    X_train_transaction_none_identity = old_train_transaction_none_identity.loc[:, X_columns]
    X_train_transaction_identity = old_train_transaction_identity.loc[:, X_columns]
    Y_train_transaction_none_identity = old_train_transaction_none_identity.loc[:, ["isFraud"]]
    Y_train_transaction_identity = old_train_transaction_identity.loc[:, ["isFraud"]]

    X_train, X_valid, y_train, y_valid = train_test_split(X_train_transaction_identity, Y_train_transaction_identity, test_size=0.46, random_state=0, stratify=Y_train_transaction_identity)
    X_none_train, X_none_valid, y_none_train, y_none_valid = train_test_split(X_train_transaction_none_identity, Y_train_transaction_none_identity,test_size=0.46, random_state=0,stratify=Y_train_transaction_none_identity)

    new_train_identity_IDs = set(list(X_train["TransactionID"].values))
    new_train_transaction_IDs = set(list(pd.concat([X_train["TransactionID"], X_none_train["TransactionID"]]).values))

    new_train_transaction = []
    new_test_transaction = []
    for item in old_train_transaction_df.itertuples():
        if item.TransactionID in new_train_transaction_IDs:
            new_train_transaction.append(item)
        else:
            new_test_transaction.append(item)
    new_train_transaction_df = pd.DataFrame(new_train_transaction)
    new_train_transaction_df = new_train_transaction_df.drop("Index", axis =1)
    new_test_transaction_df = pd.DataFrame(new_test_transaction)
    new_test_transaction_df = new_test_transaction_df.drop("Index", axis=1)

    new_sample_submission_df = new_test_transaction_df.loc[:,["TransactionID","isFraud"]]
    target_df = new_test_transaction_df.loc[:,["isFraud"]]
    new_test_transaction_df = new_test_transaction_df.drop("isFraud", axis =1)

    new_train_identity = []
    new_test_identity = []
    for item in old_train_identity_df.itertuples():
        if item.TransactionID in new_train_identity_IDs:
            new_train_identity.append(item)
        else:
            new_test_identity.append(item)
    new_train_identity_df = pd.DataFrame(new_train_identity)
    new_train_identity_df = new_train_identity_df.drop("Index", axis=1)
    new_test_identity_df = pd.DataFrame(new_test_identity)
    new_test_identity_df = new_test_identity_df.drop("Index", axis =1)

    new_train_transaction_df.to_csv(os.path.join(save_folder, "train_transaction.csv"), index=False)
    new_test_transaction_df.to_csv(os.path.join(save_folder,"test_transaction.csv"), index=False)
    new_train_identity_df.to_csv(os.path.join(save_folder,"train_identity.csv"), index=False)
    new_test_identity_df.to_csv(os.path.join(save_folder, "test_identity.csv"), index=False)
    new_sample_submission_df.to_csv(os.path.join(save_folder, "sample_submission.csv"), index=False)
    target_df.to_csv(os.path.join(save_folder, "target.csv"), index=False)

    print("hhh")


if __name__ == '__main__':
    old_folder_p = r"E:\RQ2_compete_input\IEEE-CIS Fraud Detection\ieee-fraud-detection"
    save_folder_p = r"E:\RQ2_compete_input\IEEE-CIS Fraud Detection"
    split_train_test_file(old_folder_p, save_folder_p)
