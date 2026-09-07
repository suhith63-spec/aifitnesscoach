#!/usr/bin/env python3

import streamlit as st
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv
from health_data_integration import HealthDataManager

load_dotenv()

class GoogleFitAPI:
    def __init__(self):
        self.base_url = "https://www.googleapis.com/fitness/v1/users/me"
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = None
        self.health_manager = HealthDataManager()
        
        # Try to load token from DB if user is logged in
        if 'user' in st.session_state:
            self.load_token(st.session_state.user['user_id'])

    def load_token(self, user_id: str):
        """Load OAuth token from database"""
        try:
            token_doc = self.health_manager.db.oauth_tokens.find_one({"user_id": user_id})
            if token_doc:
                self.access_token = token_doc.get("access_token")
                self.refresh_token = token_doc.get("refresh_token")
                self.token_expiry = token_doc.get("expiry")
                print(f"✅ Loaded Google Fit token for user {user_id}")
                
                # Check expiry and refresh if needed
                if self.is_token_expired():
                    print("🔄 Token expired, refreshing...")
                    self.refresh_access_token()
        except Exception as e:
            print(f"Error loading token: {e}")

    def save_token(self, user_id: str, token_data: Dict):
        """Save OAuth token to database"""
        try:
            expiry = datetime.now() + timedelta(seconds=token_data.get("expires_in", 3600))
            
            token_doc = {
                "user_id": user_id,
                "access_token": token_data.get("access_token"),
                "refresh_token": token_data.get("refresh_token", self.refresh_token), # Keep old refresh token if new one not provided
                "expiry": expiry,
                "updated_at": datetime.now()
            }
            
            self.health_manager.db.oauth_tokens.update_one(
                {"user_id": user_id},
                {"$set": token_doc},
                upsert=True
            )
            
            # Update local state
            self.access_token = token_doc["access_token"]
            self.refresh_token = token_doc["refresh_token"]
            self.token_expiry = expiry
            print(f"💾 Saved Google Fit token for {user_id}")
            return True
        except Exception as e:
            st.error(f"Error saving token: {e}")
            return False

    def is_token_expired(self) -> bool:
        """Check if current access token is expired"""
        if not self.token_expiry:
            return True
        # Buffer of 5 minutes
        return datetime.now() > (self.token_expiry - timedelta(minutes=5))

    def refresh_access_token(self) -> bool:
        """Refresh access token using refresh token"""
        if not self.refresh_token:
            print("❌ No refresh token available")
            return False
            
        try:
            client_id = os.getenv("GOOGLE_CLIENT_ID")
            client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
            token_url = "https://oauth2.googleapis.com/token"
            
            data = {
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": self.refresh_token,
                "grant_type": "refresh_token"
            }
            
            response = requests.post(token_url, data=data)
            if response.status_code == 200:
                token_data = response.json()
                if 'user' in st.session_state:
                    self.save_token(st.session_state.user['user_id'], token_data)
                return True
            else:
                print(f"❌ Refresh failed: {response.text}")
                return False
        except Exception as e:
            print(f"Error refreshing token: {e}")
            return False
    
    def get_auth_url(self) -> str:
        """Generate Google OAuth URL for Fit API access"""
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        redirect_uri = "http://localhost:8501"
        scope = "https://www.googleapis.com/auth/fitness.heart_rate.read https://www.googleapis.com/auth/fitness.activity.read https://www.googleapis.com/auth/fitness.sleep.read"
        
        auth_url = f"https://accounts.google.com/o/oauth2/auth?client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}&response_type=code&access_type=offline"
        return auth_url
    
    def exchange_code_for_token(self, auth_code: str) -> bool:
        """Exchange authorization code for access token"""
        try:
            client_id = os.getenv("GOOGLE_CLIENT_ID")
            client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
            redirect_uri = "http://localhost:8501"
            
            token_url = "https://oauth2.googleapis.com/token"
            data = {
                "client_id": client_id,
                "client_secret": client_secret,
                "code": auth_code,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri
            }
            
            response = requests.post(token_url, data=data)
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get("access_token")
                
                # Save to DB if user is logged in
                if 'user' in st.session_state:
                    self.save_token(st.session_state.user['user_id'], token_data)
                
                return True
            return False
        except Exception as e:
            st.error(f"Token exchange failed: {e}")
            return False
    
    def get_headers(self) -> Dict:
        """Get authorization headers, refreshing token if needed"""
        if self.is_token_expired():
            self.refresh_access_token()
            
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def get_heart_rate_data(self, days: int = 7) -> List[Dict]:
        """Fetch heart rate data from Google Fit"""
        try:
            if not self.access_token:
                return []
            
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            # Convert to nanoseconds (Google Fit format)
            start_ns = int(start_time.timestamp() * 1000000000)
            end_ns = int(end_time.timestamp() * 1000000000)
            
            url = f"{self.base_url}/dataSources/derived:com.google.heart_rate.bpm:com.google.android.gms:merge_heart_rate_bpm/datasets/{start_ns}-{end_ns}"
            
            response = requests.get(url, headers=self.get_headers())
            
            if response.status_code == 200:
                data = response.json()
                heart_rate_data = []
                
                for point in data.get("point", []):
                    timestamp = datetime.fromtimestamp(int(point["startTimeNanos"]) / 1000000000)
                    bpm = point["value"][0]["fpVal"]
                    
                    heart_rate_data.append({
                        "timestamp": timestamp,
                        "bpm": int(bpm),
                        "activity_type": "google_fit"
                    })
                
                return heart_rate_data
            return []
        except Exception as e:
            st.error(f"Error fetching heart rate: {e}")
            return []
    
    def get_steps_data(self, days: int = 7) -> List[Dict]:
        """Fetch steps data from Google Fit"""
        try:
            if not self.access_token:
                return []
            
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            start_ns = int(start_time.timestamp() * 1000000000)
            end_ns = int(end_time.timestamp() * 1000000000)
            
            url = f"{self.base_url}/dataSources/derived:com.google.step_count.delta:com.google.android.gms:estimated_steps/datasets/{start_ns}-{end_ns}"
            
            response = requests.get(url, headers=self.get_headers())
            
            if response.status_code == 200:
                data = response.json()
                steps_data = []
                
                for point in data.get("point", []):
                    timestamp = datetime.fromtimestamp(int(point["startTimeNanos"]) / 1000000000)
                    steps = point["value"][0]["intVal"]
                    
                    steps_data.append({
                        "date": timestamp.replace(hour=0, minute=0, second=0, microsecond=0),
                        "steps": steps,
                        "distance_km": steps * 0.0008  # Rough conversion
                    })
                
                return steps_data
            return []
        except Exception as e:
            st.error(f"Error fetching steps: {e}")
            return []
    
    def get_calories_data(self, days: int = 7) -> List[Dict]:
        """Fetch calories data from Google Fit"""
        try:
            if not self.access_token:
                return []
            
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            start_ns = int(start_time.timestamp() * 1000000000)
            end_ns = int(end_time.timestamp() * 1000000000)
            
            url = f"{self.base_url}/dataSources/derived:com.google.calories.expended:com.google.android.gms:merge_calories_expended/datasets/{start_ns}-{end_ns}"
            
            response = requests.get(url, headers=self.get_headers())
            
            if response.status_code == 200:
                data = response.json()
                calories_data = []
                
                for point in data.get("point", []):
                    timestamp = datetime.fromtimestamp(int(point["startTimeNanos"]) / 1000000000)
                    calories = point["value"][0]["fpVal"]
                    
                    calories_data.append({
                        "date": timestamp.replace(hour=0, minute=0, second=0, microsecond=0),
                        "calories_burned": int(calories),
                        "activity": "google_fit_sync"
                    })
                
                return calories_data
            return []
        except Exception as e:
            st.error(f"Error fetching calories: {e}")
            return []
    
    def get_sleep_data(self, days: int = 7) -> List[Dict]:
        """Fetch sleep data from Google Fit"""
        try:
            if not self.access_token:
                return []
            
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            start_ns = int(start_time.timestamp() * 1000000000)
            end_ns = int(end_time.timestamp() * 1000000000)
            
            url = f"{self.base_url}/dataSources/derived:com.google.sleep.segment:com.google.android.gms:merged/datasets/{start_ns}-{end_ns}"
            
            response = requests.get(url, headers=self.get_headers())
            
            if response.status_code == 200:
                data = response.json()
                sleep_data = []
                
                for point in data.get("point", []):
                    start_time_ns = int(point["startTimeNanos"])
                    end_time_ns = int(point["endTimeNanos"])
                    
                    sleep_duration = (end_time_ns - start_time_ns) / 1000000000 / 3600  # Convert to hours
                    sleep_date = datetime.fromtimestamp(start_time_ns / 1000000000)
                    
                    sleep_data.append({
                        "date": sleep_date.replace(hour=0, minute=0, second=0, microsecond=0),
                        "sleep_hours": round(sleep_duration, 1),
                        "sleep_quality": "good"  # Google Fit doesn't provide quality
                    })
                
                return sleep_data
            return []
        except Exception as e:
            st.error(f"Error fetching sleep: {e}")
            return []
    
    def get_activity_data(self, days: int = 7) -> List[Dict]:
        """Fetch activity sessions from Google Fit"""
        try:
            if not self.access_token:
                return []
            
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            start_ms = int(start_time.timestamp() * 1000)
            end_ms = int(end_time.timestamp() * 1000)
            
            url = f"{self.base_url}/sessions"
            params = {
                "startTime": start_time.isoformat() + "Z",
                "endTime": end_time.isoformat() + "Z"
            }
            
            response = requests.get(url, headers=self.get_headers(), params=params)
            
            if response.status_code == 200:
                data = response.json()
                activities_data = []
                
                for session in data.get("session", []):
                    start_time_ms = int(session["startTimeMillis"])
                    end_time_ms = int(session["endTimeMillis"])
                    
                    duration = (end_time_ms - start_time_ms) / 1000 / 60  # Convert to minutes
                    activity_type = session.get("name", "unknown")
                    
                    activities_data.append({
                        "date": datetime.fromtimestamp(start_time_ms / 1000).replace(hour=0, minute=0, second=0, microsecond=0),
                        "activity_type": activity_type.lower(),
                        "duration_minutes": int(duration),
                        "intensity": "moderate"
                    })
                
                return activities_data
            return []
        except Exception as e:
            st.error(f"Error fetching activities: {e}")
            return []
    
    def sync_all_data(self, user_id: str, days: int = 7) -> Dict:
        """Sync all Google Fit data to database"""
        try:
            sync_results = {
                "heart_rate": 0,
                "steps": 0,
                "calories": 0,
                "sleep": 0,
                "activities": 0
            }
            
            # Sync heart rate data
            heart_rate_data = self.get_heart_rate_data(days)
            for hr in heart_rate_data:
                if self.health_manager.save_heart_rate(user_id, hr["bpm"], hr["activity_type"]):
                    sync_results["heart_rate"] += 1
            
            # Sync steps data
            steps_data = self.get_steps_data(days)
            for step in steps_data:
                if self.health_manager.save_steps(user_id, step["steps"], step["distance_km"]):
                    sync_results["steps"] += 1
            
            # Sync calories data
            calories_data = self.get_calories_data(days)
            for cal in calories_data:
                if self.health_manager.save_calories(user_id, cal["calories_burned"], cal["activity"]):
                    sync_results["calories"] += 1
            
            # Sync sleep data
            sleep_data = self.get_sleep_data(days)
            for sleep in sleep_data:
                if self.health_manager.save_sleep(user_id, sleep["sleep_hours"], sleep["sleep_quality"]):
                    sync_results["sleep"] += 1
            
            # Sync activities data
            activities_data = self.get_activity_data(days)
            for activity in activities_data:
                if self.health_manager.save_activity(user_id, activity["activity_type"], activity["duration_minutes"]):
                    sync_results["activities"] += 1
            
            return sync_results
        except Exception as e:
            st.error(f"Error syncing data: {e}")
            return {}

