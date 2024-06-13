import pandas as pd
import os

def combine_csv_files(input_folder, output_file):
    # สร้างลิสต์สำหรับเก็บ DataFrame แต่ละไฟล์
    csv_list = []

    # วนลูปอ่านไฟล์ .csv ในโฟลเดอร์ที่กำหนด
    for filename in os.listdir(input_folder):
        if filename.endswith(".csv"):
            file_path = os.path.join(input_folder, filename)
            # อ่านไฟล์ .csv เป็น DataFrame และเพิ่มไปยังลิสต์
            df = pd.read_csv(file_path)
            csv_list.append(df)

    # รวม DataFrame ทั้งหมดในลิสต์เป็นหนึ่งเดียว
    combined_df = pd.concat(csv_list, ignore_index=True)

    # เขียน DataFrame ที่รวมแล้วเป็นไฟล์ .csv
    combined_df.to_csv(output_file, index=False)

    print(f"ไฟล์ CSV ถูกรวมและบันทึกใน: {output_file}")

# ตัวอย่างการใช้ฟังก์ชัน
input_folder = "./input/"  # ระบุพาธไปยังโฟลเดอร์ที่มีไฟล์ .csv
output_file = "./output/combined.csv"  # ระบุพาธและชื่อไฟล์ .csv ที่ต้องการบันทึก
combine_csv_files(input_folder, output_file)
