"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
from pymongo import MongoClient
import logging

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["mergington_high_school"]
activities_collection = db["activities"]

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# Initial activity data for database seeding
initial_activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    # Sports related activities
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 18,
        "participants": ["lucas@mergington.edu", "mia@mergington.edu"]
    },
    "Basketball Club": {
        "description": "Practice basketball skills and play friendly games",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ethan@mergington.edu", "ava@mergington.edu"]
    },
    # Artistic activities
    "Art Workshop": {
        "description": "Explore painting, drawing, and sculpture techniques",
        "schedule": "Mondays, 3:30 PM - 5:00 PM",
        "max_participants": 16,
        "participants": ["isabella@mergington.edu", "liam@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act, direct, and produce school plays and performances",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["noah@mergington.edu", "amelia@mergington.edu"]
    },
    # Intellectual activities
    "Math Olympiad": {
        "description": "Prepare for math competitions and solve challenging problems",
        "schedule": "Tuesdays, 4:00 PM - 5:00 PM",
        "max_participants": 10,
        "participants": ["oliver@mergington.edu", "charlotte@mergington.edu"]
    },
    "Science Club": {
        "description": "Conduct experiments and explore scientific concepts",
        "schedule": "Thursdays, 4:00 PM - 5:00 PM",
        "max_participants": 14,
        "participants": ["benjamin@mergington.edu", "ella@mergington.edu"]
    }
}

def initialize_database():
    """Initialize the database with activity data if it's empty"""
    if activities_collection.count_documents({}) == 0:
        for activity_name, activity_data in initial_activities.items():
            document = {
                "_id": activity_name,  # Use activity name as the key
                **activity_data
            }
            activities_collection.insert_one(document)
        logging.info("Database initialized with activity data")

# Initialize database on startup
initialize_database()


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    """Get all activities from MongoDB"""
    activities = {}
    for doc in activities_collection.find():
        activity_name = doc["_id"]
        # Remove MongoDB _id field from response
        activity_data = {k: v for k, v in doc.items() if k != "_id"}
        activities[activity_name] = activity_data
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    activity = activities_collection.find_one({"_id": activity_name})
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student already signed up for this activity")

    # Add student to activity
    activities_collection.update_one(
        {"_id": activity_name},
        {"$push": {"participants": email}}
    )
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Validate activity exists
    activity = activities_collection.find_one({"_id": activity_name})
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Validate student is signed up
    if email not in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student is not signed up for this activity")

    # Remove student from activity
    activities_collection.update_one(
        {"_id": activity_name},
        {"$pull": {"participants": email}}
    )
    return {"message": f"Unregistered {email} from {activity_name}"}

