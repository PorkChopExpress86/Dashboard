#!/usr/bin/env python3
"""
SchoolCafé Weekly Menu Scraper with viewID
Scrapes menus for the current week by navigating through days
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import os
import json
from datetime import datetime

def extract_daily_menu(soup):
    """Extract menu items from the current day's view"""
    menu = {
        "entrees": [],
        "vegetables": [],
        "fruits": [],
        "milk": [],
        "condiments": []
    }
    
    # Get text line by line
    text = soup.get_text("\n", strip=True)
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    
    current_category = None
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Category headers
        if line == "LUNCH ENTREE":
            current_category = "entrees"
            i += 1
            continue
        elif line == "VEGETABLE":
            current_category = "vegetables"
            i += 1
            continue
        elif line == "FRUIT":
            current_category = "fruits"
            i += 1
            continue
        elif line == "MILK":
            current_category = "milk"
            i += 1
            continue
        elif line == "CONDIMENT":
            current_category = "condiments"
            i += 1
            continue
        
        # Skip known non-item lines
        if line in ["Grain", "Protein", "Vegetable", "Fruit", "Milk", "Not yet rated", "Calories", "/", "Carbs", "Allergens:", "Additional Allergens:", "None listed"]:
            i += 1
            continue
        
        # Look for pattern: ItemName -> FoodType/Calories sequence
        if current_category and i + 3 < len(lines):
            # Check if this starts a food item (followed by Grain/Protein/Vegetable/Fruit/Milk, then Calories)
            if lines[i+1] in ["Grain", "Protein", "Vegetable", "Fruit", "Milk", "Calories"]:
                # Find "Calories" line
                calories_idx = None
                for j in range(i+1, min(i+6, len(lines))):
                    if lines[j] == "Calories":
                        calories_idx = j
                        break
                
                if calories_idx and calories_idx + 1 < len(lines):
                    item_name = line
                    # Next line after "Calories" is the number
                    calories_val = lines[calories_idx + 1]
                    
                    # Look for allergens
                    allergens = []
                    for j in range(calories_idx, min(calories_idx + 10, len(lines))):
                        if lines[j] == "Allergens:" and j + 1 < len(lines):
                            allergen_line = lines[j + 1]
                            if allergen_line != "None listed":
                                allergens = [a.strip() for a in allergen_line.split(",") if a.strip()]
                            break
                    
                    menu[current_category].append({
                        "name": item_name,
                        "calories": calories_val,
                        "allergens": allergens
                    })
        
        i += 1
    
    return menu


def get_date_buttons(driver):
    """Find the date navigation buttons in the weekly view"""
    try:
        # Look for date buttons (they show day abbreviation and date)
        date_elements = driver.find_elements(By.CLASS_NAME, "date-button")
        dates = []
        for elem in date_elements:
            text = elem.text.strip()
            if text:
                dates.append(text)
        return dates
    except Exception as e:
        print(f"Error finding date buttons: {e}")
        return []


