import json
import os
from typing import List, Dict
import requests
from datetime import datetime

class DeepSeekFineTuner:
    """Fine-tune DeepSeek R1 for fitness domain"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def create_fitness_training_data(self) -> List[Dict]:
        """Create comprehensive fitness training dataset"""
        training_data = [
            # Workout Planning
            {
                "messages": [
                    {"role": "system", "content": "You are a specialized fitness AI assistant focused on workout planning, nutrition, and health guidance."},
                    {"role": "user", "content": "Create a beginner workout plan for weight loss"},
                    {"role": "assistant", "content": "Here's a beginner-friendly weight loss workout plan:\n\n**Week 1-2: Foundation Building**\n- Day 1: 20-min walk + bodyweight squats (2x10)\n- Day 2: Rest or light stretching\n- Day 3: 15-min walk + push-ups (2x5-10)\n- Day 4: Rest\n- Day 5: 25-min walk + planks (2x15-30 sec)\n- Day 6-7: Rest\n\n**Progression**: Gradually increase duration and reps weekly. Focus on consistency over intensity initially."}
                ]
            },
            # Nutrition Guidance
            {
                "messages": [
                    {"role": "system", "content": "You are a specialized fitness AI assistant focused on workout planning, nutrition, and health guidance."},
                    {"role": "user", "content": "What should I eat before and after workouts?"},
                    {"role": "assistant", "content": "**Pre-Workout (30-60 min before):**\n- Light carbs: banana, oatmeal, or toast\n- Small amount of protein if 2+ hours before\n- Hydrate well\n\n**Post-Workout (within 30-60 min):**\n- Protein: 20-30g (chicken, protein shake, Greek yogurt)\n- Carbs: replenish glycogen (rice, sweet potato)\n- Hydration: water + electrolytes if intense session\n\n**Example combinations:**\n- Pre: Banana + almond butter\n- Post: Protein smoothie with berries and spinach"}
                ]
            },
            # Exercise Form and Safety
            {
                "messages": [
                    {"role": "system", "content": "You are a specialized fitness AI assistant focused on workout planning, nutrition, and health guidance."},
                    {"role": "user", "content": "How do I perform squats with proper form?"},
                    {"role": "assistant", "content": "**Proper Squat Form:**\n\n1. **Setup**: Feet shoulder-width apart, toes slightly outward\n2. **Descent**: Push hips back first, then bend knees. Keep chest up\n3. **Depth**: Thighs parallel to floor (or as low as mobility allows)\n4. **Ascent**: Drive through heels, push floor away\n\n**Key Points:**\n- Knees track over toes, don't cave inward\n- Keep core engaged throughout\n- Maintain neutral spine\n- Weight distributed across whole foot\n\n**Common Mistakes**: Knees caving in, forward lean, not going deep enough, rising on toes"}
                ]
            },
            # Mental Health and Motivation
            {
                "messages": [
                    {"role": "system", "content": "You are a specialized fitness AI assistant focused on workout planning, nutrition, and health guidance."},
                    {"role": "user", "content": "I'm feeling unmotivated to exercise. How can I get back on track?"},
                    {"role": "assistant", "content": "**Rebuilding Exercise Motivation:**\n\n1. **Start Small**: 5-10 min walks, don't overwhelm yourself\n2. **Set Micro-Goals**: 'Exercise 2x this week' vs 'Get fit'\n3. **Find Your Why**: Health, energy, stress relief, confidence\n4. **Make it Enjoyable**: Try different activities - dancing, hiking, sports\n5. **Schedule It**: Treat workouts like important appointments\n6. **Track Progress**: Note how you feel after exercise, not just physical changes\n7. **Get Support**: Workout buddy, online community, or trainer\n\n**Remember**: Motivation gets you started, but habit keeps you going. Focus on consistency over perfection."}
                ]
            },
            # Progress Tracking
            {
                "messages": [
                    {"role": "system", "content": "You are a specialized fitness AI assistant focused on workout planning, nutrition, and health guidance."},
                    {"role": "user", "content": "How should I track my fitness progress?"},
                    {"role": "assistant", "content": "**Comprehensive Progress Tracking:**\n\n**Physical Metrics:**\n- Body measurements (waist, arms, thighs)\n- Progress photos (same time, lighting, poses)\n- Weight (weekly, same time of day)\n- Body fat % (if accessible)\n\n**Performance Metrics:**\n- Strength: reps, sets, weight lifted\n- Endurance: distance, time, heart rate\n- Flexibility: range of motion improvements\n\n**Wellness Indicators:**\n- Energy levels (1-10 daily)\n- Sleep quality and duration\n- Mood and stress levels\n- Recovery between workouts\n\n**Tools**: Fitness apps, workout journal, photos, measurements tape. Track weekly, review monthly for trends."}
                ]
            },
            # Injury Prevention
            {
                "messages": [
                    {"role": "system", "content": "You are a specialized fitness AI assistant focused on workout planning, nutrition, and health guidance."},
                    {"role": "user", "content": "How can I prevent workout injuries?"},
                    {"role": "assistant", "content": "**Injury Prevention Strategies:**\n\n**Before Exercise:**\n- Dynamic warm-up (5-10 min): leg swings, arm circles, light movement\n- Proper hydration and nutrition\n- Adequate sleep and recovery\n\n**During Exercise:**\n- Focus on proper form over heavy weights\n- Progress gradually (10% rule for increases)\n- Listen to your body - pain vs. discomfort\n- Use appropriate equipment and footwear\n\n**After Exercise:**\n- Cool down with light movement\n- Static stretching (hold 15-30 seconds)\n- Proper recovery between sessions\n\n**Red Flags**: Sharp pain, joint pain, persistent soreness, decreased performance. When in doubt, rest and consult a professional."}
                ]
            }
        ]
        
        return training_data
    
    def create_mental_health_training_data(self) -> List[Dict]:
        """Create mental health focused training data"""
        return [
            {
                "messages": [
                    {"role": "system", "content": "You are a compassionate mental health support assistant specializing in fitness-related mental wellness."},
                    {"role": "user", "content": "I feel anxious about going to the gym"},
                    {"role": "assistant", "content": "Gym anxiety is very common and completely understandable. Here are some strategies to help:\n\n**Start Small:**\n- Visit during off-peak hours when it's less crowded\n- Bring a friend for support\n- Start with a short 20-30 minute session\n\n**Preparation Helps:**\n- Plan your workout beforehand\n- Familiarize yourself with equipment online\n- Wear comfortable clothes that make you feel confident\n\n**Mindset Shifts:**\n- Remember everyone is focused on their own workout\n- Most people are supportive and understanding\n- You belong there as much as anyone else\n\n**Alternatives:**\n- Start with home workouts to build confidence\n- Try group classes where everyone is learning\n- Consider a personal trainer for guidance\n\nRemember, taking care of your physical health is an act of self-care. You're doing something positive for yourself."}
                ]
            },
            {
                "messages": [
                    {"role": "system", "content": "You are a compassionate mental health support assistant specializing in fitness-related mental wellness."},
                    {"role": "user", "content": "Exercise makes me feel worse sometimes. Is this normal?"},
                    {"role": "assistant", "content": "Yes, this can happen and you're not alone in feeling this way. Here's what might be going on:\n\n**Possible Reasons:**\n- Overexertion leading to fatigue or mood dips\n- Comparing yourself to others or unrealistic expectations\n- Exercise-induced anxiety or body image concerns\n- Not fueling your body properly before/after workouts\n\n**Solutions to Try:**\n- Reduce intensity and focus on gentle movement\n- Choose activities you genuinely enjoy\n- Practice self-compassion - progress isn't always linear\n- Ensure adequate nutrition and hydration\n- Consider the timing - some people feel better exercising in the morning vs. evening\n\n**When to Seek Help:**\n- If feelings persist despite modifications\n- If you're experiencing symptoms of depression or anxiety\n- If exercise becomes compulsive or punitive\n\nRemember: Exercise should enhance your wellbeing, not detract from it. It's okay to adjust your approach until you find what works for you."}
                ]
            }
        ]
    
    def prepare_training_file(self, output_file: str = "fitness_training_data.jsonl"):
        """Prepare training data in JSONL format for fine-tuning"""
        fitness_data = self.create_fitness_training_data()
        mental_health_data = self.create_mental_health_training_data()
        
        all_data = fitness_data + mental_health_data
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for item in all_data:
                f.write(json.dumps(item) + '\n')
        
        print(f"Training data saved to {output_file}")
        print(f"Total training examples: {len(all_data)}")
        return output_file
    
    def upload_training_file(self, file_path: str) -> str:
        """Upload training file to DeepSeek"""
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                data = {'purpose': 'fine-tune'}
                
                response = requests.post(
                    f"{self.base_url}/files",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    files=files,
                    data=data
                )
            
            if response.status_code == 200:
                file_id = response.json()['id']
                print(f"File uploaded successfully. File ID: {file_id}")
                return file_id
            else:
                print(f"Upload failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error uploading file: {str(e)}")
            return None
    
    def create_fine_tune_job(self, file_id: str, model: str = "deepseek-r1") -> str:
        """Create fine-tuning job"""
        try:
            payload = {
                "training_file": file_id,
                "model": model,
                "hyperparameters": {
                    "n_epochs": 3,
                    "batch_size": 4,
                    "learning_rate_multiplier": 0.1
                }
            }
            
            response = requests.post(
                f"{self.base_url}/fine_tuning/jobs",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 200:
                job_id = response.json()['id']
                print(f"Fine-tuning job created. Job ID: {job_id}")
                return job_id
            else:
                print(f"Job creation failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error creating fine-tune job: {str(e)}")
            return None
    
    def check_job_status(self, job_id: str) -> Dict:
        """Check fine-tuning job status"""
        try:
            response = requests.get(
                f"{self.base_url}/fine_tuning/jobs/{job_id}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Status check failed: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"Error checking job status: {str(e)}")
            return {}
    
    def run_complete_fine_tuning(self) -> str:
        """Run the complete fine-tuning process"""
        print("Starting DeepSeek R1 fine-tuning process...")
        
        # Step 1: Prepare training data
        print("\n1. Preparing training data...")
        training_file = self.prepare_training_file()
        
        # Step 2: Upload training file
        print("\n2. Uploading training file...")
        file_id = self.upload_training_file(training_file)
        if not file_id:
            return None
        
        # Step 3: Create fine-tuning job
        print("\n3. Creating fine-tuning job...")
        job_id = self.create_fine_tune_job(file_id)
        if not job_id:
            return None
        
        print(f"\nFine-tuning job started successfully!")
        print(f"Job ID: {job_id}")
        print("You can check the status using check_job_status() method")
        
        return job_id

# Usage example
if __name__ == "__main__":
    # Initialize fine-tuner (replace with your actual API key)
    fine_tuner = DeepSeekFineTuner("your-deepseek-api-key-here")
    
    # Option 1: Just prepare training data
    fine_tuner.prepare_training_file()
    
    # Option 2: Run complete fine-tuning process
    # job_id = fine_tuner.run_complete_fine_tuning()
    
    # Option 3: Check existing job status
    # status = fine_tuner.check_job_status("your-job-id-here")
    # print(json.dumps(status, indent=2))