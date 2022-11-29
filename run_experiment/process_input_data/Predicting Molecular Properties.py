import pandas as pd
import random
import os
import shutil


def split_train_test_csv(train_csv_path, save_folder):
    df = pd.read_csv(train_csv_path)
    molecule_name = df.loc[:, "molecule_name"]
    molecule_name.drop_duplicates(keep='first', inplace=True)
    molecule_name = list(molecule_name)
    random.shuffle(molecule_name)
    split_pos = int(len(molecule_name) * 0.2)
    test = molecule_name[: split_pos]
    train = molecule_name[split_pos:]
    train_set = []
    test_set = []
    for row in df.itertuples():
        mole = row.molecule_name
        if mole in set(test):
            test_set.append(row)
        else:
            train_set.append(row)
    train_set = pd.DataFrame(train_set)
    test_set = pd.DataFrame(test_set)
    train_set = train_set.drop("Index", axis=1)
    test_set = test_set.drop("Index", axis=1)
    train_set.to_csv(os.path.join(save_folder, "train.csv"), index=False)
    test_set.to_csv(os.path.join(save_folder, "test.csv"), index = False)
    print("ggg")


def __get_unique_molecule_names(csv_path):
    df = pd.read_csv(csv_path)
    molecule_name = df.loc[:, "molecule_name"]
    molecule_name.drop_duplicates(keep='first', inplace=True)
    return list(molecule_name)


def __create_new_total_csv(old_total_csv_path, old_test_csv_path, save_path):
    old_molecule_name = __get_unique_molecule_names(old_test_csv_path)
    old_molecule_name = set(old_molecule_name)
    df = pd.read_csv(old_total_csv_path)
    new_df = []
    for row in df.itertuples():
        if row.molecule_name not in old_molecule_name:
            new_df.append(row)
    new_df = pd.DataFrame(new_df)
    new_df = new_df.drop("Index", axis=1)
    new_df.to_csv(save_path, index= False)


def __create_new_total_csv_files(old_folder, save_folder):
    old_test_path = os.path.join(old_folder, "test.csv")
    old_dipole_moments = os.path.join(old_folder, "dipole_moments.csv")
    old_magnetic_shielding_tensors = os.path.join(old_folder, "magnetic_shielding_tensors.csv")
    old_mulliken_charges = os.path.join(old_folder, "mulliken_charges.csv")
    old_potential_energy = os.path.join(old_folder, "potential_energy.csv")
    new_test_path = os.path.join(save_folder,"test.csv")
    old_scalar_coupling_contributions = os.path.join(old_folder, "scalar_coupling_contributions.csv")
    # __create_new_total_csv(old_dipole_moments, old_test_path, os.path.join(save_folder, "dipole_moments.csv"))
    # __create_new_total_csv(old_magnetic_shielding_tensors, old_test_path, os.path.join(save_folder, "magnetic_shielding_tensors.csv"))
    __create_new_total_csv(old_mulliken_charges, old_test_path, os.path.join(save_folder, "mulliken_charges.csv"))
    __create_new_total_csv(old_potential_energy, old_test_path, os.path.join(save_folder, "potential_energy.csv"))
    __create_new_total_csv(old_scalar_coupling_contributions, new_test_path, os.path.join(save_folder, "scalar_coupling_contributions.csv"))


def __create_new_structures_folder(old_folder, save_folder):
    if not os.path.exists(os.path.join(save_folder, "structures")):
        os.makedirs(os.path.join(save_folder, "structures"))
    structures_folder = os.path.join(old_folder, "structures")
    old_test_path = os.path.join(old_folder, "test.csv")
    old_molecule_name = __get_unique_molecule_names(old_test_path)
    old_molecule_name = set(old_molecule_name)
    for model_name in os.listdir(structures_folder):
        old_path = os.path.join(structures_folder, model_name)
        new_path = os.path.join(save_folder, "structures", model_name)
        molecule_name = model_name.replace(".xyz", "")
        if molecule_name not in old_molecule_name:
            shutil.copy(old_path, new_path)


def __train_test_id_reorder(new_train_csv, new_test_csv):
    train_df = pd.read_csv(new_train_csv)
    test_df = pd.read_csv(new_test_csv)
    train_df['id'] = range(len(train_df))
    test_df['id'] = [i + len(train_df) for i in range(len(test_df))]
    train_df.to_csv(new_train_csv, index=False)
    test_df.to_csv(new_test_csv, index=False)
    print("ffff")


def __create_submission_sample_and_target_csv(new_test_csv, save_folder):
    test_df = pd.read_csv(new_test_csv)
    target = test_df.loc[:, ["scalar_coupling_constant"]]
    sample = test_df.loc[:, ["id", "scalar_coupling_constant"]]
    sample.to_csv(os.path.join(save_folder, "sample_submission.csv"), index=False)
    target.to_csv(os.path.join(save_folder, "target.csv"), index=False)
    test_df = test_df.drop("scalar_coupling_constant", axis=1)
    test_df.to_csv(new_test_csv, index=False)


def deal_input_data(old_folder, save_folder):
    __create_new_total_csv_files(old_folder, save_folder)
    __create_new_structures_folder(old_folder, save_folder)
    new_train_csv = os.path.join(save_folder, "train.csv")
    new_test_csv = os.path.join(save_folder,"test.csv")
    __train_test_id_reorder(new_train_csv, new_test_csv)
    __create_submission_sample_and_target_csv(new_test_csv, save_folder)


if __name__ == "__main__":
    # 此分割的多次结果互不相同，分割不可复现

    tr_csv_path = r"E:\RQ2_compete_input\Predicting Molecular Properties\champs-scalar-coupling\train.csv"
    save_folder_p = r"E:\RQ2_compete_input\Predicting Molecular Properties"
    old_folder_p = r"E:\RQ2_compete_input\Predicting Molecular Properties\champs-scalar-coupling"
    split_train_test_csv(tr_csv_path, save_folder_p)
    deal_input_data(old_folder_p, save_folder_p)



