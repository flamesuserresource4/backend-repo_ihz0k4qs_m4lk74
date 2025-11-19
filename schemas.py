"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# App-specific schemas

class ContactMessage(BaseModel):
    name: str = Field(..., min_length=2, description="Sender full name")
    email: EmailStr = Field(..., description="Sender email")
    message: str = Field(..., min_length=10, max_length=2000, description="Message body")
    topic: Optional[str] = Field(None, description="Optional topic or category of inquiry")

class Subscription(BaseModel):
    email: EmailStr = Field(..., description="Subscriber email")
    name: Optional[str] = Field(None, description="Subscriber name")
    interests: Optional[List[str]] = Field(default=None, description="List of interests for targeting")

class Staff(BaseModel):
    name: str
    role: str
    bio: Optional[str] = None
    avatar: Optional[str] = None  # URL
    socials: Optional[dict] = None

class CourseCategory(BaseModel):
    slug: str
    title: str
    blurb: str
    highlights: Optional[List[str]] = None
    color: Optional[str] = None
    accent: Optional[str] = None
