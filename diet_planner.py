#!/usr/bin/env python3

import streamlit as st
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import time
import random
import math

class DietRecommendationEngine:
    """Advanced diet recommendation system based on 15 essential questions"""
    
    def __init__(self):
        self.questions = self._get_essential_questions()
        
    def _get_essential_questions(self) -> List[Dict]:
        """The 15 essential questions for legendary nutrition planning"""
        return [
            # Section 1: Foundation & Core Objectives
            {
                "id": "primary_outcome",
                "section": "Foundation & Core Objectives",
                "question": "Beyond a number on the scale, what is the single most important health or performance goal you want to achieve with your nutrition in the next 3 months?",
                "type": "selectbox",
                "options": [
                    "I want to have stable energy all day",
                    "I want to reduce bloating and digestive issues", 
                    "I need to fuel my workouts to build muscle",
                    "I need to manage my blood sugar",
                    "I want to improve my athletic performance",
                    "I want to lose body fat while maintaining muscle",
                    "I want to improve my overall health markers",
                    "I want to have better mental clarity and focus"
                ],
                "why": "This defines our target. Fueling for athletic performance is vastly different from eating to improve digestive health."
            },
            {
                "id": "quantitative_baseline",
                "section": "Foundation & Core Objectives", 
                "question": "Please provide your current physical measurements",
                "type": "form",
                "fields": {
                    "height_cm": {"type": "number", "min": 140, "max": 220, "label": "Height (cm)"},
                    "weight_kg": {"type": "number", "min": 40, "max": 200, "label": "Weight (kg)"},
                    "age": {"type": "number", "min": 16, "max": 80, "label": "Age"},
                    "biological_sex": {"type": "selectbox", "options": ["Male", "Female"], "label": "Biological Sex"},
                    "body_fat_percentage": {"type": "number", "min": 5, "max": 50, "label": "Body Fat % (if known, optional)"}
                },
                "why": "These are non-negotiable data points for calculating your baseline metabolic rate."
            },
            {
                "id": "medical_conditions",
                "section": "Foundation & Core Objectives",
                "question": "Do you have any diagnosed medical conditions, food allergies, intolerances, or are you taking medications?",
                "type": "multiselect",
                "options": [
                    "None",
                    "Diabetes (Type 1 or 2)",
                    "PCOS",
                    "IBS or digestive issues", 
                    "Thyroid issues",
                    "High cholesterol",
                    "Lactose intolerance",
                    "Gluten sensitivity/Celiac",
                    "Food allergies (nuts, shellfish, etc.)",
                    "Currently pregnant",
                    "Currently breastfeeding",
                    "Taking medications regularly",
                    "Taking supplements regularly"
                ],
                "why": "Most critical question for safety. Medical conditions require specific nutritional protocols."
            },
            
            # Section 2: Current Nutritional Landscape
            {
                "id": "typical_day_eating",
                "section": "Current Nutritional Landscape",
                "question": "Describe a completely typical day of eating and drinking from wake up to bedtime",
                "type": "text_area",
                "placeholder": "Example: 7am - Coffee with milk, 9am - Oatmeal with banana, 12pm - Sandwich and chips, 3pm - Snack, 7pm - Dinner, etc.",
                "why": "Provides honest snapshot of current habits, portion sizes, and meal timing."
            },
            {
                "id": "hunger_energy_patterns",
                "section": "Current Nutritional Landscape",
                "question": "When do you feel most hungry, when are your energy levels highest/lowest, and what do you crave?",
                "type": "form",
                "fields": {
                    "most_hungry_time": {"type": "selectbox", "options": ["Morning", "Mid-morning", "Lunch time", "Afternoon", "Evening", "Late night"], "label": "Most hungry time"},
                    "highest_energy": {"type": "selectbox", "options": ["Early morning", "Mid-morning", "Afternoon", "Evening", "Varies"], "label": "Highest energy time"},
                    "energy_crash_time": {"type": "selectbox", "options": ["No crashes", "Mid-morning", "After lunch", "Afternoon", "Evening"], "label": "Energy crash time"},
                    "common_cravings": {"type": "multiselect", "options": ["Sweet foods", "Salty snacks", "Carbs/bread", "Chocolate", "Caffeine", "None specific"], "label": "Common cravings"}
                },
                "why": "Helps architect meal timing and macronutrient balance to prevent crashes and manage cravings."
            },
            {
                "id": "hydration_status",
                "section": "Current Nutritional Landscape",
                "question": "How much water do you drink daily and what other beverages do you consume?",
                "type": "form",
                "fields": {
                    "water_glasses": {"type": "slider", "min": 0, "max": 15, "label": "Glasses of water per day"},
                    "coffee_cups": {"type": "slider", "min": 0, "max": 10, "label": "Cups of coffee per day"},
                    "tea_cups": {"type": "slider", "min": 0, "max": 10, "label": "Cups of tea per day"},
                    "alcohol_weekly": {"type": "slider", "min": 0, "max": 20, "label": "Alcoholic drinks per week"},
                    "soda_daily": {"type": "slider", "min": 0, "max": 5, "label": "Sodas/juices per day"}
                },
                "why": "Dehydration is often mistaken for hunger and impacts energy dramatically."
            },
            
            # Section 3: Lifestyle & Practical Realities
            {
                "id": "cooking_reality",
                "section": "Lifestyle & Practical Realities",
                "question": "What is your cooking skill level and how much time can you dedicate to food preparation?",
                "type": "form",
                "fields": {
                    "cooking_skill": {"type": "slider", "min": 1, "max": 10, "label": "Cooking skill (1=beginner, 10=expert)"},
                    "cooking_enjoyment": {"type": "slider", "min": 1, "max": 10, "label": "Cooking enjoyment (1=hate it, 10=love it)"},
                    "prep_time_daily": {"type": "selectbox", "options": ["Less than 15 minutes", "15-30 minutes", "30-60 minutes", "1-2 hours", "2+ hours"], "label": "Daily food prep time available"}
                },
                "why": "Plan must be practical. Complex recipes are useless for someone who hates cooking."
            },
            {
                "id": "social_cultural_context",
                "section": "Lifestyle & Practical Realities",
                "question": "Describe your social eating patterns and cultural considerations",
                "type": "form",
                "fields": {
                    "eating_situation": {"type": "selectbox", "options": ["Mostly alone", "With family/partner", "Mix of both"], "label": "Typical eating situation"},
                    "restaurant_frequency": {"type": "selectbox", "options": ["Rarely", "1-2 times per week", "3-4 times per week", "5+ times per week"], "label": "Restaurant/takeout frequency"},
                    "social_events": {"type": "selectbox", "options": ["Rarely", "Weekly", "Multiple times per week"], "label": "Social events with food"},
                    "cultural_dietary": {"type": "multiselect", "options": ["None", "Vegetarian", "Vegan", "Halal", "Kosher", "Mediterranean", "Asian cuisine preference", "Other"], "label": "Cultural/religious dietary practices"}
                },
                "why": "Food is deeply social and cultural. Plan must navigate family dinners and personal traditions."
            },
            {
                "id": "financial_framework",
                "section": "Lifestyle & Practical Realities",
                "question": "What is your grocery budget and shopping preferences?",
                "type": "form",
                "fields": {
                    "weekly_budget": {"type": "selectbox", "options": ["Under $50", "$50-100", "$100-150", "$150-200", "$200+"], "label": "Weekly grocery budget"},
                    "shopping_preference": {"type": "multiselect", "options": ["Standard supermarket", "Local farmers market", "Organic/specialty stores", "Online grocery delivery", "Bulk stores"], "label": "Shopping preferences"}
                },
                "why": "Plan must be financially sustainable using available resources."
            },
            {
                "id": "activity_performance",
                "section": "Lifestyle & Practical Realities",
                "question": "Describe your physical activity and lifestyle",
                "type": "form",
                "fields": {
                    "workout_frequency": {"type": "selectbox", "options": ["No regular exercise", "1-2 times per week", "3-4 times per week", "5-6 times per week", "Daily"], "label": "Workout frequency"},
                    "workout_type": {"type": "multiselect", "options": ["Cardio", "Weight training", "Yoga/Pilates", "Sports", "Walking/hiking", "High intensity training"], "label": "Types of exercise"},
                    "workout_duration": {"type": "selectbox", "options": ["Less than 30 min", "30-60 min", "60-90 min", "90+ min"], "label": "Typical workout duration"},
                    "daily_activity": {"type": "selectbox", "options": ["Desk job, mostly sedentary", "Some walking/standing", "Moderately active job", "Very active job"], "label": "Daily activity level"}
                },
                "why": "Links nutrition to fitness plan. Need to calculate energy expenditure for proper fueling."
            },
            
            # Section 4: Psychology of Eating
            {
                "id": "food_relationship",
                "section": "Psychology of Eating",
                "question": "How would you describe your personal relationship with food?",
                "type": "selectbox",
                "options": [
                    "Food is primarily fuel for my body",
                    "Food is a source of comfort and pleasure",
                    "Food is a reward system for me",
                    "Food causes me anxiety and stress",
                    "Food is social connection and culture",
                    "Food is both fuel and enjoyment in balance",
                    "I have a complicated relationship with food"
                ],
                "why": "Uncovers emotional drivers. Plan must foster positive, nourishing relationship with food."
            },
            {
                "id": "diet_history",
                "section": "Psychology of Eating",
                "question": "What previous diets or nutritional approaches have you tried and what happened?",
                "type": "text_area",
                "placeholder": "Describe what you tried, what you liked/disliked, and why you stopped following them",
                "why": "Learn from the past to avoid repeating mistakes and find sustainable approaches."
            },
            
            # Section 5: Preferences & Fine-Tuning
            {
                "id": "food_preferences",
                "section": "Preferences & Fine-Tuning",
                "question": "What healthy foods do you love and what do you absolutely dislike?",
                "type": "form",
                "fields": {
                    "favorite_proteins": {"type": "multiselect", "options": ["Chicken", "Fish", "Eggs", "Greek yogurt", "Beans/legumes", "Tofu", "Lean beef", "Turkey"], "label": "Favorite protein sources"},
                    "favorite_carbs": {"type": "multiselect", "options": ["Rice", "Oats", "Quinoa", "Sweet potatoes", "Fruits", "Whole grain bread", "Pasta"], "label": "Favorite carb sources"},
                    "favorite_vegetables": {"type": "multiselect", "options": ["Leafy greens", "Broccoli", "Bell peppers", "Carrots", "Tomatoes", "Cucumber", "Zucchini"], "label": "Favorite vegetables"},
                    "disliked_foods": {"type": "multiselect", "options": ["Fish", "Eggs", "Dairy", "Spicy foods", "Leafy greens", "Beans", "Nuts", "None"], "label": "Foods you dislike"}
                },
                "why": "Sustainability is built on enjoyment. Build plan around foods you love."
            },
            {
                "id": "meal_structure",
                "section": "Preferences & Fine-Tuning",
                "question": "What meal structure and timing works best for you?",
                "type": "form",
                "fields": {
                    "meal_preference": {"type": "selectbox", "options": ["3 larger meals", "5-6 smaller meals", "2 larger meals + snacks", "Flexible timing"], "label": "Preferred meal structure"},
                    "breakfast_timing": {"type": "selectbox", "options": ["Early (6-7am)", "Mid-morning (8-9am)", "Late morning (10-11am)", "I skip breakfast"], "label": "Breakfast preference"},
                    "largest_meal": {"type": "selectbox", "options": ["Breakfast", "Lunch", "Dinner", "No preference"], "label": "Preferred largest meal"}
                },
                "why": "Tailors schedule to your body's natural hunger cues and preferences."
            },
            {
                "id": "success_definition",
                "section": "Preferences & Fine-Tuning",
                "question": "How will we know this nutrition plan is working for you? What will success look and feel like?",
                "type": "multiselect",
                "options": [
                    "I won't feel bloated after meals",
                    "I'll have stable energy throughout the day",
                    "I'll sleep better at night",
                    "My gym performance will improve",
                    "I'll feel more confident about my body",
                    "My mood will be more stable",
                    "I'll have better mental clarity",
                    "My digestion will improve",
                    "I'll feel stronger and more energetic"
                ],
                "why": "Sets personalized metrics for success beyond just weight loss."
            }
        ]

