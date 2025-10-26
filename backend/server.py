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
    available_days: Optional[List[str]] = []  # days of week user is free
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserUpdate(BaseModel):
    name: Optional[str] = None
    gender: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    goal: Optional[str] = None
    equipment: Optional[List[str]] = None
    experience_level: Optional[str] = None
    available_days: Optional[List[str]] = None

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

# ========== WORKOUT ROUTES ==========

@api_router.get("/workouts/plans", response_model=List[WorkoutPlan])
async def get_workout_plans(current_user: User = Depends(get_current_user)):
    plans = await db.workout_plans.find({}, {"_id": 0}).to_list(100)
    return plans

@api_router.get("/workouts/journey")
async def get_workout_journey(current_user: User = Depends(get_current_user)):
    # Get all workout plans
    plans = await db.workout_plans.find({}, {"_id": 0}).to_list(100)
    
    # Get user's completed workouts
    completed_sessions = await db.workout_sessions.find(
        {"user_id": current_user.id},
        {"_id": 0}
    ).to_list(1000)
    
    completed_plan_ids = [session['workout_plan_id'] for session in completed_sessions]
    
    # Mark plans as completed or next
    journey = []
    for idx, plan in enumerate(plans):
        is_completed = plan['id'] in completed_plan_ids
        is_next = not is_completed and (idx == 0 or plans[idx-1]['id'] in completed_plan_ids)
        
        journey.append({
            **plan,
            "is_completed": is_completed,
            "is_next": is_next,
            "position": idx
        })
    
    return journey

@api_router.post("/workouts/complete")
async def complete_workout(workout_data: WorkoutComplete, current_user: User = Depends(get_current_user)):
    # Get workout plan
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

# ========== SCHEDULE ROUTES ==========

@api_router.post("/schedule/generate")
async def generate_schedule(current_user: User = Depends(get_current_user)):
    """Generate a personalized workout schedule based on user's available days"""
    if not current_user.available_days or len(current_user.available_days) == 0:
        raise HTTPException(status_code=400, detail="No available days set. Please update your profile.")
    
    # Delete existing schedule
    await db.scheduled_workouts.delete_many({"user_id": current_user.id})
    
    # Get workout plans filtered by experience level
    all_plans = await db.workout_plans.find({}, {"_id": 0}).to_list(100)
    
    # Filter plans by difficulty
    experience_map = {
        "beginner": "Beginner",
        "intermediate": "Intermediate",
        "advanced": "Advanced"
    }
    
    target_difficulty = experience_map.get(current_user.experience_level, "Beginner")
    suitable_plans = [p for p in all_plans if p['difficulty'] == target_difficulty or p['difficulty'] == 'Beginner']
    
    if not suitable_plans:
        suitable_plans = all_plans  # Fallback to all plans
    
    # Generate schedule for next 4 weeks
    from datetime import date, timedelta
    today = date.today()
    schedule = []
    
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    # Calculate how many workout days per week
    available_count = len(current_user.available_days)
    
    # Determine rest day frequency (every 2-3 workout days)
    rest_frequency = 3 if available_count >= 4 else 2
    
    workout_index = 0
    workout_count = 0
    
    for week in range(4):
        for day_offset in range(7):
            schedule_date = today + timedelta(days=week * 7 + day_offset)
            day_name = days_of_week[schedule_date.weekday()]
            
            # Check if user is available on this day
            if day_name in current_user.available_days:
                # Check if it should be a rest day
                is_rest = (workout_count > 0 and workout_count % rest_frequency == 0)
                
                if is_rest:
                    # Schedule rest day
                    scheduled = ScheduledWorkout(
                        user_id=current_user.id,
                        workout_plan_id="rest",
                        scheduled_date=schedule_date.isoformat(),
                        day_of_week=day_name,
                        is_rest_day=True,
                        is_completed=False
                    )
                else:
                    # Schedule workout
                    workout_plan = suitable_plans[workout_index % len(suitable_plans)]
                    scheduled = ScheduledWorkout(
                        user_id=current_user.id,
                        workout_plan_id=workout_plan['id'],
                        scheduled_date=schedule_date.isoformat(),
                        day_of_week=day_name,
                        is_rest_day=False,
                        is_completed=False
                    )
                    workout_index += 1
                
                schedule.append(scheduled.model_dump())
                schedule[-1]['created_at'] = schedule[-1]['created_at'].isoformat()
                workout_count += 1
    
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
    
    # Get workout plan details
    workout_ids = [s['workout_plan_id'] for s in scheduled if not s['is_rest_day']]
    workout_plans = await db.workout_plans.find(
        {"id": {"$in": workout_ids}},
        {"_id": 0}
    ).to_list(1000)
    
    plans_dict = {p['id']: p for p in workout_plans}
    
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
    """Delete current workout schedule"""
    result = await db.scheduled_workouts.delete_many({"user_id": current_user.id})
    return {"success": True, "deleted_count": result.deleted_count, "message": "Schedule deleted successfully"}

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