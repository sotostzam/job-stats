import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
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
        self.options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Edge(options=self.options)
        self.db = MongoDB()

    def login(self, url, username, password):
        self.driver.get(url)
        username_field = self.driver.find_element(By.ID, "username")
        username_field.send_keys(username)
        password_field = self.driver.find_element(By.ID, "password")
        password_field.send_keys(password)
        self.driver.find_element(By.CLASS_NAME, "login__form_action_container").click()

    def load_job_listings(self, url: str):
        '''
        Documentation missing
        '''

        self.job_links = []

        def infinite_scroll() -> bool:
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

            #TODO Delete me!
            if current_job_index >= 50:
                break

            if not infinite_scroll():
                break

        print(f"Exceptions found ({len(exceptions)}): {exceptions}")
        print(f"Number of jobs gathered: {len(self.job_links)}")

    def get_job_data(self):
        job_info_section = f'//div[@role="main"]/div[1]/div/div/div[1]'
        job_desc_section = f'//div[@role="main"]/section/div[1]'

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

                try:
                    job['workplace'] = self.driver.find_element(By.XPATH, job_info_section + '/div[1]/span[1]/span[3]').text
                except NoSuchElementException:
                    job['workplace'] = ''
                
                job['published']   = self.driver.find_element(By.XPATH, job_info_section + '/div[1]/span[2]/span[1]').text
                job['description'] = self.driver.find_element(By.XPATH, job_desc_section + '/div[1]').text

                #self.db.insert_one(job)
                jobs.append(job)

            except NoSuchElementException as e:
                print('Exception finding title in url:', job_url, e)

        self.db.insert_many(jobs)
    
if __name__ == "__main__":
    url = "https://www.linkedin.com/jobs/search/?currentJobId=3330508315&distance=10&geoId=103077496&keywords=Data%20Scientist&location=Athens%2C%20Attiki%2C%20Greece&refresh=true"
    url_login = "https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin"

    with open("credentials.json",'r') as secrets:
        creds = json.load(secrets)
    
    wd = LinkedInScrapper()

    wd.load_job_listings(url)

    wd.login(url_login, creds['username'], creds['password'])

    wd.get_job_data()