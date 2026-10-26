import asyncio
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
from sqlalchemy import text
from app.config import settings
from app.database import engine

async def test_connection():
    print("=" * 60)
    print(" Muraho Chatting App — Database Diagnostic Test")
    print("=" * 60)
    
    raw_url = settings.DATABASE_URL
    print(f"Configured DATABASE_URL: {raw_url[:35]}... (length: {len(raw_url)})")
    
    db_url, connect_args = settings.get_sqlalchemy_database_url()
    print(f"Engine Protocol: {db_url.split('://')[0]}")
    print(f"Connect Args (e.g. SSL): {connect_args}")
    print("-" * 60)
    
    start_time = time.time()
    try:
        print("Attempting database handshake...")
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1;"))
            row = result.scalar()
            latency = (time.time() - start_time) * 1000
            
            # Fetch PostgreSQL version if on Postgres
            try:
                ver_res = await conn.execute(text("SELECT version();"))
                ver = ver_res.scalar()
            except Exception:
                ver = "Local SQLite"

            print(f"✅ CONNECTION SUCCESSFUL! (Latency: {latency:.2f}ms)")
            print(f"Database response: {row}")
            print(f"Server version: {ver}")
            print("=" * 60)
            return True
    except Exception as e:
        latency = (time.time() - start_time) * 1000
        print(f"❌ CONNECTION FAILED after {latency:.2f}ms")
        print(f"Error details: {e}")
        print("-" * 60)
        print("💡 Troubleshooting Tips for Neon PostgreSQL:")
        print(" 1. Ensure you copied the full connection string from https://console.neon.tech")
        print(" 2. Confirm your database username and password in backend/.env")
        print(" 3. Make sure '?sslmode=require' is included in your Neon connection string.")
        print(" 4. Neon projects will pause compute after inactivity. Connecting might take a few seconds on cold start.")
        print("=" * 60)
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1)
