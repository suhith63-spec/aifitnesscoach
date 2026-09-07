#!/usr/bin/env python3

import streamlit as st
import pymongo
import hashlib
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional
import uuid
import os
from dotenv import load_dotenv
# Health data integration imports removed to avoid circular dependency
# These will be imported directly in main.py instead

# Mixpanel Analytics
try:
    from mixpanel_analytics import analytics
    ANALYTICS_AVAILABLE = True
except Exception:
    ANALYTICS_AVAILABLE = False

load_dotenv()

class FitnessDatabase:
    def __init__(self):
        connection_string = os.getenv("MONGODB_CONNECTION_STRING")
        database_name = os.getenv("MONGODB_DATABASE", "fitness_ai")
        
        self.client = pymongo.MongoClient(connection_string)
        self.db = self.client[database_name]
        
        self.users = self.db["users"]
        self.workouts = self.db["workouts"]
        self.diet_plans = self.db["diet_plans"]
        self.chat_history = self.db["chat_history"]
        self.daily_logs = self.db["daily_logs"]
        self.streaks = self.db["streaks"]
    
    def create_user(self, user_data: Dict) -> bool:
        try:
            if self.users.find_one({"email": user_data['email']}):
                return False
            
            hashed_password = hashlib.sha256(user_data['password'].encode('utf-8')).hexdigest()
            
            user_doc = {
                "user_id": str(uuid.uuid4()),
                "email": user_data['email'],
                "password": hashed_password,
                "name": user_data['name'],
                "age": user_data['age'],
                "weight": user_data['weight'],
                "height": user_data['height'],
                "gender": user_data['gender'],
                "primary_goal": user_data['goal'],
                "created_at": datetime.now(),
                "last_login": datetime.now()
            }
            
            self.users.insert_one(user_doc)
            return True
        except Exception as e:
            st.error(f"Error creating user: {e}")
            return False
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        try:
            user = self.users.find_one({"email": email})
            if user and user['password'] == hashlib.sha256(password.encode('utf-8')).hexdigest():
                self.users.update_one(
                    {"email": email},
                    {"$set": {"last_login": datetime.now()}}
                )
                return user
            return None
        except Exception as e:
            st.error(f"Authentication error: {e}")
            return None
    
    def save_workout_plan(self, user_id: str, workout_plan: Dict) -> bool:
        try:
            workout_doc = {
                "user_id": user_id,
                "plan": workout_plan,
                "created_at": datetime.now(),
                "active": True
            }
            self.workouts.insert_one(workout_doc)
            return True
        except Exception as e:
            st.error(f"Error saving workout plan: {e}")
            return False
    
    def save_diet_plan(self, user_id: str, diet_plan: Dict) -> bool:
        try:
            diet_doc = {
                "user_id": user_id,
                "plan": diet_plan,
                "created_at": datetime.now(),
                "active": True
            }
            self.diet_plans.insert_one(diet_doc)
            return True
        except Exception as e:
            st.error(f"Error saving diet plan: {e}")
            return False
    
    def save_chat_message(self, user_id: str, message: str, response: str, chat_type: str) -> bool:
        try:
            chat_doc = {
                "user_id": user_id,
                "message": message,
                "response": response,
                "chat_type": chat_type,
                "timestamp": datetime.now()
            }
            self.chat_history.insert_one(chat_doc)
            return True
        except Exception as e:
            st.error(f"Error saving chat: {e}")
            return False
    
    def log_daily_activity(self, user_id: str, activity_data: Dict) -> bool:
        try:
            today = datetime.now().date()
            
            existing_log = self.daily_logs.find_one({
                "user_id": user_id,
                "date": today
            })
            
            if existing_log:
                self.daily_logs.update_one(
                    {"user_id": user_id, "date": today},
                    {"$set": activity_data}
                )
            else:
                log_doc = {
                    "user_id": user_id,
                    "date": today,
                    **activity_data,
                    "created_at": datetime.now()
                }
                self.daily_logs.insert_one(log_doc)
            
            self.update_streak(user_id)
            return True
        except Exception as e:
            st.error(f"Error logging activity: {e}")
            return False
    
    def update_streak(self, user_id: str):
        try:
            thirty_days_ago = datetime.now().date() - timedelta(days=30)
            logs = list(self.daily_logs.find({
                "user_id": user_id,
                "date": {"$gte": thirty_days_ago}
            }).sort("date", -1))
            
            current_streak = 0
            max_streak = 0
            
            if logs:
                today = datetime.now().date()
                for i, log in enumerate(logs):
                    if log['date'] == today - timedelta(days=i):
                        current_streak += 1
                    else:
                        break
                
                consecutive_days = 0
                for i, log in enumerate(logs):
                    if i == 0:
                        consecutive_days = 1
                    else:
                        prev_date = logs[i-1]['date']
                        curr_date = log['date']
                        if (prev_date - curr_date).days == 1:
                            consecutive_days += 1
                        else:
                            max_streak = max(max_streak, consecutive_days)
                            consecutive_days = 1
                max_streak = max(max_streak, consecutive_days)
            
            self.streaks.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "current_streak": current_streak,
                        "max_streak": max_streak,
                        "last_updated": datetime.now()
                    }
                },
                upsert=True
            )
        except Exception as e:
            st.error(f"Error updating streak: {e}")
    
    def generate_reset_token(self, email: str) -> Optional[str]:
        """Generate password reset token"""
        try:
            user = self.users.find_one({"email": email})
            if not user:
                return None
            
            token = str(uuid.uuid4())[:8].upper()  # 8-character token
            expiry = datetime.now() + timedelta(hours=1)
            
            self.users.update_one(
                {"email": email},
                {"$set": {
                    "reset_token": token,
                    "reset_token_expiry": expiry
                }}
            )
            return token
        except Exception as e:
            st.error(f"Error generating reset token: {e}")
            return None
    
    def reset_password(self, email: str, token: str, new_password: str) -> bool:
        """Reset password using token"""
        try:
            user = self.users.find_one({"email": email})
            if not user:
                return False
            
            if user.get('reset_token') != token.upper():
                return False
            
            if user.get('reset_token_expiry') < datetime.now():
                return False
            
            hashed_password = hashlib.sha256(new_password.encode('utf-8')).hexdigest()
            
            self.users.update_one(
                {"email": email},
                {"$set": {
                    "password": hashed_password
                },
                "$unset": {
                    "reset_token": "",
                    "reset_token_expiry": ""
                }}
            )
            return True
        except Exception as e:
            st.error(f"Error resetting password: {e}")
            return False
    
    def get_user_data(self, user_id: str) -> Dict:
        try:
            user = self.users.find_one({"user_id": user_id})
            workout_plans = list(self.workouts.find({"user_id": user_id}).sort("created_at", -1))
            diet_plans = list(self.diet_plans.find({"user_id": user_id}).sort("created_at", -1))
            chat_history = list(self.chat_history.find({"user_id": user_id}).sort("timestamp", -1))
            daily_logs = list(self.daily_logs.find({"user_id": user_id}).sort("date", -1).limit(30))
            streak_data = self.streaks.find_one({"user_id": user_id})
            
            return {
                "user": user,
                "workout_plans": workout_plans,
                "diet_plans": diet_plans,
                "chat_history": chat_history,
                "daily_logs": daily_logs,
                "streak": streak_data or {"current_streak": 0, "max_streak": 0}
            }
        except Exception as e:
            st.error(f"Error fetching user data: {e}")
            return {}

