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
import asyncio
import random
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

load_dotenv()

class HealthDataManager:
    def __init__(self):
        connection_string = os.getenv("MONGODB_CONNECTION_STRING")
        database_name = os.getenv("MONGODB_DATABASE", "fitness_ai")
        
        self.client = pymongo.MongoClient(connection_string)
        self.db = self.client[database_name]
        
        self.health_data = self.db["health_data"]
        self.heart_rate = self.db["heart_rate"]
        self.steps = self.db["steps"]
        self.calories = self.db["calories"]
        self.sleep = self.db["sleep"]
        self.activities = self.db["activities"]
    
    def save_health_metrics(self, user_id: str, data: Dict) -> bool:
        try:
            health_doc = {
                "user_id": user_id,
                "timestamp": datetime.now(),
                "date": datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
                **data
            }
            self.health_data.insert_one(health_doc)
            return True
        except Exception as e:
            st.error(f"Error saving health data: {e}")
            return False
    
    def save_heart_rate(self, user_id: str, bpm: int, activity_type: str = "resting") -> bool:
        try:
            hr_doc = {
                "user_id": user_id,
                "bpm": bpm,
                "activity_type": activity_type,
                "timestamp": datetime.now(),
                "date": datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            }
            self.heart_rate.insert_one(hr_doc)
            return True
        except Exception as e:
            st.error(f"Error saving heart rate: {e}")
            return False
    
    def save_steps(self, user_id: str, steps: int, distance: float = 0) -> bool:
        try:
            steps_doc = {
                "user_id": user_id,
                "steps": steps,
                "distance_km": distance,
                "timestamp": datetime.now(),
                "date": datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            }
            self.steps.insert_one(steps_doc)
            return True
        except Exception as e:
            st.error(f"Error saving steps: {e}")
            return False
    
    def save_calories(self, user_id: str, calories_burned: int, activity: str = "general") -> bool:
        try:
            cal_doc = {
                "user_id": user_id,
                "calories_burned": calories_burned,
                "activity": activity,
                "timestamp": datetime.now(),
                "date": datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            }
            self.calories.insert_one(cal_doc)
            return True
        except Exception as e:
            st.error(f"Error saving calories: {e}")
            return False
    
    def save_sleep(self, user_id: str, sleep_hours: float, sleep_quality: str = "good") -> bool:
        try:
            sleep_doc = {
                "user_id": user_id,
                "sleep_hours": sleep_hours,
                "sleep_quality": sleep_quality,
                "bedtime": datetime.now() - timedelta(hours=sleep_hours),
                "wake_time": datetime.now(),
                "date": datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            }
            self.sleep.insert_one(sleep_doc)
            return True
        except Exception as e:
            st.error(f"Error saving sleep: {e}")
            return False
    
    def save_activity(self, user_id: str, activity_type: str, duration: int, intensity: str = "moderate") -> bool:
        try:
            activity_doc = {
                "user_id": user_id,
                "activity_type": activity_type,
                "duration_minutes": duration,
                "intensity": intensity,
                "timestamp": datetime.now(),
                "date": datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            }
            self.activities.insert_one(activity_doc)
            return True
        except Exception as e:
            st.error(f"Error saving activity: {e}")
            return False
    
    def get_health_analytics(self, user_id: str, days: int = 30) -> Dict:
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            # Get all health data
            heart_rate_data = list(self.heart_rate.find({
                "user_id": user_id,
                "date": {"$gte": start_date}
            }).sort("timestamp", 1))
            
            steps_data = list(self.steps.find({
                "user_id": user_id,
                "date": {"$gte": start_date}
            }).sort("date", 1))
            
            calories_data = list(self.calories.find({
                "user_id": user_id,
                "date": {"$gte": start_date}
            }).sort("date", 1))
            
            sleep_data = list(self.sleep.find({
                "user_id": user_id,
                "date": {"$gte": start_date}
            }).sort("date", 1))
            
            activities_data = list(self.activities.find({
                "user_id": user_id,
                "date": {"$gte": start_date}
            }).sort("timestamp", 1))
            
            return {
                "heart_rate": heart_rate_data,
                "steps": steps_data,
                "calories": calories_data,
                "sleep": sleep_data,
                "activities": activities_data
            }
        except Exception as e:
            st.error(f"Error fetching analytics: {e}")
            return {}

