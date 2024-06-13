from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup
import pandas as pd

def check(driver):
    for i in [
        "[data-value_id='pathogenic_snp']",
        "[data-value_id='probable_pathogenic_snp']",
        "[data-value_id='pathogenic_likely_pathogenic']",
        "[data-value_id='risk_factor']",
        "[data-value_id='snp pubmed']",
        "[data-value_id='snp pubmed_cited']",
    ]:
        try:
            element_xpath = driver.find_element(By.CSS_SELECTOR, i)
            parent_element = element_xpath.find_element(By.XPATH, "..")
            if parent_element.get_attribute("class") != "fil_val selected":
                element_xpath.click()
        except:
            pass
    for i1 in [
        "[data-value_id='inframe_deletion']",
        "[data-value_id='inframe_indel']",
        "[data-value_id='inframe_insertion']",
        "[data-value_id='initiator_codon_variant']",
        "[data-value_id='missense_snp']",
        "[data-value_id='coding_synonymous_snp']",
    ]:
        try:
            element_xpath = driver.find_element(By.CSS_SELECTOR, i1)
            parent_element = element_xpath.find_element(By.XPATH, "..")
            if parent_element.get_attribute("class") != "fil_val selected":
                element_xpath.click()
        except:
            pass

def get_data(response):
    soup = BeautifulSoup(response, "html.parser")
    tables = soup.find_all("table", id="clinical_significance_datatable")
    table_data = []
    for i1, table in enumerate(tables):
        grand_parent_table = table.parent.parent
        table_text = grand_parent_table.find_all("div", class_="sect_heading")[i1].text
        rows = table.find_all("tr")
        headers = [header.text.strip() for header in rows[0].find_all("th")]
        for row in rows[1:]:
            cells = row.find_all("td")
            row_data = {"table_name": table_text}
            for i, header in enumerate(headers):
                row_data[header] = cells[i].text.strip()
            if row_data["Clinical Significance"] in [
                "Pathogenic",
                "Likely-Pathogenic",
                "Pathogenic-Likely-Pathogenic",
                "Risk-Factor",
            ]:
                table_data.append(row_data)
                url = f'https://www.ncbi.nlm.nih.gov/clinvar/{row_data["ClinVar Accession"]}/'
                response_small = requests.get(url)
                soup_small = BeautifulSoup(response_small.content, "html.parser")
                parent = soup_small.find_all("div", id="libsummaryinfo")[0]
                tar = parent.find_all("div", class_="indented")[2]
                all_dd = tar.find_all("dd")
                row_data["Cytogenetic location"] = all_dd[2].text
                row_data["Preferred name"] = all_dd[4].text
                parent_2 = soup_small.find_all("div", id="rcv_conditions")[0]
                all_dd_2 = parent_2.find_all("dd")
                row_data["Disease name"] = all_dd_2[0].text
                row_data["Synonyms"] = all_dd_2[1].text
    return table_data

# all_gene_list = ["BAP1", "BARD1", "BLM", "BMPR1A", "BRAF", "BRCA1", "BRCA2", "BRIP1", "BUB1B", "CASR", "CBL", "CD70", "CDC73", "CDH1", "CDK4", "CDKN1B", "CDKN1C", "CDKN2A", "CEBPA", "CEP57"]