class AuthenticationUI:
    def __init__(self):
        self.db = FitnessDatabase()
    
    def show_login_page(self):
        st.title("🏋️ Fitness AI Trainer")
        
        tab1, tab2, tab3 = st.tabs(["Login", "Sign Up", "Forgot Password"])
        
        with tab1:
            self.show_login_form()
        
        with tab2:
            self.show_signup_form()
        
        with tab3:
            self.show_forgot_password_form()
    
    def show_login_form(self):
        with st.form("login_form"):
            st.subheader("Welcome Back!")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            
            if st.form_submit_button("Login", type="primary"):
                if email and password:
                    user = self.db.authenticate_user(email, password)
                    if user:
                        st.session_state.user = user
                        st.session_state.authenticated = True
                        
                        # Track login
                        if ANALYTICS_AVAILABLE:
                            try:
                                analytics.track_user_login(user['user_id'])
                            except Exception:
                                pass
                                
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
                else:
                    st.error("Please fill all fields")
    
    def show_signup_form(self):
        with st.form("signup_form"):
            st.subheader("Create Account")
            
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Full Name")
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
            
            with col2:
                age = st.number_input("Age", min_value=16, max_value=80, value=25)
                weight = st.number_input("Weight (kg)", min_value=40, max_value=200, value=70)
                height = st.number_input("Height (cm)", min_value=140, max_value=220, value=170)
            
            gender = st.selectbox("Gender", ["Male", "Female", "Prefer not to say"])
            goal = st.selectbox("Primary Goal", [
                "Lose weight", "Build muscle", "Improve endurance", 
                "General fitness", "Strength training"
            ])
            
            if st.form_submit_button("Create Account", type="primary"):
                if all([name, email, password, age, weight, height]):
                    user_data = {
                        "name": name, "email": email, "password": password,
                        "age": age, "weight": weight, "height": height,
                        "gender": gender, "goal": goal
                    }
                    
                    if self.db.create_user(user_data):
                        # Track signup
                        if ANALYTICS_AVAILABLE:
                            try:
                                # We need to fetch the user ID we just created
                                user = self.db.users.find_one({"email": email})
                                if user:
                                    analytics.track_user_signup(user['user_id'], "email")
                                    analytics.set_health_goals(
                                        user['user_id'],
                                        weight, weight, # Start and current are same
                                        weight, # Goal placeholder
                                        goal
                                    )
                            except Exception:
                                pass
                                
                        st.success("Account created successfully! Please login.")
                    else:
                        st.error("Email already exists or error creating account")
                else:
                    st.error("Please fill all fields")
    
    def show_forgot_password_form(self):
        """Password reset form"""
        st.subheader("Reset Your Password")
        
        if 'reset_email' not in st.session_state:
            # Step 1: Request reset code
            with st.form("forgot_password_form"):
                st.write("Enter your email address to receive a password reset code.")
                email = st.text_input("Email")
                
                if st.form_submit_button("Send Reset Code", type="primary"):
                    if email:
                        token = self.db.generate_reset_token(email)
                        if token:
                            # Send email with token
                            from main import send_password_reset_email
                            if send_password_reset_email(email, token):
                                st.success("✅ Reset code sent to your email!")
                                st.session_state.reset_email = email
                                st.rerun()
                            else:
                                st.warning("⚠️ Email sent, but there may be SMTP configuration issues. Your reset code is: " + token)
                                st.session_state.reset_email = email
                                st.rerun()
                        else:
                            st.error("❌ Email not found in our system")
                    else:
                        st.error("Please enter your email")
        else:
            # Step 2: Reset password with code
            with st.form("reset_password_form"):
                st.write(f"Enter the reset code sent to **{st.session_state.reset_email}**")
                token = st.text_input("Reset Code")
                new_password = st.text_input("New Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Reset Password", type="primary"):
                        if not token or not new_password or not confirm_password:
                            st.error("Please fill all fields")
                        elif new_password != confirm_password:
                            st.error("Passwords don't match")
                        elif len(new_password) < 6:
                            st.error("Password must be at least 6 characters")
                        else:
                            if self.db.reset_password(st.session_state.reset_email, token, new_password):
                                st.success("✅ Password reset successful! Please login with your new password.")
                                del st.session_state.reset_email
                                st.rerun()
                            else:
                                st.error("❌ Invalid or expired reset code")
                
                with col2:
                    if st.form_submit_button("Cancel"):
                        del st.session_state.reset_email
                        st.rerun()

