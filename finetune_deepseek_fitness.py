#!/usr/bin/env python3

import json
import os
import requests
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

class DeepSeekFineTuner:
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def prepare_training_data(self, dataset_file: str) -> str:
        """Prepare training data in JSONL format for DeepSeek fine-tuning"""
        
        with open(dataset_file, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
        
        # Convert to JSONL format required by DeepSeek
        training_file = "fitness_mental_health_training.jsonl"
        
        with open(training_file, 'w', encoding='utf-8') as f:
            for example in dataset:
                # DeepSeek fine-tuning format
                training_example = {
                    "messages": example["messages"]
                }
                f.write(json.dumps(training_example, ensure_ascii=False) + '\n')
        
        print(f"Training data prepared: {training_file}")
        print(f"Total examples: {len(dataset)}")
        
        return training_file
    
    def upload_training_file(self, file_path: str) -> str:
        """Upload training file to DeepSeek"""
        
        try:
            with open(file_path, 'rb') as f:
                files = {
                    'file': (file_path, f, 'application/jsonl'),
                    'purpose': (None, 'fine-tune')
                }
                
                response = requests.post(
                    f"{self.base_url}/files",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    files=files
                )
            
            if response.status_code == 200:
                file_info = response.json()
                print(f"File uploaded successfully: {file_info['id']}")
                return file_info['id']
            else:
                print(f"File upload failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error uploading file: {e}")
            return None
    
    def create_fine_tune_job(self, file_id: str, model_name: str = "deepseek-chat") -> str:
        """Create fine-tuning job"""
        
        payload = {
            "training_file": file_id,
            "model": model_name,
            "hyperparameters": {
                "n_epochs": 3,
                "batch_size": 8,
                "learning_rate_multiplier": 0.1
            },
            "suffix": "fitness-mental-health-v1"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/fine_tuning/jobs",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 200:
                job_info = response.json()
                print(f"Fine-tuning job created: {job_info['id']}")
                return job_info['id']
            else:
                print(f"Fine-tuning job creation failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error creating fine-tuning job: {e}")
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
                print(f"Status check failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error checking job status: {e}")
            return None
    
    def list_fine_tuned_models(self) -> List[Dict]:
        """List available fine-tuned models"""
        
        try:
            response = requests.get(
                f"{self.base_url}/fine_tuning/jobs",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Model listing failed: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"Error listing models: {e}")
            return []

class FineTunedDeepSeekClient:
    """Client for using fine-tuned DeepSeek model"""
    
    def __init__(self, model_id: str = None):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
        self.model_id = model_id or "deepseek-chat"  # Fallback to base model
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def generate_response(self, prompt: str, context: str = "", max_tokens: int = 1000) -> str:
        """Generate response using fine-tuned model"""
        
        try:
            if context:
                full_prompt = f"Context: {context}\\n\\nQuery: {prompt}"
            else:
                full_prompt = prompt
            
            payload = {
                "model": self.model_id,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a specialized AI fitness and mental health assistant. Provide helpful, accurate, and supportive advice based on your training."
                    },
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ],
                "max_tokens": max_tokens,
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
                    return "I'm having trouble generating a response. Please try again."
            else:
                return f"I'm currently experiencing technical difficulties. Please try again later."
                
        except Exception as e:
            return "I'm having trouble connecting right now. Please try again in a moment."

def main():
    """Main fine-tuning workflow"""
    
    print("=== DeepSeek Fitness & Mental Health Fine-Tuning ===\\n")
    
    # Step 1: Generate training dataset
    print("Step 1: Generating training dataset...")
    os.system("python generate_training_dataset.py")
    
    # Step 2: Initialize fine-tuner
    fine_tuner = DeepSeekFineTuner()
    
    if not fine_tuner.api_key:
        print("Error: DEEPSEEK_API_KEY not found in environment variables")
        return
    
    # Step 3: Prepare training data
    print("\\nStep 2: Preparing training data...")
    training_file = fine_tuner.prepare_training_data("comprehensive_fitness_mental_health_dataset.json")
    
    # Step 4: Upload training file
    print("\\nStep 3: Uploading training file...")
    file_id = fine_tuner.upload_training_file(training_file)
    
    if not file_id:
        print("Failed to upload training file. Exiting.")
        return
    
    # Step 5: Create fine-tuning job
    print("\\nStep 4: Creating fine-tuning job...")
    job_id = fine_tuner.create_fine_tune_job(file_id)
    
    if not job_id:
        print("Failed to create fine-tuning job. Exiting.")
        return
    
    # Step 6: Monitor job status
    print("\\nStep 5: Monitoring fine-tuning progress...")
    print(f"Job ID: {job_id}")
    print("You can check the status later using the job ID.")
    
    # Save job info for later reference
    job_info = {
        "job_id": job_id,
        "file_id": file_id,
        "training_file": training_file,
        "status": "in_progress"
    }
    
    with open("fine_tuning_job_info.json", "w") as f:
        json.dump(job_info, f, indent=2)
    
    print("\\nFine-tuning job information saved to 'fine_tuning_job_info.json'")
    print("\\nNext steps:")
    print("1. Wait for fine-tuning to complete (this may take several hours)")
    print("2. Check job status periodically")
    print("3. Once complete, update your application to use the fine-tuned model")

def check_status():
    """Check status of existing fine-tuning job"""
    
    try:
        with open("fine_tuning_job_info.json", "r") as f:
            job_info = json.load(f)
        
        fine_tuner = DeepSeekFineTuner()
        status = fine_tuner.check_job_status(job_info["job_id"])
        
        if status:
            print(f"Job Status: {status.get('status', 'unknown')}")
            print(f"Progress: {status.get('trained_tokens', 0)} tokens trained")
            
            if status.get('status') == 'succeeded':
                print(f"Fine-tuned model ID: {status.get('fine_tuned_model')}")
                
                # Update job info
                job_info["status"] = "completed"
                job_info["model_id"] = status.get('fine_tuned_model')
                
                with open("fine_tuning_job_info.json", "w") as f:
                    json.dump(job_info, f, indent=2)
                
                print("\\nFine-tuning completed successfully!")
                print("You can now use the fine-tuned model in your application.")
        
    except FileNotFoundError:
        print("No fine-tuning job info found. Run the main fine-tuning process first.")
    except Exception as e:
        print(f"Error checking status: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        check_status()
    else:
        main()