def scrape_weekly_menu(view_id="4322524b-1f7e-476a-9139-814c671143ef"):
    """
    Scrape the weekly menu for the given viewID, navigating through each day
    
    Args:
        view_id: The SchoolCafé viewID parameter
    """
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
        url = f"https://www.schoolcafe.com/CFISD/menus?viewID={view_id}"
        print(f"Loading: {url}")
        driver.get(url)
        
        # Wait for page to load
        time.sleep(8)
        
        # Function to extract week dates from current page
        def get_week_dates():
            soup = BeautifulSoup(driver.page_source, "lxml")
            text = soup.get_text("\n", strip=True)
            lines = text.split("\n")
            
            dates = []
            days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
            for i, line in enumerate(lines):
                if line.strip() in days:
                    if i+2 < len(lines):
                        date_num = lines[i+1].strip()
                        month = lines[i+2].strip()
                        dates.append(f"{line} {date_num} {month}")
            return dates
        
        # Get initial week dates
        week_dates = get_week_dates()
        print(f"\nInitial week dates found: {week_dates}")
        
        # Check if we need to navigate to current week
        # Parse the first date to check if it's in the past
        if week_dates:
            try:
                # Parse "Mon 10 NOV" format
                first_date_parts = week_dates[0].split()
                if len(first_date_parts) >= 3:
                    day_num = int(first_date_parts[1])
                    month_abbr = first_date_parts[2].upper()
                    
                    # Convert month abbreviation to number
                    month_map = {'JAN':1,'FEB':2,'MAR':3,'APR':4,'MAY':5,'JUN':6,
                                'JUL':7,'AUG':8,'SEP':9,'OCT':10,'NOV':11,'DEC':12}
                    month_num = month_map.get(month_abbr[:3], datetime.now().month)
                    
                    # Create date object for comparison
                    current_year = datetime.now().year
                    first_menu_date = datetime(current_year, month_num, day_num).date()
                    today = datetime.now().date()
                    
                    print(f"First menu date: {first_menu_date}, Today: {today}")
                    
                    # If the menu week is in the past, try clicking "next week" button
                    if first_menu_date < today:
                        print("Menu is for a past week, attempting to navigate forward...")
                        
                        # Look for next/forward navigation buttons
                        # Common selectors: arrow buttons, next buttons, etc.
                        next_button_selectors = [
                            "button[aria-label*='next']",
                            "button[aria-label*='Next']",
                            "button[title*='next']",
                            "button[title*='Next']",
                            ".next-week-button",
                            "button.MuiIconButton-root:has(svg[data-testid='ArrowForwardIosIcon'])",
                            "//button[contains(@aria-label, 'next')]",
                            "//button[contains(@aria-label, 'Next')]",
                        ]
                        
                        clicked = False
                        for selector in next_button_selectors:
                            try:
                                if selector.startswith("//"):
                                    # XPath selector
                                    button = driver.find_element(By.XPATH, selector)
                                else:
                                    # CSS selector
                                    button = driver.find_element(By.CSS_SELECTOR, selector)
                                
                                print(f"Found next button with selector: {selector}")
                                button.click()
                                time.sleep(3)
                                
                                # Check if we moved forward
                                new_week_dates = get_week_dates()
                                if new_week_dates != week_dates:
                                    week_dates = new_week_dates
                                    print(f"Successfully navigated to: {week_dates}")
                                    clicked = True
                                    break
                            except Exception as e:
                                continue
                        
                        if not clicked:
                            print("Could not find next week button, using current week shown")
            except Exception as e:
                print(f"Error checking week navigation: {e}")
        
        print(f"\nFinal week dates: {week_dates}")
        
        # Now navigate through each day and extract menus
        weekly_menus = {}
        
        # Find all date buttons
        try:
            date_buttons = driver.find_elements(By.CLASS_NAME, "date-button")
            print(f"Found {len(date_buttons)} date buttons")
            
            for idx, date_label in enumerate(week_dates):
                print(f"\nExtracting menu for {date_label}...")
                
                # Click the corresponding date button
                if idx < len(date_buttons):
                    try:
                        date_buttons[idx].click()
                        time.sleep(3)  # Wait for menu to load
                        
                        # Extract menu for this day
                        soup = BeautifulSoup(driver.page_source, "lxml")
                        daily_menu = extract_daily_menu(soup)
                        weekly_menus[date_label] = daily_menu
                        
                        # Print entrees for this day
                        print(f"  Entrees ({len(daily_menu['entrees'])}): {[e['name'] for e in daily_menu['entrees']]}")
                        
                        # Re-find date buttons after page update
                        date_buttons = driver.find_elements(By.CLASS_NAME, "date-button")
                    except Exception as e:
                        print(f"  Error clicking button: {e}")
                        # If first day failed, use already loaded page
                        if idx == 0:
                            soup = BeautifulSoup(driver.page_source, "lxml")
                            daily_menu = extract_daily_menu(soup)
                            weekly_menus[date_label] = daily_menu
                            print(f"  Using initially loaded page")
                            print(f"  Entrees ({len(daily_menu['entrees'])}): {[e['name'] for e in daily_menu['entrees']]}")
        except Exception as e:
            print(f"Error navigating days: {e}")
            # Fall back to current day only
            soup = BeautifulSoup(driver.page_source, "lxml")
            daily_menu = extract_daily_menu(soup)
            weekly_menus[week_dates[0] if week_dates else "Current Day"] = daily_menu
        
        result = {
            "view_id": view_id,
            "scraped_at": datetime.now().isoformat(),
            "week_dates": week_dates,
            "weekly_menus": weekly_menus
        }
        
        print("\n=== WEEKLY ENTREES SUMMARY ===")
        for day, menu in weekly_menus.items():
            print(f"\n{day}:")
            for entree in menu['entrees']:
                print(f"  - {entree['name']} ({entree['calories']} cal)")
        
        # Save to file
        output_file = "/work/cache/weekly_menu_data.json"
        with open(output_file, "w") as f:
            json.dump(result, f, indent=2)
        print(f"\n\nSaved complete data to {output_file}")
        
        return result
        
    finally:
        driver.quit()


if __name__ == "__main__":
    scrape_weekly_menu()