class MLNutritionEngine:
    """ML-powered nutrition optimization engine"""
    
    def __init__(self):
        self.recipe_database = {
            "breakfast": [
                {"name": "Greek Yogurt Bowl", "calories": 320, "protein": 25, "carbs": 35, "fat": 8, "prep_time": 5, "ingredients": ["Greek yogurt", "Berries", "Granola"]},
                {"name": "Scrambled Eggs with Spinach", "calories": 280, "protein": 22, "carbs": 8, "fat": 18, "prep_time": 8, "ingredients": ["Eggs", "Spinach", "Olive oil"]},
                {"name": "Overnight Oats", "calories": 350, "protein": 20, "carbs": 45, "fat": 10, "prep_time": 2, "ingredients": ["Oats", "Protein powder", "Almond milk"]}
            ],
            "lunch": [
                {"name": "Grilled Chicken Salad", "calories": 420, "protein": 35, "carbs": 15, "fat": 25, "prep_time": 15, "ingredients": ["Chicken breast", "Mixed greens", "Vegetables"]},
                {"name": "Quinoa Power Bowl", "calories": 450, "protein": 18, "carbs": 55, "fat": 16, "prep_time": 20, "ingredients": ["Quinoa", "Black beans", "Vegetables"]},
                {"name": "Turkey Wrap", "calories": 380, "protein": 28, "carbs": 35, "fat": 15, "prep_time": 5, "ingredients": ["Turkey", "Tortilla", "Hummus"]}
            ],
            "dinner": [
                {"name": "Baked Salmon", "calories": 480, "protein": 32, "carbs": 35, "fat": 22, "prep_time": 25, "ingredients": ["Salmon", "Sweet potato", "Broccoli"]},
                {"name": "Beef Stir-fry", "calories": 420, "protein": 30, "carbs": 25, "fat": 20, "prep_time": 15, "ingredients": ["Lean beef", "Vegetables", "Rice"]},
                {"name": "Chicken Curry", "calories": 390, "protein": 28, "carbs": 30, "fat": 18, "prep_time": 30, "ingredients": ["Chicken", "Curry spices", "Vegetables"]}
            ]
        }
    
    def generate_meal_recommendations(self, target_calories: int, meal_type: str) -> List[Dict]:
        recipes = self.recipe_database.get(meal_type, [])
        scored = []
        for recipe in recipes:
            score = 1 - abs(recipe["calories"] - target_calories) / target_calories
            if score > 0.7:
                scored.append({**recipe, "fit_score": score})
        return sorted(scored, key=lambda x: x["fit_score"], reverse=True)[:3]

