import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents
from schemas import ContactMessage, Subscription, Staff as StaffSchema, CourseCategory as CourseCategorySchema

app = FastAPI(title="Programming Courses API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----- Utility seeders -----

def _ensure_categories_seeded() -> List[dict]:
    if db is None:
        return []
    collection = db["coursecategory"]
    if collection.count_documents({}) == 0:
        seed: List[CourseCategorySchema] = [
            CourseCategorySchema(
                slug="web-development",
                title="Web Development",
                blurb="Build modern, responsive websites and web apps from scratch.",
                highlights=["HTML, CSS, JS", "React & Tailwind", "APIs & Auth"],
                color="#22c55e",
                accent="#10b981",
            ),
            CourseCategorySchema(
                slug="ai-programming",
                title="AI Programming",
                blurb="Learn Python for AI, machine learning, and practical LLM apps.",
                highlights=["Python & NumPy", "ML & LLMs", "Model Deployment"],
                color="#a855f7",
                accent="#8b5cf6",
            ),
            CourseCategorySchema(
                slug="robotics",
                title="Robotics",
                blurb="Program and control robots with sensors, motion, and autonomy.",
                highlights=["ROS Basics", "Sensors & Control", "Path Planning"],
                color="#0ea5e9",
                accent="#38bdf8",
            ),
            CourseCategorySchema(
                slug="drone",
                title="Drone Programming",
                blurb="Build and pilot drones, master flight control and computer vision.",
                highlights=["PX4 & MAVSDK", "Stabilization", "Aerial CV"],
                color="#22d3ee",
                accent="#06b6d4",
            ),
            CourseCategorySchema(
                slug="3d-printing",
                title="3D Product & Printing",
                blurb="Design 3D models and turn ideas into physical prototypes.",
                highlights=["Fusion/Blender", "Slicing & Materials", "Rapid Prototyping"],
                color="#f59e0b",
                accent="#fbbf24",
            ),
        ]
        docs = [s.model_dump() for s in seed]
        for d in docs:
            create_document("coursecategory", d)
    return list(collection.find({}, {"_id": 0}))


def _ensure_staff_seeded() -> List[dict]:
    if db is None:
        return []
    collection = db["staff"]
    if collection.count_documents({}) == 0:
        team: List[StaffSchema] = [
            StaffSchema(
                name="Ava Chen",
                role="Head of AI",
                bio="Leads our AI track with 8+ years in ML and LLM apps.",
                avatar="https://i.pravatar.cc/150?img=1",
                socials={"twitter": "https://twitter.com/avachen"},
            ),
            StaffSchema(
                name="Miguel Torres",
                role="Robotics Lead",
                bio="ROS expert building autonomous ground and aerial robots.",
                avatar="https://i.pravatar.cc/150?img=5",
                socials={"github": "https://github.com/miguelt"},
            ),
            StaffSchema(
                name="Sara Patel",
                role="Web Instructor",
                bio="Front-end engineer focused on React and delightful UX.",
                avatar="https://i.pravatar.cc/150?img=11",
                socials={"linkedin": "https://linkedin.com/in/sarapatel"},
            ),
        ]
        for member in team:
            create_document("staff", member)
    return list(collection.find({}, {"_id": 0}))


# ----- Models for responses -----

class MessageResponse(BaseModel):
    status: str
    detail: str


# ----- Routes -----

@app.get("/")
def root():
    return {"message": "Programming Courses API is running"}


@app.get("/api/categories")
def list_categories():
    try:
        data = _ensure_categories_seeded()
        return {"items": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/categories/{slug}")
def category_detail(slug: str):
    try:
        _ensure_categories_seeded()
        doc = db["coursecategory"].find_one({"slug": slug}, {"_id": 0}) if db else None
        if not doc:
            raise HTTPException(status_code=404, detail="Category not found")
        return doc
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/staff")
def staff_list():
    try:
        data = _ensure_staff_seeded()
        return {"items": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/contact", response_model=MessageResponse)
def contact(message: ContactMessage):
    try:
        create_document("contactmessage", message)
        return MessageResponse(status="ok", detail="Message received. We'll be in touch!")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/subscribe", response_model=MessageResponse)
def subscribe(body: Subscription):
    try:
        if db is None:
            raise Exception("Database not available")
        # Upsert by email
        db["subscription"].update_one(
            {"email": body.email},
            {"$set": {**body.model_dump(), "updated_at": __import__("datetime").datetime.utcnow()},
             "$setOnInsert": {"created_at": __import__("datetime").datetime.utcnow()}},
            upsert=True,
        )
        return MessageResponse(status="ok", detail="Subscribed successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