all_gene_list = ["BRCA2"]
for round in range(((len(all_gene_list) - 1) // 10) + 1):
    output_file_name = f"output_{round*10+1}_{(round+1)*10}.csv"
    new_df = pd.DataFrame(
        columns=[
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
            "Disease name",
            "Synonyms",
        ]
    )
    for gene_name in all_gene_list[round * 10 : (round + 1) * 10]:
        print(f"gene {gene_name}")
        driver = webdriver.Chrome()
        driver.get("https://www.ncbi.nlm.nih.gov/snp")
        element_xpath = driver.find_element(By.CLASS_NAME, "search_form")
        new_element_xpath = element_xpath.find_element(By.ID, "term")
        new_element_xpath.send_keys(gene_name)
        new_element_xpath.send_keys(Keys.RETURN)
        a = driver.find_element(By.XPATH, f'//*[@id="EntrezSystem2.PEntrez.Snp.Snp_ResultsPanel.Snp_DisplayBar.Display"]')
        a.click()
        ps200_radio_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "ps200"))
        )
        ps200_radio_button.click()
        check(driver=driver)
        list_rs_id = []
        try:
            a = driver.find_element(By.XPATH, f'//*[@id="maincontent"]/div/div[3]/div/h3')
            n = int(a.text.split(":")[1].strip())
        except:
            print("error find number check case number = 1")
            n = 0
            try:
                element_xpath = driver.find_element(By.XPATH, f'//*[@id="maincontent"]/div/div[5]/div/div[2]/div[1]/span/a')
                list_rs_id.append(element_xpath.text)
            except:
                print("error skip gene")
                new_row = {
                    "Gene": gene_name,
                    "rsId": "ERROR FIND N",
                    "Clinical_Significant": "ERROR FIND N",
                }
                df_dictionary = pd.DataFrame([new_row])
                new_df = pd.concat([new_df, df_dictionary], ignore_index=True)
                continue
        for i in range(n):
            element_xpath = driver.find_element(By.XPATH, f'//*[@id="maincontent"]/div/div[5]/div[{i+1}]/div[2]/div[1]/span/a')
            list_rs_id.append(element_xpath.text)
        print(f"list_rs_id = {list_rs_id}")
        for index, rs_id in enumerate(list_rs_id):
            check(driver=driver)
            try:
                element_xpath = driver.find_element(By.CSS_SELECTOR, f'[href="/snp/{rs_id}"]')
            except:
                print(f"error find {rs_id}")
                new_row = {
                    "Gene": gene_name,
                    "rsId": rs_id,
                    "Clinical_Significant": "no exist",
                }
                df_dictionary = pd.DataFrame([new_row])
                new_df = pd.concat([new_df, df_dictionary], ignore_index=True)
                continue
            element_xpath_alleles = driver.find_element(By.XPATH, f'//*[@id="maincontent"]/div/div[5]/div[{index+1}]/div[2]/div[1]/dl/dd[2]/span[1]')
            alleles = element_xpath_alleles.text
            element_xpath_functional_consequence = driver.find_element(By.XPATH, f'//*[@id="maincontent"]/div/div[5]/div[{index+1}]/div[2]/div[1]/dl/dd[6]')
            functional_consequence = element_xpath_functional_consequence.text
            element_xpath.click()
            try:
                element_xpath_pup_count = driver.find_element(By.XPATH, f'//*[@id="snp_pub_count"]')
                pup_count = element_xpath_pup_count.text.split()[0]
            except:
                pup_count = "non citation"
            frequency_text = []
            for elment_t in [
                '//*[@id="main_content"]/main/div/div[3]/dl[1]/dd[5]/div[1]',
                '//*[@id="main_content"]/main/div/div[3]/dl[1]/dd[5]/div[2]',
                '//*[@id="main_content"]/main/div/div[3]/dl[1]/dd[5]/span[1]',
            ]:
                try:
                    element_xpath_freq = driver.find_element(By.XPATH, elment_t)
                    frequency_text.append(element_xpath_freq.text)
                except:
                    print(f"error find {elment_t}")
            real_freq_text = ".".join(frequency_text)
            element_xpath = driver.find_element(By.XPATH, f'//*[@id="label_id_seventh"]')
            element_xpath.click()
            try:
                publication_link = driver.find_element(By.XPATH, '//*[@id="publications"]/a[2]/button')
                publication_link.click()
                next_link = driver.current_url
            except:
                next_link = ""
            element_xpath = driver.find_element(By.XPATH, f'//*[@id="label_id_sixth"]')
            element_xpath.click()
            element_xpath = driver.find_element(By.XPATH, f'//*[@id="SnpClinicalTable"]/table')
            html_content = element_xpath.get_attribute("outerHTML")
            new_table_data = get_data(response=html_content)
            for each_row in new_table_data:
                new_row = {
                    "Gene": gene_name,
                    "rsId": rs_id,
                    "Ref": alleles.split(">")[0],
                    "Alt": alleles.split(">")[1],
                    "Effect": functional_consequence,
                    "Alleles Frequency": real_freq_text,
                    "Number of citation": pup_count,
                    "Publications": next_link,
                    "Clinical Significant": each_row["Clinical Significance"],
                    "ClinVar Accession": each_row["ClinVar Accession"],
                    "Cytogenetic location": each_row["Cytogenetic location"],
                    "Variant name": each_row["Preferred name"],
                    "Disease name": each_row["Disease name"],
                    "Synonyms": each_row["Synonyms"],
                }
                df_dictionary = pd.DataFrame([new_row])
                new_df = pd.concat([new_df, df_dictionary], ignore_index=True)
            driver.back()
            driver.back()
        driver.close()
    new_df.to_csv(output_file_name, index=False)