def show_dashboard(user_data: Dict):
    st.title(f"Welcome back, {user_data['user']['name']}! 💪")
    
    with st.sidebar:
        st.subheader("Profile")
        st.write(f"**Age:** {user_data['user']['age']}")
        st.write(f"**Weight:** {user_data['user']['weight']} kg")
        st.write(f"**Height:** {user_data['user']['height']} cm")
        st.write(f"**Goal:** {user_data['user']['primary_goal']}")
        
        streak = user_data['streak']
        st.metric("Current Streak", f"{streak['current_streak']} days")
        st.metric("Best Streak", f"{streak['max_streak']} days")
        
        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Dashboard", "💪 Workouts", "🥗 Diet Plans", 
        "💬 Chat History", "📈 Analytics", "🏥 Health Data"
    ])
    
    with tab1:
        show_dashboard_overview(user_data)
    
    with tab2:
        show_workout_plans(user_data)
    
    with tab3:
        show_diet_plans(user_data)
    
    with tab4:
        show_chat_history(user_data)
    
    with tab5:
        show_analytics(user_data)
    
    with tab6:
        show_health_data_tab(user_data)

def show_dashboard_overview(user_data: Dict):
    st.subheader("Today's Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Workouts Done", len(user_data['workout_plans']))
    
    with col2:
        st.metric("Diet Plans", len(user_data['diet_plans']))
    
    with col3:
        st.metric("Chat Sessions", len(user_data['chat_history']))
    
    with col4:
        today_log = next((log for log in user_data['daily_logs'] 
                         if log['date'] == datetime.now().date()), None)
        calories = today_log.get('calories_burned', 0) if today_log else 0
        st.metric("Calories Burned", calories)
    
    st.subheader("Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🏋️ Log Workout", type="primary"):
            log_workout_session(user_data['user']['user_id'])
    
    with col2:
        if st.button("🥗 Log Meal"):
            log_meal_session(user_data['user']['user_id'])
    
    with col3:
        if st.button("💬 Quick Chat"):
            st.session_state.show_chat = True

