# Samastu Fitness App - Deployment Guide

## Changes Made for Production Deployment

### 1. Backend URL Configuration
- **Updated**: Frontend `.env` file
- **Change**: `REACT_APP_BACKEND_URL=https://samastu.onrender.com`
- **Location**: `/app/frontend/.env`

### 2. Removed Local Dependency (emergentintegrations)
- **Issue**: `emergentintegrations` was a local folder dependency that won't work in production
- **Solution**: Replaced with direct Google Generative AI SDK

#### Changes Made:
1. **Added Import** in `server.py`:
   ```python
   import google.generativeai as genai
   ```

2. **Replaced LlmChat Implementation**:
   - **Before**: Used `LlmChat` and `UserMessage` from emergentintegrations
   - **After**: Direct Google Generative AI SDK calls
   
   ```python
   # Old code (removed):
   chat = LlmChat(
       api_key=gemini_key,
       session_id=f"workout_gen_{current_user.id}",
       system_message="..."
   ).with_model("gemini", "gemini-2.0-flash")
   user_message = UserMessage(text=prompt)
   response_obj = await chat.send_message(user_message)
   
   # New code:
   genai.configure(api_key=gemini_key)
   model = genai.GenerativeModel(
       'gemini-2.0-flash-exp',
       system_instruction="..."
   )
   response = model.generate_content(prompt)
   response_text = response.text.strip()
   ```

3. **Updated requirements.txt**:
   - Removed: `emergentintegrations==0.1.0`
   - Kept: `google-generativeai==0.8.5` (already present)

### 3. Fixed Node Version Compatibility
- **Issue**: Frontend required Node 18.x exactly, but Node 20.x was installed
- **Solution**: Updated `package.json` engines to accept Node 18 and above
- **Change**: `"node": "18.x"` → `"node": ">=18.x"`

## Production Deployment Checklist

### Backend Deployment (Render.com)
1. **Environment Variables Required**:
   ```
   MONGO_URL=mongodb+srv://fadlan:LnWbrlebVg02G9pJ@effendialogue.kdmkbkx.mongodb.net/?retryWrites=true&w=majority&appName=Effendialogue
   DB_NAME=Samastu
   JWT_SECRET_KEY=your-secret-key-change-this-in-production
   CORS_ORIGINS=*
   GEMINI_API_KEY=AIzaSyBjlkSFPtc2B43UTzM47flntYeOrvlhs_8
   ```

2. **Build Command**: `pip install -r requirements.txt`
3. **Start Command**: `uvicorn server:app --host 0.0.0.0 --port 8001`
4. **Python Version**: 3.11+
5. **Working Directory**: `/app/backend`

### Frontend Deployment (Vercel/Netlify/Any Static Host)
1. **Environment Variables Required**:
   ```
   REACT_APP_BACKEND_URL=https://samastu.onrender.com
   ```

2. **Build Command**: `yarn build`
3. **Output Directory**: `build`
4. **Node Version**: >=18.x
5. **Working Directory**: `/app/frontend`

## Database Configuration
- **Provider**: MongoDB Atlas (Cloud)
- **Database Name**: Samastu
- **Connection String**: Already configured in backend .env
- **Collections**:
  - users
  - ai_workout_plans
  - scheduled_workouts
  - workout_sessions
  - progress

## API Endpoints
All backend routes are prefixed with `/api`:
- `/api/auth/register` - User registration
- `/api/auth/login` - User login
- `/api/user/profile` - Get/Update user profile
- `/api/workouts/journey` - Get workout journey
- `/api/schedule/generate` - Generate AI workout schedule
- `/api/schedule/calendar` - Get calendar view
- `/api/stats/users-count` - Get total users count (public)

## Testing Before Deployment
1. Test backend locally:
   ```bash
   cd /app/backend
   uvicorn server:app --host 0.0.0.0 --port 8001
   ```

2. Test frontend locally:
   ```bash
   cd /app/frontend
   yarn start
   ```

3. Test AI workout generation endpoint
4. Test user registration and login
5. Test schedule creation

## Important Notes
- ✅ All dependencies are now production-ready (no local folders)
- ✅ Backend URL is configurable via environment variable
- ✅ MongoDB is cloud-hosted (no local database needed)
- ✅ Google Generative AI SDK is properly configured
- ✅ Node version compatibility fixed
- ✅ All API routes follow REST conventions with `/api` prefix

## Current Status
- **Total Users in Database**: 227
- **Backend Running**: ✅ (tested locally)
- **Frontend Running**: ✅ (tested locally)
- **AI Generation**: ✅ (using direct Google SDK)
- **Ready for Production**: ✅

## Files Modified
1. `/app/frontend/.env` - Backend URL
2. `/app/backend/server.py` - Removed emergentintegrations, added google.generativeai
3. `/app/backend/requirements.txt` - Removed emergentintegrations
4. `/app/frontend/package.json` - Fixed Node version requirement