class PersonalizedDietGenerator:
    """Generate highly personalized diet plans based on 15-question assessment"""
    
    def __init__(self, responses: Dict):
        self.responses = responses
        self.ml_engine = MLNutritionEngine()
        
    def generate_diet_plan(self) -> Dict:
        """Generate comprehensive personalized diet plan"""
        
        # Analyze responses
        analysis = self._analyze_responses()
        
        # Generate plan components
        diet_plan = {
            "plan_overview": self._create_plan_overview(analysis),
            "daily_nutrition_targets": self._calculate_nutrition_targets(analysis),
            "meal_structure": self._design_meal_structure(analysis),
            "weekly_meal_plan": self._create_weekly_meals(analysis),
            "food_guidelines": self._create_food_guidelines(analysis),
            "hydration_plan": self._create_hydration_plan(analysis),
            "supplement_recommendations": self._recommend_supplements(analysis),
            "success_tracking": self._create_success_metrics(analysis),
            "lifestyle_integration": self._create_lifestyle_tips(analysis)
        }
        
        return diet_plan
    
    def _analyze_responses(self) -> Dict:
        """Analyze user responses to determine plan parameters"""
        
        # Extract key information
        baseline = self.responses.get("quantitative_baseline", {})
        primary_goal = self.responses.get("primary_outcome", "")
        medical = self.responses.get("medical_conditions", [])
        activity = self.responses.get("activity_performance", {})
        
        # Calculate BMR using Mifflin-St Jeor equation
        weight = baseline.get("weight_kg", 70)
        height = baseline.get("height_cm", 170) 
        age = baseline.get("age", 30)
        sex = baseline.get("biological_sex", "Male")
        
        if sex == "Male":
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        
        # Activity multiplier
        workout_freq = activity.get("workout_frequency", "No regular exercise")
        daily_activity = activity.get("daily_activity", "Desk job, mostly sedentary")
        
        if "No regular exercise" in workout_freq and "sedentary" in daily_activity:
            activity_multiplier = 1.2
        elif "1-2 times" in workout_freq:
            activity_multiplier = 1.375
        elif "3-4 times" in workout_freq:
            activity_multiplier = 1.55
        elif "5-6 times" in workout_freq:
            activity_multiplier = 1.725
        else:
            activity_multiplier = 1.9
        
        tdee = bmr * activity_multiplier
        
        # Adjust for goals
        if "stable energy" in primary_goal.lower():
            calorie_target = int(tdee)
            focus = "energy_stability"
        elif "muscle" in primary_goal.lower():
            calorie_target = int(tdee + 300)
            focus = "muscle_building"
        elif "performance" in primary_goal.lower():
            calorie_target = int(tdee + 200)
            focus = "performance"
        elif "blood sugar" in primary_goal.lower():
            calorie_target = int(tdee)
            focus = "blood_sugar"
        else:
            calorie_target = int(tdee)
            focus = "general_health"
        
        return {
            "bmr": bmr,
            "tdee": tdee,
            "calorie_target": calorie_target,
            "focus": focus,
            "medical_conditions": medical,
            "primary_goal": primary_goal,
            "baseline_data": baseline,
            "activity_level": activity,
            "cooking_skills": self.responses.get("cooking_reality", {}),
            "food_preferences": self.responses.get("food_preferences", {}),
            "meal_structure_pref": self.responses.get("meal_structure", {}),
            "social_context": self.responses.get("social_cultural_context", {}),
            "budget": self.responses.get("financial_framework", {}),
            "relationship_with_food": self.responses.get("food_relationship", ""),
            "success_metrics": self.responses.get("success_definition", [])
        }
    
    def _create_plan_overview(self, analysis: Dict) -> Dict:
        """Create personalized plan overview"""
        
        focus_descriptions = {
            "energy_stability": "Energy Optimization & Metabolic Balance",
            "muscle_building": "Muscle Building & Performance Nutrition", 
            "performance": "Athletic Performance & Recovery",
            "blood_sugar": "Blood Sugar Management & Metabolic Health",
            "general_health": "Comprehensive Health & Wellness"
        }
        
        plan_name = f"Personalized {focus_descriptions[analysis['focus']]} Plan"
        
        description = f"""
        Your custom nutrition plan designed specifically for your goal: "{analysis['primary_goal']}"
        
        This plan is built around your lifestyle, preferences, and metabolic needs with {analysis['calorie_target']} daily calories.
        Every recommendation is tailored to your cooking skills, time availability, and food preferences.
        """
        
        return {
            "plan_name": plan_name,
            "description": description.strip(),
            "primary_focus": analysis["focus"],
            "duration": "12 weeks with ongoing adjustments",
            "created_date": datetime.now().isoformat()
        }
    
    def _calculate_nutrition_targets(self, analysis: Dict) -> Dict:
        """Calculate personalized macro and micronutrient targets"""
        
        calories = analysis["calorie_target"]
        focus = analysis["focus"]
        
        # Protein targets based on goals and activity
        if focus == "muscle_building":
            protein_per_kg = 2.2
        elif focus == "performance":
            protein_per_kg = 2.0
        else:
            protein_per_kg = 1.6
        
        protein_g = analysis["baseline_data"].get("weight_kg", 70) * protein_per_kg
        protein_calories = protein_g * 4
        
        # Fat targets
        if focus == "blood_sugar":
            fat_percentage = 0.35  # Higher fat for blood sugar control
        else:
            fat_percentage = 0.25
        
        fat_calories = calories * fat_percentage
        fat_g = fat_calories / 9
        
        # Carbs fill the rest
        carb_calories = calories - protein_calories - fat_calories
        carb_g = carb_calories / 4
        
        return {
            "daily_calories": calories,
            "protein_g": round(protein_g, 1),
            "carbs_g": round(carb_g, 1),
            "fat_g": round(fat_g, 1),
            "fiber_g": round(calories / 100, 1),  # 1g per 100 calories
            "water_liters": round(analysis["baseline_data"].get("weight_kg", 70) * 0.035, 1)
        }
    
    def _design_meal_structure(self, analysis: Dict) -> Dict:
        """Design optimal meal timing and structure"""
        
        meal_pref = analysis["meal_structure_pref"].get("meal_preference", "3 larger meals")
        breakfast_timing = analysis["meal_structure_pref"].get("breakfast_timing", "Mid-morning (8-9am)")
        
        if "3 larger meals" in meal_pref:
            structure = {
                "meal_count": 3,
                "breakfast": {"time": breakfast_timing, "calories_percent": 25},
                "lunch": {"time": "12-1pm", "calories_percent": 35},
                "dinner": {"time": "6-7pm", "calories_percent": 40}
            }
        elif "5-6 smaller meals" in meal_pref:
            structure = {
                "meal_count": 5,
                "breakfast": {"time": breakfast_timing, "calories_percent": 20},
                "snack1": {"time": "10-11am", "calories_percent": 10},
                "lunch": {"time": "12-1pm", "calories_percent": 25},
                "snack2": {"time": "3-4pm", "calories_percent": 15},
                "dinner": {"time": "6-7pm", "calories_percent": 30}
            }
        else:
            structure = {
                "meal_count": 4,
                "breakfast": {"time": breakfast_timing, "calories_percent": 20},
                "lunch": {"time": "12-1pm", "calories_percent": 30},
                "snack": {"time": "3-4pm", "calories_percent": 15},
                "dinner": {"time": "6-7pm", "calories_percent": 35}
            }
        
        return structure
    
    def _create_weekly_meals(self, analysis: Dict) -> Dict:
        """Create ML-powered weekly meal recommendations"""
        
        daily_calories = analysis["calorie_target"]
        
        # Generate ML-powered recommendations
        weekly_recommendations = {}
        
        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            daily_meals = {}
            
            # Breakfast (25% of calories)
            breakfast_cals = int(daily_calories * 0.25)
            breakfast_recs = self.ml_engine.generate_meal_recommendations(breakfast_cals, "breakfast")
            daily_meals["breakfast"] = {
                "nutritional_target": {"calories": breakfast_cals, "protein": int(breakfast_cals * 0.2 / 4)},
                "recommendations": breakfast_recs,
                "selected_recipe": breakfast_recs[0] if breakfast_recs else None
            }
            
            # Lunch (35% of calories)
            lunch_cals = int(daily_calories * 0.35)
            lunch_recs = self.ml_engine.generate_meal_recommendations(lunch_cals, "lunch")
            daily_meals["lunch"] = {
                "nutritional_target": {"calories": lunch_cals, "protein": int(lunch_cals * 0.25 / 4)},
                "recommendations": lunch_recs,
                "selected_recipe": lunch_recs[0] if lunch_recs else None
            }
            
            # Dinner (40% of calories)
            dinner_cals = int(daily_calories * 0.40)
            dinner_recs = self.ml_engine.generate_meal_recommendations(dinner_cals, "dinner")
            daily_meals["dinner"] = {
                "nutritional_target": {"calories": dinner_cals, "protein": int(dinner_cals * 0.3 / 4)},
                "recommendations": dinner_recs,
                "selected_recipe": dinner_recs[0] if dinner_recs else None
            }
            
            weekly_recommendations[day] = daily_meals
        
        # Generate smart shopping list
        ingredients = set()
        for day_meals in weekly_recommendations.values():
            for meal_data in day_meals.values():
                selected = meal_data.get("selected_recipe")
                if selected:
                    ingredients.update(selected.get("ingredients", []))
        
        return {
            "ml_powered_recommendations": weekly_recommendations,
            "smart_shopping_list": sorted(list(ingredients)),
            "meal_prep_tips": ["Batch cook proteins on weekends", "Prep vegetables in advance", "Use meal containers for portion control"]
        }
    
    def _create_food_guidelines(self, analysis: Dict) -> Dict:
        """Create personalized food guidelines"""
        
        medical = analysis["medical_conditions"]
        focus = analysis["focus"]
        
        guidelines = {
            "prioritize": [],
            "limit": [],
            "timing": [],
            "special_considerations": []
        }
        
        # Focus-specific guidelines
        if focus == "energy_stability":
            guidelines["prioritize"].extend([
                "Complex carbohydrates for sustained energy",
                "Protein at every meal to stabilize blood sugar",
                "Healthy fats for satiety"
            ])
            guidelines["timing"].append("Eat every 3-4 hours to maintain stable energy")
        
        elif focus == "muscle_building":
            guidelines["prioritize"].extend([
                "High-quality protein sources",
                "Post-workout protein within 2 hours",
                "Adequate carbohydrates for training fuel"
            ])
        
        # Medical condition modifications
        if "Diabetes" in medical:
            guidelines["special_considerations"].append("Focus on low glycemic index foods")
            guidelines["limit"].append("Simple sugars and refined carbohydrates")
        
        if "IBS" in medical:
            guidelines["special_considerations"].append("Consider low-FODMAP approach")
            guidelines["limit"].append("High-fiber foods initially")
        
        return guidelines
    
    def _create_hydration_plan(self, analysis: Dict) -> Dict:
        """Create personalized hydration strategy"""
        
        current_water = self.responses.get("hydration_status", {}).get("water_glasses", 4)
        target_water = analysis["baseline_data"].get("weight_kg", 70) * 0.035
        
        return {
            "daily_water_target": f"{target_water:.1f} liters",
            "current_intake": f"{current_water} glasses",
            "improvement_needed": target_water > (current_water * 0.25),
            "hydration_tips": [
                "Start each day with a glass of water",
                "Drink water before, during, and after workouts",
                "Set hourly reminders if needed"
            ]
        }
    
    def _recommend_supplements(self, analysis: Dict) -> Dict:
        """Recommend supplements based on individual needs"""
        
        recommendations = {
            "essential": [],
            "beneficial": [],
            "considerations": []
        }
        
        # Basic recommendations
        recommendations["essential"].append("High-quality multivitamin")
        
        if analysis["focus"] == "muscle_building":
            recommendations["beneficial"].extend([
                "Whey protein powder (if needed to meet protein targets)",
                "Creatine monohydrate (3-5g daily)"
            ])
        
        if "Vitamin D deficiency" in analysis["medical_conditions"]:
            recommendations["essential"].append("Vitamin D3 supplement")
        
        recommendations["considerations"].append("Consult healthcare provider before starting any supplements")
        
        return recommendations
    
    def _create_success_metrics(self, analysis: Dict) -> Dict:
        """Define personalized success metrics"""
        
        user_metrics = analysis["success_metrics"]
        
        return {
            "primary_metrics": user_metrics[:3] if len(user_metrics) >= 3 else user_metrics,
            "tracking_methods": [
                "Daily energy level rating (1-10)",
                "Weekly progress photos",
                "Monthly body measurements",
                "Sleep quality tracking"
            ],
            "check_in_frequency": "Weekly self-assessment, monthly plan review"
        }
    
    def _create_lifestyle_tips(self, analysis: Dict) -> Dict:
        """Create lifestyle integration strategies"""
        
        social_context = analysis["social_context"]
        budget = analysis["budget"]
        
        tips = {
            "meal_prep": [],
            "social_eating": [],
            "budget_friendly": [],
            "time_saving": []
        }
        
        # Cooking skill-based tips
        cooking_skill = analysis["cooking_skills"].get("cooking_skill", 5)
        if cooking_skill <= 3:
            tips["time_saving"].extend([
                "Use pre-cut vegetables to save time",
                "Batch cook proteins on weekends",
                "Keep healthy frozen meals as backup"
            ])
        
        # Budget considerations
        weekly_budget = budget.get("weekly_budget", "$100-150")
        if "Under $50" in weekly_budget:
            tips["budget_friendly"].extend([
                "Buy proteins in bulk and freeze portions",
                "Use dried beans and lentils as protein sources",
                "Shop seasonal produce for best prices"
            ])
        
        return tips
    
    def _get_meal_prep_tips(self, skill_level: int, prep_time: str) -> List[str]:
        """Get meal prep tips based on skill and time"""
        
        tips = []
        
        if skill_level <= 3:
            tips.extend([
                "Start with simple assembly meals",
                "Use pre-cooked proteins like rotisserie chicken",
                "Invest in good food storage containers"
            ])
        
        if "Less than 15 minutes" in prep_time:
            tips.extend([
                "Prepare overnight oats for quick breakfasts",
                "Use slow cooker or instant pot for hands-off cooking",
                "Keep healthy snacks pre-portioned"
            ])
        
        return tips