class HealthDataSimulator:
    """Simulate health data for demo purposes"""
    
    @staticmethod
    def generate_heart_rate_data(days: int = 7) -> List[Dict]:
        data = []
        for i in range(days * 24):  # Hourly data
            timestamp = datetime.now() - timedelta(hours=i)
            
            # Simulate realistic heart rate patterns
            hour = timestamp.hour
            if 22 <= hour or hour <= 6:  # Sleep
                bpm = random.randint(50, 70)
                activity = "sleeping"
            elif 7 <= hour <= 9 or 17 <= hour <= 19:  # Active periods
                bpm = random.randint(80, 120)
                activity = "active"
            else:  # Resting
                bpm = random.randint(65, 85)
                activity = "resting"
            
            data.append({
                "timestamp": timestamp,
                "bpm": bpm,
                "activity_type": activity
            })
        return data
    
    @staticmethod
    def generate_steps_data(days: int = 7) -> List[Dict]:
        data = []
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            steps = random.randint(3000, 15000)
            distance = steps * 0.0008  # Rough conversion
            
            data.append({
                "date": date.replace(hour=0, minute=0, second=0, microsecond=0),
                "steps": steps,
                "distance_km": round(distance, 2)
            })
        return data
    
    @staticmethod
    def generate_sleep_data(days: int = 7) -> List[Dict]:
        data = []
        qualities = ["excellent", "good", "fair", "poor"]
        
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            sleep_hours = round(random.uniform(5.5, 9.5), 1)
            quality = random.choice(qualities)
            
            data.append({
                "date": date.replace(hour=0, minute=0, second=0, microsecond=0),
                "sleep_hours": sleep_hours,
                "sleep_quality": quality
            })
        return data

def health_data_input_ui(user_id: str, health_manager: HealthDataManager):
    """UI for manual health data input"""
    
    st.subheader("📊 Health Data Input")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "❤️ Heart Rate", "👟 Steps", "🔥 Calories", "💤 Sleep", "🏃 Activity"
    ])
    
    with tab1:
        st.write("**Heart Rate Monitoring**")
        col1, col2 = st.columns(2)
        with col1:
            bpm = st.number_input("Heart Rate (BPM)", min_value=40, max_value=200, value=75)
            activity_type = st.selectbox("Activity Type", ["resting", "active", "exercise", "sleeping"])
        with col2:
            if st.button("Save Heart Rate", type="primary"):
                if health_manager.save_heart_rate(user_id, bpm, activity_type):
                    st.success("Heart rate saved!")
    
    with tab2:
        st.write("**Daily Steps**")
        col1, col2 = st.columns(2)
        with col1:
            steps = st.number_input("Steps", min_value=0, max_value=50000, value=8000)
            distance = st.number_input("Distance (km)", min_value=0.0, max_value=50.0, value=6.4)
        with col2:
            if st.button("Save Steps", type="primary"):
                if health_manager.save_steps(user_id, steps, distance):
                    st.success("Steps saved!")
    
    with tab3:
        st.write("**Calories Burned**")
        col1, col2 = st.columns(2)
        with col1:
            calories = st.number_input("Calories Burned", min_value=0, max_value=2000, value=300)
            activity = st.selectbox("Activity", ["walking", "running", "cycling", "gym", "swimming", "general"])
        with col2:
            if st.button("Save Calories", type="primary"):
                if health_manager.save_calories(user_id, calories, activity):
                    st.success("Calories saved!")
    
    with tab4:
        st.write("**Sleep Tracking**")
        col1, col2 = st.columns(2)
        with col1:
            sleep_hours = st.number_input("Sleep Hours", min_value=0.0, max_value=12.0, value=7.5, step=0.5)
            sleep_quality = st.selectbox("Sleep Quality", ["excellent", "good", "fair", "poor"])
        with col2:
            if st.button("Save Sleep", type="primary"):
                if health_manager.save_sleep(user_id, sleep_hours, sleep_quality):
                    st.success("Sleep data saved!")
    
    with tab5:
        st.write("**Activity Tracking**")
        col1, col2 = st.columns(2)
        with col1:
            activity_type = st.selectbox("Activity Type", ["walking", "running", "cycling", "swimming", "gym", "yoga", "sports"])
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=300, value=30)
        with col2:
            intensity = st.selectbox("Intensity", ["light", "moderate", "vigorous"])
            if st.button("Save Activity", type="primary"):
                if health_manager.save_activity(user_id, activity_type, duration, intensity):
                    st.success("Activity saved!")

