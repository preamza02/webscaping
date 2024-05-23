import os
import pandas as pd

input_folder = "./input/"
output_folder = "./output/"
output_file_name = "merge_output_cancer_only.csv"
output_file_name_not = "merge_output_not_cancer_only.csv"
print("start add related to cancer")

cancer_list_file_path = "cancer_p_pan_dataa.txt"
with open(cancer_list_file_path, "r", encoding="utf-8") as file:
    lines = file.readlines()
cancer_text_list = [line.strip() for line in lines]
cancer_text_list.append("cancer")


def check_relate(row):
    a = False
    text = row["Clinical_Significant"]
    for cancer_text in cancer_text_list:
        if cancer_text.lower() in text.lower():
            a = True
            break
    b = False
    text = row["condition"]
    for text_name in [
        "Pathogenic",
        "Likely-Pathogenic",
        "Pathogenic-Likely-Pathogenic",
    ]:
        if text_name == text:
            b = True
            break
    return a and b


list_files = os.listdir(input_folder)
print(f"found file {list_files}")
print("start loading all file")
all_df = pd.DataFrame(
    {},
    columns=[
        "Gene",
        "rsId",
        "Ref",
        "Alt",
        "Variant type",
        "Functional Consequence",
        "condition",
        "Clinical_Significant",
        "reference",
    ],
)
left_df = pd.DataFrame(
    {},
    columns=[
        "Gene",
        "rsId",
        "Ref",
        "Alt",
        "Variant type",
        "Functional Consequence",
        "condition",
        "Clinical_Significant",
        "reference",
    ],
)


def concat_strings(series):
    return ",".join(series)


def first_strings(series):
    return series[0]


def not_relate(series):
    return "not relate"


for file_name in list_files:
    tmp_file = pd.read_csv(input_folder + file_name)
    mask = tmp_file.apply(check_relate, axis=1)
    # mask2 = tmp_file.apply(check_pathogenic, axis=1)
    conbin_mask = mask
    tmp_file_2 = tmp_file[conbin_mask]
    tmp_file_3 = tmp_file[~conbin_mask]
    group_by_tmp = tmp_file_2.groupby(
        [
            "Gene",
            "rsId",
            "Ref",
            "Alt",
        ]
    ).agg(
        {
            # "Gene": first_strings,
            # "rsId": first_strings,
            # "Ref": first_strings,
            "Variant type": concat_strings,
            "Functional Consequence": concat_strings,
            "condition": concat_strings,
            "Clinical_Significant": concat_strings,
            "reference": concat_strings,
        }
    )
    # print(group_by_tmp.index)
    g = []
    r = []
    re = []
    a = []
    for ind in group_by_tmp.index:
        g.append(ind[0])
        r.append(ind[1])
        re.append(ind[2])
        a.append(ind[3])
    group_by_tmp["Gene"] = g
    group_by_tmp["rsId"] = r
    group_by_tmp["Ref"] = re
    group_by_tmp["Alt"] = a

    def check_if_exist(row):
        if (
            row["Gene"],
            row["rsId"],
            row["Ref"],
            row["Alt"],
        ) in group_by_tmp.index.to_list():
            # print(group_by_tmp.index.to_list())
            return True
        else:
            return False

    mask_3 = tmp_file.apply(check_if_exist, axis=1)
    tmp_file_99 = tmp_file[~mask_3]
    group_by_tmp_2 = tmp_file_99.groupby(
        [
            "Gene",
            "rsId",
            "Ref",
            "Alt",
        ]
    ).agg(
        {
            # "Gene": first_strings,
            # "rsId": first_strings,
            # "Ref": first_strings,
            "Variant type": not_relate,
            "Functional Consequence": not_relate,
            "condition": not_relate,
            "Clinical_Significant": not_relate,
            "reference": not_relate,
        }
    )
    g2 = []
    r2 = []
    re2 = []
    a2 = []
    for ind in group_by_tmp_2.index:
        g2.append(ind[0])
        r2.append(ind[1])
        re2.append(ind[2])
        a2.append(ind[3])
    group_by_tmp_2["Gene"] = g2
    group_by_tmp_2["rsId"] = r2
    group_by_tmp_2["Ref"] = re2
    group_by_tmp_2["Alt"] = a2
    all_df = pd.concat([all_df, group_by_tmp], ignore_index=False)
    # all_df = pd.concat([all_df, group_by_tmp_2], ignore_index=False)
    left_df = pd.concat([left_df, tmp_file_3], ignore_index=True)


full_output_file_name = output_folder + output_file_name
full_output_file_name_not = output_folder + output_file_name_not
print(f"start save {full_output_file_name}")

all_df.sort_values(by=["Gene", "rsId"], ascending=[True, True]).to_csv(
    full_output_file_name, index=False
)
left_df.to_csv(full_output_file_name_not, index=False)
