# DeepSeek R1 Integration Setup Guide

## Overview
This guide explains how to set up DeepSeek R1 reasoning for the Fitness AI Trainer application.

## Features
- **Intelligent Query Classification**: Automatically identifies fitness/healthcare queries
- **Advanced Reasoning**: Uses DeepSeek R1 for detailed fitness analysis
- **Query Filtering**: Accepts only fitness/healthcare related queries
- **Enhanced Responses**: Provides comprehensive, evidence-based fitness advice

## Setup Instructions

### 1. Get DeepSeek API Key
1. Visit [DeepSeek Platform](https://platform.deepseek.com/)
2. Create an account or sign in
3. Navigate to API Keys section
4. Generate a new API key
5. Copy the API key for configuration

### 2. Configure Environment Variables
Create a `.env` file in the project root with:

```bash
# DeepSeek API Configuration
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Google Gemini API Configuration (fallback)
GEMINI_API_KEY=your_gemini_api_key_here

# ElevenLabs API Configuration (for voice features)
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
```

### 3. Install Required Dependencies
```bash
pip install requests python-dotenv
```

### 4. Run the Application
```bash
streamlit run main.py
```

## Query Classification Categories

The system automatically classifies queries into these categories:

### ✅ Accepted Categories
- **Exercise**: Form, technique, specific exercises
- **Nutrition**: Diet, supplements, meal planning
- **Health**: Medical advice, injury prevention, recovery
- **Mental Health**: Stress, motivation, wellness
- **Form Correction**: Technique improvement, posture
- **Workout Planning**: Routines, programming, progression

### ❌ Rejected Categories
- General knowledge unrelated to fitness
- Personal problems not fitness-related
- Academic or professional questions
- Entertainment, politics, current events
- Technical programming questions

## Example Queries

### ✅ Fitness/Health Queries (Accepted)
- "How do I improve my squat form?"
- "What's the best pre-workout meal?"
- "How many calories should I eat to lose weight?"
- "What exercises help with lower back pain?"
- "How do I create a workout routine for beginners?"

### ❌ Non-Fitness Queries (Rejected)
- "What's the weather today?"
- "How do I code in Python?"
- "What are the latest news headlines?"
- "Help me with my homework in math"

## Features

### 1. Query Classification
- Automatic detection of fitness/healthcare relevance
- Confidence scoring for classification accuracy
- Category identification (exercise, nutrition, health, etc.)

### 2. DeepSeek R1 Reasoning
- Advanced reasoning for fitness queries
- Evidence-based responses
- Comprehensive analysis and recommendations
- Safety considerations and contraindications

### 3. Enhanced Exercise Analysis
- Detailed form feedback
- Performance analysis
- Improvement recommendations
- Progression suggestions

### 4. Smart Diet Recommendations
- Personalized nutrition advice
- Macro distribution guidance
- Meal timing recommendations
- Supplement suggestions

### 5. Query Statistics
- Track fitness vs non-fitness queries
- Monitor AI service usage
- Performance metrics

## API Usage and Costs

### DeepSeek R1 Pricing
- Check current pricing at [DeepSeek Platform](https://platform.deepseek.com/)
- Usage is tracked per token
- Consider implementing rate limiting for production use

### Optimization Tips
- Cache frequent queries
- Implement query preprocessing
- Use fallback models when appropriate
- Monitor API usage and costs

## Troubleshooting

### Common Issues

1. **"DeepSeek R1: Not Available"**
   - Check if DEEPSEEK_API_KEY is set correctly
   - Verify API key is valid and has credits
   - Check internet connection

2. **"No module named 'deepseek_reasoning'"**
   - Ensure deepseek_reasoning.py is in the project directory
   - Check Python path and imports

3. **API Rate Limiting**
   - Implement delays between requests
   - Consider upgrading API plan
   - Use fallback to Gemini when needed

4. **Classification Issues**
   - Review fitness keyword patterns
   - Adjust confidence thresholds
   - Update classification logic as needed

## Security Considerations

- Never commit API keys to version control
- Use environment variables for sensitive data
- Implement proper error handling
- Consider API key rotation
- Monitor for unusual usage patterns

## Future Enhancements

- Fine-tune classification models
- Implement user preference learning
- Add more specialized fitness categories
- Integrate with fitness tracking APIs
- Implement conversation memory
- Add multi-language support
