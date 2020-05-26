# An Extensible Web Scraper for Apartments
**Scrapes, Stores in Database, Generates Metrics, Emails**
![What it looks like](/doc/apartmentscraper.gif?raw=true "Quick Demo Email")

# Getting Started
```bash
# Install the requirements by
pip install -r requirements.txt

# Create the SQLite Database
python setup_sql.py

# Run A Crawl
scrapy crawl apartments_avalon

# Send Emails
# Setup .env file
# Note: Requires Send Grid Credentials in .env
python send_email.py
```

# Send Grid
This project uses a send grid email server to send the emails. Since we just use a basic smtp with SSL, any SMTP client will work.
