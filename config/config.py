"""
Environment Configuration Module

Loads environment variables from a .env file and provides configuration constants
for the tests.
"""

import os
from dotenv import load_dotenv

load_dotenv()
BASE_URL = os.getenv("BASE_URL")
