import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time

SCROLL_TIMEOUT = 2

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

        def get_num_jobs() -> int:
            return len(self.driver.find_elements(By.XPATH, "//ul[@class='jobs-search__results-list']/li"))

        def infinite_scroll() -> bool:
            # Get scroll height
            last_height = self.driver.execute_script("return document.body.scrollHeight")

            infinite_scroller_btn = self.driver.find_elements(By.CLASS_NAME, "infinite-scroller__show-more-button--visible")
            if infinite_scroller_btn:
                infinite_scroller_btn[0].click()
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_TIMEOUT)

            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                return False
            last_height = new_height

            return True

        self.driver.get(url)

        # Number of initially loaded jobs
        job_listings = get_num_jobs()
        current_job_index = 1
        exceptions = []

        while True:
            job_listings = get_num_jobs()
            print(f'Number of jobs available: {job_listings}')

            for _ in range(current_job_index, job_listings):
                try:
                    job_url = f'//*[@id="main-content"]/section[@class="two-pane-serp-page__results-list"]/ul/li[{current_job_index}]/div/a'
                    element = self.driver.find_element(By.XPATH, job_url)
                    self.job_links.append(element.get_attribute('href'))
                except Exception:
                    exceptions.append(current_job_index)
                current_job_index += 1

            #TODO Delete me!
            if current_job_index >= 50:
                break

            if not infinite_scroll():
                break

        print(f"Exceptions found ({len(exceptions)}): {exceptions}")
        print(f"\nNumber of jobs gathered: {len(self.job_links)}")

    def get_job_data(self):
        for job_url in self.job_links:
            self.driver.get(job_url)
            time.sleep(SCROLL_TIMEOUT)
            try:
                card_path = f'//div[@role="main"]/div[1]/div/div/div[1]'
                title_path = '/h1'
                element = self.driver.find_element(By.XPATH, card_path + title_path)
                print(f'Job found:', element.text.lower())
            except NoSuchElementException as e:
                print('Exception finding title in url:', job_url, e)
    
if __name__ == "__main__":
    url = "https://www.linkedin.com/jobs/search/?currentJobId=3330508315&distance=10&geoId=103077496&keywords=Data%20Scientist&location=Athens%2C%20Attiki%2C%20Greece&refresh=true"
    url_login = "https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin"

    with open("credentials.json",'r') as secrets:
        creds = json.load(secrets)

    wd = LinkedInScrapper()

    wd.load_job_listings(url)

    wd.login(url_login, creds['username'], creds['password'])

    wd.get_job_data()
