from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time
from .common import *

TIMEOUT = 2

class KarieraScraper:
    '''
    Creates a new instance of the scraper (Kariera).

    Methods:
    -------
    - `login()`:           Performs the login to LinkedIn
    - `load_more()`:       Loads the next page until a thrueshold
    - `filter_job()`:      Uses regex to match title of job
    - `extract_job_data`:  Formats the data from each job into a dictionary
    - `get_jobs`:          Main scraping method which automates the procedure
    '''

    def __init__(self):
        self.name = self.__class__.__name__
        self.options = webdriver.EdgeOptions()
        self.options.add_argument("headless")
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument("--start-maximized")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-notifications")
        self.options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Edge(options=self.options)

    def load_more(self, url: str, current_page: int) -> bool:
        '''
        Advances the pagination to load more results.

        Returns:
        -------
        - `bool`: If a new page was found and clicked returns True
        '''

        # Check if show more button is present and click it
        pages = self.driver.find_elements(By.CLASS_NAME, "ant-pagination-item")
        for page in pages:
            if int(page.get_attribute("title")) > current_page:
                self.driver.get(url + f'&page={current_page}')
                time.sleep(TIMEOUT)
                return True
        return False

    def get_job_list(self, roles: list, location: str, max_posts: int) -> list:
        '''
        Collects all available job posts.

        Args:
        -------
        - `roles`         (list): A collection of job titles for searching
        - `location`      (str): The required location for the search
        - `max_posts`     (int, optional): How may posts to search for each role. Default is set to 250

        Returns:
        -------
        - `list`: A collection of scraped job posts with their url, id and titles
        '''

        pprint(msg=f'The location argument is not supported in this scraper as it is only available in Greece.', type=1, prefix=self.name)
        pprint(msg=f'Gathering job posts for the following roles: {roles}', type=1, prefix=self.name)
        print_progress(0, len(roles))

        job_list = []

        for i, role in enumerate(roles):
            # Replace special characters with utf characters
            role = role.replace(" ", "%20")
            url = f"https://www.kariera.gr/en/jobs?title={role}"

            # Access url with set driver
            self.driver.get(url)
            try:
                WebDriverWait(self.driver,5).until(EC.visibility_of_all_elements_located((By.ID,"CybotCookiebotDialogBodyButtonDecline")))
                self.driver.find_element(By.ID,"CybotCookiebotDialogBodyButtonDecline").click()
            except TimeoutException:
                pass

            # Number of initially loaded jobs
            current_page = 1
            current_job_index = 0

            while True:
                job_listings = self.driver.find_elements(By.XPATH, "//*[@data-testid='job-card']")

                for job_post in job_listings:
                    current_job_index += 1
                    try:
                        job_roles = filter_job(job_post.find_element(By.XPATH, './/div[1]/div[1]/div[2]/div[2]/a').text)
                        if not job_roles:
                            continue
                        job_url = job_post.find_element(By.XPATH, './/div[1]/div[1]/div[2]/div[2]/a').get_attribute('href')
                        job_id = job_url.split('/en/jobs/')[-1]

                        exists = [item for item in job_list if item[1] == job_id]
                        if not exists:
                            job_list.append((job_url, job_id, job_roles))
                    except NoSuchElementException:
                        pass

                # Limit job posts accessed as bigger number results in less accuracy of titles
                if current_job_index >= max_posts:
                    break

                if self.load_more(url, current_page):
                    current_page += 1
                else:
                    break

            print_progress(i+1, len(roles),
                msg_complete = pprint(msg=f'Number of total jobs identified: {len(job_list)}', type=1, prefix=self.name, as_str=True)
            )

        return job_list

    def extract_job_data(self, job_list: list):
        '''
        Scraps and extracts the information about a specific job post.

        Args:
        -------
        - `job_list` (list): A collection of scraped job posts with their url, id and titles

        Returns:
        -------
        - `list`: A collection containing information about the gathered job posts. Each element is a `dict`
        '''

        pprint(msg='Scraping data for each job post.', type=1, prefix=self.name)
        print_progress(0, len(job_list))

        job_data = []
        job_info_section = f'//main[@class="ant-layout-content"]/section'

        for i, job_record in enumerate(job_list):
            job_url, job_id, job_roles = job_record
            job = {}
            self.driver.get(job_url)
            time.sleep(TIMEOUT)

            try:
                job['_id']   = int(job_id)
                job['url']   = job_url
                job['title'] = self.driver.find_element(By.XPATH, job_info_section + '/div[1]/div/div/div[1]/div/div').text
                job['roles'] = job_roles

                # This site allows for no value under the company name
                try:
                    job['company']  = self.driver.find_element(By.XPATH, job_info_section + '/div[2]/div[1]/div[1]/section/div[1]/a[1]').text
                except NoSuchElementException:
                    job['company'] = '-'

                job['location'] = self.driver.find_element(By.XPATH, job_info_section + '/div[2]/div[1]/div[2]/div[1]/div[1]/a').text
                job["type"]     = self.driver.find_element(By.XPATH, job_info_section + '/div[2]/div[1]/div[2]/div[1]/div[4]/a').text
                job["level"]    = self.driver.find_element(By.XPATH, job_info_section + '/div[2]/div[1]/div[2]/div[1]/div[3]/a').text
                job["industry"] = self.driver.find_element(By.XPATH, job_info_section + '/div[2]/div[1]/div[2]/div[2]/div[1]/a').text

                try:
                    job['workplace'] = self.driver.find_element(By.XPATH, job_info_section + '/div[2]/div[1]/div[2]/div[2]/div[2]/a').text
                except NoSuchElementException:
                    job['workplace'] = 'On-site'
                
                # Get the description of the job
                #job['description'] = self.driver.find_element(By.XPATH, job_info_section + '/div[2]/div[2]').get_attribute('innerText')
                job['description'] = self.driver.find_element(By.XPATH, job_info_section + '/div[2]/div[2]').text

                job['last_accessed'] = datetime.utcnow()

                job_data.append(job)

            except NoSuchElementException as e:
                pprint(msg=f'Exception retrieving data from job url:\n{job_url}', type=3, prefix=self.name)
                print(e)
                break

            print_progress(i+1, len(job_list),
                msg_complete = pprint(msg='All job data were processed successfully.', type=4, prefix=self.name, as_str=True)
            )

        return job_data

    def get_jobs(self, roles: list, location: str, max_posts: int = 250) -> (list | bool):
        '''
        Performs the necessary steps to scrap data from LinkedIn given a job title and location.

        Args:
        -------
        - `roles`         (list): A collection of job titles for searching
        - `location`      (str):  The required location for the search
        - `max_posts`     (int):  Optional value, how may posts to search for each role. Default is set to 250

        Returns:
        -------
        - `list`: A collection containing information about the gathered job posts. Each element is a `dict`
        - `bool`: Returns False if either no job posts were found or the login failed
        '''

        job_list = self.get_job_list(roles, location, max_posts)

        if not job_list:
            pprint(msg='No jobs found during search.', type=3, prefix=self.name)
            return False

        return self.extract_job_data(job_list)
