#!/usr/bin/env python3
"""Quick test to verify the viewID URL works"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

def test_view_id():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    remote_url = os.environ.get("SELENIUM_REMOTE_URL")
    if remote_url:
        driver = webdriver.Remote(command_executor=remote_url, options=options)
    else:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    
    try:
        url = "https://www.schoolcafe.com/CFISD/menus?viewID=4322524b-1f7e-476a-9139-814c671143ef"
        print(f"Loading: {url}")
        driver.get(url)
        time.sleep(6)
        
        print(f"Title: {driver.title}")
        print(f"URL: {driver.current_url}")
        
        # Look for menu content
        page_text = driver.page_source
        if "menu" in page_text.lower():
            print("✓ Page contains menu content")
        if "Monday" in page_text or "Tuesday" in page_text:
            print("✓ Page contains day names")
        
        # Save HTML
        with open("/work/cache/viewid_test.html", "w", encoding="utf-8") as f:
            f.write(page_text)
        print("Saved HTML to cache/viewid_test.html")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    test_view_id()
