import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional

app = FastAPI(title="Inferno Guide API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Circle(BaseModel):
    id: int
    name: str
    sin: str
    guardians: List[str]
    punishment: str
    motto: str
    color: str = Field(default="#ef4444")
    quote: Optional[str] = None


CIRCLES: List[Circle] = [
    Circle(
        id=1,
        name="Limbo",
        sin="The Unbaptized & Virtuous Pagans",
        guardians=["Minos (on threshold)", "Poets"],
        punishment="Eternal longing without torment",
        motto="Where hope is a horizon you can see but never reach.",
        color="#a7f3d0",
        quote="We are those who without hope live in desire.",
    ),
    Circle(
        id=2,
        name="Lust",
        sin="Swept by passion",
        guardians=["Minos", "Francesca & Paolo"],
        punishment="Whirled in an endless storm",
        motto="To be carried by every wind is to never arrive.",
        color="#fda4af",
        quote="Love, which quickly kindles in the gentle heart…",
    ),
    Circle(
        id=3,
        name="Gluttony",
        sin="Excess and indulgence",
        guardians=["Cerberus"],
        punishment="Battered by icy rain and filth",
        motto="What consumes you is not what you eat, but what you cannot refuse.",
        color="#fde68a",
    ),
    Circle(
        id=4,
        name="Greed",
        sin="Hoarders & Wasters",
        guardians=["Plutus"],
        punishment="Push great weights against each other forever",
        motto="The weight of wanting more is heavier than gold.",
        color="#fbbf24",
    ),
    Circle(
        id=5,
        name="Wrath",
        sin="Wrathful & Sullen",
        guardians=["Phlegyas"],
        punishment="Fight on the surface; drown below",
        motto="Anger burns bright; resentment smolders cold.",
        color="#f87171",
    ),
    Circle(
        id=6,
        name="Heresy",
        sin="Denial of immortality",
        guardians=["Furies", "Medusa"],
        punishment="Burn in flaming tombs",
        motto="To deny forever is to be sealed within your own certainty.",
        color="#fb7185",
    ),
    Circle(
        id=7,
        name="Violence",
        sin="Against others, self, God & nature",
        guardians=["Minotaur", "Centaurs"],
        punishment="Boiling blood, forest of suicides, burning sand",
        motto="Violence returns to the hand that wields it.",
        color="#ef4444",
    ),
    Circle(
        id=8,
        name="Fraud",
        sin="Ten Malebolge of deception",
        guardians=["Geryon"],
        punishment="Ten ditches for ten kinds of lies",
        motto="Masks grow heavy when worn forever.",
        color="#f43f5e",
    ),
    Circle(
        id=9,
        name="Treachery",
        sin="Betrayers frozen in Cocytus",
        guardians=["Lucifer"],
        punishment="Entombed in ice at various depths",
        motto="The coldest places are reserved for those who betray trust.",
        color="#60a5fa",
    ),
]


class JourneyRequest(BaseModel):
    mood: str = Field(..., description="Current mood or vibe: curious, somber, reflective, adventurous")
    interest: str = Field(..., description="What draws you: literature, psychology, myth, morality, aesthetics")
    intensity: int = Field(5, ge=1, le=10, description="How intense a journey from 1-10")


class JourneyStop(BaseModel):
    circle_id: int
    title: str
    takeaway: str


class JourneyResponse(BaseModel):
    title: str
    path: List[JourneyStop]
    note: str


@app.get("/")
def read_root():
    return {"message": "Inferno Guide API ready"}


@app.get("/api/hello")
def hello():
    return {"message": "Welcome to the Inferno"}


@app.get("/api/inferno/circles", response_model=List[Circle])
def get_circles():
    return CIRCLES


@app.post("/api/inferno/journey", response_model=JourneyResponse)
def build_journey(req: JourneyRequest):
    mood_map = {
        "curious": [1, 2, 3, 4],
        "somber": [6, 9],
        "reflective": [1, 5, 7],
        "adventurous": [2, 7, 8],
    }
    interest_map = {
        "literature": [1, 2, 5],
        "psychology": [2, 3, 5, 7],
        "myth": [4, 6, 7, 8],
        "morality": [1, 4, 9],
        "aesthetics": [2, 6, 9],
    }

    # Build weighted set of circle ids by mood + interest + intensity
    base = set(mood_map.get(req.mood.lower(), [1, 2, 3]))
    base.update(interest_map.get(req.interest.lower(), [4, 5]))

    # Scale path length with intensity
    length = max(3, min(7, 2 + req.intensity // 2))

    ordered = sorted(list(base))[:length]
    if len(ordered) < length:
        # pad deterministically
        for c in [6, 7, 8, 9, 5, 4, 3, 2, 1]:
            if len(ordered) >= length:
                break
            if c not in ordered:
                ordered.append(c)

    stops: List[JourneyStop] = []
    for cid in ordered:
        circle = next((c for c in CIRCLES if c.id == cid), None)
        if not circle:
            continue
        title = f"{circle.name}: {circle.sin}"
        takeaway = {
            1: "Hope without action is a gentle prison.",
            2: "Desire untethered becomes a storm.",
            3: "Comfort can drown purpose.",
            4: "The pursuit of more can empty the soul.",
            5: "Anger can power you or poison you.",
            6: "Certainty can calcify curiosity.",
            7: "Violence echoes back to the source.",
            8: "Deception distorts the self first.",
            9: "Trust is a sacred architecture.",
        }.get(cid, circle.motto)
        stops.append(JourneyStop(circle_id=cid, title=title, takeaway=takeaway))

    note = "Your path is a reflection, not a sentence. Carry the insight, not the weight."
    return JourneyResponse(title="A Personal Descent", path=stops, note=note)


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        # Try to import database module
        from database import db
        
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            
            # Try to list collections to verify connectivity
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]  # Show first 10 collections
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    # Check environment variables
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
