#!/usr/bin/env python3

import os
import json
import requests
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ConversationMessage:
    role: str
    content: str
    timestamp: datetime
    category: str

class EnhancedDeepSeekClient:
    """Enhanced DeepSeek client with fine-tuned model support"""
    
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Try to load fine-tuned model info
        self.model_id = self._get_fine_tuned_model_id()
        
    def _get_fine_tuned_model_id(self) -> str:
        """Get fine-tuned model ID if available"""
        try:
            with open("fine_tuning_job_info.json", "r") as f:
                job_info = json.load(f)
                if job_info.get("status") == "completed":
                    return job_info.get("model_id", "deepseek-chat")
        except FileNotFoundError:
            pass
        
        return "deepseek-chat"  # Fallback to base model
    
    def generate_fitness_response(self, query: str, user_context: str = "") -> str:
        """Generate fitness-specific response"""
        
        system_prompt = """You are a specialized AI fitness assistant with expertise in:
- Exercise routines and workout planning
- Nutrition and meal planning
- Weight management and body composition
- Muscle building and strength training
- Cardio and endurance training
- Recovery and injury prevention
- Fitness motivation and goal setting

Provide helpful, accurate, and encouraging advice. Always prioritize safety and recommend consulting healthcare professionals when appropriate."""

        return self._generate_response(query, system_prompt, user_context, "fitness")
    
    def generate_mental_health_response(self, query: str, user_context: str = "") -> str:
        """Generate mental health-specific response"""
        
        system_prompt = """You are a specialized AI mental health support assistant with expertise in:
- Anxiety and stress management
- Depression support and coping strategies
- Self-esteem and confidence building
- Motivation and goal achievement
- Social connection and relationship support
- Exercise and mental health connections
- Mindfulness and relaxation techniques

Provide empathetic, supportive, and helpful guidance. Always emphasize that you're not a replacement for professional mental health care. Include crisis resources when appropriate."""

        return self._generate_response(query, system_prompt, user_context, "mental_health")
    
    def _generate_response(self, query: str, system_prompt: str, context: str, category: str) -> str:
        """Generate response using fine-tuned model"""
        
        try:
            # Prepare the full prompt with context
            if context:
                full_prompt = f"Previous conversation context: {context}\\n\\nCurrent question: {query}"
            else:
                full_prompt = query
            
            payload = {
                "model": self.model_id,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ],
                "max_tokens": 1500,
                "temperature": 0.7,
                "stream": False
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"]
                else:
                    return self._get_fallback_response(query, category)
            
            elif response.status_code == 402:
                return self._get_fallback_response(query, category)
            
            else:
                return self._get_fallback_response(query, category)
                
        except Exception as e:
            return self._get_fallback_response(query, category)
    
    def _get_fallback_response(self, query: str, category: str) -> str:
        """Provide fallback responses when API is unavailable"""
        
        if category == "fitness":
            return self._get_fitness_fallback(query)
        elif category == "mental_health":
            return self._get_mental_health_fallback(query)
        else:
            return "I'm currently using basic responses. I can still help with fitness, nutrition, and wellness questions!"
    
    def _get_fitness_fallback(self, query: str) -> str:
        """Enhanced fitness fallback responses"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['workout', 'exercise', 'routine', 'training']):
            if 'beginner' in query_lower:
                return """**Beginner Workout Plan:**

**Week 1-2: Foundation Building**
- Bodyweight squats: 2 sets of 8-12 reps
- Wall or knee push-ups: 2 sets of 5-10 reps
- Plank hold: 2 sets of 15-30 seconds
- Walking: 10-15 minutes daily

**Week 3-4: Progression**
- Add 2-3 more reps to each exercise
- Increase plank time by 10-15 seconds
- Extend walking to 20-25 minutes

**Key Tips:**
- Focus on proper form over speed
- Rest 48 hours between strength sessions
- Listen to your body and progress gradually
- Consistency is more important than intensity

**Safety First:** Start slowly and consult a healthcare provider if you have any health concerns."""

            elif 'home' in query_lower:
                return """**Complete Home Workout (No Equipment Needed):**

**Upper Body (10-15 minutes):**
- Push-ups (wall, knee, or full): 3 sets of 5-15 reps
- Pike push-ups (shoulders): 2 sets of 5-10 reps
- Tricep dips (chair): 2 sets of 8-12 reps
- Arm circles: 30 seconds each direction

**Lower Body (10-15 minutes):**
- Bodyweight squats: 3 sets of 10-20 reps
- Lunges: 2 sets of 8-12 each leg
- Calf raises: 2 sets of 15-25 reps
- Glute bridges: 2 sets of 12-20 reps

