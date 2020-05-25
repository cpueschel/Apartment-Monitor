# web-spider
A web scraper for all the things that we are interested in grabbing

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

# What it looks like

