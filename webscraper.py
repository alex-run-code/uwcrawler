import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from fake_useragent import UserAgent
import json
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Crawler:

    def __init__(self):
        self.url = 'https://www.upwork.com/ab/account-security/login'
        self.username_xpath = '//*[@id="login_username"]'
        self.continue_mail_xpath = '//*[@id="login_password_continue"]'
        self.password_xpath = '//*[@id="login_password"]'
        self.login_button_xpath = '//*[@id="login_control_continue"]'
        self.job_list = []
        self.driver = None
        self.user_agent = UserAgent().google  

    def login(self):
        self.driver.get(self.url)
        time.sleep(1)
        print('writing username...')
        self.driver.find_element(By.XPATH, self.username_xpath).send_keys('bobsuperworker')
        self.driver.find_element(By.XPATH, self.continue_mail_xpath).click()
        time.sleep(1)
        print('writing password...')
        # improvment : Password should be stored as an environment variable
        self.driver.find_element(By.XPATH, self.password_xpath).send_keys('Argyleawesome123!')
        self.driver.find_element(By.XPATH, self.login_button_xpath).click()
        print('loggin in...')
        time.sleep(5)

    def initialize_driver(self):
        options = Options()
        options.add_argument(f"user-agent={self.user_agent}")
        options.add_argument("start-maximized")
        options.add_argument("--headless")
        self.driver = webdriver.Chrome(chrome_options=options)
        self.driver.get(self.url)
        print('Driver Initialized')
        return self.driver

    def get_sections(self):
        sections = self.driver.find_elements(By.TAG_NAME, 'section')
        return sections

    def get_title(self, section):
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "h4")))
        return section.find_element(By.TAG_NAME, 'h4').text

    def job_infos(self, section):
        # Improvment : each section could be stored independently
        return section.find_element(By.XPATH, './/div/div/div/div[2]/div/small[1]').text

    def job_description(self, section):
        return section.find_element(By.XPATH, './/div/div/div/div[2]/div/div[2]/div/div').text

    def job_skills(self, section):
        # Improvment : each skill could be stored in a list
        try:
            skills = section.find_element(By.CLASS_NAME, 'skills').text
        except Exception:
            skills = 'None'
        return skills

    def job_proposals(self, section):
        return section.find_element(By.XPATH, './/div/div/div/div[2]/div/div[3]').text

    def get_payment_info(self, section):
        payment = section.find_element(By.XPATH, './/div/div/div/div[2]/div/small[2]/span/span/span[3]/span')
        if payment.text == 'Payment verified':
            return True
        else:
            return False

    def get_amount_spent(self, section):
        return section.find_element(By.XPATH, './/div/div/div/div[2]/div/small[2]/span/span/span[4]').text

    def get_client_location(self, section):
        try:
            return section.find_element(By.CLASS_NAME, 'client-location').text
        except Exception:
            return 'None'

    def access_profile_page(self):
        profile = self.driver.find_element(By.XPATH, '//*[@id="nav-right"]/ul/li[1]/ul/li[4]/a')
        profile_path = profile.get_attribute('href')
        self.driver.get(profile_path)

    def get_personnal_details(self):
        time.sleep(3)
        section = self.driver.find_element(By.XPATH, '//*[@id="main"]/div[2]/div[2]/div[2]/div/div[1]/div[1]/section[1]/div/div[1]/div[1]/div')
        profile = {}
        profile['name'] =  section.find_element(By.XPATH, './/div[2]/div/div[1]').text
        profile['location'] =  section.find_element(By.XPATH, './/div[2]/div/div[2]').text
        profile['avatar'] =  section.find_element(By.XPATH, './/div[1]/div/div/img').text
        return profile
          
    def get_professional_details(self):
        section = self.driver.find_element(By.XPATH, '//*[@id="main"]/div[2]/div[2]/div[2]/div/div[1]/div[1]/section[2]')
        profile = {}
        profile['profession'] = section.find_element(By.XPATH, './/div[2]/section[1]/div[1]/div/div[1]/h2').text
        profile['rate'] = section.find_element(By.XPATH, './/div[2]/section[1]/div[1]/div/div[2]/div[1]/h3/span').text
        profile['description'] = section.find_element(By.XPATH, './/*[@id="up-line-clamp-v2-2"]/span').text
        profile['availability'] = section.find_element(By.XPATH, './/div[1]/aside/section[4]/div[2]/p/span').text
        profile['languages'] = section.find_element(By.XPATH, './/div[1]/aside/section[4]/div[3]/ul').text
        profile['education'] = section.find_element(By.XPATH, './/div[1]/aside/section[4]/div[5]/ul').text
        profile['work_history'] = section.find_element(By.XPATH, './/div[2]/section[2]/div/div[3]/div/span').text
        profile['skills'] =  section.find_element(By.XPATH, './/div[2]/section[4]/div/ul').text
        profile['employment_history'] =  self.driver.find_element(By.XPATH, '//*[@id="main"]/div[2]/div[2]/div[2]/div/div[1]/div[9]/section/div/ul').text
        return profile

    def get_profile_data(self):
        profile = {**self.get_personnal_details(), **self.get_professional_details()}
        return profile

    def write_json_file(self, object, file_name):
        f = open(f"{file_name}.json", "w")
        f.write(json.dumps(object))
        f.close()
        

    def run(self):
        self.initialize_driver()
        self.login()
        sections = self.get_sections()
        jobs = []
        for s in sections:
            data = {}
            data['tite'] = self.get_title(s)
            data['infos'] = self.job_infos(s)
            data['description'] = self.job_description(s)
            data['skills'] = self.job_skills(s)
            data['proposals'] = self.job_proposals(s)
            data['payment_verified'] = self.get_payment_info(s)
            data['amount'] = self.get_amount_spent(s)
            data['location'] = self.get_client_location(s)
            jobs.append(data)
        self.write_json_file(jobs, 'jobs')
        self.access_profile_page()
        profile_data = self.get_profile_data()
        self.write_json_file(profile_data, 'profile')
        
    

if __name__ == "__main__":
    Crawler().run()