**Core (5-10 minutes):**
- Plank: 2-3 sets of 20-60 seconds
- Mountain climbers: 2 sets of 10-20 reps
- Dead bug: 2 sets of 8-12 each side

**Cardio Options:**
- Jumping jacks, high knees, or dancing to music

**Schedule:** 3-4 times per week with rest days between sessions."""

            else:
                return """**Balanced Workout Structure:**

**Warm-up (5-10 minutes):**
- Light cardio (walking, marching in place)
- Dynamic stretching (arm circles, leg swings)
- Joint mobility movements

**Strength Training (20-30 minutes):**
- Compound exercises (squats, push-ups, rows)
- 2-3 sets of 8-15 repetitions
- Focus on major muscle groups
- Progressive overload (gradually increase difficulty)

**Cardio (15-30 minutes):**
- Moderate intensity (can hold conversation)
- Options: walking, cycling, swimming, dancing
- Start with 15 minutes, build to 30+

**Cool-down (5-10 minutes):**
- Static stretching
- Deep breathing
- Gentle movements

**Weekly Schedule:**
- 3-4 strength sessions
- 2-3 cardio sessions
- 1-2 complete rest days
- Daily light movement (walking, stretching)"""

        elif any(word in query_lower for word in ['diet', 'nutrition', 'protein', 'food', 'meal']):
            if 'protein' in query_lower:
                return """**Complete Protein Guide:**

**Daily Protein Needs:**
- Sedentary adults: 0.8g per kg body weight
- Active individuals: 1.2-1.6g per kg
- Muscle building: 1.6-2.2g per kg
- Weight loss: 1.8-2.4g per kg (preserves muscle)

**High-Quality Protein Sources:**

**Animal Proteins:**
- Chicken breast: 25g per 100g
- Fish (salmon, tuna): 20-25g per 100g
- Eggs: 6g per large egg
- Greek yogurt: 15-20g per cup
- Cottage cheese: 14g per 1/2 cup

**Plant Proteins:**
- Lentils: 18g per cup cooked
- Quinoa: 8g per cup cooked
- Tofu: 10g per 100g
- Beans: 12-15g per cup
- Nuts/seeds: 4-8g per ounce

**Timing Tips:**
- Distribute evenly across meals (20-30g per meal)
- Post-workout: 20-40g within 2 hours
- Before bed: slow-digesting protein (Greek yogurt, casein)

**Sample Daily Plan:**
- Breakfast: Greek yogurt with berries (20g)
- Lunch: Chicken salad (25g)
- Snack: Protein shake (25g)
- Dinner: Salmon with quinoa (30g)
- Total: ~100g protein"""

            elif 'weight loss' in query_lower or 'lose weight' in query_lower:
                return """**Sustainable Weight Loss Nutrition:**

**Calorie Management:**
- Create moderate deficit: 300-500 calories below maintenance
- Use online calculators to estimate needs
- Track intake with apps (MyFitnessPal, Cronometer)
- Aim for 1-2 pounds loss per week

**Macronutrient Balance:**
- Protein: 25-30% of calories (preserves muscle)
- Carbs: 35-45% (fuel for workouts)
- Fats: 20-30% (hormone production, satiety)

**Food Choices:**
- Prioritize whole, unprocessed foods
- Lean proteins at every meal
- Plenty of vegetables (low calorie, high nutrients)
- Complex carbs (oats, quinoa, sweet potatoes)
- Healthy fats (avocado, nuts, olive oil)

**Meal Timing:**
- Eat regular meals to prevent overeating
- Don't skip meals (leads to poor choices later)
- Consider intermittent fasting if it fits your lifestyle

**Hydration:**
- Drink water before meals (helps with satiety)
- Often thirst is mistaken for hunger
- Aim for 8-10 glasses daily

**Sustainable Habits:**
- Plan and prep meals in advance
- Allow for occasional treats (80/20 rule)
- Focus on progress, not perfection
- Address emotional eating patterns"""

            else:
                return """**Balanced Nutrition for Active Individuals:**

**Daily Nutrition Framework:**

**Breakfast:**
- Protein source (eggs, Greek yogurt, protein powder)
- Complex carbs (oats, whole grain toast)
- Healthy fats (nuts, avocado)
- Fruits or vegetables

**Lunch:**
- Lean protein (chicken, fish, tofu)
- Vegetables (aim for variety and color)
- Complex carbs (quinoa, brown rice, sweet potato)
- Healthy fats (olive oil, nuts, seeds)

**Dinner:**
- Similar to lunch but potentially lighter portions
- Focus on vegetables and lean protein
- Limit heavy carbs if not training later

