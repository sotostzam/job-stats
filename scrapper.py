import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import date
from db import MongoDB

TIMEOUT = 2

class LinkedInScrapper:
    '''
    Constructor for the ``Edge`` driver with parameters.
    '''
    def __init__(self):
        self.options = webdriver.EdgeOptions()
        self.options.add_argument("headless") #TODO Include this to make browser not appear
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument("--start-maximized")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-notifications")
        self.options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Edge(options=self.options)
        self.db = MongoDB()

    def login(self, username, password):
        self.driver.get("https://www.linkedin.com/")
        WebDriverWait(self.driver,5).until(EC.visibility_of_all_elements_located((By.ID,"session_key")))
        self.driver.find_element(By.ID, 'session_key').send_keys(username)
        self.driver.find_element(By.ID, 'session_password').send_keys(password)
        self.driver.find_element(By.CLASS_NAME, "sign-in-form__submit-button").click()
        WebDriverWait(self.driver, 100).until(EC.presence_of_element_located((By.ID, "global-nav")))
        print("Login was successful.")

    def infinite_scroll(self) -> bool:
        # Get scroll height
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        infinite_scroller_btn = self.driver.find_elements(By.CLASS_NAME, "infinite-scroller__show-more-button--visible")
        if infinite_scroller_btn:
            infinite_scroller_btn[0].click()
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(TIMEOUT)

        # Calculate new scroll height and compare with last scroll height
        new_height = self.driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            return False
        last_height = new_height

        return True

    def load_job_listings(self, url: str):
        '''
        Documentation missing
        '''

        self.job_links = []
        self.driver.get(url)

        # Number of initially loaded jobs
        current_job_index = 1
        exceptions = []

        while True:
            job_listings = len(self.driver.find_elements(By.XPATH, "//ul[@class='jobs-search__results-list']/li"))

            for _ in range(current_job_index, job_listings):
                try:
                    job_path = f'//*[@id="main-content"]/section[@class="two-pane-serp-page__results-list"]/ul/li[{current_job_index}]/div'
                    job_url = self.driver.find_element(By.XPATH, job_path + '/a').get_attribute('href')
                    job_id = self.driver.find_element(By.XPATH, job_path).get_attribute('data-entity-urn').split(":")[-1]
                    self.job_links.append((job_url, job_id))
                except Exception:
                    exceptions.append(current_job_index)
                current_job_index += 1

            #TODO Check if loading more jobs means less accuracy
            if current_job_index >= 50:
                break

            if not self.infinite_scroll():
                break

        print(f"Exceptions found ({len(exceptions)}): {exceptions}")
        print(f"Number of jobs gathered: {len(self.job_links)}")

    def get_job_data(self):
        job_info_section = f'//div[@role="main"]/div[1]/div/div/div[1]'
        jobs = []

        for job_record in self.job_links:
            job_url, job_id = job_record
            job = {}
            self.driver.get(job_url)
            time.sleep(TIMEOUT)

            try:
                job['id']       = int(job_id)
                job['url']      = job_url
                job['title']    = self.driver.find_element(By.XPATH, job_info_section + '/h1').text
                job['company']  = self.driver.find_element(By.XPATH, job_info_section + '/div[1]/span[1]/span[1]').text
                job['location'] = self.driver.find_element(By.XPATH, job_info_section + '/div[1]/span[1]/span[2]').text
                
                job_type = self.driver.find_element(By.XPATH, job_info_section + '/div[2]/ul/li[1]/span').text.split(" · ")
                job["type"]  = job_type[0]
                if len(job_type) > 1:
                    job["level"] = job_type[1]

                job_insights = self.driver.find_element(By.XPATH, job_info_section + '/div[2]/ul/li[2]/span').text.split(" · ")
                job["company_size"] = job_insights[0].removesuffix(' employees')
                if len(job_insights) > 1:
                    job["industry"] = job_insights[1]

                try:
                    job['workplace'] = self.driver.find_element(By.XPATH, job_info_section + '/div[1]/span[1]/span[3]').text
                except NoSuchElementException:
                    pass
                
                job['published']     = self.driver.find_element(By.XPATH, job_info_section + '/div[1]/span[2]/span[1]').text
                job['description']   = self.driver.find_element(By.ID, 'job-details').text
                job['date_inserted'] = date.today().strftime("%d/%m/%Y")

                jobs.append(job)
                print(f'Jobs parsed: {len(jobs)}')

            except NoSuchElementException as e:
                print('Exception finding title in url:', job_url, e.msg)

        self.db.insert_many(jobs)
    
if __name__ == "__main__":
    url = "https://www.linkedin.com/jobs/search/?currentJobId=3330508315&distance=10&geoId=103077496&keywords=Data%20Scientist&location=Athens%2C%20Attiki%2C%20Greece&refresh=true"

    with open("credentials.json",'r') as secrets:
        creds = json.load(secrets)
    
    wd = LinkedInScrapper()

    wd.load_job_listings(url)

    wd.login(creds['username'], creds['password'])

    wd.get_job_data()