def log_workout_session(user_id: str):
    st.subheader("Log Today's Workout")
    
    with st.form("workout_log"):
        exercise = st.text_input("Exercise Name")
        reps = st.number_input("Reps", min_value=0, value=10)
        sets = st.number_input("Sets", min_value=0, value=3)
        duration = st.number_input("Duration (minutes)", min_value=0, value=30)
        calories = st.number_input("Estimated Calories Burned", min_value=0, value=200)
        
        if st.form_submit_button("Log Workout"):
            db = FitnessDatabase()
            activity_data = {
                "exercise": exercise,
                "reps": reps,
                "sets": sets,
                "duration_minutes": duration,
                "calories_burned": calories,
                "workout_completed": True
            }
            
            if db.log_daily_activity(user_id, activity_data):
                st.success("Workout logged successfully!")
                st.rerun()

def log_meal_session(user_id: str):
    st.subheader("Log Today's Meal")
    
    with st.form("meal_log"):
        meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack"])
        food_items = st.text_area("Food Items")
        calories = st.number_input("Calories", min_value=0, value=400)
        
        if st.form_submit_button("Log Meal"):
            db = FitnessDatabase()
            meal_data = {
                "meal_type": meal_type,
                "food_items": food_items,
                "meal_calories": calories
            }
            
            if db.save_diet_plan(user_id, meal_data):
                st.success("Meal logged successfully!")
                st.rerun()

def show_workout_plans(user_data: Dict):
    st.subheader("Your Workout Plans")
    
    if user_data['workout_plans']:
        for i, plan in enumerate(user_data['workout_plans']):
            with st.expander(f"Plan {i+1} - {plan['created_at'].strftime('%Y-%m-%d')}"):
                st.json(plan['plan'])
    else:
        st.info("No workout plans yet. Create your first plan!")

def show_diet_plans(user_data: Dict):
    st.subheader("Your Diet Plans")
    
    if user_data['diet_plans']:
        for i, plan in enumerate(user_data['diet_plans']):
            with st.expander(f"Diet Plan {i+1} - {plan['created_at'].strftime('%Y-%m-%d')}"):
                st.json(plan['plan'])
    else:
        st.info("No diet plans yet. Create your first plan!")

def show_chat_history(user_data: Dict):
    st.subheader("Chat History")
    
    if user_data['chat_history']:
        for chat in user_data['chat_history'][:10]:
            with st.expander(f"{chat['chat_type'].title()} - {chat['timestamp'].strftime('%Y-%m-%d %H:%M')}"):
                st.write(f"**You:** {chat['message']}")
                st.write(f"**AI:** {chat['response']}")
    else:
        st.info("No chat history yet.")

def show_analytics(user_data: Dict):
    st.subheader("Your Progress Analytics")
    
    if user_data['daily_logs']:
        dates = [log['date'].strftime('%Y-%m-%d') for log in user_data['daily_logs']]
        calories = [log.get('calories_burned', 0) for log in user_data['daily_logs']]
        
        chart_data = {"Date": dates, "Calories": calories}
        st.line_chart(chart_data, x="Date", y="Calories")
        
        st.subheader("This Week's Summary")
        week_logs = [log for log in user_data['daily_logs'] 
                    if (datetime.now().date() - log['date']).days <= 7]
        
        if week_logs:
            total_calories = sum(log.get('calories_burned', 0) for log in week_logs)
            total_workouts = len(week_logs)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Calories Burned", total_calories)
            with col2:
                st.metric("Workouts Completed", total_workouts)
    else:
        st.info("Start logging your workouts to see analytics!")

def show_health_data_tab(user_data: Dict):
    """Health data integration tab - placeholder for now"""
    st.subheader("🏥 Health Data Integration")
    st.info("Health data features will be integrated in the main app tabs.")
    st.write("Use the main app's 'Health Data' tab for full functionality.")


def main():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        auth_ui = AuthenticationUI()
        auth_ui.show_login_page()
    else:
        db = FitnessDatabase()
        user_data = db.get_user_data(st.session_state.user['user_id'])
        show_dashboard(user_data)

if __name__ == "__main__":
    main()