**Snacks:**
- Protein-rich options
- Fruits with nut butter
- Greek yogurt with berries
- Hummus with vegetables

**Pre-Workout (1-2 hours before):**
- Easily digestible carbs (banana, oats)
- Small amount of protein
- Minimal fat and fiber
- Adequate hydration

**Post-Workout (within 2 hours):**
- Protein for muscle recovery (20-40g)
- Carbs to replenish glycogen
- Examples: protein shake with fruit, chocolate milk

**Hydration:**
- 35ml per kg body weight daily
- More during exercise and hot weather
- Monitor urine color (pale yellow is ideal)

**Supplements to Consider:**
- Multivitamin (insurance policy)
- Vitamin D (if limited sun exposure)
- Omega-3 (if low fish intake)
- Protein powder (convenience)"""

        elif any(word in query_lower for word in ['weight', 'lose', 'gain', 'fat', 'calories']):
            if 'gain' in query_lower:
                return """**Healthy Weight Gain Strategy:**

**Caloric Surplus:**
- Eat 300-500 calories above maintenance
- Focus on nutrient-dense, calorie-rich foods
- Don't rely on junk food for extra calories

**Protein Priority:**
- 1.6-2.2g per kg body weight
- Include protein at every meal and snack
- Consider protein shakes between meals

**Calorie-Dense Healthy Foods:**
- Nuts, nut butters, and seeds
- Avocados and olive oil
- Whole grains and starchy vegetables
- Dried fruits and smoothies
- Fatty fish like salmon

**Meal Frequency:**
- Eat every 2-3 hours
- Don't skip meals
- Add healthy snacks between meals
- Consider liquid calories (smoothies, milk)

**Strength Training:**
- Essential for gaining muscle, not just fat
- Focus on compound movements
- Progressive overload principle
- 3-4 sessions per week

**Sample Day:**
- Breakfast: Oatmeal with nuts, banana, protein powder
- Snack: Trail mix and Greek yogurt
- Lunch: Quinoa bowl with chicken, avocado, olive oil
- Snack: Smoothie with protein, fruits, nut butter
- Dinner: Salmon, sweet potato, vegetables with olive oil
- Evening: Greek yogurt with nuts

**Timeline:** Healthy weight gain is 0.5-1 pound per week"""

            else:
                return """**Sustainable Weight Management:**

**Understanding Energy Balance:**
- Weight loss: Calories in < Calories out
- Weight maintenance: Calories in = Calories out
- Weight gain: Calories in > Calories out

**Creating a Calorie Deficit for Weight Loss:**
- Moderate deficit: 300-500 calories daily
- Combine diet and exercise
- Don't go below 1200 calories (women) or 1500 (men)
- Aim for 1-2 pounds loss per week

**Metabolism Factors:**
- Muscle tissue burns more calories at rest
- Strength training preserves muscle during weight loss
- Cardio burns calories during activity
- NEAT (daily movement) significantly impacts metabolism

**Sustainable Strategies:**
- Make gradual changes to eating habits
- Focus on whole, unprocessed foods
- Practice portion control
- Stay hydrated
- Get adequate sleep (affects hunger hormones)
- Manage stress (cortisol affects weight)

**Tracking Progress:**
- Use multiple metrics (weight, measurements, photos)
- Weight fluctuates daily (water, food, hormones)
- Focus on trends over time
- Celebrate non-scale victories

**Avoiding Common Mistakes:**
- Don't drastically cut calories
- Don't eliminate entire food groups
- Don't rely solely on cardio
- Don't expect linear progress
- Don't ignore strength training

**Long-term Success:**
- Build sustainable habits
- Allow for flexibility and treats
- Address emotional eating
- Seek support when needed
- Focus on health, not just appearance"""

        elif any(word in query_lower for word in ['muscle', 'strength', 'build', 'mass']):
            return """**Complete Muscle Building Guide:**

**Training Principles:**
- Progressive overload: gradually increase weight, reps, or sets
- Compound exercises: squats, deadlifts, pull-ups, push-ups
- Rep ranges: 6-12 reps for hypertrophy (muscle growth)
- Sets: 2-4 sets per exercise
- Frequency: train each muscle group 2-3 times per week

**Essential Exercises:**

**Upper Body:**
- Push-ups (chest, shoulders, triceps)
- Pull-ups/rows (back, biceps)
- Pike push-ups (shoulders)
- Tricep dips

**Lower Body:**
- Squats (quads, glutes)
- Lunges (quads, glutes, hamstrings)
- Glute bridges (glutes, hamstrings)
- Calf raises

