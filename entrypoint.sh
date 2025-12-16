#!/bin/bash
set -e

echo "Setting up cron job for menu scraper..."

# Install Python dependencies
pip install --no-cache-dir -r /work/requirements.txt

# Install cron
apt-get update && apt-get install -y cron

# Create cron.d file (system-wide format: includes user field)
cat > /etc/cron.d/scraper-cron <<'EOF'
# Run the lunch menu scraper daily at 10 PM (Central Time)
0 22 * * * root cd /work && /usr/local/bin/python /work/scripts/scrape_weekly_menu.py >> /var/log/cron.log 2>&1

EOF
chmod 0644 /etc/cron.d/scraper-cron

# Create log file
touch /var/log/cron.log

# Run the scraper immediately on startup to populate initial data
echo "Running initial menu scrape..."
cd /work && python /work/scripts/scrape_weekly_menu.py

# Start cron in foreground so container stays alive
echo "Starting cron daemon..."
cron -f &
tail -f /var/log/cron.log
