#!/usr/bin/env python3
"""Quick test of the viewID-based scraper - Weekly menu extraction"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import os
import json

def scrape_weekly_menu():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    remote_url = os.environ.get("SELENIUM_REMOTE_URL")
    if remote_url:
        driver = webdriver.Remote(command_executor=remote_url, options=options)
    else:
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    
    try:
        # Direct URL with viewID for Post Elementary, Grade 1, Lunch
        url = "https://www.schoolcafe.com/CFISD/menus?viewID=4322524b-1f7e-476a-9139-814c671143ef"
        print(f"Loading: {url}")
        driver.get(url)
        
        # Wait for menu content to load
        print("Waiting for menu content to load...")
        time.sleep(8)  # Wait for Angular app to fully load
        
        print(f"Title: {driver.title}")
        print(f"URL: {driver.current_url}")
        
        # Extract menu content
        html = driver.page_source
        soup = BeautifulSoup(html, "lxml")
        
        # Extract weekly menu - SchoolCafé typically organizes by day
        weekly_menu = {}
        
        # Look for calendar/day-based structure (FullCalendar uses fc-day)
        days = soup.find_all(['td', 'div'], class_=lambda x: x and 'fc-day' in str(x))
        print(f"Found {len(days)} day elements")
        
        # Look for day headers
        day_headers = soup.find_all(['th', 'div', 'h5'], class_=lambda x: x and any(d in str(x).lower() for d in ['day', 'date', 'week']))
        print(f"Found {len(day_headers)} day headers")
        
        # Extract menu items by category
        categories = ["protein", "grain", "vegetable", "fruit", "milk"]
        category_items = {}
        
        for category in categories:
            items = soup.find_all(['li', 'div'], class_=lambda x: x and category in str(x).lower())
            category_items[category] = [item.get_text(strip=True) for item in items if item.get_text(strip=True)]
        
        # Try to find all menu-item-list items
        menu_lists = soup.find_all(['ul'], class_=lambda x: x and 'menu-item-list' in str(x))
        all_items = []
        for ul in menu_lists:
            items = ul.find_all('li')
            for item in items:
                text = item.get_text(strip=True)
                if text:
                    all_items.append(text)
        
        # Build result
        result = {
            "url": driver.current_url,
            "title": driver.title,
            "weekly_menu": weekly_menu,
            "category_items": category_items,
            "all_menu_items": all_items,
            "days_found": len(days),
            "headers_found": len(day_headers)
        }
        
        print("\n=== WEEKLY MENU DATA ===")
        print(json.dumps(result, indent=2))
        
        # Save HTML for inspection
        with open("/work/cache/weekly_menu.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("\nSaved HTML to cache/weekly_menu.html")
        
        # Also save just the body content for easier inspection
        body = soup.find('body')
        if body:
            with open("/work/cache/menu_body.txt", "w", encoding="utf-8") as f:
                f.write(body.get_text("\n", strip=True))
            print("Saved body text to cache/menu_body.txt")
        
        return result
        
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_weekly_menu()