def legendary_health_analytics(user_id: str, health_manager: HealthDataManager):
    """Legendary health data analytics dashboard"""
    
    st.title("🏆 Legendary Health Analytics")
    
    # Get analytics data
    analytics_data = health_manager.get_health_analytics(user_id, days=30)
    
    if not any(analytics_data.values()):
        st.info("No health data available. Add some data or generate sample data below.")
        
        if st.button("🎲 Generate Sample Data (Demo)"):
            simulator = HealthDataSimulator()
            
            # Generate and save sample data
            heart_data = simulator.generate_heart_rate_data(7)
            for hr in heart_data[:50]:  # Limit for demo
                health_manager.save_heart_rate(user_id, hr["bpm"], hr["activity_type"])
            
            steps_data = simulator.generate_steps_data(7)
            for step in steps_data:
                health_manager.save_steps(user_id, step["steps"], step["distance_km"])
            
            sleep_data = simulator.generate_sleep_data(7)
            for sleep in sleep_data:
                health_manager.save_sleep(user_id, sleep["sleep_hours"], sleep["sleep_quality"])
            
            st.success("Sample data generated! Refresh to see analytics.")
            st.rerun()
        return
    
    # Create comprehensive analytics
    col1, col2, col3, col4 = st.columns(4)
    
    # Key metrics
    with col1:
        if analytics_data["heart_rate"]:
            avg_hr = sum(hr["bpm"] for hr in analytics_data["heart_rate"]) / len(analytics_data["heart_rate"])
            st.metric("Avg Heart Rate", f"{int(avg_hr)} BPM")
    
    with col2:
        if analytics_data["steps"]:
            total_steps = sum(step["steps"] for step in analytics_data["steps"])
            st.metric("Total Steps", f"{total_steps:,}")
    
    with col3:
        if analytics_data["calories"]:
            total_calories = sum(cal["calories_burned"] for cal in analytics_data["calories"])
            st.metric("Calories Burned", f"{total_calories:,}")
    
    with col4:
        if analytics_data["sleep"]:
            avg_sleep = sum(sleep["sleep_hours"] for sleep in analytics_data["sleep"]) / len(analytics_data["sleep"])
            st.metric("Avg Sleep", f"{avg_sleep:.1f}h")
    
    # Heart Rate Analysis
    if analytics_data["heart_rate"]:
        st.subheader("❤️ Heart Rate Analysis")
        
        hr_df = pd.DataFrame(analytics_data["heart_rate"])
        hr_df['timestamp'] = pd.to_datetime(hr_df['timestamp'])
        
        fig_hr = px.line(hr_df, x='timestamp', y='bpm', color='activity_type',
                title="Heart Rate Over Time")
        st.plotly_chart(fig_hr)
        
        # Heart rate zones
        col1, col2 = st.columns(2)
        with col1:
            hr_zones = {
                "Resting (50-70)": len([hr for hr in analytics_data["heart_rate"] if 50 <= hr["bpm"] <= 70]),
                "Fat Burn (70-85)": len([hr for hr in analytics_data["heart_rate"] if 70 < hr["bpm"] <= 85]),
                "Cardio (85-120)": len([hr for hr in analytics_data["heart_rate"] if 85 < hr["bpm"] <= 120]),
                "Peak (120+)": len([hr for hr in analytics_data["heart_rate"] if hr["bpm"] > 120])
            }
            
            fig_zones = px.pie(values=list(hr_zones.values()), names=list(hr_zones.keys()),
                              title="Heart Rate Zones Distribution")
            st.plotly_chart(fig_zones)
        
        with col2:
            # Heart rate variability insights
            st.write("**Heart Rate Insights:**")
            max_hr = max(hr["bpm"] for hr in analytics_data["heart_rate"])
            min_hr = min(hr["bpm"] for hr in analytics_data["heart_rate"])
            
            st.write(f"• Max HR: {max_hr} BPM")
            st.write(f"• Min HR: {min_hr} BPM")
            st.write(f"• HR Range: {max_hr - min_hr} BPM")
            
            if avg_hr < 60:
                st.success("🏃 Excellent cardiovascular fitness!")
            elif avg_hr < 80:
                st.info("💪 Good cardiovascular health")
            else:
                st.warning("⚠️ Consider more cardio exercise")
    
    # Steps and Activity Analysis
    if analytics_data["steps"]:
        st.subheader("👟 Steps & Activity Analysis")
        
        steps_df = pd.DataFrame(analytics_data["steps"])
        steps_df['date'] = pd.to_datetime(steps_df['date'])
        
        fig_steps = px.bar(steps_df, x='date', y='steps',
                  title="Daily Steps")
        st.plotly_chart(fig_steps)
        
        col1, col2 = st.columns(2)
        with col1:
            avg_steps = total_steps / len(analytics_data["steps"])
            st.write("**Steps Analysis:**")
            st.write(f"• Daily Average: {int(avg_steps):,} steps")
            st.write(f"• Best Day: {max(step['steps'] for step in analytics_data['steps']):,} steps")
            
            if avg_steps >= 10000:
                st.success("🎯 Excellent! Meeting daily step goal")
            elif avg_steps >= 7500:
                st.info("👍 Good activity level")
            else:
                st.warning("📈 Try to increase daily steps")
        
        with col2:
            total_distance = sum(step["distance_km"] for step in analytics_data["steps"])
            st.write("**Distance Analysis:**")
            st.write(f"• Total Distance: {total_distance:.1f} km")
            st.write(f"• Daily Average: {total_distance/len(analytics_data['steps']):.1f} km")
    
    # Sleep Analysis
    if analytics_data["sleep"]:
        st.subheader("💤 Sleep Analysis")
        
        sleep_df = pd.DataFrame(analytics_data["sleep"])
        sleep_df['date'] = pd.to_datetime(sleep_df['date'])
        
        fig_sleep = px.bar(sleep_df, x='date', y='sleep_hours', color='sleep_quality',
                  title="Sleep Duration and Quality")
        st.plotly_chart(fig_sleep)
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Sleep Insights:**")
            st.write(f"• Average Sleep: {avg_sleep:.1f} hours")
            
            quality_counts = {}
            for sleep in analytics_data["sleep"]:
                quality = sleep["sleep_quality"]
                quality_counts[quality] = quality_counts.get(quality, 0) + 1
            
            best_quality = max(quality_counts, key=quality_counts.get)
            st.write(f"• Most Common Quality: {best_quality}")
            
            if avg_sleep >= 7.5:
                st.success("😴 Excellent sleep duration!")
            elif avg_sleep >= 6.5:
                st.info("🌙 Adequate sleep")
            else:
                st.warning("⏰ Consider more sleep")
        
        with col2:
            fig_quality = px.pie(values=list(quality_counts.values()), 
                               names=list(quality_counts.keys()),
                               title="Sleep Quality Distribution")
            st.plotly_chart(fig_quality)
    
    # Activity Summary
    if analytics_data["activities"]:
        st.subheader("🏃 Activity Summary")
        
        activity_counts = {}
        total_duration = 0
        
        for activity in analytics_data["activities"]:
            act_type = activity["activity_type"]
            duration = activity["duration_minutes"]
            
            activity_counts[act_type] = activity_counts.get(act_type, 0) + duration
            total_duration += duration
        
        col1, col2 = st.columns(2)
        with col1:
            fig_activities = px.pie(values=list(activity_counts.values()),
                                  names=list(activity_counts.keys()),
                                  title="Activity Types Distribution")
            st.plotly_chart(fig_activities)
        
        with col2:
            st.write("**Activity Insights:**")
            st.write(f"• Total Exercise Time: {total_duration} minutes")
            st.write(f"• Daily Average: {total_duration/7:.1f} minutes")
            
            most_common = max(activity_counts, key=activity_counts.get)
            st.write(f"• Favorite Activity: {most_common}")
            
            if total_duration >= 150:  # WHO recommendation
                st.success("🏆 Meeting weekly exercise goals!")
            else:
                st.info("💪 Try to reach 150 minutes/week")
    
    # Health Score
    st.subheader("🏆 Overall Health Score")
    
    score = 0
    max_score = 100
    
    # Heart rate score (25 points)
    if analytics_data["heart_rate"] and avg_hr:
        if avg_hr <= 70:
            score += 25
        elif avg_hr <= 85:
            score += 20
        elif avg_hr <= 100:
            score += 15
        else:
            score += 10
    
    # Steps score (25 points)
    if analytics_data["steps"] and avg_steps:
        if avg_steps >= 10000:
            score += 25
        elif avg_steps >= 7500:
            score += 20
        elif avg_steps >= 5000:
            score += 15
        else:
            score += 10
    
    # Sleep score (25 points)
    if analytics_data["sleep"] and avg_sleep:
        if avg_sleep >= 7.5:
            score += 25
        elif avg_sleep >= 6.5:
            score += 20
        elif avg_sleep >= 5.5:
            score += 15
        else:
            score += 10
    
    # Activity score (25 points)
    if analytics_data["activities"] and total_duration:
        if total_duration >= 150:
            score += 25
        elif total_duration >= 100:
            score += 20
        elif total_duration >= 50:
            score += 15
        else:
            score += 10
    
    # Display health score
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        fig_score = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Health Score"},
            delta = {'reference': 80},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        st.plotly_chart(fig_score)
    
    if score >= 90:
        st.success("🏆 LEGENDARY! Outstanding health metrics!")
    elif score >= 80:
        st.success("🌟 EXCELLENT! Great health status!")
    elif score >= 70:
        st.info("👍 GOOD! Solid health foundation!")
    elif score >= 60:
        st.warning("📈 FAIR! Room for improvement!")
    else:
        st.error("⚠️ NEEDS ATTENTION! Focus on health improvements!")

def main():
    st.set_page_config(page_title="Health Data Integration", layout="wide")
    
    # Initialize health manager
    health_manager = HealthDataManager()
    
    # Mock user ID for demo (replace with actual auth)
    user_id = "demo_user_123"
    
    st.title("🏥 Health Data Integration System")
    
    tab1, tab2 = st.tabs(["📊 Data Input", "🏆 Legendary Analytics"])
    
    with tab1:
        health_data_input_ui(user_id, health_manager)
    
    with tab2:
        legendary_health_analytics(user_id, health_manager)

if __name__ == "__main__":
    main()