import os
from dotenv import load_dotenv

# Load environment variables from the local .env in this directory
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)
