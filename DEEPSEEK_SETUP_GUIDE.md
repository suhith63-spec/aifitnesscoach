# DeepSeek R1 Fitness AI Setup Guide

This guide will help you set up and use the DeepSeek R1 powered fitness AI system that replaces Google API with a fine-tuned DeepSeek model.

## 🎯 Features

- **Fine-tuned DeepSeek R1** for fitness and health domain
- **Content Filtering** - Only responds to fitness/health related queries
- **Database Integration** - Stores user interactions and learns from patterns
- **Smart Recommendations** - Analyzes user data for personalized advice
- **Mental Health Support** - Specialized mental wellness assistance
- **Progress Tracking** - Monitors user fitness journey

## 📋 Prerequisites

1. **Python 3.8+** installed
2. **DeepSeek API Key** from [DeepSeek Platform](https://platform.deepseek.com/)
3. **Virtual Environment** (recommended)

## 🚀 Installation Steps

### Step 1: Get DeepSeek API Key

1. Visit [DeepSeek Platform](https://platform.deepseek.com/)
2. Create an account or sign in
3. Navigate to API Keys section
4. Generate a new API key
5. Copy the API key for later use

### Step 2: Environment Setup

1. **Update .env file** with your DeepSeek API key:
```bash
# Replace 'your-deepseek-api-key-here' with your actual API key
DEEPSEEK_API_KEY=sk-your-actual-deepseek-api-key-here
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

### Step 3: Initialize System

1. **Check configuration**:
```bash
python run_deepseek_fitness_ai.py check
```

2. **Setup database**:
```bash
python run_deepseek_fitness_ai.py setup
```

3. **Test the system**:
```bash
python run_deepseek_fitness_ai.py test
```

## 🎯 Fine-tuning DeepSeek R1

### Option 1: Use Pre-configured Training Data

```bash
python run_deepseek_fitness_ai.py finetune
```

This will:
- Create fitness-specific training data
- Upload to DeepSeek platform
- Start fine-tuning job
- Return job ID for monitoring

### Option 2: Custom Fine-tuning

```python
from finetune_deepseek import DeepSeekFineTuner

# Initialize fine-tuner
fine_tuner = DeepSeekFineTuner("your-api-key")

# Create custom training data
training_data = [
    {
        "messages": [
            {"role": "system", "content": "You are a fitness expert..."},
            {"role": "user", "content": "Custom fitness question"},
            {"role": "assistant", "content": "Expert fitness response"}
        ]
    }
    # Add more training examples
]

# Run fine-tuning
job_id = fine_tuner.run_complete_fine_tuning()
```

## 🤖 Running the Chatbot

### Start the Enhanced Chatbot

```bash
python run_deepseek_fitness_ai.py chatbot
```

Or run directly:
```bash
streamlit run enhanced_fitness_chatbot.py
```

### Features Available:

1. **Fitness Coaching**
   - Workout plan creation
   - Exercise form guidance
   - Progress tracking

2. **Nutrition Advice**
   - Meal planning
   - Macro calculations
   - Supplement guidance

3. **Mental Health Support**
   - Stress management
   - Motivation coaching
   - Wellness strategies

## 📊 Database Schema

The system uses SQLite with these tables:

- **users** - User profiles and goals
- **workout_plans** - Personalized workout schedules
- **interactions** - Chat history and context
- **mental_health_sessions** - Mental wellness tracking
- **progress_tracking** - Fitness metrics and improvements

## 🔧 Configuration Options

### Environment Variables (.env)

```bash
# DeepSeek Configuration
DEEPSEEK_API_KEY=your-api-key
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-r1
DEEPSEEK_MAX_TOKENS=1000
DEEPSEEK_TEMPERATURE=0.7

# Database Settings
DATABASE_PATH=fitness_ai.db
MAX_INTERACTIONS=1000

# Content Filtering
STRICT_FILTERING=true
```

### Customizing Content Filters

Edit `config.py` to modify fitness keywords:

```python
FITNESS_KEYWORDS = [
    'exercise', 'workout', 'fitness', 'training',
    # Add your custom keywords
]
```

## 🎯 Usage Examples

### Basic Chat Interaction

```python
from deepseek_fitness_ai import FitnessAIAssistant

assistant = FitnessAIAssistant("your-api-key")
response, category = assistant.process_query("user123", "What's a good beginner workout?")
print(f"Response: {response}")
print(f"Category: {category}")
```

### Workout Schedule Query

```python
# Get tomorrow's workout
schedule = assistant.get_workout_schedule("user123", "tomorrow")
print(schedule)
```

### Mental Health Support

```python
# Handle mental health query
response = assistant.handle_mental_health_query("user123", "I'm feeling stressed about my fitness goals")
print(response)
```

## 📈 Monitoring and Analytics

### Check Fine-tuning Status

```python
from finetune_deepseek import DeepSeekFineTuner

fine_tuner = DeepSeekFineTuner("your-api-key")
status = fine_tuner.check_job_status("your-job-id")
print(status)
```

### Database Queries

```python
from deepseek_fitness_ai import DatabaseManager

db = DatabaseManager()
user_context = db.get_user_context("user123", limit=10)
workout_plan = db.get_workout_plan("user123")
```

## 🔍 Troubleshooting

### Common Issues

1. **API Key Error**
   - Verify your DeepSeek API key is correct
   - Check if you have sufficient credits

2. **Database Issues**
   - Run `python run_deepseek_fitness_ai.py setup` to reinitialize
   - Check file permissions for database file

3. **Import Errors**
   - Ensure all requirements are installed: `pip install -r requirements.txt`
   - Check Python version compatibility

4. **Streamlit Issues**
   - Update Streamlit: `pip install --upgrade streamlit`
   - Clear cache: `streamlit cache clear`

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🚀 Advanced Features

### Custom System Prompts

Modify system prompts in `config.py`:

```python
SYSTEM_PROMPTS = {
    "fitness": "Your custom fitness coach prompt...",
    "nutrition": "Your custom nutrition advisor prompt...",
    "mental_health": "Your custom mental health support prompt..."
}
```

### Adding New Categories

1. Update `FitnessContentFilter` class
2. Add new keywords to filter lists
3. Create corresponding system prompts
4. Update database schema if needed

### Integration with Existing Code

The system is designed to work alongside your existing fitness trainer:

```python
# In your existing code
from deepseek_fitness_ai import FitnessAIAssistant

# Initialize alongside existing components
ai_assistant = FitnessAIAssistant(api_key)

# Use in your exercise detection pipeline
def handle_user_query(query):
    response, category = ai_assistant.process_query(user_id, query)
    return response
```

## 📞 Support

For issues and questions:
1. Check this guide first
2. Review error messages carefully
3. Test with simple queries
4. Verify API key and configuration

## 🔄 Updates and Maintenance

### Regular Tasks

1. **Monitor API Usage** - Check DeepSeek dashboard
2. **Backup Database** - Regular SQLite backups
3. **Update Training Data** - Improve fine-tuning periodically
4. **Review User Interactions** - Analyze for improvements

### Version Updates

Keep the system updated:
```bash
pip install --upgrade -r requirements.txt
```

## 🎉 Success!

You now have a fully functional DeepSeek R1 powered fitness AI system that:
- ✅ Filters non-fitness content
- ✅ Learns from user interactions
- ✅ Provides personalized recommendations
- ✅ Supports mental health queries
- ✅ Tracks progress and patterns
- ✅ Integrates with your existing fitness trainer

Start the chatbot and begin your AI-powered fitness journey!