import os
import pandas as pd

input_folder = "./input/"
output_folder = "./output/"
output_file_name = "merge_output.csv"
list_files = os.listdir(input_folder)
print(f"found file {list_files}")
print("start loading all file")
all_df = pd.DataFrame({})
for file_name in list_files:
    tmp_file = pd.read_csv(input_folder + file_name)
    all_df = pd.concat([all_df, tmp_file], ignore_index=True)
print("start add related to cancer")


def add_cancer_retate(df):
    cancer_list_file_path = "cancer_scraped_data.txt"
    with open(cancer_list_file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
    cancer_text_list = [line.strip() for line in lines]
    cancer_text_list.append("cancer")

    def check_relate(text):
        for cancer_text in lines:
            if (
                text.lower() in cancer_text.lower()
                or cancer_text.lower() in text.lower()
            ):
                return True
        return False

    df["related_2_cancer"] = df["Clinical_Significant"].apply(check_relate)


add_cancer_retate(all_df)
# print(all_df)

full_output_file_name = output_folder + output_file_name
print(f"start save {full_output_file_name}")
all_df.to_csv(full_output_file_name, index=False)
