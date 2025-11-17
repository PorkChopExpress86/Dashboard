"""School menu service"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


def get_weekly_menu() -> Dict[str, List[str]]:
    """
    Get the weekly school lunch menu
    
    Returns:
        Dictionary with day names as keys and list of entrees as values
    """
    cache_file = Path(__file__).resolve().parent.parent.parent / "cache" / "weekly_menu_data.json"
    
    if not cache_file.exists():
        return {}
    
    try:
        with open(cache_file, 'r') as f:
            data = json.load(f)
        
        # Extract just the entrees for each day
        weekly_menus = data.get('weekly_menus', {})
        menu_by_day = {}
        
        for day_label, menu_data in weekly_menus.items():
            # Parse day label (e.g., "Mon 10 NOV" -> "Monday 11/10")
            parts = day_label.split()
            if len(parts) >= 3:
                day_abbr = parts[0]  # Mon, Tue, etc.
                date_num = parts[1]
                month_abbr = parts[2]
                
                # Get entree names
                entrees = [item['name'] for item in menu_data.get('entrees', [])]
                
                # Use simple format: "Mon 11/10"
                day_key = f"{day_abbr} {date_num}"
                menu_by_day[day_key] = entrees
        
        return menu_by_day
    except Exception as e:
        print(f"Error loading menu: {e}")
        return {}


def refresh_menu():
    """
    Trigger a refresh of the menu data by running the scraper
    This should be called periodically (e.g., nightly) to keep menu up to date
    """
    # This would run the scraper - for now, just a placeholder
    # In production, you'd want to run this as a background task
    pass


def get_today_menu(now: datetime) -> Optional[List[str]]:
    """
    Get today's lunch menu entrees
    
    Args:
        now: Current datetime
        
    Returns:
        List of entree names for today, or None if not a school day or menu not available
    """
    # Don't show menu on weekends
    if now.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
        return None
    
    weekly_menu = get_weekly_menu()
    
    # Format today's date to match menu keys (e.g., "Mon 10", "Tue 11")
    day_abbr = now.strftime('%a')  # Mon, Tue, Wed, etc.
    date_num = now.strftime('%-d') if os.name != 'nt' else now.strftime('%#d')  # Remove leading zero
    
    today_key = f"{day_abbr} {date_num}"
    
    return weekly_menu.get(today_key)


def get_tomorrow_menu(now: datetime) -> Optional[List[str]]:
    """
    Get tomorrow's lunch menu entrees
    
    Args:
        now: Current datetime
        
    Returns:
        List of entree names for tomorrow, or None if not a school day or menu not available
    """
    from datetime import timedelta
    tomorrow = now + timedelta(days=1)
    
    # Don't show menu if tomorrow is a weekend
    if tomorrow.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
        return None
    
    weekly_menu = get_weekly_menu()
    
    # Format tomorrow's date to match menu keys (e.g., "Mon 10", "Tue 11")
    day_abbr = tomorrow.strftime('%a')  # Mon, Tue, Wed, etc.
    date_num = tomorrow.strftime('%-d') if os.name != 'nt' else tomorrow.strftime('%#d')  # Remove leading zero
    
    tomorrow_key = f"{day_abbr} {date_num}"
    
    return weekly_menu.get(tomorrow_key)
