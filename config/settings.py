import os
from dotenv import load_dotenv

# .env dosyasını belleğe yükle
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("KRİTİK HATA: .env dosyasında SUPABASE_URL veya SUPABASE_KEY bulunamadı.")