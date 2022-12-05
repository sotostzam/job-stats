from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time
from .common import *

TIMEOUT = 2

class IndeedScraper:
    '''
    Creates a new instance of the scraper (Indeed).

    Methods:
    -------
    - `login()`:           Performs the login to LinkedIn
    - `infinite_scroll()`: Scrolls to the end of the page
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

        pprint(msg=f'Gathering job posts for the following roles: {roles}', type=1, prefix=self.name)
        print_progress(0, len(roles))

        job_list = []

        for i, role in enumerate(roles):
            # Replace special characters with utf characters
            role = role.replace(" ", "%20")
            location = location.replace(", ", "%2C%20")
            url = f"https://gr.indeed.com/jobs?q={role}&l={location}"

        return job_list