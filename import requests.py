import requests

# URL ของเว็บไซต์ที่ต้องการเข้าถึง
url = 'http://httpbin.org/ip/'

try:
    # ส่งคำขอไปยังเว็บไซต์เพื่อรับข้อมูล IP ของคุณ
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    print('IP :', response.json())
except requests.exceptions.RequestException as e:
    print(f'error:', e)

