"""
Legendary Mixpanel Health Analytics Module
Provides comprehensive health data tracking and analytics for Forever Fit
"""

import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from mixpanel import Mixpanel, Consumer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class HealthAnalytics:
    """
    Advanced health analytics tracker using Mixpanel
    Tracks workouts, nutrition, mental health, and user engagement
    """
    
    def __init__(self):
        """Initialize Mixpanel with project token"""
        self.project_token = os.getenv("MIXPANEL_PROJECT_TOKEN")
        self.api_secret = os.getenv("MIXPANEL_API_SECRET")
        self.project_id = os.getenv("MIXPANEL_PROJECT_ID")
        
        if self.project_token:
            self.mp = Mixpanel(self.project_token)
            self.enabled = True
            print("✅ Mixpanel Health Analytics initialized successfully")
        else:
            self.mp = None
            self.enabled = False
            print("⚠️  Mixpanel not configured - analytics disabled")
    
    def track_event(self, user_id: str, event_name: str, properties: Dict[str, Any] = None):
        """
        Track a custom event
        
        Args:
            user_id: Unique user identifier
            event_name: Name of the event
            properties: Event properties dictionary
        """
        if not self.enabled:
            return
        
        try:
            props = properties or {}
            props['timestamp'] = datetime.now().isoformat()
            props['app_version'] = '1.0.0'
            
            self.mp.track(user_id, event_name, props)
        except Exception as e:
            print(f"❌ Mixpanel tracking error: {e}")
    
    # ==================== WORKOUT ANALYTICS ====================
    
    def track_workout_started(self, user_id: str, exercise: str, reps_target: int, sets_target: int):
        """Track when user starts a workout"""
        self.track_event(user_id, "Workout Started", {
            "exercise_type": exercise.lower().replace(" ", "_"),
            "reps_target": reps_target,
            "sets_target": sets_target,
            "muscle_group": self._get_muscle_group(exercise)
        })
    
    def track_rep_completed(self, user_id: str, exercise: str, rep_number: int, 
                           form_score: int, form_correct: bool, confidence: int):
        """Track each completed rep with form analysis"""
        self.track_event(user_id, "Rep Completed", {
            "exercise_type": exercise.lower().replace(" ", "_"),
            "rep_number": rep_number,
            "form_score": form_score,
            "form_correct": form_correct,
            "movement_confidence": confidence,
            "muscle_group": self._get_muscle_group(exercise)
        })
    
    def track_set_completed(self, user_id: str, exercise: str, set_number: int, 
                           reps_completed: int, average_form_score: float):
        """Track set completion"""
        self.track_event(user_id, "Set Completed", {
            "exercise_type": exercise.lower().replace(" ", "_"),
            "set_number": set_number,
            "reps_completed": reps_completed,
            "average_form_score": average_form_score,
            "muscle_group": self._get_muscle_group(exercise)
        })
    
    def track_workout_completed(self, user_id: str, exercise: str, total_reps: int, 
                               total_sets: int, duration_seconds: int, 
                               average_form_score: float, calories_burned: int = None):
        """Track full workout completion"""
        self.track_event(user_id, "Workout Completed", {
            "exercise_type": exercise.lower().replace(" ", "_"),
            "total_reps": total_reps,
            "total_sets": total_sets,
            "duration_seconds": duration_seconds,
            "duration_minutes": round(duration_seconds / 60, 2),
            "average_form_score": average_form_score,
            "calories_burned": calories_burned or self._estimate_calories(exercise, total_reps),
            "muscle_group": self._get_muscle_group(exercise)
        })
    
    def track_form_correction(self, user_id: str, exercise: str, correction_type: str, 
                             form_score: int):
        """Track when form needs correction"""
        self.track_event(user_id, "Form Correction", {
            "exercise_type": exercise.lower().replace(" ", "_"),
            "correction_type": correction_type,
            "form_score": form_score,
            "muscle_group": self._get_muscle_group(exercise)
        })
    
    def track_personal_record(self, user_id: str, exercise: str, record_type: str, 
                             value: int, previous_value: int = None):
        """Track personal records"""
        self.track_event(user_id, "Personal Record", {
            "exercise_type": exercise.lower().replace(" ", "_"),
            "record_type": record_type,  # "max_reps", "max_sets", "best_form"
            "new_value": value,
            "previous_value": previous_value,
            "improvement": value - previous_value if previous_value else 0
        })
    
    # ==================== NUTRITION ANALYTICS ====================
    
    def track_meal_logged(self, user_id: str, meal_type: str, calories: int, 
                         protein: float, carbs: float, fat: float, meets_goals: bool):
        """Track nutrition logging"""
        self.track_event(user_id, "Meal Logged", {
            "meal_type": meal_type,  # breakfast, lunch, dinner, snack
            "calories": calories,
            "protein_g": protein,
            "carbs_g": carbs,
            "fat_g": fat,
            "meets_goals": meets_goals
        })
    
    def track_daily_goal_met(self, user_id: str, goal_type: str, target: int, actual: int):
        """Track daily nutrition goals"""
        self.track_event(user_id, "Daily Goal Met", {
            "goal_type": goal_type,  # calories, protein, carbs, fat
            "target_value": target,
            "actual_value": actual,
            "achievement_percent": round((actual / target) * 100, 1) if target > 0 else 0
        })
    
    def track_nutrition_plan_created(self, user_id: str, diet_type: str, 
                                    daily_calories: int, goal: str):
        """Track AI diet plan creation"""
        self.track_event(user_id, "Nutrition Plan Created", {
            "diet_type": diet_type,
            "daily_calorie_target": daily_calories,
            "goal": goal  # weight_loss, muscle_gain, maintenance
        })
    
    # ==================== MENTAL HEALTH ANALYTICS ====================
    
    def track_mood_logged(self, user_id: str, mood: str, stress_level: int, 
                         energy_level: int, sleep_quality: int = None):
        """Track mental health check-ins"""
        self.track_event(user_id, "Mood Logged", {
            "mood": mood,  # happy, energized, calm, stressed, tired, etc.
            "stress_level": stress_level,  # 1-10
            "energy_level": energy_level,  # 1-10
            "sleep_quality": sleep_quality  # 1-10
        })
    
    def track_meditation_session(self, user_id: str, duration_minutes: int, 
                                mood_before: str, mood_after: str):
        """Track meditation/mindfulness sessions"""
        self.track_event(user_id, "Meditation Session", {
            "duration_minutes": duration_minutes,
            "mood_before": mood_before,
            "mood_after": mood_after,
            "mood_improved": mood_before != mood_after
        })
    
    # ==================== USER PROFILE MANAGEMENT ====================
    
    def update_user_profile(self, user_id: str, properties: Dict[str, Any]):
        """Update user profile properties"""
        if not self.enabled:
            return
        
        try:
            self.mp.people_set(user_id, properties)
        except Exception as e:
            print(f"❌ Mixpanel profile update error: {e}")
    
    def set_fitness_stats(self, user_id: str, total_workouts: int, total_reps: int,
                         average_form_score: float, favorite_exercise: str,
                         current_streak: int, fitness_level: str):
        """Set user fitness statistics"""
        self.update_user_profile(user_id, {
            "total_workouts": total_workouts,
            "total_reps": total_reps,
            "average_form_score": average_form_score,
            "favorite_exercise": favorite_exercise,
            "current_streak": current_streak,
            "fitness_level": fitness_level,
            "last_workout": datetime.now().isoformat()
        })
    
    def set_health_goals(self, user_id: str, weight_start: float, weight_current: float,
                        weight_goal: float, goal_type: str):
        """Set user health goals"""
        progress = 0
        if weight_start != weight_goal:
            progress = round(((weight_start - weight_current) / (weight_start - weight_goal)) * 100, 1)
        
        self.update_user_profile(user_id, {
            "weight_start": weight_start,
            "weight_current": weight_current,
            "weight_goal": weight_goal,
            "goal_type": goal_type,
            "goal_progress_percent": max(0, min(100, progress))
        })
    
    def set_nutrition_preferences(self, user_id: str, daily_calorie_target: int,
                                 diet_preference: str, meals_logged_week: int):
        """Set nutrition preferences"""
        self.update_user_profile(user_id, {
            "daily_calorie_target": daily_calorie_target,
            "diet_preference": diet_preference,
            "meals_logged_week": meals_logged_week
        })
    
    def increment_workout_count(self, user_id: str):
        """Increment total workout count"""
        if not self.enabled:
            return
        
        try:
            self.mp.people_increment(user_id, {"total_workouts": 1})
        except Exception as e:
            print(f"❌ Mixpanel increment error: {e}")
    
    # ==================== USER ENGAGEMENT ====================
    
    def track_user_signup(self, user_id: str, signup_method: str):
        """Track new user signup"""
        self.track_event(user_id, "User Signup", {
            "signup_method": signup_method,
            "signup_date": datetime.now().isoformat()
        })
        
        # Set initial profile
        self.update_user_profile(user_id, {
            "signup_date": datetime.now().isoformat(),
            "total_workouts": 0,
            "total_reps": 0,
            "current_streak": 0,
            "fitness_level": "beginner"
        })
    
    def track_user_login(self, user_id: str):
        """Track user login"""
        self.track_event(user_id, "User Login", {
            "login_time": datetime.now().isoformat()
        })
    
    def track_feature_used(self, user_id: str, feature_name: str):
        """Track feature usage"""
        self.track_event(user_id, "Feature Used", {
            "feature_name": feature_name
        })
    
    # ==================== HELPER METHODS ====================
    
    def _get_muscle_group(self, exercise: str) -> str:
        """Get muscle group for exercise"""
        exercise_lower = exercise.lower()
        muscle_groups = {
            "bicep": "arms",
            "curl": "arms",
            "push": "chest",
            "shoulder": "shoulders",
            "press": "shoulders",
            "pull": "back",
            "squat": "legs",
            "lunge": "legs",
            "plank": "core"
        }
        
        for key, group in muscle_groups.items():
            if key in exercise_lower:
                return group
        return "full_body"
    
    def _estimate_calories(self, exercise: str, reps: int) -> int:
        """Estimate calories burned (rough approximation)"""
        calories_per_rep = {
            "bicep_curl": 0.3,
            "push_up": 0.5,
            "squat": 0.4,
            "shoulder_press": 0.35,
            "pull_up": 0.6
        }
        
        exercise_key = exercise.lower().replace(" ", "_")
        cal_per_rep = calories_per_rep.get(exercise_key, 0.4)
        return int(reps * cal_per_rep)


# Global analytics instance
analytics = HealthAnalytics()


# Convenience functions for easy import
def track_workout_started(user_id: str, exercise: str, reps: int, sets: int):
    """Quick function to track workout start"""
    analytics.track_workout_started(user_id, exercise, reps, sets)


def track_workout_completed(user_id: str, exercise: str, total_reps: int, 
                           total_sets: int, duration: int, avg_form: float):
    """Quick function to track workout completion"""
    analytics.track_workout_completed(user_id, exercise, total_reps, total_sets, 
                                     duration, avg_form)


def track_rep(user_id: str, exercise: str, rep_num: int, form_score: int, 
             form_correct: bool, confidence: int):
    """Quick function to track rep"""
    analytics.track_rep_completed(user_id, exercise, rep_num, form_score, 
                                 form_correct, confidence)
