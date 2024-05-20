import requests
from bs4 import BeautifulSoup

url = "https://www.cancer.gov/types"

response = requests.get(url)

if response.status_code == 200:
    with open("cancer_scraped_data.txt", "w", encoding="utf-8") as file:
        soup = BeautifulSoup(response.content, "html.parser")
        main_content = soup.find("main")
        # body = main_content.find_all("div")
        paragraphs_li = main_content.find_all("li")
        for paragraphs in paragraphs_li:
            paragraphs_li_a = paragraphs.find_all("a")
            for i in paragraphs_li_a:
                text = i.text.replace("\n", "").strip()
                if text != "":
                    # print(text)
                    file.write(f"{text}\n")


else:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
