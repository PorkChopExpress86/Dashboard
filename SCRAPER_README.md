# Automated Lunch Menu Scraper

## Overview
The lunch menu scraper runs automatically every night at 10 PM to keep the school menu up to date.

## How It Works

### Components
- **scraper service**: Docker container that runs the menu scraper on a schedule
- **selenium service**: Provides headless Chrome browser for web scraping
- **cron**: Runs the scraper script at scheduled times

### Schedule
The scraper runs every night at **10:00 PM** (22:00) local time.

### Files
- `scraper.cron`: Cron schedule definition
- `entrypoint.sh`: Container startup script that:
  - Installs Python dependencies
  - Sets up the cron job
  - Runs an initial scrape immediately
  - Starts the cron daemon
- `Dockerfile.scraper`: Docker image for the scraper service
- `scripts/scrape_weekly_menu.py`: The scraping script

### Data
The scraper saves menu data to:
```
cache/weekly_menu_data.json
```

This file contains the weekly lunch menu with entrees, calories, and allergen information.

## Management Commands

### View scraper logs
```powershell
docker compose logs scraper
```

### Check cron job status
```powershell
docker exec schoolcafe-scraper crontab -l
```

### View cron execution logs
```powershell
docker exec schoolcafe-scraper cat /var/log/cron.log
```

### Manually trigger scraper
```powershell
docker exec schoolcafe-scraper python /work/scripts/scrape_weekly_menu.py
```

### Restart scraper service
```powershell
docker compose restart scraper
```

## Troubleshooting

### Scraper not running
1. Check if the container is running:
   ```powershell
   docker compose ps
   ```

2. Check the logs for errors:
   ```powershell
   docker compose logs scraper
   ```

3. Verify cron is installed:
   ```powershell
   docker exec schoolcafe-scraper which cron
   ```

### Menu data not updating
1. Check the last scraped timestamp in the data file:
   ```powershell
   Get-Content .\cache\weekly_menu_data.json | ConvertFrom-Json | Select-Object scraped_at
   ```

2. Check cron execution logs:
   ```powershell
   docker exec schoolcafe-scraper cat /var/log/cron.log
   ```

### Changing the schedule
Edit `scraper.cron` and rebuild:
```powershell
docker compose build scraper
docker compose up -d scraper
```

The cron format is: `minute hour day_of_month month day_of_week`
- Example: `0 22 * * *` = Every day at 10 PM
- Example: `0 8 * * 1` = Every Monday at 8 AM
