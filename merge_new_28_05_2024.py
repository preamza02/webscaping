import os
import pandas as pd

input_folder = "./input/"
output_folder = "./output/"
output_file_name = "merge_output_new.csv"
output_file_name_not = "merge_output_new_not.csv"
print("start add related to cancer")
list_col = [
    "Gene",
    "rsId",
    "Ref",
    "Alt",
    "Effect",
    "Alleles Frequency",
    "Number of citation",
    "Publications",
    "Clinical Significant",
    "ClinVar Accession",
    "Cytogenetic location",
    "Variant name",
    "Diease name",
    "Synonyms",
]

cancer_list_file_path = "cancer_p_pan_dataa.txt"
with open(cancer_list_file_path, "r", encoding="utf-8") as file:
    lines = file.readlines()
cancer_text_list = [line.strip() for line in lines]
cancer_text_list.append("cancer")


def check_clinical(row):
    a = False
    text = row["Clinical Significant"]
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
    new_series = set(series)
    last_series = [str(x).strip().replace("\n", "") for x in new_series]
    print(last_series)
    return ", ".join(last_series)


def first_strings(series):
    return series[0]


def not_relate(series):
    return "not relate"


def create_group(tmp_file, mask_func, func, list_exist: list = None):
    print(list_exist)
    if len(tmp_file) == 0:
        return pd.DataFrame({})
    new_tmp_file = tmp_file.copy()
    mask_not_relate = new_tmp_file.apply(mask_func, axis=1)
    # print(mask_not_relate)

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

    if list_exist is not None:
        print("exist condition")
        condition_exist = new_tmp_file.apply(check_if_exist, axis=1)
        tmp_file_77 = new_tmp_file[~mask_not_relate & condition_exist]
    else:
        tmp_file_77 = new_tmp_file[mask_not_relate]
    # print(tmp_file_77)
    group_by_tmp = tmp_file_77.groupby(
        [
            "Gene",
            "rsId",
            "Ref",
            "Alt",
        ]
    ).agg(
        {
            "Effect": func,
            "Alleles Frequency": func,
            "Number of citation": func,
            "Publications": func,
            "Clinical Significant": func,
            "ClinVar Accession": func,
            "Cytogenetic location": func,
            "Variant name": func,
            "Diease name": func,
            "Synonyms": func,
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
    group_by_tmp = group_by_tmp[list_col]
    return group_by_tmp


for file_name in list_files:
    tmp_file = pd.read_csv(input_folder + file_name)

    # tmp_file = tmp_file.drop(columns=["related_2_cancer"])
    def return_true(series):
        return True

    print()
    group_by_tmp = create_group(
        tmp_file,
        return_true,
        concat_strings,
    )
    # mask = tmp_file.apply(return_true, axis=1)
    # mask2 = tmp_file.apply(check_pathogenic, axis=1)
    # conbin_mask = mask
    # tmp_file_2 = tmp_file[conbin_mask]
    # tmp_file_3 = tmp_file[~conbin_mask]
    # group_by_tmp = tmp_file_2.groupby(
    #     [
    #         "Gene",
    #         "rsId",
    #         "Ref",
    #         "Alt",
    #     ]
    # ).agg(
    #     {
    #         "Effect": concat_strings,
    #         "Alleles Frequency": concat_strings,
    #         "Number of citation": concat_strings,
    #         "Publications": concat_strings,
    #         "Clinical Significant": concat_strings,
    #         "ClinVar Accession": concat_strings,
    #         "Cytogenetic location": concat_strings,
    #         "Variant name": concat_strings,
    #         "Diease name": concat_strings,
    #         "Synonyms": concat_strings,
    #     }
    # )
    # # print(group_by_tmp.index)
    # g = []
    # r = []
    # re = []
    # a = []
    # for ind in group_by_tmp.index:
    #     g.append(ind[0])
    #     r.append(ind[1])
    #     re.append(ind[2])
    #     a.append(ind[3])
    # group_by_tmp["Gene"] = g
    # group_by_tmp["rsId"] = r
    # group_by_tmp["Ref"] = re
    # group_by_tmp["Alt"] = a

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

    all_df = pd.concat([all_df, group_by_tmp], ignore_index=True)
    print(all_df)
    # after_clinical_not_relate = create_group(
    #     tmp_file,
    #     check_clinical_after,
    #     not_related_text,
    #     list_exist=all_df.index.to_list(),
    # )
    # print(len(all_df.index.to_list()), len(after_clinical_not_relate))
    # all_df = pd.concat([all_df, after_clinical_not_relate], ignore_index=False)
    # new_index = all_df.index.to_list()
    # after_condition_not_phatogenic = create_group(
    #     tmp_file,
    #     check_condition_after,
    #     not_phatogenic,
    #     list_exist=new_index,
    # )
    # print(new_index)
    # print(len(new_index))
    # all_df = pd.concat([all_df, after_condition_not_phatogenic], ignore_index=True)
    # left_df = pd.concat([left_df, tmp_file_3], ignore_index=True)


full_output_file_name = output_folder + output_file_name
full_output_file_name_not = output_folder + output_file_name_not
print(f"start save {full_output_file_name}")
# all_df.index = range(len(all_df))
print(all_df.index)
all_df.sort_values(by=["Gene", "rsId"], ascending=[True, True]).to_csv(
    full_output_file_name, index=False
)
left_df.to_csv(full_output_file_name_not, index=False)
