from typing import Optional, List, Any, Dict
from pydantic import BaseModel, EmailStr, Field

# ----------------- AUTH & USER SCHEMAS -----------------

class RegisterRequest(BaseModel):
    fullName: str
    username: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = "password123"
    avatar: Optional[str] = None
    bio: Optional[str] = None

class LoginRequest(BaseModel):
    emailOrPhone: str
    password: str
    rememberMe: Optional[bool] = False

class SendOtpRequest(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    fullName: Optional[str] = "Friend"

class VerifyOtpRequest(BaseModel):
    otpCode: str
    email: Optional[str] = None
    phone: Optional[str] = None

class ResetPasswordRequest(BaseModel):
    emailOrPhone: str

class ResetPasswordConfirmRequest(BaseModel):
    emailOrPhone: str
    otpCode: str
    newPassword: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

class UserResponse(BaseModel):
    id: str
    name: str
    username: str
    email: str
    phone: Optional[str] = None
    avatar: Optional[str] = None
    bio: Optional[str] = None
    status: Optional[str] = "online"
    role: Optional[str] = "user"
    isBusiness: Optional[bool] = False
    businessId: Optional[str] = None
    joinedDate: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None

class UserUpdateRequest(BaseModel):
    name: Optional[str] = None
    username: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None

class ContactResponse(BaseModel):
    id: str
    name: str
    username: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    avatar: Optional[str] = None
    bio: Optional[str] = None
    status: Optional[str] = "offline"
    lastSeen: Optional[str] = "Recently"
    isFavorite: Optional[bool] = False
    isBlocked: Optional[bool] = False
    label: Optional[str] = None

class ContactCreateRequest(BaseModel):
    contactId: str
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    label: Optional[str] = None

class ContactUpdateRequest(BaseModel):
    name: Optional[str] = None
    label: Optional[str] = None
    isFavorite: Optional[bool] = None
    isBlocked: Optional[bool] = None

# ----------------- MESSAGE SCHEMAS -----------------

class ReactionItem(BaseModel):
    emoji: str
    count: int = 1
    users: List[str] = []

class ReplyToItem(BaseModel):
    id: str
    senderName: str
    text: str

class MessageSendRequest(BaseModel):
    conversationId: Optional[str] = None
    text: Optional[str] = None
    type: str = "text" # 'text', 'image', 'audio', 'document'
    mediaUrl: Optional[str] = None
    fileName: Optional[str] = None
    fileSize: Optional[str] = None
    duration: Optional[str] = None
    caption: Optional[str] = None
    replyTo: Optional[ReplyToItem] = None

class MessageEditRequest(BaseModel):
    text: str

class ReactionRequest(BaseModel):
    emoji: str

class ForwardRequest(BaseModel):
    targetChatId: str

class MessageResponse(BaseModel):
    id: str
    conversationId: str
    senderId: str
    senderName: Optional[str] = None
    senderAvatar: Optional[str] = None
    text: Optional[str] = None
    timestamp: Optional[str] = None
    date: Optional[str] = "Today"
    status: Optional[str] = "sent"
    type: str = "text"
    mediaUrl: Optional[str] = None
    fileName: Optional[str] = None
    fileSize: Optional[str] = None
    duration: Optional[str] = None
    caption: Optional[str] = None
    isPinned: Optional[bool] = False
    isEdited: Optional[bool] = False
    isForwarded: Optional[bool] = False
    replyTo: Optional[Dict[str, Any]] = None
    reactions: Optional[List[Dict[str, Any]]] = []

# ----------------- CONVERSATION SCHEMAS -----------------

class ConversationCreateRequest(BaseModel):
    type: str = "direct" # 'direct' or 'group'
    participantId: Optional[str] = None
    name: str
    avatar: Optional[str] = None
    tags: Optional[List[str]] = []

class ConversationResponse(BaseModel):
    id: str
    type: str
    participantId: Optional[str] = None
    groupId: Optional[str] = None
    name: str
    avatar: Optional[str] = None
    memberCount: Optional[int] = 2
    isPinned: Optional[bool] = False
    isMuted: Optional[bool] = False
    unreadCount: Optional[int] = 0
    isTyping: Optional[bool] = False
    typingUser: Optional[str] = None
    lastMessage: Optional[Dict[str, Any]] = None
    draft: Optional[str] = ""
    tags: Optional[List[str]] = []

# ----------------- GROUP SCHEMAS -----------------

class GroupMemberItem(BaseModel):
    id: str
    name: str
    role: str = "member"
    avatar: Optional[str] = None

class GroupCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    avatar: Optional[str] = None
    memberIds: List[str] = []

class GroupResponse(BaseModel):
    id: str
    name: str
    avatar: Optional[str] = None
    description: Optional[str] = None
    createdAt: Optional[str] = None
    members: List[Dict[str, Any]] = []
    settings: Optional[Dict[str, Any]] = None

# ----------------- STATUS SCHEMAS -----------------

class StatusItemCreate(BaseModel):
    type: str = "text"
    backgroundColor: Optional[str] = "from-teal-600 to-emerald-800"
    text: Optional[str] = None
    mediaUrl: Optional[str] = None
    caption: Optional[str] = None

class StatusCreateRequest(BaseModel):
    items: List[StatusItemCreate]

class StatusResponse(BaseModel):
    id: str
    userId: str
    userName: str
    userAvatar: Optional[str] = None
    isMe: Optional[bool] = False
    hasUnseen: Optional[bool] = True
    timestamp: Optional[str] = "Just now"
    items: List[Dict[str, Any]] = []

# ----------------- CHANNEL SCHEMAS -----------------

class ChannelPostCreateRequest(BaseModel):
    title: str
    content: str
    mediaUrl: Optional[str] = None

class ChannelResponse(BaseModel):
    id: str
    name: str
    handle: str
    avatar: Optional[str] = None
    category: Optional[str] = "General"
    description: Optional[str] = None
    subscribers: Optional[int] = 0
    isSubscribed: Optional[bool] = False
    isVerified: Optional[bool] = False
    isPremium: Optional[bool] = False
    posts: Optional[List[Dict[str, Any]]] = []

# ----------------- BUSINESS SCHEMAS -----------------

class ProductCreateRequest(BaseModel):
    name: str
    category: str
    price: float
    stock: int = 10
    image: Optional[str] = None
    description: Optional[str] = None

class ProductUpdateRequest(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    status: Optional[str] = None
    image: Optional[str] = None
    description: Optional[str] = None

class ProductResponse(BaseModel):
    id: str
    name: str
    category: str
    price: float
    currency: str = "RWF"
    stock: int
    status: str
    image: Optional[str] = None
    description: Optional[str] = None
    salesCount: Optional[int] = 0

class CustomerTicketUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    note: Optional[str] = None

class AiSupportTestRequest(BaseModel):
    question: str

class FaqCreateRequest(BaseModel):
    question: str
    answer: str

# ----------------- CALL SCHEMAS -----------------

class CallLogCreateRequest(BaseModel):
    contactId: str
    name: str
    avatar: Optional[str] = None
    type: str = "voice" # 'voice', 'video'
    direction: str = "outgoing" # 'incoming', 'outgoing', 'missed'
    status: str = "completed"
    duration: Optional[str] = "0s"

class CallLogResponse(BaseModel):
    id: str
    contactId: str
    name: str
    avatar: Optional[str] = None
    type: str
    direction: str
    status: str
    timestamp: str
    duration: str

# ----------------- AD & SUBSCRIPTION SCHEMAS -----------------

class AdCampaignCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    audience: Optional[str] = None
    budgetRwf: float
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    creativeUrl: Optional[str] = None

class CheckoutRequest(BaseModel):
    planId: str
    billingCycle: str = "monthly" # 'monthly', 'yearly'
    paymentMethod: str = "momo" # 'momo', 'card'
    phoneNumber: Optional[str] = None
