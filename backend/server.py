from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext
import jwt
import json
from emergentintegrations.llm.chat import LlmChat, UserMessage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'samastu-secret-key-change-in-production')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30
security = HTTPBearer()

app = FastAPI()
api_router = APIRouter(prefix="/api")

# ========== MODELS ==========

class Exercise(BaseModel):
    name: str
    reps: str
    sets: int
    rest_seconds: int
    icon: str

class WorkoutPlan(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    difficulty: str
    exercises: List[Exercise]
    target_muscles: str
    xp_reward: int
    duration_minutes: int

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    gender: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    goal: Optional[str] = None
    equipment: Optional[List[str]] = []

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    name: str
    gender: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    goal: Optional[str] = None
    equipment: Optional[List[str]] = []
    experience_level: Optional[str] = None  # beginner, intermediate, advanced
    available_days: Optional[List[dict]] = []  # [{"day": "Monday", "minutes": 30}]
    plan_duration: Optional[int] = 4  # Duration number (default 4 weeks)
    plan_duration_unit: Optional[str] = "weeks"  # weeks, months, years
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserUpdate(BaseModel):
    name: Optional[str] = None
    gender: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    goal: Optional[str] = None
    equipment: Optional[List[str]] = None
    experience_level: Optional[str] = None
    available_days: Optional[List[dict]] = None
    plan_duration: Optional[int] = None
    plan_duration_unit: Optional[str] = None

class WorkoutSession(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    workout_plan_id: str
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    xp_earned: int
    duration_minutes: int
    status: str

class Progress(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_id: str
    total_xp: int = 0
    level: int = 1
    streak: int = 0
    current_streak_start: Optional[datetime] = None
    last_workout_date: Optional[datetime] = None
    achievements: List[str] = []
    body_weight_history: List[dict] = []

class WorkoutComplete(BaseModel):
    workout_plan_id: str
    duration_minutes: int

class ScheduledWorkout(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    workout_plan_id: str
    scheduled_date: str  # YYYY-MM-DD format
    day_of_week: str  # Monday, Tuesday, etc.
    is_rest_day: bool = False
    is_completed: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: User

# ========== AUTH HELPERS ==========

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_doc = await db.users.find_one({"id": user_id}, {"_id": 0, "password_hash": 0})
    if user_doc is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    if isinstance(user_doc.get('created_at'), str):
        user_doc['created_at'] = datetime.fromisoformat(user_doc['created_at'])
    
    return User(**user_doc)

# ========== SEED WORKOUT PLANS ==========

async def seed_workout_plans():
    existing = await db.workout_plans.count_documents({})
    if existing > 0:
        return
    
    workout_plans = [
        {
            "id": str(uuid.uuid4()),
            "name": "Full Body Starter",
            "difficulty": "Beginner",
            "exercises": [
                {"name": "Jumping Jacks", "reps": "30 reps", "sets": 2, "rest_seconds": 30, "icon": "zap"},
                {"name": "Push-ups", "reps": "10 reps", "sets": 3, "rest_seconds": 45, "icon": "activity"},
                {"name": "Squats", "reps": "15 reps", "sets": 3, "rest_seconds": 45, "icon": "trending-up"},
                {"name": "Plank", "reps": "30 sec", "sets": 2, "rest_seconds": 30, "icon": "minus"},
            ],
            "target_muscles": "Full Body",
            "xp_reward": 50,
            "duration_minutes": 20
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Core Crush",
            "difficulty": "Beginner",
            "exercises": [
                {"name": "Crunches", "reps": "20 reps", "sets": 3, "rest_seconds": 30, "icon": "circle"},
                {"name": "Bicycle Crunches", "reps": "15 reps", "sets": 3, "rest_seconds": 30, "icon": "repeat"},
                {"name": "Leg Raises", "reps": "12 reps", "sets": 3, "rest_seconds": 30, "icon": "arrow-up"},
                {"name": "Mountain Climbers", "reps": "20 reps", "sets": 2, "rest_seconds": 45, "icon": "triangle"},
            ],
            "target_muscles": "Core",
            "xp_reward": 50,
            "duration_minutes": 15
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Upper Body Push",
            "difficulty": "Intermediate",
            "exercises": [
                {"name": "Push-ups", "reps": "15 reps", "sets": 4, "rest_seconds": 45, "icon": "activity"},
                {"name": "Diamond Push-ups", "reps": "10 reps", "sets": 3, "rest_seconds": 45, "icon": "diamond"},
                {"name": "Tricep Dips", "reps": "12 reps", "sets": 3, "rest_seconds": 45, "icon": "chevron-down"},
                {"name": "Shoulder Taps", "reps": "20 reps", "sets": 3, "rest_seconds": 30, "icon": "hand"},
            ],
            "target_muscles": "Chest, Shoulders, Triceps",
            "xp_reward": 50,
            "duration_minutes": 25
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Lower Body Power",
            "difficulty": "Intermediate",
            "exercises": [
                {"name": "Squats", "reps": "20 reps", "sets": 4, "rest_seconds": 45, "icon": "trending-up"},
                {"name": "Lunges", "reps": "12 each", "sets": 3, "rest_seconds": 45, "icon": "move"},
                {"name": "Glute Bridges", "reps": "15 reps", "sets": 3, "rest_seconds": 30, "icon": "chevrons-up"},
                {"name": "Calf Raises", "reps": "20 reps", "sets": 3, "rest_seconds": 30, "icon": "arrow-up-circle"},
            ],
            "target_muscles": "Legs, Glutes",
            "xp_reward": 50,
            "duration_minutes": 25
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Cardio Flow",
            "difficulty": "Beginner",
            "exercises": [
                {"name": "High Knees", "reps": "30 sec", "sets": 3, "rest_seconds": 30, "icon": "zap"},
                {"name": "Butt Kicks", "reps": "30 sec", "sets": 3, "rest_seconds": 30, "icon": "wind"},
                {"name": "Jump Squats", "reps": "10 reps", "sets": 3, "rest_seconds": 45, "icon": "trending-up"},
                {"name": "Burpees", "reps": "8 reps", "sets": 2, "rest_seconds": 60, "icon": "layers"},
            ],
            "target_muscles": "Cardio",
            "xp_reward": 50,
            "duration_minutes": 18
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Core & Cardio Mix",
            "difficulty": "Intermediate",
            "exercises": [
                {"name": "Plank to Downward Dog", "reps": "12 reps", "sets": 3, "rest_seconds": 30, "icon": "minus"},
                {"name": "Russian Twists", "reps": "20 reps", "sets": 3, "rest_seconds": 30, "icon": "rotate-cw"},
                {"name": "High Knees", "reps": "40 sec", "sets": 3, "rest_seconds": 30, "icon": "zap"},
                {"name": "V-ups", "reps": "10 reps", "sets": 3, "rest_seconds": 45, "icon": "chevron-up"},
            ],
            "target_muscles": "Core, Cardio",
            "xp_reward": 50,
            "duration_minutes": 22
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Upper Body Pull",
            "difficulty": "Intermediate",
            "exercises": [
                {"name": "Pull-up Hold", "reps": "20 sec", "sets": 3, "rest_seconds": 45, "icon": "arrow-up"},
                {"name": "Inverted Rows", "reps": "12 reps", "sets": 3, "rest_seconds": 45, "icon": "minimize-2"},
                {"name": "Superman Hold", "reps": "30 sec", "sets": 3, "rest_seconds": 30, "icon": "user"},
                {"name": "Arm Circles", "reps": "20 each", "sets": 2, "rest_seconds": 20, "icon": "disc"},
            ],
            "target_muscles": "Back, Biceps",
            "xp_reward": 50,
            "duration_minutes": 20
        },
        {
            "id": str(uuid.uuid4()),
            "name": "HIIT Challenge",
            "difficulty": "Advanced",
            "exercises": [
                {"name": "Burpees", "reps": "15 reps", "sets": 4, "rest_seconds": 45, "icon": "layers"},
                {"name": "Jump Lunges", "reps": "10 each", "sets": 3, "rest_seconds": 45, "icon": "move"},
                {"name": "Plank Jacks", "reps": "20 reps", "sets": 3, "rest_seconds": 30, "icon": "minus"},
                {"name": "Tuck Jumps", "reps": "12 reps", "sets": 3, "rest_seconds": 60, "icon": "arrow-up-circle"},
            ],
            "target_muscles": "Full Body, Cardio",
            "xp_reward": 50,
            "duration_minutes": 28
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Full Body Blast",
            "difficulty": "Intermediate",
            "exercises": [
                {"name": "Push-ups", "reps": "15 reps", "sets": 3, "rest_seconds": 45, "icon": "activity"},
                {"name": "Squats", "reps": "20 reps", "sets": 3, "rest_seconds": 45, "icon": "trending-up"},
                {"name": "Plank", "reps": "45 sec", "sets": 3, "rest_seconds": 30, "icon": "minus"},
                {"name": "Jumping Jacks", "reps": "40 reps", "sets": 3, "rest_seconds": 30, "icon": "zap"},
            ],
            "target_muscles": "Full Body",
            "xp_reward": 50,
            "duration_minutes": 24
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Recovery Stretch",
            "difficulty": "Beginner",
            "exercises": [
                {"name": "Hamstring Stretch", "reps": "30 sec", "sets": 2, "rest_seconds": 15, "icon": "minimize"},
                {"name": "Shoulder Stretch", "reps": "30 sec", "sets": 2, "rest_seconds": 15, "icon": "move-horizontal"},
                {"name": "Cat-Cow Pose", "reps": "10 reps", "sets": 2, "rest_seconds": 15, "icon": "wave"},
                {"name": "Child's Pose", "reps": "60 sec", "sets": 1, "rest_seconds": 0, "icon": "heart"},
            ],
            "target_muscles": "Flexibility",
            "xp_reward": 50,
            "duration_minutes": 12
        },
    ]
    
    await db.workout_plans.insert_many(workout_plans)
    logger.info(f"Seeded {len(workout_plans)} workout plans")

# ========== AUTH ROUTES ==========

@api_router.post("/auth/register", response_model=TokenResponse)
async def register(user_data: UserCreate):
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_dict = user_data.model_dump(exclude={"password"})
    user_obj = User(**user_dict)
    user_doc = user_obj.model_dump()
    user_doc['password_hash'] = hash_password(user_data.password)
    user_doc['created_at'] = user_doc['created_at'].isoformat()
    
    await db.users.insert_one(user_doc)
    
    # Initialize progress
    progress = Progress(user_id=user_obj.id)
    progress_doc = progress.model_dump()
    await db.progress.insert_one(progress_doc)
    
    access_token = create_access_token(data={"sub": user_obj.id})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_obj
    )

@api_router.post("/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    user_doc = await db.users.find_one({"email": credentials.email})
    if not user_doc:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not verify_password(credentials.password, user_doc['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    user_doc.pop('password_hash', None)
    user_doc.pop('_id', None)
    
    if isinstance(user_doc.get('created_at'), str):
        user_doc['created_at'] = datetime.fromisoformat(user_doc['created_at'])
    
    user_obj = User(**user_doc)
    access_token = create_access_token(data={"sub": user_obj.id})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_obj
    )

@api_router.get("/auth/me", response_model=User)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

# ========== USER ROUTES ==========

@api_router.get("/user/profile", response_model=User)
async def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

@api_router.put("/user/profile", response_model=User)
async def update_profile(user_update: UserUpdate, current_user: User = Depends(get_current_user)):
    update_data = user_update.model_dump(exclude_unset=True)
    if update_data:
        await db.users.update_one(
            {"id": current_user.id},
            {"$set": update_data}
        )
    
    updated_user_doc = await db.users.find_one({"id": current_user.id}, {"_id": 0, "password_hash": 0})
    if isinstance(updated_user_doc.get('created_at'), str):
        updated_user_doc['created_at'] = datetime.fromisoformat(updated_user_doc['created_at'])
    
    return User(**updated_user_doc)

@api_router.delete("/user/account")
async def delete_account(current_user: User = Depends(get_current_user)):
    """Delete user account and all associated data"""
    # Delete all user data
    await db.users.delete_one({"id": current_user.id})
    await db.workout_sessions.delete_many({"user_id": current_user.id})
    await db.progress.delete_many({"user_id": current_user.id})
    await db.scheduled_workouts.delete_many({"user_id": current_user.id})
    
    return {"success": True, "message": "Account deleted successfully"}

# ========== WORKOUT ROUTES ==========

@api_router.get("/workouts/plans", response_model=List[WorkoutPlan])
async def get_workout_plans(current_user: User = Depends(get_current_user)):
    # First try to get user's AI-generated plans
    ai_plans = await db.ai_workout_plans.find(
        {"user_id": current_user.id}, 
        {"_id": 0}
    ).to_list(100)
    
    # Fallback to default workout plans if no AI plans exist
    if not ai_plans:
        plans = await db.workout_plans.find({}, {"_id": 0}).to_list(100)
        return plans
    
    return ai_plans

@api_router.get("/workouts/journey")
async def get_workout_journey(current_user: User = Depends(get_current_user)):
    """Get user's workout journey based on their schedule"""
    # Get user's scheduled workouts
    scheduled = await db.scheduled_workouts.find(
        {"user_id": current_user.id},
        {"_id": 0}
    ).sort("scheduled_date", 1).to_list(1000)
    
    if not scheduled:
        # Fallback to old behavior if no schedule
        # First try to get user's AI-generated plans
        plans = await db.ai_workout_plans.find(
            {"user_id": current_user.id}, 
            {"_id": 0}
        ).to_list(100)
        
        # Fallback to default workout plans if no AI plans exist
        if not plans:
            plans = await db.workout_plans.find({}, {"_id": 0}).to_list(100)
        completed_sessions = await db.workout_sessions.find(
            {"user_id": current_user.id},
            {"_id": 0}
        ).to_list(1000)
        
        completed_plan_ids = [session['workout_plan_id'] for session in completed_sessions]
        
        journey = []
        for idx, plan in enumerate(plans):
            is_completed = plan['id'] in completed_plan_ids
            is_next = not is_completed and (idx == 0 or plans[idx-1]['id'] in completed_plan_ids)
            
            journey.append({
                **plan,
                "is_completed": is_completed,
                "is_next": is_next,
                "is_rest_day": False,
                "scheduled_date": None,
                "position": idx
            })
        
        return journey
    
    # Get workout plan details from AI-generated plans
    workout_ids = [s['workout_plan_id'] for s in scheduled if not s['is_rest_day']]
    
    # First try to get from AI-generated plans
    ai_workout_plans = await db.ai_workout_plans.find(
        {"id": {"$in": workout_ids}},
        {"_id": 0}
    ).to_list(1000)
    
    # Fallback to regular workout_plans if needed (for backwards compatibility)
    if not ai_workout_plans:
        ai_workout_plans = await db.workout_plans.find(
            {"id": {"$in": workout_ids}},
            {"_id": 0}
        ).to_list(1000)
    
    plans_dict = {p['id']: p for p in ai_workout_plans}
    
    # Build journey from schedule
    today = datetime.now(timezone.utc).date().isoformat()
    journey = []
    
    for idx, item in enumerate(scheduled):
        if item['is_rest_day']:
            # Rest day node
            journey.append({
                "id": item['id'],
                "name": "Rest Day",
                "difficulty": "Recovery",
                "exercises": [],
                "target_muscles": "Recovery",
                "xp_reward": 0,
                "duration_minutes": 0,
                "is_completed": item['is_completed'],
                "is_next": item['scheduled_date'] == today and not item['is_completed'],
                "is_rest_day": True,
                "scheduled_date": item['scheduled_date'],
                "is_locked": item['scheduled_date'] > today,
                "position": idx
            })
        else:
            # Workout day node
            plan = plans_dict.get(item['workout_plan_id'], {})
            is_next = item['scheduled_date'] == today and not item['is_completed']
            is_locked = item['scheduled_date'] > today
            
            journey.append({
                **plan,
                "id": item['workout_plan_id'],
                "schedule_id": item['id'],
                "is_completed": item['is_completed'],
                "is_next": is_next,
                "is_rest_day": False,
                "scheduled_date": item['scheduled_date'],
                "is_locked": is_locked,
                "position": idx
            })
    
    return journey

@api_router.post("/workouts/complete")
async def complete_workout(workout_data: WorkoutComplete, current_user: User = Depends(get_current_user)):
    # Get workout plan from AI-generated plans first
    plan = await db.ai_workout_plans.find_one({"id": workout_data.workout_plan_id})
    
    # Fallback to regular workout_plans if needed (for backwards compatibility)
    if not plan:
        plan = await db.workout_plans.find_one({"id": workout_data.workout_plan_id})
    
    if not plan:
        raise HTTPException(status_code=404, detail="Workout plan not found")
    
    # Create workout session
    session = WorkoutSession(
        user_id=current_user.id,
        workout_plan_id=workout_data.workout_plan_id,
        xp_earned=plan['xp_reward'],
        duration_minutes=workout_data.duration_minutes,
        status="completed"
    )
    session_doc = session.model_dump()
    session_doc['date'] = session_doc['date'].isoformat()
    await db.workout_sessions.insert_one(session_doc)
    
    # Update progress
    progress_doc = await db.progress.find_one({"user_id": current_user.id})
    if not progress_doc:
        progress_doc = Progress(user_id=current_user.id).model_dump()
    
    # Update XP and level
    new_total_xp = progress_doc.get('total_xp', 0) + plan['xp_reward']
    new_level = (new_total_xp // 500) + 1
    
    # Update streak
    today = datetime.now(timezone.utc).date()
    last_workout_date = progress_doc.get('last_workout_date')
    
    if isinstance(last_workout_date, str):
        last_workout_date = datetime.fromisoformat(last_workout_date).date()
    elif isinstance(last_workout_date, datetime):
        last_workout_date = last_workout_date.date()
    
    current_streak = progress_doc.get('streak', 0)
    
    if last_workout_date:
        days_diff = (today - last_workout_date).days
        if days_diff == 0:
            # Same day, no change
            new_streak = current_streak
        elif days_diff == 1:
            # Consecutive day
            new_streak = current_streak + 1
        else:
            # Streak broken
            new_streak = 1
    else:
        new_streak = 1
    
    # Check achievements
    achievements = progress_doc.get('achievements', [])
    total_workouts = await db.workout_sessions.count_documents({"user_id": current_user.id})
    
    if total_workouts >= 5 and "first_5" not in achievements:
        achievements.append("first_5")
    if total_workouts >= 10 and "first_10" not in achievements:
        achievements.append("first_10")
    if total_workouts >= 50 and "warrior_50" not in achievements:
        achievements.append("warrior_50")
    if new_streak >= 7 and "streak_7" not in achievements:
        achievements.append("streak_7")
    if new_streak >= 30 and "streak_30" not in achievements:
        achievements.append("streak_30")
    
    # Update progress document
    update_data = {
        "total_xp": new_total_xp,
        "level": new_level,
        "streak": new_streak,
        "last_workout_date": today.isoformat(),
        "achievements": achievements
    }
    
    await db.progress.update_one(
        {"user_id": current_user.id},
        {"$set": update_data},
        upsert=True
    )
    
    # Get new achievements (just unlocked)
    old_achievements = progress_doc.get('achievements', [])
    new_achievements = [a for a in achievements if a not in old_achievements]
    
    return {
        "success": True,
        "xp_earned": plan['xp_reward'],
        "new_total_xp": new_total_xp,
        "new_level": new_level,
        "new_streak": new_streak,
        "new_achievements": new_achievements
    }

# ========== PROGRESS ROUTES ==========

@api_router.get("/progress", response_model=Progress)
async def get_progress(current_user: User = Depends(get_current_user)):
    progress_doc = await db.progress.find_one({"user_id": current_user.id}, {"_id": 0})
    if not progress_doc:
        progress = Progress(user_id=current_user.id)
        return progress
    
    # Convert date strings back to datetime if needed
    if isinstance(progress_doc.get('current_streak_start'), str):
        progress_doc['current_streak_start'] = datetime.fromisoformat(progress_doc['current_streak_start'])
    if isinstance(progress_doc.get('last_workout_date'), str):
        progress_doc['last_workout_date'] = datetime.fromisoformat(progress_doc['last_workout_date'])
    
    return Progress(**progress_doc)

@api_router.get("/achievements")
async def get_achievements(current_user: User = Depends(get_current_user)):
    progress_doc = await db.progress.find_one({"user_id": current_user.id})
    achievements = progress_doc.get('achievements', []) if progress_doc else []
    
    total_workouts = await db.workout_sessions.count_documents({"user_id": current_user.id})
    
    achievement_list = [
        {"id": "first_5", "name": "First Steps", "description": "Complete 5 workouts", "unlocked": "first_5" in achievements, "icon": "award"},
        {"id": "first_10", "name": "Getting Strong", "description": "Complete 10 workouts", "unlocked": "first_10" in achievements, "icon": "trophy"},
        {"id": "warrior_50", "name": "Warrior", "description": "Complete 50 workouts", "unlocked": "warrior_50" in achievements, "icon": "crown"},
        {"id": "streak_7", "name": "Week Warrior", "description": "7-day streak", "unlocked": "streak_7" in achievements, "icon": "flame"},
        {"id": "streak_30", "name": "Unstoppable", "description": "30-day streak", "unlocked": "streak_30" in achievements, "icon": "zap"},
    ]
    
    return {
        "achievements": achievement_list,
        "total_workouts": total_workouts
    }

# ========== AI WORKOUT GENERATION ==========

@api_router.post("/workouts/generate-ai")
async def generate_ai_workout(current_user: User = Depends(get_current_user)):
    """Generate personalized workout plans using Gemini AI"""
    
    # Build user profile context
    user_context = f"""
User Profile:
- Experience Level: {current_user.experience_level or 'beginner'}
- Goal: {current_user.goal or 'general fitness'}
- Equipment Available: {', '.join(current_user.equipment) if current_user.equipment else 'none'}
- Available Days: {len(current_user.available_days) if current_user.available_days else 0} days per week
"""
    
    if current_user.available_days:
        user_context += "\nTime per day:\n"
        for day_info in current_user.available_days:
            user_context += f"- {day_info['day']}: {day_info['minutes']} minutes\n"
    
    # Create prompt for Gemini
    prompt = f"""{user_context}

Based on this user profile, generate a personalized 4-week workout plan. Create workouts that:
1. Match the user's experience level
2. Align with their fitness goals
3. Use only available equipment
4. Fit within their time constraints
5. Include rest days appropriately (every 2-3 workout days)

Return ONLY a valid JSON array with this exact structure:
[
  {{
    "name": "Workout Name",
    "difficulty": "Beginner|Intermediate|Advanced",
    "target_muscles": "Muscle groups",
    "duration_minutes": 20,
    "xp_reward": 50,
    "exercises": [
      {{
        "name": "Exercise Name",
        "reps": "10 reps",
        "sets": 3,
        "rest_seconds": 45,
        "icon": "activity"
      }}
    ]
  }}
]

Generate 6-8 varied workouts. Each workout should:
- Have 4-6 exercises
- Be realistically completable in the time available
- Include proper warm-up/cool-down exercises
- Use icons from: activity, zap, trending-up, minus, circle, repeat, arrow-up, triangle, diamond, chevron-down, hand, move, chevrons-up, arrow-up-circle, wind, layers, rotate-cw, chevron-up, minimize-2, user, disc

Return ONLY the JSON array, no other text."""

    try:
        # Initialize Gemini chat
        gemini_key = os.environ.get('GEMINI_API_KEY')
        if not gemini_key:
            raise HTTPException(status_code=500, detail="Gemini API key not configured")
        
        chat = LlmChat(
            api_key=gemini_key,
            session_id=f"workout_gen_{current_user.id}",
            system_message="You are a professional fitness trainer and workout planner. Generate realistic, safe, and effective workout plans in valid JSON format."
        ).with_model("gemini", "gemini-2.0-flash")
        
        user_message = UserMessage(text=prompt)
        response_obj = await chat.send_message(user_message)
        
        # Get the text response
        response_text = response_obj.text if hasattr(response_obj, 'text') else str(response_obj)
        response_text = response_text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith('```'):
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]
            response_text = response_text.strip()
        
        # Parse JSON
        workout_plans = json.loads(response_text)
        
        # Add IDs to plans
        for plan in workout_plans:
            plan['id'] = str(uuid.uuid4())
        
        # Create a copy for database insertion (will have _id added by MongoDB)
        plans_for_db = []
        timestamp = datetime.now(timezone.utc).isoformat()
        for plan in workout_plans:
            db_plan = json.loads(json.dumps(plan))  # Deep copy
            db_plan['user_id'] = current_user.id
            db_plan['created_at'] = timestamp
            plans_for_db.append(db_plan)
        
        # Delete old AI-generated plans for this user
        await db.ai_workout_plans.delete_many({"user_id": current_user.id})
        
        # Store new plans in database
        if plans_for_db:
            await db.ai_workout_plans.insert_many(plans_for_db)
        
        # Return the original clean workout_plans (without user_id, created_at, or MongoDB _id)
        return {
            "success": True,
            "plans": workout_plans,
            "message": f"Generated {len(workout_plans)} personalized workouts using AI"
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini response: {e}")
        logger.error(f"Response was: {response_text if 'response_text' in locals() else 'N/A'}")
        raise HTTPException(status_code=500, detail="Failed to parse AI response. Please try again.")
    except Exception as e:
        logger.error(f"AI workout generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate AI workouts: {str(e)}")

@api_router.get("/workouts/ai-plans")
async def get_ai_plans(current_user: User = Depends(get_current_user)):
    """Get user's AI-generated workout plans"""
    plans = await db.ai_workout_plans.find(
        {"user_id": current_user.id},
        {"_id": 0}
    ).to_list(100)
    return plans

# ========== SCHEDULE ROUTES ==========

@api_router.post("/schedule/generate")
async def generate_schedule(current_user: User = Depends(get_current_user)):
    """Generate a personalized workout schedule based on user's available days using AI-generated plans"""
    if not current_user.available_days or len(current_user.available_days) == 0:
        raise HTTPException(status_code=400, detail="No available days set. Please update your profile.")
    
    # Delete existing schedule
    await db.scheduled_workouts.delete_many({"user_id": current_user.id})
    
    # Check if user has AI-generated plans, if not generate them
    ai_plans = await db.ai_workout_plans.find({"user_id": current_user.id}, {"_id": 0}).to_list(100)
    
    if not ai_plans:
        # Auto-generate AI workout plans
        logger.info(f"No AI plans found for user {current_user.id}, generating now...")
        
        # Build user profile context
        user_context = f"""
User Profile:
- Experience Level: {current_user.experience_level or 'beginner'}
- Goal: {current_user.goal or 'general fitness'}
- Equipment Available: {', '.join(current_user.equipment) if current_user.equipment else 'none'}
- Available Days: {len(current_user.available_days) if current_user.available_days else 0} days per week
"""
        
        if current_user.available_days:
            user_context += "\nTime per day:\n"
            for day_info in current_user.available_days:
                user_context += f"- {day_info['day']}: {day_info['minutes']} minutes\n"
        
        # Get plan duration
        duration = current_user.plan_duration or 4
        duration_unit = current_user.plan_duration_unit or "weeks"
        
        # Create prompt for Gemini
        prompt = f"""{user_context}
- Plan Duration: {duration} {duration_unit}

Based on this user profile, generate a personalized workout plan for {duration} {duration_unit}. Create workouts that:
1. Match the user's experience level
2. Align with their fitness goals
3. Use only available equipment
4. Fit within their time constraints
5. Include rest days appropriately (every 2-3 workout days)

Return ONLY a valid JSON array with this exact structure:
[
  {{
    "name": "Workout Name",
    "difficulty": "Beginner|Intermediate|Advanced",
    "target_muscles": "Muscle groups",
    "duration_minutes": 20,
    "xp_reward": 50,
    "exercises": [
      {{
        "name": "Exercise Name",
        "reps": "10 reps",
        "sets": 3,
        "rest_seconds": 45,
        "icon": "activity"
      }}
    ]
  }}
]

Generate 6-8 varied workouts. Each workout should:
- Have 4-6 exercises
- Be realistically completable in the time available
- Include proper warm-up/cool-down exercises
- Use icons from: activity, zap, trending-up, minus, circle, repeat, arrow-up, triangle, diamond, chevron-down, hand, move, chevrons-up, arrow-up-circle, wind, layers, rotate-cw, chevron-up, minimize-2, user, disc

Return ONLY the JSON array, no other text."""

        try:
            # Initialize Gemini chat
            gemini_key = os.environ.get('GEMINI_API_KEY')
            if not gemini_key:
                raise HTTPException(status_code=500, detail="Gemini API key not configured")
            
            chat = LlmChat(
                api_key=gemini_key,
                session_id=f"workout_gen_{current_user.id}",
                system_message="You are a professional fitness trainer and workout planner. Generate realistic, safe, and effective workout plans in valid JSON format."
            ).with_model("gemini", "gemini-2.0-flash")
            
            user_message = UserMessage(text=prompt)
            response_obj = await chat.send_message(user_message)
            
            # Get the text response
            response_text = response_obj.text if hasattr(response_obj, 'text') else str(response_obj)
            response_text = response_text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
                response_text = response_text.strip()
            
            # Parse JSON
            workout_plans = json.loads(response_text)
            
            # Add IDs to plans
            for plan in workout_plans:
                plan['id'] = str(uuid.uuid4())
            
            # Create a copy for database insertion
            plans_for_db = []
            timestamp = datetime.now(timezone.utc).isoformat()
            for plan in workout_plans:
                db_plan = json.loads(json.dumps(plan))  # Deep copy
                db_plan['user_id'] = current_user.id
                db_plan['created_at'] = timestamp
                plans_for_db.append(db_plan)
            
            # Store new plans in database
            if plans_for_db:
                await db.ai_workout_plans.insert_many(plans_for_db)
            
            ai_plans = workout_plans
            logger.info(f"Successfully generated {len(ai_plans)} AI workout plans for user {current_user.id}")
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response: {e}")
            raise HTTPException(status_code=500, detail="Failed to parse AI response. Please try again.")
        except Exception as e:
            logger.error(f"AI workout generation error: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to generate AI workouts: {str(e)}")
    
    # Use AI-generated plans for scheduling
    suitable_plans = ai_plans
    
    # Create a map of day to minutes
    day_minutes_map = {item['day']: item['minutes'] for item in current_user.available_days}
    available_day_names = list(day_minutes_map.keys())
    
    # Calculate duration in weeks
    duration = current_user.plan_duration or 4
    duration_unit = current_user.plan_duration_unit or "weeks"
    
    if duration_unit == "months":
        total_weeks = duration * 4  # Approximate 4 weeks per month
    elif duration_unit == "years":
        total_weeks = duration * 52  # 52 weeks per year
    else:  # weeks
        total_weeks = duration
    
    # Apply max limit of 3 years (156 weeks)
    total_weeks = min(total_weeks, 156)
    
    from datetime import date, timedelta
    today = date.today()
    
    # Align start date to nearest Monday
    days_until_monday = (today.weekday() - 0) % 7  # 0 = Monday
    if days_until_monday > 0:
        start_date = today - timedelta(days=days_until_monday)
    else:
        start_date = today  # Already Monday
    
    schedule = []
    
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    # Smart rest day logic - check if user has consecutive workout days
    day_indices = {day: days_of_week.index(day) for day in available_day_names}
    sorted_indices = sorted(day_indices.values())
    
    # Check for consecutive days - find max consecutive count
    has_consecutive = False
    max_consecutive_count = 1
    current_consecutive = 1
    
    for i in range(1, len(sorted_indices)):
        if sorted_indices[i] == sorted_indices[i-1] + 1:
            current_consecutive += 1
            has_consecutive = True
            max_consecutive_count = max(max_consecutive_count, current_consecutive)
        else:
            current_consecutive = 1
    
    # Only add rest days if user has 2+ consecutive workout days
    should_add_rest_days = has_consecutive and max_consecutive_count >= 2
    # Set rest frequency based on max consecutive count to ensure rest days are added within consecutive pairs
    rest_frequency = max_consecutive_count if max_consecutive_count >= 2 else 2
    
    workout_index = 0
    consecutive_workout_count = 0  # Track consecutive workouts only
    
    for week in range(total_weeks):
        for day_offset in range(7):
            schedule_date = start_date + timedelta(days=week * 7 + day_offset)
            day_name = days_of_week[schedule_date.weekday()]
            
            # Check if user is available on this day
            if day_name in available_day_names:
                # Check if it should be a rest day (only if they have consecutive workout days)
                is_rest = should_add_rest_days and (consecutive_workout_count > 0 and consecutive_workout_count % rest_frequency == 0)
                
                if is_rest:
                    # Schedule rest day on available day
                    scheduled = ScheduledWorkout(
                        user_id=current_user.id,
                        workout_plan_id="rest",
                        scheduled_date=schedule_date.isoformat(),
                        day_of_week=day_name,
                        is_rest_day=True,
                        is_completed=False
                    )
                    consecutive_workout_count = 0  # Reset counter after rest
                else:
                    # Get time available for this day
                    minutes_available = day_minutes_map[day_name]
                    
                    # Filter workouts that fit this day's time
                    day_suitable_plans = [p for p in suitable_plans if p['duration_minutes'] <= minutes_available]
                    
                    if not day_suitable_plans:
                        day_suitable_plans = suitable_plans  # Fallback
                    
                    # Schedule workout
                    workout_plan = day_suitable_plans[workout_index % len(day_suitable_plans)]
                    scheduled = ScheduledWorkout(
                        user_id=current_user.id,
                        workout_plan_id=workout_plan['id'],
                        scheduled_date=schedule_date.isoformat(),
                        day_of_week=day_name,
                        is_rest_day=False,
                        is_completed=False
                    )
                    workout_index += 1
                    consecutive_workout_count += 1  # Increment consecutive counter
                
                schedule.append(scheduled.model_dump())
                schedule[-1]['created_at'] = schedule[-1]['created_at'].isoformat()
            else:
                # Day not available for user - natural rest day, reset consecutive counter
                consecutive_workout_count = 0
    
    if schedule:
        await db.scheduled_workouts.insert_many(schedule)
    
    return {"success": True, "scheduled_count": len(schedule), "message": "Workout schedule generated successfully"}

@api_router.get("/schedule/calendar")
async def get_calendar(current_user: User = Depends(get_current_user)):
    """Get user's workout calendar"""
    scheduled = await db.scheduled_workouts.find(
        {"user_id": current_user.id},
        {"_id": 0}
    ).sort("scheduled_date", 1).to_list(1000)
    
    # Get workout plan details from AI-generated plans
    workout_ids = [s['workout_plan_id'] for s in scheduled if not s['is_rest_day']]
    
    # First try to get from AI-generated plans
    ai_workout_plans = await db.ai_workout_plans.find(
        {"id": {"$in": workout_ids}},
        {"_id": 0}
    ).to_list(1000)
    
    # Fallback to regular workout_plans if needed (for backwards compatibility)
    if not ai_workout_plans:
        ai_workout_plans = await db.workout_plans.find(
            {"id": {"$in": workout_ids}},
            {"_id": 0}
        ).to_list(1000)
    
    plans_dict = {p['id']: p for p in ai_workout_plans}
    
    # Enrich scheduled workouts with plan details
    for item in scheduled:
        if not item['is_rest_day']:
            item['workout_details'] = plans_dict.get(item['workout_plan_id'])
        else:
            item['workout_details'] = {
                'name': 'Rest Day',
                'difficulty': 'Recovery',
                'duration_minutes': 0,
                'xp_reward': 0
            }
    
    return scheduled

@api_router.delete("/schedule/reset")
async def reset_schedule(current_user: User = Depends(get_current_user)):
    """Delete current workout schedule and AI-generated plans (will regenerate on next schedule creation)"""
    # Delete scheduled workouts
    schedule_result = await db.scheduled_workouts.delete_many({"user_id": current_user.id})
    
    # Delete AI-generated plans
    ai_plans_result = await db.ai_workout_plans.delete_many({"user_id": current_user.id})
    
    return {
        "success": True, 
        "deleted_schedule_count": schedule_result.deleted_count,
        "deleted_ai_plans_count": ai_plans_result.deleted_count,
        "message": "Schedule and AI plans deleted successfully. New AI plans will be generated when you create a new schedule."
    }

@api_router.post("/schedule/complete/{schedule_id}")
async def complete_scheduled_workout(schedule_id: str, duration_minutes: int, current_user: User = Depends(get_current_user)):
    """Mark a scheduled workout as completed"""
    scheduled = await db.scheduled_workouts.find_one({"id": schedule_id, "user_id": current_user.id})
    
    if not scheduled:
        raise HTTPException(status_code=404, detail="Scheduled workout not found")
    
    if scheduled['is_rest_day']:
        raise HTTPException(status_code=400, detail="Cannot complete a rest day")
    
    # Mark as completed
    await db.scheduled_workouts.update_one(
        {"id": schedule_id},
        {"$set": {"is_completed": True}}
    )
    
    # Record workout session (same as before)
    # Get workout plan from AI-generated plans first
    plan = await db.ai_workout_plans.find_one({"id": scheduled['workout_plan_id']})
    
    # Fallback to regular workout_plans if needed (for backwards compatibility)
    if not plan:
        plan = await db.workout_plans.find_one({"id": scheduled['workout_plan_id']})
    
    if not plan:
        raise HTTPException(status_code=404, detail="Workout plan not found")
    
    session = WorkoutSession(
        user_id=current_user.id,
        workout_plan_id=scheduled['workout_plan_id'],
        xp_earned=plan['xp_reward'],
        duration_minutes=duration_minutes,
        status="completed"
    )
    session_doc = session.model_dump()
    session_doc['date'] = session_doc['date'].isoformat()
    await db.workout_sessions.insert_one(session_doc)
    
    # Update progress (same as before)
    progress_doc = await db.progress.find_one({"user_id": current_user.id})
    if not progress_doc:
        progress_doc = Progress(user_id=current_user.id).model_dump()
    
    new_total_xp = progress_doc.get('total_xp', 0) + plan['xp_reward']
    new_level = (new_total_xp // 500) + 1
    
    today = datetime.now(timezone.utc).date()
    last_workout_date = progress_doc.get('last_workout_date')
    
    if isinstance(last_workout_date, str):
        last_workout_date = datetime.fromisoformat(last_workout_date).date()
    elif isinstance(last_workout_date, datetime):
        last_workout_date = last_workout_date.date()
    
    current_streak = progress_doc.get('streak', 0)
    
    if last_workout_date:
        days_diff = (today - last_workout_date).days
        if days_diff == 0:
            new_streak = current_streak
        elif days_diff == 1:
            new_streak = current_streak + 1
        else:
            new_streak = 1
    else:
        new_streak = 1
    
    achievements = progress_doc.get('achievements', [])
    total_workouts = await db.workout_sessions.count_documents({"user_id": current_user.id})
    
    if total_workouts >= 5 and "first_5" not in achievements:
        achievements.append("first_5")
    if total_workouts >= 10 and "first_10" not in achievements:
        achievements.append("first_10")
    if total_workouts >= 50 and "warrior_50" not in achievements:
        achievements.append("warrior_50")
    if new_streak >= 7 and "streak_7" not in achievements:
        achievements.append("streak_7")
    if new_streak >= 30 and "streak_30" not in achievements:
        achievements.append("streak_30")
    
    update_data = {
        "total_xp": new_total_xp,
        "level": new_level,
        "streak": new_streak,
        "last_workout_date": today.isoformat(),
        "achievements": achievements
    }
    
    await db.progress.update_one(
        {"user_id": current_user.id},
        {"$set": update_data},
        upsert=True
    )
    
    old_achievements = progress_doc.get('achievements', [])
    new_achievements = [a for a in achievements if a not in old_achievements]
    
    return {
        "success": True,
        "xp_earned": plan['xp_reward'],
        "new_total_xp": new_total_xp,
        "new_level": new_level,
        "new_streak": new_streak,
        "new_achievements": new_achievements
    }

# ========== STARTUP ==========

@app.on_event("startup")
async def startup_event():
    await seed_workout_plans()
    logger.info("Application started")

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()