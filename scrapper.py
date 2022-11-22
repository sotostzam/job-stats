from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

SCROLL_TIMEOUT = 1.5

class WebDriver:
    '''
    Constructor for the ``Edge`` driver with parameters.
    '''
    def __init__(self):
        self.options = webdriver.EdgeOptions()
        #self.options.add_argument("headless") #TODO Include this to make browser not appear
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

    def scroll_to_infinity(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def scrap_website(self, url):
        tp = 0

        self.driver.get(url)
        #time.sleep(10) #TODO This should be removed to allow for content to be loaded in a dynamic way

        # Get scroll height
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while True:
            self.scroll_to_infinity()
            time.sleep(SCROLL_TIMEOUT)

            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            try:
                self.driver.find_element(By.CLASS_NAME, "infinite-scroller__show-more-button").click()
                if new_height == last_height:
                    break
                last_height = new_height
                print("Pressed load more jobs!")
            except:
                pass

        page_source = self.driver.page_source
        
        content = BeautifulSoup(page_source, 'html.parser')
        jobs = []
        job_selector = content.find_all('div', class_='job-search-card')
        for job in job_selector:
            titles = job.find_all('div', class_='base-search-card__info')
            for title in titles:
                title_job = title.find('h3', 'base-search-card__title').get_text()
                title_job = title_job.strip()
                jobs.append(title_job)
        print(jobs)
        print(f"Number of jobs found: {len(jobs)}")
    
if __name__ == "__main__":
    url = "https://www.linkedin.com/jobs/search/?currentJobId=3330508315&distance=5&geoId=103077496&keywords=Data%20Scientist&location=Athens%2C%20Attiki%2C%20Greece&refresh=true"

    wd = WebDriver()

    wd.scrap_website(url)
