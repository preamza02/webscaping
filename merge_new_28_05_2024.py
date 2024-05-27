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


def check_clinical(row):
    a = False
    text = row["Clinical_Significant"]
    for cancer_text in cancer_text_list:
        if cancer_text.lower() in text.lower():
            a = True
            break
    return a


def check_condiiton(row):
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
    return b


def check_clinical_after(row):
    if row["Clinical_Significant"] == "NOT report":
        return True
    else:
        return check_clinical(row)


def check_condition_after(row):
    if row["condition"] == "NOT report":
        return True
    else:
        return check_condiiton(row)


def check_relate(row):
    a = check_clinical(row)
    b = check_condiiton(row)
    return a and b


list_files = os.listdir(input_folder)
print(f"found file {list_files}")
print("start loading all file")
all_df = pd.DataFrame(
    {},
)
left_df = pd.DataFrame(
    {},
)


def concat_strings(series):
    return ",".join(series)


def first_strings(series):
    return series[0]


def not_relate(series):
    return "not relate"


def create_group(tmp_file, mask_func, func, list_exist: list = None):
    try:
        print(list_exist)
        if len(tmp_file) == 0:
            return pd.DataFrame({})
        new_tmp_file = tmp_file.copy()
        mask_not_relate = new_tmp_file.apply(mask_func, axis=1)

        def check_if_exist(row):
            if (
                row["Gene"],
                row["rsId"],
                row["Ref"],
                row["Alt"],
            ) in list_exist:
                print("exist", row["Gene"], row["rsId"])
                return True
            else:
                return False

        condition_exist = ~new_tmp_file.apply(check_if_exist, axis=1)
        if list_exist is not None:
            print("exist condition")
            condition_exist = new_tmp_file.apply(check_if_exist, axis=1)
            tmp_file_77 = new_tmp_file[~mask_not_relate & ~condition_exist]
        else:
            tmp_file_77 = new_tmp_file[~mask_not_relate]
        group_by_tmp = tmp_file_77.groupby(
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
                "Variant type": func,
                "Functional Consequence": func,
                "condition": func,
                "Clinical_Significant": func,
                "reference": func,
            }
        )
        g2 = []
        r2 = []
        re2 = []
        a2 = []
        for ind in group_by_tmp.index:
            g2.append(ind[0])
            r2.append(ind[1])
            re2.append(ind[2])
            a2.append(ind[3])
        group_by_tmp["Gene"] = g2
        group_by_tmp["rsId"] = r2
        group_by_tmp["Ref"] = re2
        group_by_tmp["Alt"] = a2
        return group_by_tmp
    except Exception as error:
        print(f"error der {error}")
        return pd.DataFrame({})


for file_name in list_files:
    tmp_file = pd.read_csv(input_folder + file_name)
    # tmp_file = tmp_file.drop(columns=["related_2_cancer"])
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

    def not_phatogenic(series):
        return "Not Pathogenic"

    def not_related_text(series):
        return "Not relate"

    all_df = pd.concat([all_df, group_by_tmp], ignore_index=False)
    after_clinical_not_relate = create_group(
        tmp_file,
        check_clinical_after,
        not_related_text,
        list_exist=all_df.index.to_list(),
    )
    print(len(all_df.index.to_list()), len(after_clinical_not_relate))
    all_df = pd.concat([all_df, after_clinical_not_relate], ignore_index=False)
    new_index = all_df.index.to_list()
    after_condition_not_phatogenic = create_group(
        tmp_file,
        check_condition_after,
        not_phatogenic,
        list_exist=new_index,
    )
    print(new_index)
    print(len(new_index))
    all_df = pd.concat([all_df, after_condition_not_phatogenic], ignore_index=True)
    left_df = pd.concat([left_df, tmp_file_3], ignore_index=True)


full_output_file_name = output_folder + output_file_name
full_output_file_name_not = output_folder + output_file_name_not
print(f"start save {full_output_file_name}")

all_df.sort_values(by=["Gene", "rsId"], ascending=[True, True]).to_csv(
    full_output_file_name, index=False
)
left_df.to_csv(full_output_file_name_not, index=False)