def google_fit_integration_ui(user_id: str):
    """Streamlit UI for Google Fit integration"""
    
    st.subheader("🔗 Google Fit Integration")
    
    if 'google_fit_api' not in st.session_state:
        st.session_state.google_fit_api = GoogleFitAPI()
    
    # Check if user is authenticated
    if not st.session_state.google_fit_api.access_token:
        st.info("Connect your Google Fit account to sync fitness data from all your wearables!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Supported Devices:**")
            st.write("• Apple Watch (via Apple Health)")
            st.write("• Samsung Galaxy Watch")
            st.write("• Fitbit devices")
            st.write("• Wear OS watches")
            st.write("• Mi Band / Amazfit")
            st.write("• Any device that syncs to Google Fit")
        
        with col2:
            st.write("**Data We'll Sync:**")
            st.write("❤️ Heart rate data")
            st.write("👟 Daily steps & distance")
            st.write("🔥 Calories burned")
            st.write("💤 Sleep duration")
            st.write("🏃 Workout sessions")
        
        # Google Fit authentication
        if not os.getenv("GOOGLE_CLIENT_ID") or not os.getenv("GOOGLE_CLIENT_SECRET"):
            st.error("⚠️ Google Cloud Credentials not found!")
            st.info("Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in your .env file.")
            with st.expander("Help: How to get credentials"):
                st.markdown("""
                1. Go to Google Cloud Console
                2. Create OAuth 2.0 Credentials
                3. Add to .env file
                """)
            return

        auth_url = st.session_state.google_fit_api.get_auth_url()
        
        st.markdown("### Step 1: Authorize Google Fit Access")
        st.link_button("🔗 Connect Google Fit Account", auth_url, type="primary")
        
        st.markdown("### Step 2: Enter Authorization Code")
        auth_code = st.text_input("Paste the authorization code here:")
        
        if st.button("🔐 Authenticate", type="primary"):
            if auth_code:
                if st.session_state.google_fit_api.exchange_code_for_token(auth_code):
                    st.success("✅ Google Fit connected successfully!")
                    st.rerun()
                else:
                    st.error("❌ Authentication failed. Please try again.")
            else:
                st.error("Please enter the authorization code.")
    
    else:
        st.success("✅ Google Fit is connected!")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            sync_days = st.selectbox("Sync Period", [1, 7, 14, 30], index=1)
        
        with col2:
            if st.button("🔄 Sync Now", type="primary"):
                with st.spinner("Syncing Google Fit data..."):
                    results = st.session_state.google_fit_api.sync_all_data(user_id, sync_days)
                    
                    if results:
                        st.success("✅ Sync completed!")
                        
                        # Show sync results
                        st.write("**Synced Data:**")
                        for data_type, count in results.items():
                            if count > 0:
                                st.write(f"• {data_type.replace('_', ' ').title()}: {count} records")
                    else:
                        st.error("❌ Sync failed. Please try again.")
        
        with col3:
            if st.button("🔓 Disconnect"):
                # Remove from DB
                if 'user' in st.session_state:
                    st.session_state.google_fit_api.health_manager.db.oauth_tokens.delete_one(
                        {"user_id": st.session_state.user['user_id']}
                    )
                st.session_state.google_fit_api.access_token = None
                st.session_state.google_fit_api.refresh_token = None
                st.success("Google Fit disconnected.")
                st.rerun()
        
        # Auto-sync option
        st.markdown("---")
        st.subheader("⚙️ Auto-Sync Settings")
        
        auto_sync = st.checkbox("Enable automatic daily sync")
        if auto_sync:
            st.info("🔄 Auto-sync will run daily to keep your data up to date.")
            
            # You can implement a background task here for auto-sync
            # For now, just show the option

def main():
    st.set_page_config(page_title="Google Fit Integration", layout="wide")
    
    st.title("🔗 Google Fit Integration")
    
    # Mock user ID for demo
    user_id = "demo_user_123"
    
    google_fit_integration_ui(user_id)
    
    # Instructions for setup
    with st.expander("🛠️ Setup Instructions"):
        st.markdown("""
        **To enable Google Fit integration:**
        
        1. **Create Google Cloud Project:**
           - Go to [Google Cloud Console](https://console.cloud.google.com/)
           - Create a new project or select existing one
           
        2. **Enable Google Fit API:**
           - Go to APIs & Services > Library
           - Search for "Fitness API" and enable it
           
        3. **Create OAuth Credentials:**
           - Go to APIs & Services > Credentials
           - Create OAuth 2.0 Client ID
           - Add `http://localhost:8501` as authorized redirect URI
           
        4. **Add to .env file:**
           ```
           GOOGLE_CLIENT_ID=your-client-id
           GOOGLE_CLIENT_SECRET=your-client-secret
           ```
           
        5. **Install required packages:**
           ```bash
           pip install google-auth google-auth-oauthlib google-auth-httplib2
           ```
        """)

if __name__ == "__main__":
    main()