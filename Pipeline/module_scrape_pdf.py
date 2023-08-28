# Load libraries
# Note. For selenium to work, have Google Chrome and install the following: pip install selenium==4.11.2, pip install webdriver_manager
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import os
import time

def scrape_pdf(scraping_page, scrape_all=False, download_folder="Pipeline"):

    try:
    
        # Get the full path of the current directory
        current_directory = os.getcwd()

        # Setup chrome options
        chrome_options = webdriver.ChromeOptions()

        # Define options to download file to specific folder
        prefs = {
            'download.default_directory': os.path.join(current_directory, download_folder),
            "download.prompt_for_download": False,     # set False to auto download the file
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True # set True to download pdf files
        }

        # add experimental options
        chrome_options.add_experimental_option("prefs", prefs)

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        # open quartely earning reports website section
        driver.get(scraping_page)

        # find all the links to the reports on the page
        elems = driver.find_elements(By.XPATH, '//a[@class="module_link module_link-letter"]')

        if scrape_all == False:
            # download the last report
            driver.get(elems[0].get_attribute('href'))
            time.sleep(2.5)
        
        else:
            # select the year dropdown
            dd = driver.find_element(By.XPATH,"//select[@id='module-financial-quarter_select']")
            selectList = Select(dd)
            options = selectList.options
            selectList.select_by_value("2023")
            # get urls of all the reports
            home_urls = []
            for year in range(2023, 2010, -1):
                value_to_select = str(year)
                selectList.select_by_value(value_to_select)
                time.sleep(1.5)
                elem = driver.find_elements(By.XPATH, '//a[@class="module_link module_link-letter"]')
                for link in elem:
                    home_urls.append(link.get_attribute('href'))
            # download all the reports from the urls
            for url in home_urls:
                driver.get(url)

        # close the tab
        driver.close()

        # close the browser
        driver.quit()

        return "PDF file(s) downloaded successfully"
    
    except Exception as e:

        return "Error downloading PDF file: " + str(e)
