import os
from dotenv import load_dotenv

load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL', 'your_supabase_project_url')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', 'your_supabase_anon_key')

print(SUPABASE_URL)
print(SUPABASE_KEY)

# You can also set these directly here for testing:
# SUPABASE_URL = "https://your-project.supabase.co"
# SUPABASE_KEY = "your-anon-key"
