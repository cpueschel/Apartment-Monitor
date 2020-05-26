import os
import json
from dotenv import load_dotenv

BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, '.env'), override=True)

SENDER_EMAIL = os.environ['APARTMENT_SPIDER_SENDER_EMAIL']
RECIPIENT_EMAILS = json.loads(os.environ['APARTMENT_SPIDER_RECIPIENT_EMAILS'])
RECIPIENT_NAMES = json.loads(os.environ['APARTMENT_SPIDER_RECIPIENT_NAMES'])
API_KEY  = os.environ['APARTMENT_SPIDER_API_KEY']
PORT = os.environ['APARTMENT_SPIDER_API_PORT']
