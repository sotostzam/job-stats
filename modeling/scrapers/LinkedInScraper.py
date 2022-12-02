from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time
import re

TIMEOUT = 2.5

class LinkedInScraper:
    '''
    Constructor for the ``Edge`` driver with parameters.
    '''

    def __init__(self, username, password):
        self.options = webdriver.EdgeOptions()
        self.options.add_argument("headless")
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument("--start-maximized")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-notifications")
        self.options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Edge(options=self.options)

        self.url_index = "https://www.linkedin.com/"

        self.username = username
        self.password = password

    def login(self):
        self.driver.get(self.url_index)
        WebDriverWait(self.driver,5).until(EC.visibility_of_all_elements_located((By.ID,"session_key")))
        self.driver.find_element(By.ID, 'session_key').send_keys(self.username)
        self.driver.find_element(By.ID, 'session_password').send_keys(self.password)
        self.driver.find_element(By.CLASS_NAME, "sign-in-form__submit-button").click()
        try:
            print('Attempting login phase...')
            WebDriverWait(self.driver, 100).until(EC.presence_of_element_located((By.ID, "global-nav")))
            print("Login was successful.")
        except TimeoutException:
            print('Login failed.')
            return False
        return True

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

    def filter_job(self, job_role: str) -> list:

        re_matches = {
            'Data Scientist': [r'.*[Dd]ata.?[Ss]cien.*'],
            'Data Analyst':   [r'.*[Dd]ata.?[Aa]nalyst.*'],
            'ML Engineer':    [r'.*[Mm]achine.?[Ll]earning.*', r'.*[Mm][Ll].?[Ee]ngineer.*'],
            'Deep Learning':  [r'.*[Dd]eep.?[Ll]earning.*'],
            'AI Engineer':    [r'.*[Aa]rtificial.?[Ii]ntelligence.*', r'(?:^|(?<=[\s]))\(?[Aa][Ii]\)?(?=[\s]|$)'],
            'MLOps':          [r'.*[Mm][Ll].?[Oo]ps']
        }

        roles = []
        for role in re_matches:
            for reg_ex in re_matches[role]:
                if re.search(reg_ex, job_role) != None:
                    roles.append(role)
        return roles

    def get_job_list(self, url: str) -> list:
        '''
        Documentation missing
        '''
        
        print('LinkedIn Scraper | INFO: Gathering job posts. Please wait...\n')

        job_list = []

        self.driver.get(url)

        # Number of initially loaded jobs
        current_job_index = 0
        exceptions = 0

        while True:
            job_listings = len(self.driver.find_elements(By.XPATH, "//ul[@class='jobs-search__results-list']/li"))

            for _ in range(current_job_index, job_listings):
                current_job_index += 1
                try:
                    job_path = f'//*[@id="main-content"]/section[@class="two-pane-serp-page__results-list"]/ul/li[{current_job_index}]/div'
                    job_roles = self.filter_job(self.driver.find_element(By.XPATH, job_path + '/div[2]/h3').text)
                    if len(job_roles) == 0:
                        continue
                    job_url = self.driver.find_element(By.XPATH, job_path + '/a').get_attribute('href')
                    job_id = self.driver.find_element(By.XPATH, job_path).get_attribute('data-entity-urn').split(":")[-1]
                    job_list.append((job_url, job_id, job_roles))
                except NoSuchElementException:
                    exceptions += 1

            #TODO Check if loading more jobs means less accuracy
            if current_job_index >= 500:
                break

            if not self.infinite_scroll():
                break

        print(f"LinkedIn Scraper | WARN: Number of corrupted links found: {exceptions}")
        print(f"LinkedIn Scraper | INFO: Number of matched jobs gathered: {len(job_list)}/{current_job_index}\n")

        return job_list

    def extract_job_data(self, job_list: list):
        job_data = []
        job_info_section = f'//div[@role="main"]/div[1]/div/div/div[1]'

        for job_record in job_list:
            job_url, job_id, job_roles = job_record
            job = {}
            self.driver.get(job_url)
            time.sleep(TIMEOUT)

            try:
                job['id']       = int(job_id)
                job['url']      = job_url
                job['title']    = self.driver.find_element(By.XPATH, job_info_section + '/h1').text
                job['roles']    = job_roles
                job['company']  = self.driver.find_element(By.XPATH, job_info_section + '/div[1]/span[1]/span[1]').text
                job['location'] = self.driver.find_element(By.XPATH, job_info_section + '/div[1]/span[1]/span[2]').text
                
                job_type = self.driver.find_element(By.XPATH, job_info_section + '/div[2]/ul/li[1]/span').text.split(" · ")
                job["type"] = job_type[0]
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
                job['description']   = self.driver.find_element(By.XPATH, f'//div[@role="main"]/section/div[1]/div').text
                job['date_inserted'] = datetime.utcnow()

                job_data.append(job)

            except NoSuchElementException:
                print('LinkedIn Scraper | ERROR: Exception finding title in url:', job_url)

        return job_data

    def get_jobs(self, role: str, location: str) -> (list | bool):
        role = role.replace(" ", "%20")
        location = location.replace(", ", "%2C%20")
        url = self.url_index + f"jobs/search?keywords={role}&location={location}"

        print('LinkedIn Scraper | INFO: Generating job list...')

        job_list = self.get_job_list(url)

        if not job_list:
            print('LinkedIn Scraper | ERROR: No jobs found during search.')
            return False

        if self.login():
            return self.extract_job_data(job_list) 
        else:
            print('LinkedIn Scraper | ERROR: Login failed.')
            return False
