#!/usr/bin/env python3
"""
Main script to run the DeepSeek R1 powered Fitness AI system
"""

import os
import sys
import argparse
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from config import config
from deepseek_fitness_ai import FitnessAIAssistant
from enhanced_fitness_chatbot import EnhancedFitnessChatbot
from finetune_deepseek import DeepSeekFineTuner

def check_environment():
    """Check if environment is properly configured"""
    print("🔍 Checking environment configuration...")
    
    # Check MongoDB connection
    try:
        from pymongo import MongoClient
        client = MongoClient(os.getenv("MONGODB_CONNECTION_STRING"))
        client.admin.command('ping')
        print("✅ MongoDB connection: PASS")
        mongodb_ok = True
    except Exception as e:
        print(f"❌ MongoDB connection: FAIL - {str(e)}")
        mongodb_ok = False
    
    # Check DeepSeek API key
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    if deepseek_key and deepseek_key != "your-deepseek-api-key-here":
        print("✅ DeepSeek API key: PASS")
        deepseek_ok = True
    else:
        print("❌ DeepSeek API key: FAIL")
        deepseek_ok = False
    
    # Check other environment variables
    env_vars = ['ELEVENLABS_API_KEY', 'MONGODB_DATABASE']
    env_ok = True
    for var in env_vars:
        if os.getenv(var):
            print(f"✅ {var}: PASS")
        else:
            print(f"⚠️  {var}: MISSING (optional)")
    
    all_ok = mongodb_ok and deepseek_ok
    
    if not all_ok:
        print("\n⚠️  Some configuration checks failed. Please review your .env file.")
        return False
    
    print("\n✅ Environment configuration looks good!")
    return True

def run_chatbot():
    """Run the enhanced fitness chatbot"""
    print("🚀 Starting Enhanced Fitness Chatbot...")
    
    if not check_environment():
        print("❌ Environment check failed. Please fix configuration issues.")
        return
    
    try:
        chatbot = EnhancedFitnessChatbot()
        chatbot.run_chatbot_ui()
    except Exception as e:
        print(f"❌ Error starting chatbot: {str(e)}")
        print("Make sure you have installed all requirements: pip install -r requirements.txt")

def run_fine_tuning():
    """Run the fine-tuning process"""
    print("🎯 Starting DeepSeek R1 Fine-tuning Process...")
    
    if not config.deepseek_config.api_key or config.deepseek_config.api_key == "your-deepseek-api-key-here":
        print("❌ DeepSeek API key not configured. Please update your .env file.")
        return
    
    try:
        fine_tuner = DeepSeekFineTuner(config.deepseek_config.api_key)
        job_id = fine_tuner.run_complete_fine_tuning()
        
        if job_id:
            print(f"✅ Fine-tuning job started successfully!")
            print(f"📝 Job ID: {job_id}")
            print("You can check the status later using the check_job_status() method")
        else:
            print("❌ Fine-tuning job failed to start")
            
    except Exception as e:
        print(f"❌ Error during fine-tuning: {str(e)}")

def test_ai_assistant():
    """Test the AI assistant functionality"""
    print("🧪 Testing AI Assistant...")
    
    if not config.deepseek_config.api_key or config.deepseek_config.api_key == "your-deepseek-api-key-here":
        print("❌ DeepSeek API key not configured. Please update your .env file.")
        return
    
    try:
        assistant = FitnessAIAssistant(config.deepseek_config.api_key)
        
        test_queries = [
            "What's a good beginner workout plan?",
            "I'm feeling stressed about my fitness goals",
            "Can you help me with meal planning?",
            "What's the weather like today?",  # Should be filtered out
        ]
        
        print("\n📝 Running test queries...")
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. Query: {query}")
            response, category = assistant.process_query("test_user", query)
            print(f"   Category: {category}")
            print(f"   Response: {response[:100]}...")
            
        print("\n✅ AI Assistant test completed!")
        
    except Exception as e:
        print(f"❌ Error testing AI assistant: {str(e)}")

def setup_database():
    """Initialize MongoDB and add sample data"""
    print("🗄️  Setting up MongoDB...")
    
    try:
        from deepseek_fitness_ai import DatabaseManager
        from datetime import datetime
        
        db_manager = DatabaseManager()
        print("✅ MongoDB connected successfully!")
        
        # Add sample data
        print("📝 Adding sample data...")
        
        # Sample user
        db_manager.db.users.update_one(
            {'user_id': 'sample_user'},
            {'$set': {
                'name': 'John Doe',
                'age': 30,
                'weight': 75.0,
                'height': 175.0,
                'fitness_level': 'Intermediate',
                'goals': 'Weight loss and muscle gain',
                'created_at': datetime.now()
            }},
            upsert=True
        )
        
        # Sample workout plan
        db_manager.db.workout_plans.update_one(
            {'plan_id': 'sample_plan'},
            {'$set': {
                'user_id': 'sample_user',
                'plan_name': 'Beginner Full Body',
                'exercises': ['Push-ups', 'Squats', 'Planks', 'Lunges', 'Burpees'],
                'schedule': {
                    'Monday': ['Push-ups', 'Squats'],
                    'Wednesday': ['Planks', 'Lunges'],
                    'Friday': ['Burpees', 'Push-ups']
                },
                'created_at': datetime.now()
            }},
            upsert=True
        )
        
        print("✅ Sample data added to MongoDB successfully!")
        
    except Exception as e:
        print(f"❌ Error setting up MongoDB: {str(e)}")
        print("Make sure your MongoDB connection string is correct in .env file")

def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description="DeepSeek R1 Fitness AI System")
    parser.add_argument(
        "command",
        choices=["chatbot", "finetune", "test", "setup", "check"],
        help="Command to run"
    )
    
    args = parser.parse_args()
    
    print("💪 DeepSeek R1 Fitness AI System")
    print("=" * 40)
    
    if args.command == "chatbot":
        run_chatbot()
    elif args.command == "finetune":
        run_fine_tuning()
    elif args.command == "test":
        test_ai_assistant()
    elif args.command == "setup":
        setup_database()
    elif args.command == "check":
        check_environment()

if __name__ == "__main__":
    # If no command line arguments, show help
    if len(sys.argv) == 1:
        print("💪 DeepSeek R1 Fitness AI System")
        print("=" * 40)
        print("\nAvailable commands:")
        print("  chatbot  - Run the enhanced fitness chatbot")
        print("  finetune - Start the fine-tuning process")
        print("  test     - Test the AI assistant functionality")
        print("  setup    - Initialize database with sample data")
        print("  check    - Check environment configuration")
        print("\nUsage: python run_deepseek_fitness_ai.py <command>")
        print("\nExample: python run_deepseek_fitness_ai.py chatbot")
    else:
        main()