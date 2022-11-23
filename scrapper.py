import json
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

SCROLL_TIMEOUT = 2

class WebDriver:
    '''
    Constructor for the ``Edge`` driver with parameters.
    '''
    def __init__(self):
        self.options = webdriver.EdgeOptions()
        self.options.add_argument("headless") #TODO Include this to make browser not appear
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Edge(options=self.options)

    def scrap_website(self, url: str):
        '''
        Documentation missing
        '''

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
        #time.sleep(10) #TODO This should be removed to allow for content to be loaded in a dynamic way

        # Number of initially loaded jobs
        job_listings = get_num_jobs()
        current_job_index = 1
        exceptions = []

        print('# Jobs:', str(job_listings))

        while True:
            for _ in range(current_job_index, job_listings):
                try:
                    el_path = f'//*[@id="main-content"]/section[@class="two-pane-serp-page__results-list"]/ul/li[{current_job_index}]/div/div[@class="base-search-card__info"]/h3'
                    element = self.driver.find_element(By.XPATH, el_path)
                    current_job_index += 1
                    #self.driver.find_element(By.XPATH, f'//*[@id="main-content"]/section[@class="two-pane-serp-page__results-list"]/ul/li[{current_job_index}]/div').click()
                    #time.sleep(1)
                    print(f'Job number #{current_job_index}:', element.text.lower())
                except Exception:
                    exceptions.append(current_job_index)
                    current_job_index += 1
            if not infinite_scroll():
                break
            job_listings = get_num_jobs()
            print(job_listings)

        print(f"Exceptions found ({len(exceptions)}): {exceptions}")
        print(f"Number of jobs found: {get_num_jobs()}")
    
if __name__ == "__main__":
    url = "https://www.linkedin.com/jobs/search/?currentJobId=3330508315&distance=10&geoId=103077496&keywords=Data%20Scientist&location=Athens%2C%20Attiki%2C%20Greece&refresh=true"

    wd = WebDriver()

    wd.scrap_website(url)
