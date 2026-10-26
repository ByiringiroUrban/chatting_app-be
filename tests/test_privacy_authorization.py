import uuid
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.security import create_access_token, hash_password
from app.database import AsyncSessionLocal
from app.models.user import User

@pytest_asyncio.fixture
async def setup_test_users():
    uid_suffix = uuid.uuid4().hex[:6]
    uid_a = f"user_a_{uid_suffix}"
    uid_b = f"user_b_{uid_suffix}"
    uid_c = f"user_c_{uid_suffix}"

    async with AsyncSessionLocal() as s:
        for uid, name, email in [
            (uid_a, 'Alice A', f'{uid_a}@test.rw'),
            (uid_b, 'Bob B', f'{uid_b}@test.rw'),
            (uid_c, 'Charlie C', f'{uid_c}@test.rw')
        ]:
            s.add(User(
                id=uid, name=name, username=uid, email=email,
                hashed_password=hash_password('pass123')
            ))
        await s.commit()

    return uid_a, uid_b, uid_c

@pytest.mark.asyncio
async def test_account_isolation_and_authorization(setup_test_users):
    uid_a, uid_b, uid_c = setup_test_users

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Unauthenticated requests are rejected
        res_no_auth = await ac.get("/api/v1/conversations")
        assert res_no_auth.status_code == 401, "Unauthenticated request must be rejected with 401"

        # 2. Auth tokens for users A, B, and C
        headers_a = {"Authorization": f"Bearer {create_access_token(uid_a)}"}
        headers_b = {"Authorization": f"Bearer {create_access_token(uid_b)}"}
        headers_c = {"Authorization": f"Bearer {create_access_token(uid_c)}"}

        # 3. Newly registered User C starts with empty conversation list
        res_c_init = await ac.get("/api/v1/conversations", headers=headers_c)
        assert res_c_init.status_code == 200
        assert len(res_c_init.json()) == 0, "New account C must start with 0 conversations"

        # 4. User A creates private conversation with User B
        res_create = await ac.post("/api/v1/conversations", headers=headers_a, json={
            "type": "direct",
            "participantId": uid_b,
            "name": "Bob B"
        })
        assert res_create.status_code == 200
        conv_ab_id = res_create.json()["id"]

        # 5. User A sends a message in conv_ab
        res_send = await ac.post(f"/api/v1/conversations/{conv_ab_id}/messages", headers=headers_a, json={
            "text": "Private message between A and B",
            "type": "text"
        })
        assert res_send.status_code == 200
        msg_id = res_send.json()["id"]

        # 6. User B can view messages
        res_b_msgs = await ac.get(f"/api/v1/conversations/{conv_ab_id}/messages", headers=headers_b)
        assert res_b_msgs.status_code == 200
        assert any(m["id"] == msg_id for m in res_b_msgs.json())

        # 7. User C CANNOT access or spy on A&B messages (Must return 403 Forbidden)
        res_c_leak = await ac.get(f"/api/v1/conversations/{conv_ab_id}/messages", headers=headers_c)
        assert res_c_leak.status_code == 403, "Non-participant must receive 403 Forbidden when fetching messages"

        # 8. User C CANNOT send a message into A&B conversation (Must return 403 Forbidden)
        res_c_send = await ac.post(f"/api/v1/conversations/{conv_ab_id}/messages", headers=headers_c, json={
            "text": "Intruder message",
            "type": "text"
        })
        assert res_c_send.status_code == 403, "Non-participant must receive 403 Forbidden when sending messages"

        # 9. User B CANNOT edit User A's message (enforces message sender ownership)
        res_b_edit = await ac.patch(f"/api/v1/messages/{msg_id}", headers=headers_b, json={
            "text": "Forged edit"
        })
        assert res_b_edit.status_code == 403, "Only the author may edit a message"

        # 10. User C CANNOT delete User A's message
        res_c_del = await ac.delete(f"/api/v1/messages/{msg_id}", headers=headers_c)
        assert res_c_del.status_code == 403, "Non-author must receive 403 Forbidden on delete"

        # 11. When User A messages User C, C sees ONLY that conversation
        res_ac = await ac.post("/api/v1/conversations", headers=headers_a, json={
            "type": "direct",
            "participantId": uid_c,
            "name": "Charlie C"
        })
        assert res_ac.status_code == 200
        conv_ac_id = res_ac.json()["id"]

        res_c_list = await ac.get("/api/v1/conversations", headers=headers_c)
        assert res_c_list.status_code == 200
        conv_ids = [c["id"] for c in res_c_list.json()]
        assert conv_ids == [conv_ac_id], "User C must only see their conversation with A"
        assert conv_ab_id not in conv_ids, "User C must never see A and B's conversation"

        # 12. Selecting/creating conversation with B again reuses existing conversation (deduplication)
        res_ab_dupe = await ac.post("/api/v1/conversations", headers=headers_a, json={
            "type": "direct",
            "participantId": uid_b,
            "name": "Bob B"
        })
        assert res_ab_dupe.status_code == 200
        assert res_ab_dupe.json()["id"] == conv_ab_id, "Re-creating direct conversation must return existing conversation ID"

        # Also from B to A simultaneously
        res_ba_dupe = await ac.post("/api/v1/conversations", headers=headers_b, json={
            "type": "direct",
            "participantId": uid_a,
            "name": "Alice A"
        })
        assert res_ba_dupe.status_code == 200
        assert res_ba_dupe.json()["id"] == conv_ab_id, "B contacting A must resolve to the identical conversation ID"

        # 13. Contacts isolation: A saves B with a private nickname
        res_add_contact = await ac.post("/api/v1/users/contacts", headers=headers_a, json={
            "contactId": uid_b,
            "name": "My Best Buddy Bob",
            "label": "VIP Partner"
        })
        assert res_add_contact.status_code == 200

        # A sees Bob in contacts with private nickname
        res_a_contacts = await ac.get("/api/v1/users/contacts", headers=headers_a)
        assert res_a_contacts.status_code == 200
        assert any(c["id"] == uid_b and c["name"] == "My Best Buddy Bob" for c in res_a_contacts.json())

        # C's contacts must remain 0 (contacts are not shared across accounts)
        res_c_contacts = await ac.get("/api/v1/users/contacts", headers=headers_c)
        assert res_c_contacts.status_code == 200
        assert len(res_c_contacts.json()) == 0, "User C must not see User A's private contacts"

        # 14. Discovery search: search finds public profile without exposing conversations
        res_search = await ac.get(f"/api/v1/users/search?q={uid_b}", headers=headers_c)
        assert res_search.status_code == 200
        search_data = res_search.json()
        assert any(u["id"] == uid_b for u in search_data)
        for u in search_data:
            assert "messages" not in u
            assert "conversations" not in u

        # 15. Blocking: A blocks B, message sending is rejected
        res_block = await ac.patch(f"/api/v1/users/contacts/{uid_b}", headers=headers_a, json={
            "isBlocked": True
        })
        assert res_block.status_code == 200

        res_send_blocked = await ac.post(f"/api/v1/conversations/{conv_ab_id}/messages", headers=headers_b, json={
            "text": "Blocked attempt",
            "type": "text"
        })
        assert res_send_blocked.status_code == 403, "Sending message to/from a blocked contact must return 403"
