import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app, lifespan

async def run_tests():
    print("=" * 60)
    print(" Muraho Backend API Integration Test Suite")
    print("=" * 60)

    async with lifespan(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            # 1. Health check
            res = await client.get("/health")
            assert res.status_code == 200, f"Health check failed: {res.text}"
            print(" [PASS] 1. GET /health -> 200 OK")

            # 2. Get Me
            res = await client.get("/api/v1/users/me")
            assert res.status_code == 200
            user = res.json()
            assert user["name"] == "Jean-Luc Mugisha"
            print(f" [PASS] 2. GET /api/v1/users/me -> {user['name']} (@{user['username']})")

            # 3. Get Contacts
            res = await client.get("/api/v1/users/contacts")
            assert res.status_code == 200
            contacts = res.json()
            assert len(contacts) > 0
            print(f" [PASS] 3. GET /api/v1/users/contacts -> {len(contacts)} contacts")

            # 4. Conversations
            res = await client.get("/api/v1/conversations")
            assert res.status_code == 200
            convs = res.json()
            assert len(convs) >= 6
            print(f" [PASS] 4. GET /api/v1/conversations -> {len(convs)} active conversations")

            # 5. Messages
            res = await client.get("/api/v1/conversations/conv_1/messages")
            assert res.status_code == 200
            msgs = res.json()
            print(f" [PASS] 5. GET /api/v1/conversations/conv_1/messages -> {len(msgs)} messages in thread")

            # 6. Send Message
            send_payload = {
                "text": "Muraho! Testing automated API message dispatch.",
                "type": "text"
            }
            res = await client.post("/api/v1/conversations/conv_1/messages", json=send_payload)
            assert res.status_code == 200
            sent_msg = res.json()
            assert sent_msg["text"] == send_payload["text"]
            print(f" [PASS] 6. POST /api/v1/conversations/conv_1/messages -> Sent message ID: {sent_msg['id']}")

            # 7. Groups
            res = await client.get("/api/v1/groups")
            assert res.status_code == 200
            groups = res.json()
            print(f" [PASS] 7. GET /api/v1/groups -> {len(groups)} Rwandan tech communities")

            # 8. Statuses Feed
            res = await client.get("/api/v1/statuses/feed")
            assert res.status_code == 200
            statuses = res.json()
            print(f" [PASS] 8. GET /api/v1/statuses/feed -> {len(statuses)} stories loaded")

            # 9. Channels
            res = await client.get("/api/v1/channels")
            assert res.status_code == 200
            channels = res.json()
            print(f" [PASS] 9. GET /api/v1/channels -> {len(channels)} channels loaded")

            # 10. Business Profile
            res = await client.get("/api/v1/business/profile")
            assert res.status_code == 200
            biz = res.json()
            assert biz["name"] == "Kigali Tech Innovations & Artisans Ltd"
            print(f" [PASS] 10. GET /api/v1/business/profile -> {biz['name']}")

            # 11. Product Catalog
            res = await client.get("/api/v1/business/catalog")
            assert res.status_code == 200
            prods = res.json()
            assert len(prods) >= 6
            print(f" [PASS] 11. GET /api/v1/business/catalog -> {len(prods)} products priced in RWF")

            # 12. AI Support Simulator
            ai_query = {"question": "What payment methods do you accept for coffee orders?"}
            res = await client.post("/api/v1/business/ai-support/test", json=ai_query)
            assert res.status_code == 200
            ai_res = res.json()
            assert "MTN Mobile Money" in ai_res["answer"]
            print(f" [PASS] 12. POST /api/v1/business/ai-support/test -> Confidence: {ai_res['confidence']} | Answer: {ai_res['answer'][:40]}...")

            # 13. Calls History
            res = await client.get("/api/v1/calls/history")
            assert res.status_code == 200
            calls = res.json()
            print(f" [PASS] 13. GET /api/v1/calls/history -> {len(calls)} calls in log")

            # 14. Subscriptions Plans
            res = await client.get("/api/v1/subscriptions/plans")
            assert res.status_code == 200
            plans = res.json()
            print(f" [PASS] 14. GET /api/v1/subscriptions/plans -> {len(plans)} plans available")

    print("=" * 60)
    print(" ALL 14 TEST SUITES PASSED FLAWLESSLY! ")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(run_tests())
