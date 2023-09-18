import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Function to download a report
def download_report(driver, url, download_folder):
    driver.get(url)
    wait = WebDriverWait(driver, 60)  # Increased the timeout to 60 seconds
    wait.until(lambda driver: os.path.exists(os.path.join(download_folder, url.split("/")[-1])))

# Function to scrape PDFs
def scrape_pdf(scraping_page, scrape_all=False, download_folder="Pipeline"):
    try:
        start_time = time.time()
        current_directory = os.getcwd()

        chrome_options = webdriver.ChromeOptions()
        prefs = {
            'download.default_directory': os.path.join(current_directory, download_folder),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True
        }
        chrome_options.add_experimental_option("prefs", prefs)

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get(scraping_page)

        elems = driver.find_elements(By.XPATH, '//a[@class="module_link module_link-letter"]')

        if scrape_all:
            dd = driver.find_element(By.XPATH, "//select[@id='module-financial-quarter_select']")
            selectList = Select(dd)
            selectList.select_by_value("2023")

            home_urls = []
            for year in range(2023, 2010, -1):
                value_to_select = str(year)
                selectList.select_by_value(value_to_select)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//a[@class="module_link module_link-letter"]')))
                elem = driver.find_elements(By.XPATH, '//a[@class="module_link module_link-letter"]')
                home_urls.extend(link.get_attribute('href') for link in elem)

            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(download_report, driver, url, download_folder) for url in home_urls]

                for future in as_completed(futures):
                    pass  # Wait for all downloads to complete

        else:
            download_report(driver, elems[0].get_attribute('href'), download_folder)

        # Close the driver
        driver.quit()

        end_time = time.time()
        execution_time = end_time - start_time
        return f"PDF file(s) downloaded successfully in {execution_time:.2f} seconds"

    except Exception as e:
        return "Error downloading PDF file: " + str(e)


if __name__ == "__main__":
    main()
