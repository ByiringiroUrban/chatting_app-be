from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User, Contact
from app.models.conversation import Conversation, ConversationParticipant
from app.models.message import Message
from app.models.group import Group
from app.models.status import StatusStory
from app.models.channel import Channel
from app.models.business import BusinessProfile, Product, CustomerTicket, BusinessAnalytics
from app.models.call import CallLog
from app.models.ad import AdCampaign
from app.models.subscription import SubscriptionPlan, BillingInvoice
from app.core.security import hash_password

async def seed_all_data(db: AsyncSession):
    """Checks if database is empty and seeds initial Rwandan platform dataset"""
    existing_user = await db.execute(select(User).limit(1))
    if existing_user.scalar_one_or_none():
        print("[Muraho Seeder] Database already populated. Skipping seed.")
        return

    print("[Muraho Seeder] Seeding database with initial Rwandan platform data...")
    default_pw_hash = hash_password("muraho123")

    # 1. Users
    users_data = [
        User(
            id="user_me",
            name="Jean-Luc Mugisha",
            username="jeanluc_m",
            email="jeanluc@muraho.rw",
            phone="+250 788 456 789",
            hashed_password=default_pw_hash,
            avatar="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80",
            bio="Building impactful software in Kigali 🇷🇼 | Tech enthusiast & Founder",
            status="online",
            role="business_admin",
            is_business=True,
            business_id="biz_kigali_tech",
            joined_date="January 2024",
            settings={
                "lastSeen": "everyone",
                "readReceipts": True,
                "theme": "light",
                "accentColor": "#0F766E",
                "language": "en",
                "notifications": True
            }
        ),
        User(
            id="user_1",
            name="Aline Uwase",
            username="aline_u",
            email="aline.uwase@example.rw",
            phone="+250 788 112 233",
            hashed_password=default_pw_hash,
            avatar="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=300&q=80",
            bio="Product Designer @ InnovateRwanda 🎨",
            status="online",
            role="user",
            is_business=False
        ),
        User(
            id="user_2",
            name="David Nkurunziza",
            username="david_nk",
            email="david.nk@fintech.rw",
            phone="+250 783 445 566",
            hashed_password=default_pw_hash,
            avatar="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=300&q=80",
            bio="Fintech solutions architect & open source contributor 💻",
            status="offline",
            role="user",
            is_business=False
        ),
        User(
            id="user_3",
            name="Diane Mutoni",
            username="diane_m",
            email="mutoni.diane@agrihub.rw",
            phone="+250 789 778 899",
            hashed_password=default_pw_hash,
            avatar="https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?auto=format&fit=crop&w=300&q=80",
            bio="AgriTech entrepreneur & community builder 🌾",
            status="online",
            role="user",
            is_business=False
        ),
        User(
            id="user_4",
            name="Patrick Habimana",
            username="patrick_h",
            email="patrick.h@cloudsolutions.com",
            phone="+250 785 334 455",
            hashed_password=default_pw_hash,
            avatar="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=300&q=80",
            bio="DevOps Engineer | Cloud Native & Kubernetes",
            status="offline",
            role="user",
            is_business=False
        ),
        User(
            id="user_5",
            name="Sonia Keza",
            username="sonia_k",
            email="keza.sonia@creative.rw",
            phone="+250 782 990 011",
            hashed_password=default_pw_hash,
            avatar="https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=300&q=80",
            bio="Marketing Director at Kigali Pulse Media 📱",
            status="online",
            role="user",
            is_business=False
        ),
        User(
            id="user_6",
            name="Eric Manzi",
            username="eric_m",
            email="eric.manzi@ai-research.rw",
            phone="+250 781 223 344",
            hashed_password=default_pw_hash,
            avatar="https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?auto=format&fit=crop&w=300&q=80",
            bio="AI Researcher working on NLP for African languages",
            status="offline",
            role="user",
            is_business=False
        )
    ]
    for u in users_data:
        db.add(u)

    # 2. Contacts for user_me
    contacts_data = [
        Contact(
            id="cnt_user_me_1",
            user_id="user_me",
            contact_id="user_1",
            name="Aline Uwase",
            username="aline_u",
            phone="+250 788 112 233",
            email="aline.uwase@example.rw",
            avatar="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=300&q=80",
            bio="Product Designer @ InnovateRwanda 🎨",
            status="online",
            last_seen="Just now",
            is_favorite=True,
            label="Lead Designer"
        ),
        Contact(
            id="cnt_user_me_2",
            user_id="user_me",
            contact_id="user_2",
            name="David Nkurunziza",
            username="david_nk",
            phone="+250 783 445 566",
            email="david.nk@fintech.rw",
            avatar="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=300&q=80",
            bio="Fintech solutions architect & open source contributor 💻",
            status="offline",
            last_seen="15m ago",
            is_favorite=True,
            label="VIP Client"
        ),
        Contact(
            id="cnt_user_me_3",
            user_id="user_me",
            contact_id="user_3",
            name="Diane Mutoni",
            username="diane_m",
            phone="+250 789 778 899",
            email="mutoni.diane@agrihub.rw",
            avatar="https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?auto=format&fit=crop&w=300&q=80",
            bio="AgriTech entrepreneur & community builder 🌾",
            status="online",
            last_seen="Online",
            is_favorite=False,
            label="Partner"
        ),
        Contact(
            id="cnt_user_me_4",
            user_id="user_me",
            contact_id="user_4",
            name="Patrick Habimana",
            username="patrick_h",
            phone="+250 785 334 455",
            email="patrick.h@cloudsolutions.com",
            avatar="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=300&q=80",
            bio="DevOps Engineer | Cloud Native & Kubernetes",
            status="offline",
            last_seen="2 hours ago",
            is_favorite=False,
            label="Contractor"
        ),
        Contact(
            id="cnt_user_me_5",
            user_id="user_me",
            contact_id="user_5",
            name="Sonia Keza",
            username="sonia_k",
            phone="+250 782 990 011",
            email="keza.sonia@creative.rw",
            avatar="https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=300&q=80",
            bio="Marketing Director at Kigali Pulse Media 📱",
            status="online",
            last_seen="Online",
            is_favorite=True,
            label="Marketing"
        ),
        Contact(
            id="cnt_user_me_6",
            user_id="user_me",
            contact_id="user_6",
            name="Eric Manzi",
            username="eric_m",
            phone="+250 781 223 344",
            email="eric.manzi@ai-research.rw",
            avatar="https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?auto=format&fit=crop&w=300&q=80",
            bio="AI Researcher working on NLP for African languages",
            status="offline",
            last_seen="Yesterday at 18:30",
            is_favorite=False,
            label="Researcher"
        )
    ]
    for c in contacts_data:
        db.add(c)

    # 3. Conversations
    convs_data = [
        Conversation(
            id="conv_1",
            type="direct",
            participant_id="user_1",
            name="Aline Uwase",
            avatar="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=300&q=80",
            is_pinned=True,
            is_muted=False,
            unread_count=2,
            tags=["Work", "Design"]
        ),
        Conversation(
            id="conv_2",
            type="group",
            group_id="group_1",
            name="Software Developers Rwanda",
            avatar="https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=300&q=80",
            member_count=142,
            is_pinned=True,
            is_muted=False,
            unread_count=5,
            tags=["Community", "Tech"]
        ),
        Conversation(
            id="conv_3",
            type="direct",
            participant_id="user_2",
            name="David Nkurunziza",
            avatar="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=300&q=80",
            is_pinned=False,
            is_muted=False,
            unread_count=0,
            tags=["Fintech", "VIP"]
        ),
        Conversation(
            id="conv_4",
            type="group",
            group_id="group_2",
            name="AI & Machine Learning Rwanda",
            avatar="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=300&q=80",
            member_count=88,
            is_pinned=False,
            is_muted=True,
            unread_count=0,
            tags=["AI", "Research"]
        ),
        Conversation(
            id="conv_5",
            type="direct",
            participant_id="user_3",
            name="Diane Mutoni",
            avatar="https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?auto=format&fit=crop&w=300&q=80",
            is_pinned=False,
            is_muted=False,
            unread_count=0,
            tags=["AgriTech"]
        ),
        Conversation(
            id="conv_6",
            type="direct",
            participant_id="user_5",
            name="Sonia Keza",
            avatar="https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=300&q=80",
            is_pinned=False,
            is_muted=False,
            unread_count=0,
            tags=["Marketing"]
        )
    ]
    for cv in convs_data:
        db.add(cv)

    # Conversation participants linking
    participants_seed = [
        # conv_1: Jean-Luc (user_me) & Aline (user_1)
        ConversationParticipant(id="cp_1_me", conversation_id="conv_1", user_id="user_me", role="member"),
        ConversationParticipant(id="cp_1_u1", conversation_id="conv_1", user_id="user_1", role="member"),
        # conv_2: Group 1 (Software Developers Rwanda)
        ConversationParticipant(id="cp_2_me", conversation_id="conv_2", user_id="user_me", role="admin"),
        ConversationParticipant(id="cp_2_u1", conversation_id="conv_2", user_id="user_1", role="admin"),
        ConversationParticipant(id="cp_2_u2", conversation_id="conv_2", user_id="user_2", role="member"),
        ConversationParticipant(id="cp_2_u4", conversation_id="conv_2", user_id="user_4", role="member"),
        ConversationParticipant(id="cp_2_u6", conversation_id="conv_2", user_id="user_6", role="member"),
        # conv_3: Jean-Luc (user_me) & David (user_2)
        ConversationParticipant(id="cp_3_me", conversation_id="conv_3", user_id="user_me", role="member"),
        ConversationParticipant(id="cp_3_u2", conversation_id="conv_3", user_id="user_2", role="member"),
        # conv_4: Group 2 (AI & Machine Learning Rwanda)
        ConversationParticipant(id="cp_4_u6", conversation_id="conv_4", user_id="user_6", role="admin"),
        ConversationParticipant(id="cp_4_me", conversation_id="conv_4", user_id="user_me", role="member"),
        ConversationParticipant(id="cp_4_u4", conversation_id="conv_4", user_id="user_4", role="member"),
        # conv_5: Jean-Luc (user_me) & Diane (user_3)
        ConversationParticipant(id="cp_5_me", conversation_id="conv_5", user_id="user_me", role="member"),
        ConversationParticipant(id="cp_5_u3", conversation_id="conv_5", user_id="user_3", role="member"),
        # conv_6: Jean-Luc (user_me) & Sonia (user_5)
        ConversationParticipant(id="cp_6_me", conversation_id="conv_6", user_id="user_me", role="member"),
        ConversationParticipant(id="cp_6_u5", conversation_id="conv_6", user_id="user_5", role="member"),
    ]
    for cp in participants_seed:
        db.add(cp)

    # 4. Messages
    msgs_data = [
        Message(
            id="m_1_1",
            conversation_id="conv_1",
            sender_id="user_me",
            sender_name="Jean-Luc Mugisha",
            text="Mwaramutse Aline! Did you get a chance to review the new responsive navigation mockup?",
            timestamp="10:15 AM",
            date="Today",
            status="read",
            type="text",
            reactions=[{"emoji": "👋", "count": 1, "users": ["user_1"]}]
        ),
        Message(
            id="m_1_2",
            conversation_id="conv_1",
            sender_id="user_1",
            sender_name="Aline Uwase",
            text="Yego Jean-Luc! Yes, I love the clean teal branding and the three-panel desktop layout. Here is the updated component screenshot for the dark mode cards:",
            timestamp="10:20 AM",
            date="Today",
            status="read",
            type="image",
            media_url="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=800&q=80",
            caption="Brand palette tokens & dark mode card elevation",
            reactions=[{"emoji": "🔥", "count": 2, "users": ["user_me", "user_1"]}]
        ),
        Message(
            id="m_1_3",
            conversation_id="conv_1",
            sender_id="user_me",
            sender_name="Jean-Luc Mugisha",
            reply_to={"id": "m_1_2", "senderName": "Aline Uwase", "text": "Brand palette tokens & dark mode card elevation"},
            text="This contrast ratio is phenomenal! It will feel super comfortable in low light.",
            timestamp="10:28 AM",
            date="Today",
            status="read",
            type="text",
            reactions=[{"emoji": "❤️", "count": 1, "users": ["user_1"]}]
        ),
        Message(
            id="m_1_4",
            conversation_id="conv_1",
            sender_id="user_1",
            sender_name="Aline Uwase",
            text="Voice note regarding the micro-interaction timings",
            timestamp="10:36 AM",
            date="Today",
            status="read",
            type="audio",
            duration="0:24",
            media_url="https://actions.google.com/sounds/v1/water/rain_heavy.ogg",
            reactions=[{"emoji": "👍", "count": 1, "users": ["user_me"]}]
        ),
        Message(
            id="m_1_5",
            conversation_id="conv_1",
            sender_id="user_1",
            sender_name="Aline Uwase",
            text="I sent over the revised design system tokens for the mobile view! Let me know what you think.",
            timestamp="10:42 AM",
            date="Today",
            status="read",
            type="text",
            reactions=[]
        ),
        Message(
            id="m_grp1_1",
            conversation_id="conv_2",
            sender_id="user_4",
            sender_name="Patrick Habimana",
            text="Morning devs! Quick reminder to migrate your Vite plugins to the latest major version if you encountered peer dependency warnings.",
            timestamp="09:12 AM",
            date="Today",
            status="read",
            type="text",
            reactions=[{"emoji": "🚀", "count": 5, "users": ["user_me", "user_1", "user_6"]}]
        ),
        Message(
            id="m_grp1_2",
            conversation_id="conv_2",
            sender_id="user_6",
            sender_name="Eric Manzi",
            text="Who is attending the Kigali Tech Summit next Friday at BK Arena? 🇷🇼",
            timestamp="10:35 AM",
            date="Today",
            status="delivered",
            type="text",
            reactions=[{"emoji": "🇷🇼", "count": 8, "users": ["user_me", "user_2"]}]
        ),
        Message(
            id="m_2_1",
            conversation_id="conv_3",
            sender_id="user_me",
            sender_name="Jean-Luc Mugisha",
            text="Voice note sent (0:38)",
            timestamp="Yesterday",
            date="Yesterday",
            status="read",
            type="audio",
            duration="0:38",
            reactions=[]
        )
    ]
    for m in msgs_data:
        db.add(m)

    # 5. Groups
    groups_data = [
        Group(
            id="group_1",
            name="Software Developers Rwanda",
            avatar="https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=300&q=80",
            description="The official engineering community for Rwandan software developers, tech architects, and innovators.",
            created_at="2023-05-10",
            members=[
                {"id": "user_me", "name": "Jean-Luc Mugisha", "role": "admin", "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80"},
                {"id": "user_1", "name": "Aline Uwase", "role": "admin", "avatar": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=300&q=80"},
                {"id": "user_2", "name": "David Nkurunziza", "role": "member", "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=300&q=80"},
                {"id": "user_4", "name": "Patrick Habimana", "role": "member", "avatar": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=300&q=80"},
                {"id": "user_6", "name": "Eric Manzi", "role": "member", "avatar": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?auto=format&fit=crop&w=300&q=80"}
            ],
            settings={"onlyAdminsCanPost": False, "approveNewMembers": True, "allowMediaSharing": True}
        ),
        Group(
            id="group_2",
            name="AI & Machine Learning Rwanda",
            avatar="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=300&q=80",
            description="Deep learning, NLP, computer vision and African language AI models research group.",
            created_at="2023-08-15",
            members=[
                {"id": "user_6", "name": "Eric Manzi", "role": "admin", "avatar": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?auto=format&fit=crop&w=300&q=80"},
                {"id": "user_me", "name": "Jean-Luc Mugisha", "role": "member", "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80"},
                {"id": "user_4", "name": "Patrick Habimana", "role": "member", "avatar": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=300&q=80"}
            ],
            settings={"onlyAdminsCanPost": False, "approveNewMembers": False, "allowMediaSharing": True}
        )
    ]
    for g in groups_data:
        db.add(g)

    # 6. Statuses
    statuses_data = [
        StatusStory(
            id="status_me",
            user_id="user_me",
            user_name="My Status",
            user_avatar="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80",
            is_me=True,
            has_unseen=False,
            timestamp="32m ago",
            items=[
                {
                    "id": "item_me_1",
                    "type": "image",
                    "mediaUrl": "https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?auto=format&fit=crop&w=800&q=80",
                    "caption": "Demo day rehearsal at Norrsken Kigali! Excited to reveal our roadmap. 🚀🇷🇼",
                    "timestamp": "32 minutes ago",
                    "views": 48,
                    "viewers": ["Aline Uwase", "David Nkurunziza", "Diane Mutoni", "Patrick Habimana", "Eric Manzi"]
                }
            ]
        ),
        StatusStory(
            id="status_1",
            user_id="user_1",
            user_name="Aline Uwase",
            user_avatar="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=300&q=80",
            is_me=False,
            has_unseen=True,
            timestamp="12m ago",
            items=[
                {
                    "id": "item_1_1",
                    "type": "text",
                    "backgroundColor": "from-teal-600 to-emerald-800",
                    "text": "“Design is not just what it looks like and feels like. Design is how it works.” — Steve Jobs ✨",
                    "timestamp": "12 minutes ago",
                    "views": 29
                }
            ]
        )
    ]
    for s in statuses_data:
        db.add(s)

    # 7. Channels
    channels_data = [
        Channel(
            id="channel_1",
            name="Rwanda Tech Community",
            handle="@rwanda_tech",
            avatar="https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=300&q=80",
            category="Technology",
            description="Official channel for Rwanda's engineering ecosystem. Hackathons, tech job openings, developer events, and local innovations.",
            subscribers=14250,
            is_subscribed=True,
            is_verified=True,
            is_premium=False,
            posts=[
                {
                    "id": "post_1_1",
                    "title": "Kigali Global Tech Hub Expo 2024 Registration Open",
                    "content": "Join over 2,500 software engineers, researchers, and venture capitalists at the BK Arena for three days of keynotes, hackathons, and product launches.",
                    "mediaUrl": "https://images.unsplash.com/photo-1540575467063-178a50c2df87?auto=format&fit=crop&w=800&q=80",
                    "timestamp": "2 hours ago",
                    "views": "4.8K",
                    "reactions": [{"emoji": "🔥", "count": 142}, {"emoji": "🚀", "count": 89}]
                }
            ]
        ),
        Channel(
            id="channel_2",
            name="AI & Future Intelligence News",
            handle="@ainews_rw",
            avatar="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=300&q=80",
            category="AI & Innovation",
            description="Breaking artificial intelligence research, machine learning tooling, open models, and frontier computing benchmarks.",
            subscribers=8920,
            is_subscribed=True,
            is_verified=True,
            is_premium=False,
            posts=[
                {
                    "id": "post_2_1",
                    "title": "Multilingual LLM trained on 15 African languages open-sourced",
                    "content": "Researchers have published new checkpoints with state-of-the-art tokenization efficiency for Kinyarwanda, Swahili, and Luganda.",
                    "timestamp": "5 hours ago",
                    "views": "3.1K",
                    "reactions": [{"emoji": "🧠", "count": 98}, {"emoji": "🎉", "count": 114}]
                }
            ]
        )
    ]
    for ch in channels_data:
        db.add(ch)

    # 8. Business Suite & Products (RWF Currency)
    biz_profile = BusinessProfile(
        id="biz_kigali_tech",
        user_id="user_me",
        name="Kigali Tech Innovations & Artisans Ltd",
        logo="https://images.unsplash.com/photo-1572021335469-31706a17aaef?auto=format&fit=crop&w=300&q=80",
        category="Software & Local Artisan Commerce",
        description="Bridging Rwandan handcrafted excellence and modern digital products. Serving domestic and international customers.",
        email="support@kigalitech.rw",
        phone="+250 788 456 789",
        website="https://kigalitech.rw",
        location="Norrsken House Kigali, 1 KN 78 St, Kiyovu",
        working_hours="Monday – Friday: 08:00 AM – 06:00 PM CAT",
        social_links={"twitter": "@kigalitech_rw", "instagram": "@kigalitechartisans"},
        greeting_message="Muraho! Welcome to Kigali Tech Innovations & Artisans. How can we help you today?",
        greeting_enabled=True,
        away_message="Muraho! We are currently away from the desk. Our team will get back to you promptly at 8:00 AM.",
        away_enabled=True,
        quick_replies=[
            {"id": "qr_1", "shortcut": "/pricing", "title": "Product Pricing", "text": "You can view our complete product catalog and real-time prices right here in the chat menu or at kigalitech.rw/catalog."},
            {"id": "qr_2", "shortcut": "/delivery", "title": "Delivery Info", "text": "We offer same-day express delivery in Kigali (2,000 RWF) and 24h delivery across all provinces in Rwanda (4,000 RWF)."},
            {"id": "qr_3", "shortcut": "/momo", "title": "MoMo Pay Code", "text": "To pay via MTN Mobile Money, dial *182*8*1*123456# (Kigali Tech Ltd). Thank you!"}
        ],
        ai_support={
            "enabled": True,
            "confidenceThreshold": 0.85,
            "autoHandoffToHuman": True,
            "faqs": [
                {"id": "faq_1", "question": "What payment methods do you accept?", "answer": "We accept MTN Mobile Money, Airtel Money, Bank Transfer (Bank of Kigali, I&M Bank), and international Visa/Mastercard."},
                {"id": "faq_2", "question": "How long does shipping take within Rwanda?", "answer": "Within Kigali, orders placed before 3:00 PM are delivered same-day. Upcountry deliveries arrive within 24 hours."},
                {"id": "faq_3", "question": "Can I customize the Agaseke baskets or leather goods?", "answer": "Yes! Custom colors, dimensions, and corporate branded embossing are available for orders over 10 pieces."},
                {"id": "faq_4", "question": "How do I get a custom software MVP quote?", "answer": "Our software sprint starts at 650,000 RWF. Send us your requirements document or schedule a 15-minute call with Jean-Luc."}
            ]
        }
    )
    db.add(biz_profile)

    products_data = [
        Product(
            id="prod_1",
            name="Single-Origin Bourbon Arabica Coffee (500g)",
            category="Food & Beverage",
            price=12500,
            currency="RWF",
            stock=85,
            status="in_stock",
            image="https://images.unsplash.com/photo-1559056199-641a0ac8b55e?auto=format&fit=crop&w=600&q=80",
            description="Washed Arabica beans grown in Huye high-altitude volcanic soil. Notes of dark chocolate, berry, and caramel.",
            sales_count=142
        ),
        Product(
            id="prod_2",
            name="Handwoven Traditional Agaseke Peace Basket",
            category="Handicrafts & Art",
            price=28000,
            currency="RWF",
            stock=24,
            status="in_stock",
            image="https://images.unsplash.com/photo-1590736969955-71cc94801759?auto=format&fit=crop&w=600&q=80",
            description="Authentic handcrafted sisal fiber and sweetgrass basket made by artisan women cooperatives in Nyanza.",
            sales_count=68
        ),
        Product(
            id="prod_3",
            name="Web & Mobile App MVP Sprint (2 Weeks)",
            category="Digital Services",
            price=650000,
            currency="RWF",
            stock=5,
            status="in_stock",
            image="https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=600&q=80",
            description="Turn your concept into a live interactive prototype with React, Node, and responsive UX design.",
            sales_count=12
        ),
        Product(
            id="prod_4",
            name="Organic Virunga Highland Black Tea (250g)",
            category="Food & Beverage",
            price=7500,
            currency="RWF",
            stock=120,
            status="in_stock",
            image="https://images.unsplash.com/photo-1576092768241-dec231879fc3?auto=format&fit=crop&w=600&q=80",
            description="Rich, aromatic orthodox black tea leaves harvested from the misty slopes of the Virunga mountains.",
            sales_count=215
        ),
        Product(
            id="prod_5",
            name="Kigali Tech Summit VIP Delegate Pass",
            category="Events & Tickets",
            price=35000,
            currency="RWF",
            stock=40,
            status="in_stock",
            image="https://images.unsplash.com/photo-1540575467063-178a50c2df87?auto=format&fit=crop&w=600&q=80",
            description="Access to all keynotes, VIP networking lounge, investor speed-dating, and after-party at Norrsken House.",
            sales_count=310
        ),
        Product(
            id="prod_6",
            name="Handcrafted Rwandan Full-Grain Leather Sleeve",
            category="Accessories",
            price=42000,
            currency="RWF",
            stock=18,
            status="in_stock",
            image="https://images.unsplash.com/photo-1544816155-12df9643f363?auto=format&fit=crop&w=600&q=80",
            description="Vegetable-tanned leather sleeve tailored for 13-inch and 15-inch MacBooks with brass hardware.",
            sales_count=45
        )
    ]
    for p in products_data:
        db.add(p)

    tickets_data = [
        CustomerTicket(
            id="cust_1",
            customer_name="Aline Uwase",
            customer_phone="+250 788 112 233",
            customer_avatar="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=300&q=80",
            issue_summary="Inquiry about custom corporate branding for 50 Agaseke baskets",
            last_message="Muraho! Can we emboss our company emblem in bronze on the lid?",
            timestamp="12m ago",
            status="Open",
            priority="High",
            channel="Chat",
            notes=["Oct 15: Client requested sample mockup before full deposit."],
            unread=True
        ),
        CustomerTicket(
            id="cust_2",
            customer_name="David Nkurunziza",
            customer_phone="+250 783 445 566",
            customer_avatar="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=300&q=80",
            issue_summary="Payment verification for MVP Sprint milestone #1",
            last_message="MoMo confirmation ID: MP241014.8829. Sent 325,000 RWF.",
            timestamp="1h ago",
            status="Pending",
            priority="Normal",
            channel="MoMo Support",
            notes=["Oct 14: Confirmed with finance. Receipt sent to client."],
            unread=False
        )
    ]
    for tk in tickets_data:
        db.add(tk)

    biz_analytics = BusinessAnalytics(
        id="biz_analytics_1",
        business_id="biz_kigali_tech",
        total_messages=1420,
        response_rate="98.4%",
        avg_response_time="1.8m",
        active_customers=380,
        revenue_rwf=4850000,
        daily_conversations=[
            {"day": "Mon", "count": 180},
            {"day": "Tue", "count": 220},
            {"day": "Wed", "count": 290},
            {"day": "Thu", "count": 240},
            {"day": "Fri", "count": 310},
            {"day": "Sat", "count": 190},
            {"day": "Sun", "count": 140}
        ],
        channel_breakdown=[
            {"name": "Direct Chat", "value": 65},
            {"name": "Catalog Share", "value": 20},
            {"name": "MoMo Pay Link", "value": 15}
        ],
        satisfaction_rate="4.9/5"
    )
    db.add(biz_analytics)

    # 9. Call History
    calls_data = [
        CallLog(
            id="call_1",
            contact_id="user_1",
            name="Aline Uwase",
            avatar="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=300&q=80",
            type="video",
            direction="incoming",
            status="completed",
            timestamp="Today, 09:20 AM",
            duration="14m 22s"
        ),
        CallLog(
            id="call_2",
            contact_id="user_2",
            name="David Nkurunziza",
            avatar="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=300&q=80",
            type="voice",
            direction="missed",
            status="missed",
            timestamp="Yesterday, 04:15 PM",
            duration="0s"
        )
    ]
    for cl in calls_data:
        db.add(cl)

    # 10. Ads
    ads_data = [
        AdCampaign(
            id="ad_1",
            title="Specialty Bourbon Coffee Launch — Free Delivery in Kigali",
            description="Promoting freshly roasted 500g Arabica coffee bags to coffee enthusiasts and offices in Kigali.",
            audience="Tech & Office Workers in Kigali (Ages 22-55)",
            budget_rwf=150000,
            spent_rwf=112500,
            start_date="2024-10-01",
            end_date="2024-10-20",
            status="Active",
            creative_url="https://images.unsplash.com/photo-1559056199-641a0ac8b55e?auto=format&fit=crop&w=600&q=80",
            impressions=48200,
            clicks=3410,
            ctr="7.07%",
            conversions=215,
            cpc_rwf=33
        )
    ]
    for ad in ads_data:
        db.add(ad)

    # 11. Plans & Invoices
    plans_data = [
        SubscriptionPlan(
            id="plan_free",
            name="Personal",
            tagline="Everyday free messaging for individuals and communities.",
            price_monthly=0,
            price_yearly=0,
            badge="Free Forever",
            highlight=False,
            features=[
                "Individual unlimited messaging",
                "Group chats up to 256 members",
                "HD voice & video calling interface",
                "Voice notes & media attachments up to 25MB",
                "Access to public public channels & statuses",
                "Dark and light sleek themes"
            ],
            button_text="Current Plan"
        ),
        SubscriptionPlan(
            id="plan_premium",
            name="Muraho Premium",
            tagline="For power users, creators, and professionals needing extra polish.",
            price_monthly=3000,
            price_yearly=28800,
            badge="Popular Personal",
            highlight=False,
            features=[
                "All Personal Plan features",
                "Cloud storage boost up to 100GB (UI)",
                "Exclusive animated profile badges",
                "Access to paid premium channels",
                "Custom themes & custom chat wallpapers",
                "Pin up to 20 chats simultaneously"
            ],
            button_text="Upgrade to Premium"
        ),
        SubscriptionPlan(
            id="plan_business",
            name="Business Starter",
            tagline="Everything you need to sell, respond, and engage customers seamlessly.",
            price_monthly=15000,
            price_yearly=144000,
            badge="Most Popular for SMEs",
            highlight=True,
            features=[
                "Official Verified Business profile badge",
                "Dedicated Customer Inbox with status tags",
                "Product Catalog with in-chat ordering",
                "Automated greeting & away responses",
                "Quick reply shortcuts (/pricing, /momo)",
                "Real-time analytics dashboard & reports"
            ],
            button_text="Get Business Starter"
        ),
        SubscriptionPlan(
            id="plan_business_ai",
            name="Business AI Suite",
            tagline="Supercharge your business with 24/7 AI-driven customer support.",
            price_monthly=30000,
            price_yearly=288000,
            badge="Full Automation",
            highlight=False,
            features=[
                "All Business Starter features included",
                "24/7 AI Customer Support auto-responder",
                "Custom Business Knowledge Base & FAQs",
                "AI composer: rewrite, translate, fix grammar",
                "Instant conversation summarization",
                "Smart human handoff triggers"
            ],
            button_text="Activate Business AI"
        )
    ]
    for pl in plans_data:
        db.add(pl)

    invoices_data = [
        BillingInvoice(
            id="inv_2024_09",
            user_id="user_me",
            invoice_number="INV-2024-0091",
            date="Sep 01, 2024",
            description="Business Starter — Monthly Subscription",
            amount="15,000 RWF",
            status="Paid",
            payment_method="MTN MoMo (*182#)"
        ),
        BillingInvoice(
            id="inv_2024_08",
            user_id="user_me",
            invoice_number="INV-2024-0082",
            date="Aug 01, 2024",
            description="Business Starter — Monthly Subscription",
            amount="15,000 RWF",
            status="Paid",
            payment_method="MTN MoMo (*182#)"
        )
    ]
    for inv in invoices_data:
        db.add(inv)

    await db.commit()
    print("[Muraho Seeder] Database successfully populated with initial data.")
