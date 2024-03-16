from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=options)
driver.get("https://kktix.com/users/sign_in?back_to=https%3A%2F%2Fkktix.com%2F")

# 登录
account_input = driver.find_element(By.ID, "user_login")
password_input = driver.find_element(By.ID, "user_password")
account_input.send_keys("ray123045608075@gmail.com")
password_input.send_keys("12304560Yt")
password_input.send_keys(Keys.ENTER)
time.sleep(3)
driver.get("https://kktix.com/events/goldenwave/registrations/new")

for i in range(14, 21):
    xpath = f"/html/body/div[3]/div[4]/div/div/div[5]/div[1]/div/div[3]/div[2]/div[{i}]/div/div/span[4]/button[2]"
    try:
        tic_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        tic_button.click()
        break
    except:
        print(f"XPath {xpath} not found, trying next...")

org_management = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "person_agree_terms")))
org_management.click()

org_group = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[3]/div[4]/div/div/div[5]/div[4]/button")))
org_group.click()