**Core:**
- Planks (entire core)
- Dead bugs (deep core stability)
- Mountain climbers (dynamic core)

**Nutrition for Muscle Growth:**
- Protein: 1.6-2.2g per kg body weight daily
- Caloric surplus: 200-500 calories above maintenance
- Carbs: 4-7g per kg (fuel for workouts)
- Fats: 0.8-1.2g per kg (hormone production)

**Recovery Requirements:**
- Sleep: 7-9 hours per night (growth hormone release)
- Rest days: 48 hours between training same muscles
- Hydration: adequate water intake
- Stress management: chronic stress impairs recovery

**Timeline Expectations:**
- Noticeable changes: 4-6 weeks
- Significant muscle gain: 3-6 months
- Substantial transformation: 1-2 years
- Consistency is key!

**Beginner Program (3 days/week):**
- Day 1: Push-ups, squats, planks
- Day 2: Rest or light cardio
- Day 3: Pull-ups/rows, lunges, side planks
- Day 4: Rest
- Day 5: Full body circuit
- Days 6-7: Rest or light activity"""

        elif any(word in query_lower for word in ['cardio', 'running', 'walking', 'endurance']):
            return """**Complete Cardio Guide:**

**Types of Cardiovascular Exercise:**

**HIIT (High-Intensity Interval Training):**
- Alternates high intensity with recovery periods
- Duration: 15-30 minutes
- Frequency: 2-3 times per week
- Benefits: time-efficient, burns calories during and after exercise
- Example: 30 seconds sprint, 90 seconds walk, repeat 8-12 times

**Steady-State Cardio:**
- Consistent moderate intensity
- Duration: 30-60 minutes
- Frequency: 3-5 times per week
- Benefits: builds aerobic base, easier recovery
- Examples: jogging, cycling, swimming at conversational pace

**LISS (Low-Intensity Steady State):**
- Low intensity for extended periods
- Duration: 45-90 minutes
- Frequency: daily if desired
- Benefits: active recovery, fat burning, low stress on body
- Examples: walking, easy cycling, gentle swimming

**Heart Rate Zones:**
- Zone 1 (50-60% max HR): Active recovery
- Zone 2 (60-70% max HR): Fat burning, aerobic base
- Zone 3 (70-80% max HR): Aerobic fitness
- Zone 4 (80-90% max HR): Lactate threshold
- Zone 5 (90-100% max HR): Neuromuscular power

**Max Heart Rate Estimate:** 220 - your age

**Beginner Cardio Program:**
- Week 1-2: 15-20 minutes easy walking daily
- Week 3-4: 20-25 minutes, add 2-3 minutes jogging intervals
- Week 5-6: 25-30 minutes, increase jogging intervals
- Week 7-8: 30+ minutes, mix walking and jogging as comfortable

**Benefits of Regular Cardio:**
- Improved heart and lung health
- Better circulation and blood pressure
- Enhanced mood and mental health
- Increased energy and endurance
- Better sleep quality
- Weight management support
- Reduced risk of chronic diseases

**Making Cardio Enjoyable:**
- Choose activities you enjoy
- Listen to music, podcasts, or audiobooks
- Exercise with friends or groups
- Vary your routes and activities
- Set small, achievable goals
- Track progress to stay motivated"""

        else:
            return """**Comprehensive Fitness Guidance:**

I'm here to help with all aspects of fitness and health! Here are the key areas I can assist with:

**Workout Planning:**
- Beginner to advanced exercise routines
- Home workouts with no equipment
- Gym-based strength training programs
- Cardio and endurance training
- Flexibility and mobility work

**Nutrition Support:**
- Meal planning for various goals
- Protein requirements and sources
- Pre and post-workout nutrition
- Weight management strategies
- Healthy eating habits

**Goal-Specific Guidance:**
- Weight loss and fat burning
- Muscle building and strength gains
- Improved fitness and endurance
- Better health and wellness
- Sport-specific training

**Motivation and Habits:**
- Setting realistic, achievable goals
- Building consistent exercise habits
- Overcoming common obstacles
- Tracking progress effectively
- Staying motivated long-term

**Safety and Recovery:**
- Proper exercise form and technique
- Injury prevention strategies
- Recovery and rest day planning
- When to seek professional help

**Getting Started Tips:**
1. Start with small, manageable changes
2. Focus on consistency over perfection
3. Listen to your body and progress gradually
4. Combine both exercise and nutrition improvements
5. Seek support from friends, family, or professionals

