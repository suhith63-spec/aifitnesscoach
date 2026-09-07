#!/usr/bin/env python3

import os
import json
import subprocess
import sys

def check_requirements():
    """Check if all required packages are installed"""
    required_packages = [
        'streamlit',
        'requests',
        'python-dotenv',
        'numpy',
        'opencv-python',
        'mediapipe'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        for package in missing_packages:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print("All packages installed successfully!")
    else:
        print("All required packages are already installed.")

def setup_environment():
    """Setup environment variables"""
    env_file = ".env"
    
    if not os.path.exists(env_file):
        print("Creating .env file...")
        with open(env_file, 'w') as f:
            f.write("""# ElevenLabs API Key for voice feedback
# Get your API key from: https://elevenlabs.io/
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# DeepSeek R1 API Configuration
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_MAX_TOKENS=1000
DEEPSEEK_TEMPERATURE=0.7
DEEPSEEK_TIMEOUT=30

# MongoDB Atlas Configuration (optional)
MONGODB_CONNECTION_STRING=your_mongodb_connection_string_here
MONGODB_DATABASE=fitness_ai

# Content Filtering
STRICT_FILTERING=true
""")
        print(".env file created. Please update it with your API keys.")
    else:
        print(".env file already exists.")

def generate_training_data():
    """Generate training dataset"""
    print("Generating comprehensive training dataset...")
    try:
        subprocess.check_call([sys.executable, "generate_training_dataset.py"])
        print("Training dataset generated successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error generating training data: {e}")

def check_deepseek_api():
    """Check if DeepSeek API is working"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key or api_key == "your_deepseek_api_key_here":
            print("❌ DeepSeek API key not configured in .env file")
            return False
        
        import requests
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": "Hello, this is a test message."}
            ],
            "max_tokens": 50
        }
        
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ DeepSeek API is working correctly!")
            return True
        elif response.status_code == 402:
            print("⚠️ DeepSeek API key has insufficient balance")
            return False
        else:
            print(f"❌ DeepSeek API error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing DeepSeek API: {e}")
        return False

def start_fine_tuning():
    """Start the fine-tuning process"""
    print("\n=== Starting Fine-Tuning Process ===")
    
    if not check_deepseek_api():
        print("Cannot proceed with fine-tuning due to API issues.")
        return
    
    try:
        print("Starting fine-tuning job...")
        subprocess.check_call([sys.executable, "finetune_deepseek_fitness.py"])
        print("Fine-tuning job started successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error starting fine-tuning: {e}")

def check_fine_tuning_status():
    """Check fine-tuning job status"""
    try:
        subprocess.check_call([sys.executable, "finetune_deepseek_fitness.py", "status"])
    except subprocess.CalledProcessError as e:
        print(f"Error checking status: {e}")

def main():
    print("=== Fitness AI Fine-Tuning Setup ===\n")
    
    while True:
        print("\nChoose an option:")
        print("1. Check and install requirements")
        print("2. Setup environment (.env file)")
        print("3. Generate training dataset")
        print("4. Test DeepSeek API connection")
        print("5. Start fine-tuning process")
        print("6. Check fine-tuning status")
        print("7. Run complete setup (1-4)")
        print("8. Exit")
        
        choice = input("\nEnter your choice (1-8): ").strip()
        
        if choice == "1":
            check_requirements()
        elif choice == "2":
            setup_environment()
        elif choice == "3":
            generate_training_data()
        elif choice == "4":
            check_deepseek_api()
        elif choice == "5":
            start_fine_tuning()
        elif choice == "6":
            check_fine_tuning_status()
        elif choice == "7":
            print("Running complete setup...")
            check_requirements()
            setup_environment()
            generate_training_data()
            check_deepseek_api()
            print("\nSetup complete! You can now start fine-tuning (option 5) or run the application.")
        elif choice == "8":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()