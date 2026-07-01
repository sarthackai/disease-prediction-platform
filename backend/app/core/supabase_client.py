"""
supabase_client.py
Creates a single shared Supabase client for the whole backend.
"""
from supabase import create_client, Client
from app.core.config import SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)