What specific aspect of fitness would you like to focus on today?"""

    def _get_mental_health_fallback(self, query: str) -> str:
        """Enhanced mental health fallback responses"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['anxious', 'anxiety', 'stress', 'worried', 'panic', 'overwhelmed']):
            return """**Understanding and Managing Anxiety:**

**Immediate Anxiety Relief Techniques:**

**Breathing Exercises:**
- 4-7-8 breathing: Inhale for 4, hold for 7, exhale for 8
- Box breathing: 4 counts in, 4 hold, 4 out, 4 hold
- Belly breathing: Focus on expanding your diaphragm

**Grounding Techniques:**
- 5-4-3-2-1 method: Name 5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste
- Progressive muscle relaxation: Tense and release each muscle group
- Mindful observation: Focus intently on one object for 2-3 minutes

**Physical Strategies:**
- Gentle exercise: walking, stretching, yoga
- Cold water on wrists or face
- Gentle self-massage (temples, shoulders, hands)

**Cognitive Approaches:**
- Challenge anxious thoughts: "Is this thought helpful? Is it realistic?"
- Practice self-compassion: "What would I tell a good friend in this situation?"
- Focus on what you can control right now

**Exercise and Anxiety:**
- Regular physical activity reduces anxiety over time
- Start with gentle movement: 10-15 minute walks
- Yoga and tai chi are particularly beneficial
- Avoid intense exercise during acute anxiety

**Building Long-term Resilience:**
- Maintain regular sleep schedule (7-9 hours)
- Limit caffeine and alcohol
- Practice daily stress management
- Build strong social connections
- Consider professional therapy (CBT is very effective for anxiety)

**When to Seek Professional Help:**
- Anxiety interferes with daily activities
- Physical symptoms are severe or frequent
- You're avoiding important activities due to anxiety
- Anxiety persists despite self-help efforts

**Crisis Resources:**
- National Suicide Prevention Lifeline: 988
- Crisis Text Line: Text HOME to 741741
- Local emergency services: 911

Remember: Anxiety is treatable, and you don't have to face it alone."""

        elif any(word in query_lower for word in ['depressed', 'depression', 'sad', 'hopeless', 'low', 'down']):
            return """**Understanding and Coping with Depression:**

**Gentle First Steps:**

**Micro-Activities (Choose just ONE daily):**
- Step outside for 2-3 minutes
- Take a shower or wash your face
- Make your bed
- Eat one nutritious meal
- Text one supportive person
- Listen to one favorite song
- Do 5 minutes of gentle stretching

**Why These Small Steps Matter:**
- Depression tells us we can't do anything
- Small successes build momentum
- Each action is an act of self-care
- Progress doesn't have to be dramatic

**Exercise and Depression:**
- Physical activity is as effective as medication for mild-moderate depression
- Start incredibly small: 5-10 minute walks
- Natural sunlight helps regulate mood
- Any movement counts - dancing, gardening, cleaning
- Exercise releases natural mood-boosters (endorphins, serotonin)

**Daily Structure:**
- Try to wake up at the same time each day
- Plan one small, achievable goal
- Include basic self-care (eating, hygiene)
- Connect with at least one person
- Spend some time outdoors if possible

**Challenging Depressive Thoughts:**
- Depression distorts thinking patterns
- Practice self-compassion: "I'm doing the best I can right now"
- Remember: feelings are temporary, even when they don't feel like it
- Focus on facts, not feelings: "I am safe right now"

**Building Support:**
- Reach out to trusted friends or family
- Consider joining support groups (online or in-person)
- Don't isolate yourself, even when it feels easier
- Let people know how they can help you

**Professional Support:**
- Therapy (especially CBT and IPT) is highly effective
- Medication can be helpful for many people
- Your primary care doctor is a good starting point
- Many communities have sliding-scale mental health services

**Crisis Resources:**
- National Suicide Prevention Lifeline: 988
- Crisis Text Line: Text HOME to 741741
- National Alliance on Mental Illness (NAMI): 1-800-950-NAMI

**Important Reminders:**
- Depression is a medical condition, not a character flaw
- Recovery is possible with proper support and treatment
- You are not alone in this experience
- Seeking help is a sign of strength, not weakness
- Your life has value, even when depression tells you otherwise

What feels most manageable for you to try today?"""

        elif any(word in query_lower for word in ['confidence', 'self-esteem', 'insecure', 'body image', 'judged', 'embarrassed']):
            return """**Building Confidence and Self-Esteem:**

**Understanding Low Self-Esteem:**
- Often develops from past experiences or comparisons
- Negative self-talk becomes automatic
- Can affect all areas of life, including fitness
- Is changeable with consistent effort and practice

**Cognitive Strategies:**

**Challenge Negative Self-Talk:**
- Notice when you're being self-critical
- Ask: "Would I talk to a friend this way?"
- Replace harsh criticism with constructive feedback
- Practice the "best friend" test: What would you tell a good friend?

**Reframe Comparisons:**
- Compare yourself to your past self, not others
- Remember: social media shows highlight reels, not reality
- Focus on your unique strengths and progress
- Celebrate small victories and improvements

**Body Image and Exercise:**
- Focus on what your body can DO, not just how it looks
- Appreciate your body's strength, endurance, and capabilities
- Choose activities that make you feel strong and capable
- Wear comfortable clothes that make you feel good

**Building Confidence Through Action:**

**Start Small:**
- Set tiny, achievable goals you can definitely accomplish
- Build momentum with consistent small successes
- Gradually increase challenges as confidence grows

**Develop Competence:**
- Learn new skills (exercise techniques, healthy recipes)
- Practice regularly to build mastery
- Seek guidance from qualified instructors or trainers
- Remember: everyone starts as a beginner

**Social Confidence:**
- Start exercising in comfortable environments (home, less crowded times)
- Bring a supportive friend initially
- Remember: most people are focused on their own workouts
- Practice positive body language (stand tall, make eye contact)

**Self-Compassion Practices:**
- Treat yourself with the same kindness you'd show a good friend
- Acknowledge that everyone struggles sometimes
- Practice mindfulness: observe thoughts without judgment
- Use encouraging self-talk: "I'm learning and growing"

**Building a Support Network:**
- Surround yourself with positive, encouraging people
- Limit time with those who are consistently negative or critical
- Join communities aligned with your values and goals
- Consider working with a therapist who specializes in self-esteem

**Daily Confidence-Building Habits:**
- Keep a gratitude journal (3 things daily)
- Write down one thing you did well each day
- Practice good posture and confident body language
- Engage in activities that make you feel capable and strong
- Dress in a way that makes you feel good about yourself

**Professional Support:**
- Therapy can be very effective for self-esteem issues
- Cognitive Behavioral Therapy (CBT) is particularly helpful
- Support groups provide connection with others facing similar challenges

**Remember:**
- Confidence is built through action, not just thinking
- Progress isn't always linear - expect ups and downs
- You are worthy of respect and kindness, especially from yourself
- Your value as a person isn't determined by your appearance or fitness level

What's one small step you could take today to show yourself kindness?"""

        elif any(word in query_lower for word in ['motivation', 'goals', 'quit', 'giving up', 'consistency', 'habits']):
            return """**Building Lasting Motivation and Habits:**

**Understanding Motivation:**
- Motivation gets you started, but habits keep you going
- It's normal for motivation to fluctuate
- Relying solely on motivation leads to inconsistency
- Systems and habits are more reliable than willpower

**Setting Effective Goals:**

**SMART Goals Framework:**
- Specific: Clear and well-defined
- Measurable: Trackable progress
- Achievable: Realistic given your current situation
- Relevant: Meaningful to your life and values
- Time-bound: Has a deadline

**Process vs. Outcome Goals:**
- Process: "Exercise 3 times this week"
- Outcome: "Lose 10 pounds"
- Focus more on process goals (you control the actions)

**Building Sustainable Habits:**

**Start Ridiculously Small:**
- 5-minute walks instead of 60-minute workouts
- 1 push-up instead of 50
- One healthy meal instead of complete diet overhaul
- Success builds momentum

**Habit Stacking:**
- Attach new habits to existing routines
- "After I brush my teeth, I will do 10 squats"
- "After I pour my morning coffee, I will review my workout plan"

**Environment Design:**
- Make good choices easier (lay out workout clothes)
- Remove barriers to success (prep healthy snacks)
- Create visual reminders of your goals

**Overcoming Setbacks:**

**Expect and Plan for Obstacles:**
- Identify potential challenges in advance
- Create "if-then" plans: "If it's raining, then I'll do an indoor workout"
- Have backup options ready

**The "Two-Day Rule":**
- Never allow yourself to go more than two days without doing your habit
- One day off is fine, two days starts breaking the chain
- Get back on track immediately after a miss

**Reframe Setbacks:**
- View them as learning opportunities, not failures
- Ask: "What can I learn from this?"
- Focus on getting back on track, not on the mistake

**Maintaining Long-term Motivation:**

**Connect to Your "Why":**
- Identify deeper reasons beyond surface goals
- Examples: "I want energy to play with my kids" vs. "I want to look good"
- Write down your reasons and review them regularly

**Track Multiple Metrics:**
- Energy levels and mood
- Strength and endurance improvements
- Sleep quality
- Stress levels
- Not just weight or appearance

**Celebrate Progress:**
- Acknowledge small wins along the way
- Reward consistency, not just outcomes
- Share successes with supportive people
- Keep a progress journal or photo log

**Social Support and Accountability:**
- Find workout partners or accountability buddies
- Join communities with similar goals
- Share your goals with supportive friends and family
- Consider working with a trainer or coach

**Dealing with Perfectionism:**
- Progress over perfection
- "Good enough" is better than not doing anything
- 80% consistency is much better than 0%
- Focus on showing up, not perfect performance

**Seasonal Motivation Strategies:**
- Expect motivation to ebb and flow
- Have different strategies for high and low motivation periods
- During low periods: focus on minimum effective dose
- During high periods: build momentum but don't overdo it

**Professional Support:**
- Consider working with a therapist if motivation issues are part of larger mental health concerns
- A personal trainer can provide external accountability and expertise
- Life coaches specialize in goal achievement and habit formation

**Remember:**
- Consistency beats intensity
- Small actions compound over time
- You don't have to feel motivated to take action
- Every day is a new opportunity to make progress

What's the smallest step you could commit to taking consistently?"""

        elif any(word in query_lower for word in ['lonely', 'isolated', 'alone', 'social', 'friends']):
            return """**Overcoming Loneliness and Building Connections:**

**Understanding Loneliness:**
- Loneliness is about quality, not quantity of relationships
- It's a common human experience, especially in modern society
- Can affect physical and mental health
- Is changeable with intentional effort and time

**Exercise as Social Connection:**

**Group Activities:**
- Fitness classes (yoga, Zumba, spin, boot camp)
- Walking or running groups
- Recreational sports leagues
- Hiking clubs or outdoor groups
- Dance classes
- Martial arts or self-defense classes

**Gym and Fitness Center Connections:**
- Attend classes regularly to see familiar faces
- Ask for help with equipment or form
- Offer encouragement to others
- Participate in gym challenges or events
- Consider working with a personal trainer

**Starting Small:**
- Make eye contact and smile
- Say "good morning" or "have a great workout"
- Compliment someone genuinely
- Ask simple questions about exercises or classes
- Be consistent - relationships take time to develop

**Building Broader Social Connections:**

**Community Involvement:**
- Volunteer for causes you care about
- Join clubs or groups based on interests
- Attend community events and activities
- Take classes (cooking, art, language, etc.)
- Participate in religious or spiritual communities

**Online to Offline:**
- Join online communities related to your interests
- Attend meetups or events organized through apps
- Participate in virtual fitness challenges that have local components
- Use social media to find local groups and activities

**Workplace and Neighborhood:**
- Suggest walking meetings with colleagues
- Organize or join workplace fitness challenges
- Get to know neighbors through community activities
- Participate in local events and festivals

**Overcoming Social Anxiety:**

**Gradual Exposure:**
- Start with low-pressure social situations
- Practice small talk in safe environments (cashiers, neighbors)
- Attend events with the goal of just showing up, not necessarily talking
- Bring a friend initially for support

**Conversation Starters:**
- Ask about someone's workout routine or favorite exercises
- Comment on classes or gym equipment
- Ask for recommendations (restaurants, activities, etc.)
- Share appropriate personal experiences

**Managing Expectations:**
- Not every interaction will lead to friendship
- Focus on being friendly rather than making friends
- Quality connections take time to develop
- Be patient with yourself and the process

**Self-Care While Building Connections:**

**Maintain Individual Interests:**
- Continue activities you enjoy alone
- Develop hobbies and skills independently
- Practice self-compassion during lonely periods
- Remember that alone time can be valuable too

**Mental Health Support:**
- Consider therapy if loneliness is severely impacting your life
- Practice mindfulness and self-acceptance
- Address any underlying depression or anxiety
- Build a relationship with yourself first

**Online Communities and Support:**
- Join fitness-focused online communities
- Participate in virtual workout groups
- Use apps that connect people with similar interests
- Remember: online connections can supplement but not replace in-person relationships

**Creating Opportunities:**
- Host or organize activities yourself
- Invite acquaintances to join you for activities
- Be the person who reaches out first
- Suggest post-workout activities (coffee, healthy meals)

**Professional and Structured Support:**
- Group therapy or support groups
- Community centers often have social programs
- Religious or spiritual communities
- Professional networking groups
- Volunteer organizations

**Remember:**
- Many people are also looking for connections
- Your openness and friendliness might be exactly what someone else needs
- Building relationships takes time and consistent effort
- Quality is more important than quantity
- You have value to offer in relationships

**Crisis Resources:**
If loneliness is leading to thoughts of self-harm:
- National Suicide Prevention Lifeline: 988
- Crisis Text Line: Text HOME to 741741
- Local emergency services: 911

What's one small social step you feel comfortable taking this week?"""

        else:
            return """**Mental Health and Wellness Support:**

Thank you for reaching out. Taking care of your mental health is just as important as physical health, and I'm here to provide support and guidance.

**Common Mental Health Topics I Can Help With:**

**Anxiety and Stress Management:**
- Coping strategies and relaxation techniques
- Exercise as anxiety relief
- Building resilience and managing worry
- Breathing exercises and grounding techniques

**Depression and Low Mood:**
- Gentle activities to improve mood
- Building daily structure and routine
- Using exercise as natural mood support
- Finding motivation during difficult times

**Self-Esteem and Confidence:**
- Building body confidence through fitness
- Overcoming gym anxiety and social fears
- Developing self-compassion and positive self-talk
- Setting and achieving personal goals

**Motivation and Goal Achievement:**
- Creating sustainable habits and routines
- Overcoming perfectionism and all-or-nothing thinking
- Building consistency and accountability
- Dealing with setbacks and maintaining progress

**Social Connection and Loneliness:**
- Finding community through fitness and activities
- Building social skills and confidence
- Overcoming isolation and making connections
- Balancing alone time with social interaction

**Exercise and Mental Health Connection:**
- How physical activity improves mood and reduces anxiety
- Using movement as stress relief and emotional regulation
- Finding the right type of exercise for mental health benefits
- Creating a balanced approach to fitness and wellness

**Important Reminders:**
- You are not alone in whatever you're experiencing
- Seeking help and support is a sign of strength
- Mental health challenges are treatable and manageable
- Small steps and gradual progress are perfectly valid
- Professional help is available and can be very effective

**When to Seek Professional Help:**
- If you're having thoughts of self-harm or suicide
- If symptoms interfere significantly with daily life
- If you're using substances to cope
- If you feel overwhelmed and unable to manage on your own
- If friends or family have expressed concern about you

**Crisis Resources:**
- National Suicide Prevention Lifeline: 988
- Crisis Text Line: Text HOME to 741741
- National Alliance on Mental Illness (NAMI): 1-800-950-NAMI
- Local emergency services: 911

**Professional Support Options:**
- Therapy (CBT, DBT, and other approaches are very effective)
- Support groups (in-person and online)
- Your primary care doctor can provide referrals
- Many employers offer Employee Assistance Programs (EAP)
- Community mental health centers often offer sliding-scale fees

Remember: You deserve support, care, and compassion - especially from yourself. What's one area you'd like to focus on today?"""

