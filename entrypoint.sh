#!/bin/bash
set -e

echo "Setting up cron job for menu scraper..."

# Install Python dependencies
pip install --no-cache-dir -r /work/requirements.txt

# Install cron
apt-get update && apt-get install -y cron

# Copy cron job and ensure it has proper line endings
cp /work/scraper.cron /etc/cron.d/scraper-cron

# Give execution rights
chmod 0644 /etc/cron.d/scraper-cron

# Create the crontab directly instead of copying
echo "0 22 * * * root cd /work && /usr/local/bin/python /work/scripts/scrape_weekly_menu.py >> /var/log/cron.log 2>&1" > /etc/cron.d/scraper-cron
echo "" >> /etc/cron.d/scraper-cron
chmod 0644 /etc/cron.d/scraper-cron

# Apply cron job
crontab /etc/cron.d/scraper-cron

# Create log file
touch /var/log/cron.log

# Run the scraper immediately on startup to populate initial data
echo "Running initial menu scrape..."
cd /work && python /work/scripts/scrape_weekly_menu.py

# Start cron in foreground
echo "Starting cron daemon..."
cron && tail -f /var/log/cron.log
