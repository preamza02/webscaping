from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# ตั้งค่า Chrome Options
options = Options()
options.add_argument("start-maximized")  # เปิดเบราว์เซอร์ในโหมดเต็มหน้าจอ

# สร้าง WebDriver
driver = webdriver.Chrome(service=Service('/path/to/chromedriver'), options=options)

# เปิดเบราว์เซอร์ที่ URL ใดก็ได้
driver.get('chrome://settings/clearBrowserData')

# รอให้หน้าโหลด
driver.implicitly_wait(10)

# เรียกใช้คีย์ลัดเพื่อเปิดหน้าต่างการเคลียร์แคช
actions = ActionChains(driver)
actions.send_keys(Keys.TAB * 6 + Keys.SPACE).perform()

# รอสักครู่ให้การเคลียร์แคชทำงาน
driver.implicitly_wait(5)

# ปิดเบราว์เซอร์
driver.quit()
