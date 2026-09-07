#!/usr/bin/env python3

import json
import random
from typing import List, Dict

class FitnessDatasetGenerator:
    def __init__(self):
        self.fitness_topics = {
            "workout_routines": [
                "What's the best workout routine for beginners?",
                "How do I create a full body workout?",
                "What exercises should I do for upper body strength?",
                "Can you suggest a home workout without equipment?",
                "What's a good 30-minute workout routine?",
                "How often should I work out each week?",
                "What's the difference between strength and cardio training?",
                "How do I build a workout routine for weight loss?",
                "What exercises are best for building muscle?",
                "Can you help me plan a weekly workout schedule?"
            ],
            "nutrition": [
                "How much protein should I eat daily?",
                "What's a good pre-workout meal?",
                "How do I meal prep for muscle building?",
                "What foods help with recovery after exercise?",
                "How many calories should I eat to lose weight?",
                "What are the best sources of healthy carbs?",
                "Should I take protein supplements?",
                "How much water should I drink during workouts?",
                "What's a balanced diet for an active person?",
                "How do I eat for endurance training?"
            ],
            "weight_management": [
                "How do I lose weight safely?",
                "What's the best way to gain healthy weight?",
                "How fast should I expect to lose weight?",
                "Why am I not losing weight despite exercising?",
                "How do I break through a weight loss plateau?",
                "What's more important for weight loss: diet or exercise?",
                "How do I maintain my weight after losing it?",
                "Is it possible to lose fat and gain muscle simultaneously?",
                "What's a realistic weight loss goal?",
                "How do I calculate my daily calorie needs?"
            ],
            "muscle_building": [
                "How do I build muscle as a beginner?",
                "What's the best rep range for muscle growth?",
                "How long does it take to see muscle gains?",
                "Should I lift heavy weights or do more reps?",
                "How important is rest for muscle building?",
                "What supplements help with muscle growth?",
                "How do I prevent muscle loss while cutting?",
                "What's the role of progressive overload?",
                "How do I build muscle without a gym?",
                "Why aren't my muscles growing despite working out?"
            ],
            "cardio_fitness": [
                "What's the best cardio for weight loss?",
                "How long should my cardio sessions be?",
                "Is HIIT better than steady-state cardio?",
                "How do I improve my running endurance?",
                "What's a good cardio routine for beginners?",
                "How often should I do cardio?",
                "Can I do cardio every day?",
                "What's the best time to do cardio?",
                "How do I make cardio more enjoyable?",
                "What heart rate should I target during cardio?"
            ]
        }
        
        self.mental_health_topics = {
            "anxiety_stress": [
                "I'm feeling anxious about starting to exercise",
                "How can exercise help with my anxiety?",
                "I get panic attacks during workouts, what should I do?",
                "I'm stressed about work and can't relax",
                "How do I manage stress through fitness?",
                "I feel overwhelmed with my fitness goals",
                "Exercise makes me more anxious, is this normal?",
                "How do I calm my mind before working out?",
                "I'm worried about exercising in public",
                "Stress is affecting my sleep, can you help?"
            ],
            "depression_mood": [
                "I'm feeling depressed and have no motivation to exercise",
                "How can working out help with depression?",
                "I feel sad all the time, will exercise help?",
                "I have no energy for anything, including exercise",
                "How do I start exercising when I'm depressed?",
                "I feel hopeless about my fitness journey",
                "Exercise used to make me happy, but not anymore",
                "I'm in a dark place mentally, can fitness help?",
                "How do I find motivation when I'm feeling low?",
                "I cry during workouts, is this normal?"
            ],
            "self_esteem_confidence": [
                "I'm insecure about my body at the gym",
                "How do I build confidence through fitness?",
                "I feel judged when I exercise in public",
                "I hate how I look, will working out help?",
                "I'm embarrassed about my fitness level",
                "How do I overcome body image issues?",
                "I feel like I don't belong at the gym",
                "Everyone seems fitter than me, I feel discouraged",
                "How do I stop comparing myself to others?",
                "I lack confidence in my ability to get fit"
            ],
            "motivation_goals": [
                "How do I stay motivated to work out consistently?",
                "I keep giving up on my fitness goals",
                "I start strong but always quit after a few weeks",
                "How do I set realistic fitness goals?",
                "I feel like I'm not making progress",
                "How do I get back on track after a setback?",
                "I've lost motivation, how do I get it back?",
                "How do I maintain long-term fitness habits?",
                "I'm struggling with consistency in my workouts",
                "How do I celebrate fitness milestones?"
            ],
            "social_isolation": [
                "I feel lonely and isolated, can exercise help?",
                "How do I make friends through fitness?",
                "I prefer working out alone but feel lonely",
                "Are there social aspects to fitness I'm missing?",
                "I'm too shy to join group fitness classes",
                "How do I find workout partners?",
                "I feel disconnected from others, will gym help?",
                "I'm new to the area and want to meet people through fitness",
                "How do I overcome social anxiety at the gym?",
                "I miss the social aspect of team sports"
            ]
        }

    def generate_fitness_response(self, query: str) -> str:
        """Generate comprehensive fitness responses"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['routine', 'workout', 'exercise', 'training']):
            return self._generate_workout_response(query)
        elif any(word in query_lower for word in ['protein', 'nutrition', 'diet', 'food', 'meal']):
            return self._generate_nutrition_response(query)
        elif any(word in query_lower for word in ['weight', 'lose', 'gain', 'fat', 'calories']):
            return self._generate_weight_response(query)
        elif any(word in query_lower for word in ['muscle', 'strength', 'build', 'mass']):
            return self._generate_muscle_response(query)
        elif any(word in query_lower for word in ['cardio', 'running', 'endurance', 'hiit']):
            return self._generate_cardio_response(query)
        else:
            return self._generate_general_fitness_response(query)

    def generate_mental_health_response(self, query: str) -> str:
        """Generate comprehensive mental health responses"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['anxious', 'anxiety', 'stress', 'worried', 'panic']):
            return self._generate_anxiety_response(query)
        elif any(word in query_lower for word in ['depressed', 'depression', 'sad', 'hopeless', 'low']):
            return self._generate_depression_response(query)
        elif any(word in query_lower for word in ['confidence', 'insecure', 'body image', 'judged', 'embarrassed']):
            return self._generate_confidence_response(query)
        elif any(word in query_lower for word in ['motivation', 'goals', 'quit', 'giving up', 'consistency']):
            return self._generate_motivation_response(query)
        elif any(word in query_lower for word in ['lonely', 'isolated', 'friends', 'social', 'alone']):
            return self._generate_social_response(query)
        else:
            return self._generate_general_mental_health_response(query)

    def _generate_workout_response(self, query: str) -> str:
        responses = [
            "Here's a comprehensive workout approach:\n\n**Beginner Full-Body Routine (3x/week):**\n- Bodyweight squats: 2-3 sets of 8-15 reps\n- Push-ups (modified if needed): 2-3 sets of 5-12 reps\n- Plank: 2-3 sets of 15-45 seconds\n- Walking/light jogging: 10-20 minutes\n\n**Key Principles:**\n- Progressive overload: gradually increase difficulty\n- Proper form over speed or weight\n- Rest 48 hours between sessions\n- Listen to your body\n\n**Progression Tips:**\n- Week 1-2: Focus on form and consistency\n- Week 3-4: Increase reps or duration\n- Week 5+: Add new exercises or resistance\n\nWould you like specific modifications based on your fitness level?",
            
            "Let me design a workout that fits your needs:\n\n**Upper Body Focus:**\n- Push-ups (wall, knee, or full): 3 sets\n- Pike push-ups for shoulders: 2 sets\n- Tricep dips (chair/couch): 2 sets\n- Arm circles and stretches: 5 minutes\n\n**Lower Body Focus:**\n- Squats: 3 sets of 10-20 reps\n- Lunges: 2 sets of 8-12 each leg\n- Calf raises: 2 sets of 15-25 reps\n- Glute bridges: 2 sets of 12-20 reps\n\n**Core Strengthening:**\n- Plank variations: 2-3 sets\n- Dead bug: 2 sets of 8-12 each side\n- Bird dog: 2 sets of 8-12 each side\n\n**Important:** Start with 2-3 exercises per session and build up gradually. Consistency beats intensity!"
        ]
        return random.choice(responses)

    def _generate_nutrition_response(self, query: str) -> str:
        responses = [
            "Here's your comprehensive nutrition guide:\n\n**Protein Requirements:**\n- General health: 0.8-1g per kg body weight\n- Active individuals: 1.2-1.6g per kg\n- Muscle building: 1.6-2.2g per kg\n- Weight loss: 1.8-2.4g per kg (higher protein preserves muscle)\n\n**Quality Protein Sources:**\n- Animal: chicken, fish, eggs, Greek yogurt, cottage cheese\n- Plant: beans, lentils, quinoa, tofu, tempeh, nuts\n- Supplements: whey, casein, or plant-based protein powder\n\n**Meal Timing:**\n- Distribute protein evenly across meals (20-30g per meal)\n- Post-workout: 20-40g protein within 2 hours\n- Before bed: slow-digesting protein (casein or Greek yogurt)\n\n**Hydration:** 35ml per kg body weight daily, more during exercise\n\nWould you like a specific meal plan based on your goals?",
            
            "Let's optimize your nutrition for results:\n\n**Pre-Workout Nutrition (1-2 hours before):**\n- Carbs for energy: banana, oatmeal, or toast\n- Light protein: Greek yogurt or small protein shake\n- Avoid high fat/fiber foods\n- Hydrate well\n\n**Post-Workout Recovery (within 2 hours):**\n- Protein: 20-40g for muscle repair\n- Carbs: replenish glycogen stores\n- Examples: protein shake with banana, chocolate milk, chicken and rice\n\n**Daily Nutrition Framework:**\n- Breakfast: protein + complex carbs\n- Lunch: lean protein + vegetables + healthy fats\n- Dinner: similar to lunch, lighter portions\n- Snacks: protein-rich options\n\n**Meal Prep Tips:**\n- Batch cook proteins on weekends\n- Pre-cut vegetables\n- Prepare grab-and-go snacks\n- Use containers for portion control"
        ]
        return random.choice(responses)

    def _generate_anxiety_response(self, query: str) -> str:
        responses = [
            "I understand that anxiety around exercise can feel overwhelming. You're not alone in this experience:\n\n**Immediate Anxiety Management:**\n- Deep breathing: 4 counts in, 6 counts out\n- Progressive muscle relaxation\n- Grounding technique: 5-4-3-2-1 (things you can see, touch, hear, smell, taste)\n- Remind yourself: 'This feeling will pass'\n\n**Exercise Modifications for Anxiety:**\n- Start with 5-10 minute sessions\n- Exercise in familiar, comfortable environments\n- Try gentle activities: walking, stretching, yoga\n- Exercise with a trusted friend or family member\n- Avoid caffeine before workouts\n\n**Building Confidence Gradually:**\n- Set tiny, achievable goals\n- Celebrate every small success\n- Focus on how exercise makes you feel afterward\n- Remember that everyone starts somewhere\n\n**Professional Support:**\n- Consider therapy for anxiety management\n- Speak with your doctor about exercise and anxiety\n- Look into anxiety support groups\n\nRemember: Exercise can actually reduce anxiety over time. What feels most manageable for you to try first?",
            
            "Anxiety during exercise is more common than you might think. Let's work through this together:\n\n**Understanding Exercise Anxiety:**\n- Physical sensations (increased heart rate, sweating) can trigger anxiety\n- Fear of judgment from others is normal\n- Perfectionism can create pressure\n- Past negative experiences may contribute\n\n**Gentle Approaches:**\n- Start with activities that feel safe (walking in nature)\n- Use guided meditation apps during/after exercise\n- Try online workout videos at home first\n- Focus on movement for mental health, not appearance\n\n**Coping Strategies:**\n- Prepare positive self-talk phrases\n- Bring headphones for distraction\n- Have an 'exit strategy' if you need to leave\n- Practice self-compassion when anxiety arises\n\n**When to Seek Help:**\n- If anxiety prevents you from daily activities\n- If panic attacks occur regularly\n- If you're avoiding all physical activity\n\nYour mental health is just as important as physical health. Would you like specific breathing exercises to try?"
        ]
        return random.choice(responses)

    def _generate_depression_response(self, query: str) -> str:
        responses = [
            "I hear you, and I want you to know that reaching out shows incredible strength. Depression can make everything feel impossible, including exercise:\n\n**Start Incredibly Small:**\n- Step outside for 2 minutes\n- Do 3 gentle stretches in bed\n- Walk to your mailbox and back\n- Dance to one favorite song\n- Sit in sunlight for 5 minutes\n\n**Why Movement Helps Depression:**\n- Releases natural mood-boosters (endorphins, serotonin)\n- Provides structure and routine\n- Improves sleep quality\n- Increases energy levels over time\n- Creates sense of accomplishment\n\n**Depression-Friendly Exercise:**\n- Walking in nature (even 10 minutes helps)\n- Gentle yoga or stretching\n- Swimming (if accessible)\n- Gardening or outdoor activities\n- Dancing to music you love\n\n**Be Patient With Yourself:**\n- Some days, just surviving is enough\n- Progress isn't linear\n- Celebrate tiny victories\n- Don't judge yourself for 'bad' days\n\n**Crisis Resources:**\n- National Suicide Prevention Lifeline: 988\n- Crisis Text Line: Text HOME to 741741\n- Consider professional counseling\n\nYou matter, and this feeling won't last forever. What feels most doable for you today?",
            
            "Depression can make even simple tasks feel overwhelming. Let's find gentle ways to support your mental health through movement:\n\n**Micro-Movements (Choose ONE):**\n- Stretch your arms above your head 5 times\n- Walk around your living space once\n- Do wall push-ups (3-5 reps)\n- March in place for 30 seconds\n- Take 5 deep breaths while moving your arms\n\n**Building Momentum:**\n- Set timer for 5 minutes of any movement\n- Focus on how you feel AFTER, not during\n- Track mood before and after activity\n- Use movement as self-care, not punishment\n\n**Social Support:**\n- Ask a friend to walk with you\n- Join online fitness communities\n- Consider group classes when ready\n- Share your goals with supportive people\n\n**Professional Help:**\n- Therapy can provide coping strategies\n- Medication might help if appropriate\n- Support groups connect you with others\n- Your doctor can assess if exercise is safe\n\n**Remember:** You're taking a brave step by asking for help. Depression lies to you about your worth and capabilities. You deserve care and support."
        ]
        return random.choice(responses)

    def generate_dataset(self, num_samples: int = 10000) -> List[Dict]:
        """Generate comprehensive training dataset"""
        dataset = []
        
        # Load base examples
        try:
            with open('fitness_mental_health_dataset.json', 'r') as f:
                base_examples = json.load(f)
                dataset.extend(base_examples)
        except FileNotFoundError:
            pass
        
        # Generate fitness queries
        fitness_queries = []
        for topic, queries in self.fitness_topics.items():
            fitness_queries.extend(queries)
        
        # Generate mental health queries
        mental_health_queries = []
        for topic, queries in self.mental_health_topics.items():
            mental_health_queries.extend(queries)
        
        # Create variations and responses
        for i in range(num_samples - len(dataset)):
            if i % 2 == 0:  # Fitness query
                query = random.choice(fitness_queries)
                response = self.generate_fitness_response(query)
                category = "fitness"
            else:  # Mental health query
                query = random.choice(mental_health_queries)
                response = self.generate_mental_health_response(query)
                category = "mental_health"
            
            # Add variations to queries
            query_variations = self._create_query_variations(query)
            final_query = random.choice(query_variations)
            
            dataset.append({
                "messages": [
                    {
                        "role": "system",
                        "content": f"You are a specialized AI {category} assistant. Provide helpful, accurate, and supportive advice."
                    },
                    {
                        "role": "user",
                        "content": final_query
                    },
                    {
                        "role": "assistant",
                        "content": response
                    }
                ],
                "category": category
            })
        
        return dataset

    def _create_query_variations(self, base_query: str) -> List[str]:
        """Create variations of queries to increase dataset diversity"""
        variations = [base_query]
        
        # Add casual variations
        casual_starters = ["Hey, ", "Hi, ", "Hello, ", "Can you help me? ", "I need advice: "]
        for starter in casual_starters:
            variations.append(starter + base_query.lower())
        
        # Add question variations
        if not base_query.endswith('?'):
            variations.append(base_query + "?")
        
        # Add personal variations
        personal_starters = ["I'm wondering about ", "I need help with ", "Can you explain "]
        for starter in personal_starters:
            if base_query.startswith(("What", "How", "Why")):
                modified = base_query.lower().replace("what", "").replace("how", "").replace("why", "").strip()
                variations.append(starter + modified)
        
        return variations

    def _generate_muscle_response(self, query: str) -> str:
        return "To build muscle effectively:\n\n**Training Principles:**\n- Progressive overload: gradually increase weight/reps\n- Compound exercises: squats, deadlifts, pull-ups, push-ups\n- 3-4 strength sessions per week\n- 6-12 rep range for hypertrophy\n- 2-3 sets per exercise\n\n**Nutrition for Muscle Growth:**\n- Protein: 1.6-2.2g per kg body weight\n- Caloric surplus: 200-500 calories above maintenance\n- Post-workout protein within 2 hours\n- Adequate carbs for energy\n\n**Recovery Essentials:**\n- 7-9 hours quality sleep\n- Rest days between training same muscles\n- Manage stress levels\n- Stay hydrated\n\n**Timeline:** Noticeable changes in 4-6 weeks, significant gains in 3-6 months with consistency."

    def _generate_cardio_response(self, query: str) -> str:
        return "Here's your complete cardio guide:\n\n**Types of Cardio:**\n- HIIT: High intensity intervals (20-30 min, 3x/week)\n- Steady-state: Moderate pace (30-60 min, 3-5x/week)\n- LISS: Low intensity (45-90 min, daily if desired)\n\n**Benefits:**\n- Heart health and endurance\n- Calorie burning and weight management\n- Improved mood and mental health\n- Better sleep quality\n\n**Getting Started:**\n- Begin with 10-15 minutes\n- Choose activities you enjoy\n- Gradually increase duration before intensity\n- Mix different types for variety\n\n**Heart Rate Zones:**\n- Fat burning: 60-70% max heart rate\n- Aerobic: 70-80% max heart rate\n- Anaerobic: 80-90% max heart rate\n\nMax HR estimate: 220 - your age"

    def _generate_weight_response(self, query: str) -> str:
        return "Sustainable weight management approach:\n\n**For Weight Loss:**\n- Create moderate calorie deficit (300-500 calories/day)\n- Combine diet and exercise\n- Aim for 1-2 lbs per week\n- Focus on whole foods, lean proteins, vegetables\n- Stay hydrated and get adequate sleep\n\n**For Weight Gain:**\n- Calorie surplus of 300-500 calories/day\n- Emphasize nutrient-dense foods\n- Include strength training\n- Eat frequent, balanced meals\n- Be patient - healthy gain is gradual\n\n**Key Principles:**\n- Consistency over perfection\n- Track progress beyond the scale\n- Address underlying habits\n- Seek professional guidance if needed\n\n**Remember:** Sustainable changes take time. Focus on building healthy habits rather than quick fixes."

    def _generate_confidence_response(self, query: str) -> str:
        return "Building confidence through fitness is a journey. Here's how to start:\n\n**Mindset Shifts:**\n- Focus on what your body can DO, not just how it looks\n- Compare yourself to your past self, not others\n- Celebrate small victories and progress\n- Remember everyone started as a beginner\n\n**Practical Strategies:**\n- Start with home workouts to build confidence\n- Choose less crowded gym times initially\n- Bring headphones for focus\n- Have a plan before arriving\n- Consider working with a trainer initially\n\n**Building Self-Compassion:**\n- Talk to yourself like you would a good friend\n- Acknowledge that learning takes time\n- Focus on effort over results\n- Practice positive self-talk\n\n**Community Support:**\n- Find beginner-friendly classes\n- Connect with supportive fitness communities\n- Share your journey with encouraging friends\n\nRemember: Confidence grows with competence. Every workout builds both physical and mental strength."

    def _generate_motivation_response(self, query: str) -> str:
        return "Staying motivated is one of the biggest challenges. Here's a comprehensive approach:\n\n**Goal Setting:**\n- Set SMART goals (Specific, Measurable, Achievable, Relevant, Time-bound)\n- Break large goals into smaller milestones\n- Focus on process goals, not just outcome goals\n- Write down your 'why' for exercising\n\n**Building Habits:**\n- Start with 2-3 workouts per week\n- Same time each day creates routine\n- Prepare everything the night before\n- Stack exercise with existing habits\n\n**Tracking Progress:**\n- Keep a workout log\n- Take progress photos\n- Track how you feel, not just numbers\n- Celebrate consistency streaks\n\n**Overcoming Setbacks:**\n- Expect ups and downs\n- One missed workout isn't failure\n- Adjust goals if they're too ambitious\n- Focus on getting back on track quickly\n\n**Accountability:**\n- Find a workout partner\n- Join fitness communities\n- Share goals with supportive people\n- Consider hiring a trainer\n\nMotivation gets you started, but habits keep you going."

    def _generate_social_response(self, query: str) -> str:
        return "Exercise can be a wonderful way to connect with others and combat loneliness:\n\n**Social Exercise Options:**\n- Group fitness classes (yoga, Zumba, spin, boot camp)\n- Walking or running clubs\n- Recreational sports leagues\n- Hiking groups or outdoor clubs\n- Dance classes\n- Martial arts or self-defense classes\n\n**Starting Small:**\n- Smile and make eye contact at the gym\n- Ask for help with equipment or form\n- Attend the same classes regularly to see familiar faces\n- Volunteer for active charity events\n\n**Online Communities:**\n- Join fitness apps with social features\n- Participate in virtual challenges\n- Share your journey on social media\n- Find accountability partners online\n\n**Mental Health Benefits:**\n- Exercise releases mood-boosting endorphins\n- Shared activities create natural conversation\n- Regular routines provide structure\n- Physical activity reduces stress and anxiety\n\n**Building Connections:**\n- Be consistent - relationships take time\n- Show genuine interest in others\n- Offer encouragement and support\n- Suggest post-workout activities (healthy meals, smoothies)\n\nRemember: Many people at gyms and classes are also looking to connect. Your openness might be exactly what someone else needs too."

    def _generate_general_fitness_response(self, query: str) -> str:
        return "Here's comprehensive fitness guidance:\n\n**Foundation Principles:**\n- Consistency beats intensity\n- Progressive overload for improvement\n- Balance strength, cardio, and flexibility\n- Listen to your body\n- Proper form prevents injury\n\n**Weekly Structure:**\n- 3-4 strength training sessions\n- 2-3 cardio sessions\n- Daily movement (walking, stretching)\n- 1-2 complete rest days\n\n**Getting Started:**\n- Begin with bodyweight exercises\n- Focus on major movement patterns\n- Start with 20-30 minute sessions\n- Gradually increase duration and intensity\n\n**Key Habits:**\n- Regular sleep schedule (7-9 hours)\n- Adequate hydration\n- Balanced nutrition\n- Stress management\n- Recovery and rest\n\nFitness is a lifelong journey. Focus on building sustainable habits rather than seeking quick fixes."

    def _generate_general_mental_health_response(self, query: str) -> str:
        return "Thank you for reaching out about your mental health. Here's supportive guidance:\n\n**Exercise and Mental Health:**\n- Physical activity releases natural mood boosters\n- Regular exercise reduces anxiety and depression symptoms\n- Movement improves sleep quality and energy\n- Fitness provides structure and routine\n- Achievement in exercise builds confidence\n\n**Gentle Starting Points:**\n- 10-15 minute walks in nature\n- Simple stretching or yoga\n- Dancing to favorite music\n- Gardening or outdoor activities\n- Any movement that brings joy\n\n**Building Mental Resilience:**\n- Practice self-compassion\n- Set small, achievable goals\n- Connect with supportive people\n- Maintain regular routines\n- Seek professional help when needed\n\n**Crisis Resources:**\n- National Suicide Prevention Lifeline: 988\n- Crisis Text Line: Text HOME to 741741\n- Local mental health services\n- Trusted healthcare providers\n\n**Remember:** Seeking help is a sign of strength. You deserve support and care. Mental health is just as important as physical health, and both can be improved together.\n\nWhat feels most manageable for you to try first?"

def main():
    generator = FitnessDatasetGenerator()
    
    print("Generating comprehensive fitness and mental health training dataset...")
    dataset = generator.generate_dataset(10000)
    
    # Save the dataset
    with open('comprehensive_fitness_mental_health_dataset.json', 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    
    print(f"Generated {len(dataset)} training examples")
    print("Dataset saved as 'comprehensive_fitness_mental_health_dataset.json'")
    
    # Print some statistics
    fitness_count = sum(1 for item in dataset if item.get('category') == 'fitness')
    mental_health_count = sum(1 for item in dataset if item.get('category') == 'mental_health')
    
    print(f"\nDataset Statistics:")
    print(f"- Fitness queries: {fitness_count}")
    print(f"- Mental health queries: {mental_health_count}")
    print(f"- Total examples: {len(dataset)}")

if __name__ == "__main__":
    main()