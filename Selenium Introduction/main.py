import time
import os
import pandas as pd

from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_PATH = os.path.join(BASE_DIR, "generated_report", "report.html")
SCREENSHOT_DIR = os.path.join(BASE_DIR, "doughnut_chart_screenshots")


class SeleniumWebDriverContextManager:
    def __init__(self):
        self.driver = None

    def __enter__(self):
        from selenium.webdriver.chrome.options import Options
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        self.driver = webdriver.Chrome(options=options)
        return self.driver

    def __exit__(self, exc_type, exc_value, traceback):
        if self.driver:
            self.driver.quit()


def save_table(driver: WebDriver):
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "g.y-column text.cell-text"))
        )
        time.sleep(1)
        columns = driver.find_elements(By.XPATH, "//*[name()='g' and contains(@class,'y-column')]")

        data = []
        for col in columns:
            cells = col.find_elements(By.CSS_SELECTOR, "text.cell-text")
            data.append([c.get_attribute("textContent").strip() for c in cells])

        header = [col[0] for col in data]            # first cell of each column = header
        rows = list(zip(*[col[1:] for col in data]))  # turn columns into rows

        pd.DataFrame(rows, columns=header).to_csv(os.path.join(BASE_DIR, "table.csv"), index=False)
        print("table.csv saved")
    except (TimeoutException, NoSuchElementException) as e:
        print(f"Could not read the table: {e}")


def save_doughnut_data(driver: WebDriver, index: int):
    rows = []
    for slice_text in driver.find_elements(By.CLASS_NAME, "slicetext"):
        parts = [t.get_attribute("textContent") for t in slice_text.find_elements(By.TAG_NAME, "tspan")]
        if len(parts) >= 2:
            rows.append([parts[0].strip(), parts[1].strip()])

    #if all filters are unselected rows is empty -> csv with only the header
    df = pd.DataFrame(rows, columns=["Facility Type", "Min Average Time Spent"])
    df.to_csv(os.path.join(BASE_DIR, f"doughnut{index}.csv"), index=False)


def process_doughnut(driver: WebDriver):
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "slicetext"))
        )
        time.sleep(1)

        # initial state
        driver.save_screenshot(os.path.join(SCREENSHOT_DIR, "screenshot0.png"))
        save_doughnut_data(driver, 0)

        filters_count = len(driver.find_elements(By.CSS_SELECTOR, "g.legend g.traces"))

        for i in range(filters_count):
            # find the legend again each time
            legend_items = driver.find_elements(By.CSS_SELECTOR, "g.legend g.traces")
            legend_items[i].find_element(By.CLASS_NAME, "legendtoggle").click()
            time.sleep(1)

            driver.save_screenshot(os.path.join(SCREENSHOT_DIR, f"screenshot{i + 1}.png"))
            save_doughnut_data(driver, i + 1)
    except (TimeoutException, NoSuchElementException) as e:
        print(f"Doughnut chart problem: {e}")


if __name__ == "__main__":
    with SeleniumWebDriverContextManager() as driver:
        driver.get(f"file://{REPORT_PATH}")
        save_table(driver)
        process_doughnut(driver)