class ConversationManager:
    """Manages conversation history and context"""
    
    def __init__(self):
        self.conversations = {}
    
    def add_message(self, user_id: str, role: str, content: str, category: str):
        """Add message to conversation history"""
        if user_id not in self.conversations:
            self.conversations[user_id] = []
        
        message = ConversationMessage(
            role=role,
            content=content,
            timestamp=datetime.now(),
            category=category
        )
        
        self.conversations[user_id].append(message)
        
        # Keep only last 10 messages to manage context length
        if len(self.conversations[user_id]) > 10:
            self.conversations[user_id] = self.conversations[user_id][-10:]
    
    def get_context(self, user_id: str, category: str = None) -> str:
        """Get conversation context for user"""
        if user_id not in self.conversations:
            return ""
        
        messages = self.conversations[user_id]
        
        # Filter by category if specified
        if category:
            messages = [msg for msg in messages if msg.category == category]
        
        # Get last 5 messages for context
        recent_messages = messages[-5:]
        
        context_parts = []
        for msg in recent_messages:
            context_parts.append(f"{msg.role}: {msg.content[:100]}...")
        
        return "\\n".join(context_parts)

# Global instances
enhanced_client = EnhancedDeepSeekClient()
conversation_manager = ConversationManager()

def get_fitness_response(user_id: str, query: str) -> str:
    """Get fitness response with conversation context"""
    context = conversation_manager.get_context(user_id, "fitness")
    response = enhanced_client.generate_fitness_response(query, context)
    
    # Add to conversation history
    conversation_manager.add_message(user_id, "user", query, "fitness")
    conversation_manager.add_message(user_id, "assistant", response, "fitness")
    
    return response

def get_mental_health_response(user_id: str, query: str) -> str:
    """Get mental health response with conversation context"""
    context = conversation_manager.get_context(user_id, "mental_health")
    response = enhanced_client.generate_mental_health_response(query, context)
    
    # Add to conversation history
    conversation_manager.add_message(user_id, "user", query, "mental_health")
    conversation_manager.add_message(user_id, "assistant", response, "mental_health")
    
    return response