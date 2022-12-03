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
    Creates a new instance of the scraper (LinkedIn).

    Args:
    -------
    - `username` (str): The username used to login to LinkedIn
    - `password` (str): The password used to login to LinkedIn

    Methods:
    -------
    - `login()`: Performs the login to LinkedIn
    - `infinite_scroll()`: Scrolls to the end of the page
    - `filter_job()`: Uses regex to match title of job
    - `extract_job_data`: Formats the data from each job into a dictionary
    - `get_jobs`: Main scraping method which automates the procedure
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

    def login(self) -> bool:
        '''
        Performs the login process to LinkedIn.

        Returns:
        -------
        - `bool`: True if login was successful, otherwise False
        '''
        self.driver.get(self.url_index)
        WebDriverWait(self.driver,5).until(EC.visibility_of_all_elements_located((By.ID,"session_key")))
        self.driver.find_element(By.ID, 'session_key').send_keys(self.username)
        self.driver.find_element(By.ID, 'session_password').send_keys(self.password)
        self.driver.find_element(By.CLASS_NAME, "sign-in-form__submit-button").click()
        try:
            WebDriverWait(self.driver, 100).until(EC.presence_of_element_located((By.ID, "global-nav")))
        except TimeoutException:
            print(f'Scraper (LinkedIn) | ERROR: Login to LinkedIn failed.')
            return False
        print('Scraper (LinkedIn) | INFO: Login to LinkedIn was successful.')
        return True

    def infinite_scroll(self) -> bool:
        '''
        Scrolls down to the end of the page.

        Returns:
        -------
        - `bool`: If scroll was successful returns True. When the end of the page is found returns False
        '''

        # Get scroll height
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        # Check if show more button is present and click it
        infinite_scroller_btn = self.driver.find_elements(By.CLASS_NAME, "infinite-scroller__show-more-button--visible")
        if infinite_scroller_btn:
            infinite_scroller_btn[0].click()
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(TIMEOUT)

        # Calculate new scroll height and compare with last value
        new_height = self.driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            return False

        last_height = new_height

        return True

    def filter_job(self, regex_matches: dict, job_role: str) -> list:
        '''
        Tries to match a given job title against a list of regular expressions.

        Args:
        -------
        - `regex_matches` (dict): Dictionary containing regular expressions for each job title
        - `job_role` (str): The title or role of the job

        Returns:
        -------
        - `list`: List containing all matched job titles. May be empty if no matches were made.
        '''

        roles = []
        for role in regex_matches:
            for reg_ex in regex_matches[role]:
                if re.search(reg_ex, job_role) != None:
                    roles.append(role)
        return roles

    def get_job_list(self, roles: list, location: str, regex_matches: dict, max_posts: int) -> list:
        '''
        Collects all available job posts.

        Args:
        -------
        - `roles` (list): A collection of job titles for searching
        - `location` (str): The required location for the search
        - `regex_matches` (dict): Dictionary containing regular expressions for each job title. Used for the `filter_job` method
        - `max_posts` (int): Optional value, how may posts to search for each role. Default is set to 250

        Returns:
        -------
        - `list`: A collection of scraped job posts with their url, id and titles
        '''
        print(f'Scraper (LinkedIn) | INFO: Gathering job posts for roles: {roles}')

        job_list = []

        for role in roles:
            # Replace special characters with utf characters
            role = role.replace(" ", "%20")
            location = location.replace(", ", "%2C%20")
            url = self.url_index + f"jobs/search?keywords={role}&location={location}"

            # Access url with set driver
            self.driver.get(url)

            # Number of initially loaded jobs
            current_job_index = 0

            while True:
                job_listings = len(self.driver.find_elements(By.XPATH, "//ul[@class='jobs-search__results-list']/li"))

                for _ in range(current_job_index, job_listings):
                    current_job_index += 1
                    try:
                        job_path = f'//*[@id="main-content"]/section[@class="two-pane-serp-page__results-list"]/ul/li[{current_job_index}]/div'
                        job_roles = self.filter_job(regex_matches, self.driver.find_element(By.XPATH, job_path + '/div[2]/h3').text)
                        if not job_roles:
                            continue
                        job_url = self.driver.find_element(By.XPATH, job_path + '/a').get_attribute('href')
                        job_id = self.driver.find_element(By.XPATH, job_path).get_attribute('data-entity-urn').split(":")[-1]

                        exists = [item for item in job_list if item[1] == job_id]
                        if not exists:
                            job_list.append((job_url, job_id, job_roles))
                    except NoSuchElementException:
                        pass

                # Limit job posts accessed as bigger number results in less accuracy of titles
                if current_job_index >= max_posts:
                    break

                # Check if page has been scrolled
                if not self.infinite_scroll():
                    break

        print(f"Scraper (LinkedIn) | INFO: Number of total jobs identified: {len(job_list)}")

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

        print('Scraper (LinkedIn) | INFO: Scraping data for each job post.')

        job_data = []
        job_info_section = f'//div[@role="main"]/div[1]/div/div/div[1]'

        for job_record in job_list:
            job_url, job_id, job_roles = job_record
            job = {}
            self.driver.get(job_url)
            time.sleep(TIMEOUT)

            try:
                job['_id']      = int(job_id)
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
                if len(job_insights) > 1:
                    job["industry"] = job_insights[1]

                try:
                    job['workplace'] = self.driver.find_element(By.XPATH, job_info_section + '/div[1]/span[1]/span[3]').text
                except NoSuchElementException:
                    pass
                
                # Get the description of the job
                job['description'] = self.driver.find_element(By.XPATH, f'//div[@id="job-details"]/span').get_attribute('innerText')

                job['last_accessed'] = datetime.utcnow()

                job_data.append(job)

            except NoSuchElementException:
                print(f'Scraper (LinkedIn) | ERROR: Exception retrieving data from job url:\n\t{job_url}')
                break

        return job_data

    def get_jobs(self, roles: list, location: str, regex_matches: dict, max_posts: int = 250) -> (list | bool):
        '''
        Performs the necessary steps to scrap data from LinkedIn given a job title and location.

        Args:
        -------
        - `roles` (list): A collection of job titles for searching
        - `location` (str): The required location for the search
        - `regex_matches` (dict): Dictionary containing regular expressions for each job title
        - `max_posts` (int): Optional value, how may posts to search for each role. Default is set to 250

        Returns:
        -------
        - `list`: A collection containing information about the gathered job posts. Each element is a `dict`
        - `bool`: Returns False if either no job posts were found or the login failed
        '''

        job_list = self.get_job_list(roles, location, regex_matches, max_posts)

        if not job_list:
            print('Scraper (LinkedIn) | ERROR: No jobs found during search.')
            return False

        if self.login():
            return self.extract_job_data(job_list) 
        else:
            return False