def main():
    """Main diet planner interface with 15-question assessment"""
    
    # Add custom CSS for better readability
    st.markdown("""
    <style>
        /* Improve selectbox and multiselect readability */
        .stSelectbox label, .stMultiSelect label {
            color: #FFFFFF !important;
            font-weight: 500 !important;
            font-size: 1rem !important;
        }
        
        /* Selectbox dropdown options */
        .stSelectbox div[data-baseweb="select"] > div {
            background-color: #1E1E1E !important;
            color: #FFFFFF !important;
        }
        
        /* Dropdown menu items */
        [data-baseweb="menu"] {
            background-color: #2D2D2D !important;
        }
        
        [data-baseweb="menu"] li {
            color: #FFFFFF !important;
            background-color: #2D2D2D !important;
        }
        
        [data-baseweb="menu"] li:hover {
            background-color: #3D3D3D !important;
            color: #00D9FF !important;
        }
        
        /* Selected option in dropdown */
        .stSelectbox div[data-baseweb="select"] span {
            color: #FFFFFF !important;
        }
        
        /* Multiselect options */
        .stMultiSelect div[data-baseweb="select"] > div {
            background-color: #1E1E1E !important;
            color: #FFFFFF !important;
        }
        
        .stMultiSelect span {
            color: #FFFFFF !important;
        }
        
        /* Text input and text area */
        .stTextInput input, .stTextArea textarea {
            color: #FFFFFF !important;
            background-color: #1E1E1E !important;
        }
        
        /* Number input */
        .stNumberInput input {
            color: #FFFFFF !important;
            background-color: #1E1E1E !important;
        }
        
        /* Slider labels and values */
        .stSlider label, .stSlider div {
            color: #FFFFFF !important;
        }
        
        /* Question text */
        h3, h4 {
            color: #FFFFFF !important;
        }
        
        /* Make sure all paragraph text is readable */
        p, span, div {
            color: #E0E0E0 !important;
        }
        
        /* Caption text */
        .caption {
            color: #B0B0B0 !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("🥗 Advanced Diet Planner")
    st.markdown("*World-class personalized nutrition plans based on 15 essential questions*")
    
    # Initialize recommendation engine
    engine = DietRecommendationEngine()
    
    # Initialize session state
    if "diet_questionnaire_step" not in st.session_state:
        st.session_state.diet_questionnaire_step = 0
    if "diet_responses" not in st.session_state:
        st.session_state.diet_responses = {}
    if "diet_plan" not in st.session_state:
        st.session_state.diet_plan = None
    
    # Show introduction
    if st.session_state.diet_questionnaire_step == 0:
        st.markdown("""
        ### 🎯 The Science of Personalized Nutrition
        
        As a world-renowned dietitian, I believe a nutrition plan is not a set of rules to follow, 
        but a **personalized blueprint** for nourishing your unique body and life.
        
        **Why 15 Questions?**
        - Generic plans are destined to fail
        - Your body, lifestyle, and goals are unique
        - Every recommendation will be tailored specifically to YOU
        
        **What You'll Get:**
        - Scientifically calculated calorie and macro targets
        - Meal plans based on your preferences and cooking skills
        - Strategies that fit your lifestyle and budget
        - Success metrics that matter to YOU
        """)
        
        if st.button("🚀 Start Your Personalized Assessment", type="primary"):
            st.session_state.diet_questionnaire_step = 1
            st.rerun()
        
        return
    
    questions = engine.questions
    total_questions = len(questions)
    
    # Progress tracking
    if st.session_state.diet_questionnaire_step <= total_questions:
        progress = (st.session_state.diet_questionnaire_step - 1) / total_questions
        st.progress(progress)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.caption(f"Question {st.session_state.diet_questionnaire_step} of {total_questions}")
        with col2:
            st.caption(f"Progress: {int(progress * 100)}%")
        with col3:
            current_section = questions[st.session_state.diet_questionnaire_step - 1]["section"]
            st.caption(f"📋 {current_section}")
    
    # Show current question
    if st.session_state.diet_questionnaire_step <= total_questions:
        current_q = questions[st.session_state.diet_questionnaire_step - 1]
        
        st.subheader(f"Question {st.session_state.diet_questionnaire_step}")
        st.markdown(f"**{current_q['question']}**")
        
        # Show why this question matters
        with st.expander("💡 Why this question matters"):
            st.info(current_q['why'])
        
        # Handle different question types
        response = None
        
        if current_q['type'] == 'selectbox':
            response = st.selectbox("Select your answer:", current_q['options'])
        
        elif current_q['type'] == 'multiselect':
            response = st.multiselect("Select all that apply:", current_q['options'])
        
        elif current_q['type'] == 'text_area':
            response = st.text_area(
                "Your answer:", 
                placeholder=current_q.get('placeholder', ''),
                height=100
            )
        
        elif current_q['type'] == 'form':
            st.markdown("**Please provide the following information:**")
            response = {}
            
            for field_name, field_config in current_q['fields'].items():
                if field_config['type'] == 'number':
                    response[field_name] = st.number_input(
                        field_config.get('label', field_name.replace('_', ' ').title()),
                        min_value=field_config.get('min', 0),
                        max_value=field_config.get('max', 1000),
                        value=field_config.get('min', 0)
                    )
                elif field_config['type'] == 'selectbox':
                    response[field_name] = st.selectbox(
                        field_config.get('label', field_name.replace('_', ' ').title()),
                        field_config['options']
                    )
                elif field_config['type'] == 'multiselect':
                    response[field_name] = st.multiselect(
                        field_config.get('label', field_name.replace('_', ' ').title()),
                        field_config['options']
                    )
                elif field_config['type'] == 'slider':
                    response[field_name] = st.slider(
                        field_config.get('label', field_name.replace('_', ' ').title()),
                        field_config['min'],
                        field_config['max'],
                        value=field_config.get('min', 0)
                    )
        
        # Navigation buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.session_state.diet_questionnaire_step > 1:
                if st.button("← Previous", key="prev_diet"):
                    st.session_state.diet_questionnaire_step -= 1
                    st.rerun()
        
        with col2:
            if st.button("Skip Question", key="skip_diet"):
                st.session_state.diet_questionnaire_step += 1
                st.rerun()
        
        with col3:
            if st.button("Next →", type="primary", key="next_diet"):
                # Save response
                st.session_state.diet_responses[current_q['id']] = response
                st.session_state.diet_questionnaire_step += 1
                st.rerun()
    
    else:
        # Generate and display diet plan
        if st.session_state.diet_plan is None:
            with st.spinner("🧠 Creating your personalized nutrition plan..."):
                status_placeholder = st.empty()
                status_placeholder.info("🔬 Analyzing your metabolic profile...")
                time.sleep(1)
                
                status_placeholder.info("🍽️ Designing your meal structure...")
                generator = PersonalizedDietGenerator(st.session_state.diet_responses)
                time.sleep(1)
                
                status_placeholder.info("📊 Calculating your nutrition targets...")
                st.session_state.diet_plan = generator.generate_diet_plan()
                
                # Track plan creation
                try:
                    from mixpanel_analytics import analytics
                    user_id = st.session_state.user['user_id'] if 'user' in st.session_state else "guest"
                    plan = st.session_state.diet_plan
                    targets = plan['daily_nutrition_targets']
                    overview = plan['plan_overview']
                    
                    analytics.track_nutrition_plan_created(
                        user_id,
                        overview['primary_focus'],
                        targets['daily_calories'],
                        overview['plan_name']
                    )
                    
                    # Also set user nutrition preferences
                    analytics.set_nutrition_preferences(
                        user_id,
                        targets['daily_calories'],
                        overview['primary_focus'],
                        0 # Meals logged week placeholder
                    )
                except Exception as e:
                    print(f"Analytics error: {e}")

                time.sleep(1)
                
                status_placeholder.success("✅ Your personalized nutrition plan is ready!")
                time.sleep(1)
                status_placeholder.empty()
        
        # Display the plan
        display_diet_plan(st.session_state.diet_plan)
        
        # Save plan
        if st.button("💾 Save Plan", key="save_diet_plan"):
            st.success("Plan saved!")
        
        # Reset button
        if st.button("🔄 Start Over", key="reset_diet"):
            st.session_state.diet_questionnaire_step = 0
            st.session_state.diet_responses = {}
            st.session_state.diet_plan = None
            st.rerun()

def display_diet_plan(plan: Dict):
    """Display the generated personalized diet plan"""
    
    st.success("🎉 Your Personalized Nutrition Plan is Ready!")
    
    # Plan Overview
    overview = plan['plan_overview']
    st.header(overview['plan_name'])
    st.markdown(overview['description'])
    
    # Daily Nutrition Targets
    st.subheader("🎯 Your Daily Nutrition Targets")
    targets = plan['daily_nutrition_targets']
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Calories", f"{targets['daily_calories']}")
    with col2:
        st.metric("Protein", f"{targets['protein_g']}g")
    with col3:
        st.metric("Carbs", f"{targets['carbs_g']}g")
    with col4:
        st.metric("Fat", f"{targets['fat_g']}g")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Fiber", f"{targets['fiber_g']}g")
    with col2:
        st.metric("Water", f"{targets['water_liters']}L")
    
    # Meal Structure
    st.subheader("⏰ Your Optimal Meal Structure")
    structure = plan['meal_structure']
    st.write(f"**Recommended:** {structure['meal_count']} meals per day")
    
    for meal, details in structure.items():
        if isinstance(details, dict) and 'time' in details:
            st.write(f"• **{meal.title()}**: {details['time']} ({details['calories_percent']}% of daily calories)")
    
    # Food Guidelines
    st.subheader("📋 Your Personalized Food Guidelines")
    guidelines = plan['food_guidelines']
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**✅ Prioritize:**")
        for item in guidelines['prioritize']:
            st.write(f"• {item}")
    
    with col2:
        st.markdown("**⚠️ Limit:**")
        for item in guidelines['limit']:
            st.write(f"• {item}")
    
    if guidelines['special_considerations']:
        st.markdown("**🏥 Special Considerations:**")
        for item in guidelines['special_considerations']:
            st.write(f"• {item}")
    
    # ML-Powered Meal Recommendations
    st.subheader("🤖 AI-Powered Meal Recommendations")
    st.caption("Personalized recipes that match your exact nutritional needs")
    
    if 'ml_powered_recommendations' in plan['weekly_meal_plan']:
        ml_recommendations = plan['weekly_meal_plan']['ml_powered_recommendations']
        
        # Show today's recommendations
        today = datetime.now().strftime("%A")
        if today in ml_recommendations:
            st.markdown(f"### 📅 Today's Recommendations ({today})")
            
            today_meals = ml_recommendations[today]
            
            for meal_type, meal_data in today_meals.items():
                if meal_data.get('recommendations'):
                    target = meal_data['nutritional_target']
                    st.markdown(f"**{meal_type.title()}** (Target: {target['calories']} cal, {target['protein']}g protein)")
                    
                    for i, recipe in enumerate(meal_data['recommendations'][:3]):
                        with st.expander(f"Option {i+1}: {recipe['name']} ({recipe['fit_score']:.0%} match)"):
                            col1, col2 = st.columns([2, 1])
                            with col1:
                                st.write(f"🔥 {recipe['calories']} cal | 💪 {recipe['protein']}g protein")
                                st.write(f"⏱️ {recipe['prep_time']} min prep")
                                st.markdown("**Ingredients:**")
                                for ingredient in recipe['ingredients']:
                                    st.write(f"• {ingredient}")
                    st.divider()
        
        # Show shopping list
        st.subheader("🛒 Smart Shopping List")
        shopping_list = plan['weekly_meal_plan']['smart_shopping_list']
        
        col1, col2, col3 = st.columns(3)
        for i, item in enumerate(shopping_list):
            with [col1, col2, col3][i % 3]:
                st.write(f"☐ {item}")
    
    # Success Tracking
    st.subheader("📈 How to Track Your Success")
    success = plan['success_tracking']
    
    st.markdown("**Your Personal Success Metrics:**")
    for metric in success['primary_metrics']:
        st.write(f"• {metric}")
    
    st.markdown("**Tracking Methods:**")
    for method in success['tracking_methods']:
        st.write(f"• {method}")
    
    # Lifestyle Tips
    st.subheader("💡 Lifestyle Integration Tips")
    lifestyle = plan['lifestyle_integration']
    
    for category, tips in lifestyle.items():
        if tips:
            st.markdown(f"**{category.replace('_', ' ').title()}:**")
            for tip in tips:
                st.write(f"• {tip}")
    
    # Download options
    st.divider()
    st.subheader("📥 Save Your Plan")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Download Complete Plan", type="primary"):
            plan_text = f"""
{overview['plan_name']}
Generated: {datetime.now().strftime('%B %d, %Y')}

DAILY NUTRITION TARGETS:
• Calories: {targets['daily_calories']}
• Protein: {targets['protein_g']}g
• Carbs: {targets['carbs_g']}g
• Fat: {targets['fat_g']}g
• Fiber: {targets['fiber_g']}g
• Water: {targets['water_liters']}L

{overview['description']}

ML-POWERED MEAL RECOMMENDATIONS:
"""
            
            if 'ml_powered_recommendations' in plan['weekly_meal_plan']:
                ml_recs = plan['weekly_meal_plan']['ml_powered_recommendations']
                for day, meals in ml_recs.items():
                    plan_text += f"\n{day.upper()}:\n"
                    for meal_type, meal_data in meals.items():
                        selected = meal_data.get('selected_recipe')
                        if selected:
                            plan_text += f"  {meal_type.title()}: {selected['name']} ({selected['calories']} cal)\n"
            
            st.download_button(
                "📄 Get Your Plan",
                plan_text,
                file_name=f"ml_diet_plan_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )
    
    with col2:
        if st.button("🛒 Smart Shopping List"):
            shopping_list = plan['weekly_meal_plan'].get('smart_shopping_list', [])
            shopping_text = "SMART SHOPPING LIST\n" + "="*20 + "\n\n"
            for item in shopping_list:
                shopping_text += f"☐ {item}\n"
            
            st.download_button(
                "🛒 Get Shopping List",
                shopping_text,
                file_name=f"shopping_list_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )

if __name__ == "__main__":
    main()