import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app, lifespan

async def test_auth_registration():
    print("=" * 60)
    print(" Muraho Auth Registration (WhatsApp Flow) Test Suite")
    print("=" * 60)

    async with lifespan(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            timestamp = int(asyncio.get_event_loop().time() * 1000)

            # 1. Test Phone-First Registration (Like WhatsApp)
            phone_number = f"+250 788 {timestamp % 1000:03d} {timestamp % 10000:04d}"
            phone_reg_payload = {
                "fullName": "Keza Uwase",
                "phone": phone_number,
                "password": "Password123!",
                "bio": "Muraho Rwanda! Using WhatsApp-style onboarding.",
                "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80"
            }
            res = await client.post("/api/v1/auth/register", json=phone_reg_payload)
            assert res.status_code == 200, f"Phone registration failed: {res.status_code} - {res.text}"
            data = res.json()
            assert "access_token" in data
            assert data["user"]["phone"] == phone_number
            assert data["user"]["name"] == "Keza Uwase"
            print(f" [PASS] 1. Phone-First Registration -> User ID: {data['user']['id']}, Phone: {data['user']['phone']}")

            # 2. Test Email-First Registration
            email_address = f"kevin_{timestamp}@muraho.rw"
            email_reg_payload = {
                "fullName": "Kevin Habimana",
                "email": email_address,
                "password": "Password123!",
                "bio": "Building fast web apps in Kigali.",
                "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=300&q=80"
            }
            res = await client.post("/api/v1/auth/register", json=email_reg_payload)
            assert res.status_code == 200, f"Email registration failed: {res.status_code} - {res.text}"
            data = res.json()
            assert "access_token" in data
            assert data["user"]["email"] == email_address
            assert data["user"]["name"] == "Kevin Habimana"
            print(f" [PASS] 2. Email-First Registration -> User ID: {data['user']['id']}, Email: {data['user']['email']}")

            # 3. Test Duplicate Registration Prevention
            res = await client.post("/api/v1/auth/register", json=email_reg_payload)
            assert res.status_code == 400, f"Expected 400 for duplicate email, got: {res.status_code}"
            print(" [PASS] 3. Duplicate Prevention Check -> Correctly blocked with 400 Bad Request")

            # 4. Test Login with Phone
            login_phone_res = await client.post("/api/v1/auth/login", json={
                "emailOrPhone": phone_number,
                "password": "Password123!"
            })
            assert login_phone_res.status_code == 200, f"Login with phone failed: {login_phone_res.text}"
            print(f" [PASS] 4. Login with Phone -> Token acquired for {phone_number}")

            # 5. Test Login with Email
            login_email_res = await client.post("/api/v1/auth/login", json={
                "emailOrPhone": email_address,
                "password": "Password123!"
            })
            assert login_email_res.status_code == 200, f"Login with email failed: {login_email_res.text}"
            print(f" [PASS] 5. Login with Email -> Token acquired for {email_address}")

    print("=" * 60)
    print(" ALL AUTH REGISTRATION & LOGIN TESTS PASSED! ")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_auth_registration())
