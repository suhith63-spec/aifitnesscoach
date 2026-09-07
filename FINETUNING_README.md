# 🏋️ Fitness AI Fine-Tuning Guide

This guide explains how to fine-tune DeepSeek R1 for specialized fitness and mental health responses.

## 📋 Overview

The fine-tuning process creates a specialized AI model trained on 10,000 fitness and mental health queries, providing more accurate and contextual responses than the base model.

## 🚀 Quick Start

### 1. Run Setup Script
```bash
python setup_finetuning.py
```
Choose option 7 for complete setup.

### 2. Configure API Keys
Update your `.env` file with your DeepSeek API key:
```
DEEPSEEK_API_KEY=sk-your-actual-api-key-here
```

### 3. Start Fine-Tuning
```bash
python finetune_deepseek_fitness.py
```

## 📊 Training Dataset

### Dataset Statistics
- **Total Examples**: 10,000
- **Fitness Queries**: ~5,000
- **Mental Health Queries**: ~5,000
- **Format**: OpenAI ChatML format for DeepSeek compatibility

### Dataset Categories

#### Fitness Topics:
- Workout routines and exercise planning
- Nutrition and meal planning  
- Weight management (loss/gain)
- Muscle building and strength training
- Cardio and endurance training
- Recovery and injury prevention

#### Mental Health Topics:
- Anxiety and stress management
- Depression and mood support
- Self-esteem and confidence building
- Motivation and goal achievement
- Social connection and loneliness
- Exercise-mental health connections

### Sample Training Example:
```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a specialized AI fitness assistant with expertise in exercise, nutrition, and wellness."
    },
    {
      "role": "user", 
      "content": "What's the best workout routine for beginners?"
    },
    {
      "role": "assistant",
      "content": "For beginners, I recommend starting with a simple 3-day full-body routine:\n\n**Day 1, 3, 5: Full Body Workout**\n- Bodyweight squats: 2 sets of 8-12 reps\n- Push-ups (modified if needed): 2 sets of 5-10 reps\n- Plank: 2 sets of 15-30 seconds\n- Walking or light jogging: 10-15 minutes\n\n**Key Tips:**\n- Start with 2 sets and gradually increase\n- Rest 48 hours between workouts\n- Focus on proper form over speed\n- Listen to your body and progress gradually"
    }
  ]
}
```

## 🔧 Fine-Tuning Process

### Step 1: Dataset Generation
```bash
python generate_training_dataset.py
```
Creates `comprehensive_fitness_mental_health_dataset.json` with 10,000 examples.

### Step 2: Data Preparation
The script converts the dataset to JSONL format required by DeepSeek:
```bash
python finetune_deepseek_fitness.py
```

### Step 3: Upload Training Data
Training file is uploaded to DeepSeek's servers for processing.

### Step 4: Create Fine-Tuning Job
A fine-tuning job is created with these parameters:
- **Model**: deepseek-chat
- **Epochs**: 3
- **Batch Size**: 8
- **Learning Rate Multiplier**: 0.1

### Step 5: Monitor Progress
Check job status:
```bash
python finetune_deepseek_fitness.py status
```

## 📁 Generated Files

### Training Files:
- `comprehensive_fitness_mental_health_dataset.json` - Full training dataset
- `fitness_mental_health_training.jsonl` - JSONL format for DeepSeek
- `fine_tuning_job_info.json` - Job tracking information

### Integration Files:
- `enhanced_deepseek_integration.py` - Enhanced client with fine-tuned model support
- `chatbot.py` - Updated fitness chatbot
- `mental_health_chatbot.py` - Updated mental health chatbot

## 🎯 Expected Results

### Before Fine-Tuning (Base Model):
- Generic responses
- Limited fitness knowledge
- Basic mental health support
- No conversation context

### After Fine-Tuning:
- ✅ Specialized fitness and nutrition knowledge
- ✅ Comprehensive mental health support
- ✅ Context-aware conversations
- ✅ Personalized recommendations
- ✅ Professional, empathetic tone
- ✅ Crisis resource integration

## 🔄 Using the Fine-Tuned Model

### Automatic Detection:
The application automatically detects and uses the fine-tuned model when available.

### Manual Configuration:
Update `enhanced_deepseek_integration.py` with your fine-tuned model ID:
```python
self.model_id = "ft:deepseek-chat:your-model-id"
```

### Fallback System:
If the fine-tuned model is unavailable, the system falls back to:
1. Base DeepSeek model
2. Enhanced built-in responses
3. Simple rule-based responses

## 💰 Cost Estimation

### Fine-Tuning Costs (Approximate):
- **Training**: $20-50 for 10,000 examples
- **Usage**: Standard API rates apply
- **Storage**: Minimal cost for model storage

### Cost Optimization:
- Start with smaller dataset (1,000-2,000 examples)
- Monitor usage and adjust as needed
- Use fallback responses when appropriate

## 🛠️ Troubleshooting

### Common Issues:

#### 1. API Key Issues
```
Error: 401 Unauthorized
```
**Solution**: Verify DEEPSEEK_API_KEY in .env file

#### 2. Insufficient Balance
```
Error: 402 Payment Required
```
**Solution**: Add credits to your DeepSeek account

#### 3. File Upload Errors
```
Error: File upload failed
```
**Solution**: Check file format and size limits

#### 4. Job Creation Fails
```
Error: Fine-tuning job creation failed
```
**Solution**: Verify file upload completed successfully

### Debug Mode:
Enable detailed logging by setting:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Performance Monitoring

### Metrics to Track:
- Response quality and relevance
- User satisfaction ratings
- Conversation completion rates
- Fallback usage frequency

### A/B Testing:
Compare fine-tuned vs. base model responses to measure improvement.

## 🔄 Model Updates

### Continuous Improvement:
1. Collect user feedback
2. Add new training examples
3. Retrain model periodically
4. Deploy updated model

### Version Control:
- Tag model versions
- Keep training data versioned
- Document changes and improvements

## 🤝 Support

### Getting Help:
1. Check DeepSeek documentation
2. Review error logs
3. Test with smaller datasets first
4. Contact DeepSeek support for API issues

### Community:
- Share successful training strategies
- Contribute to dataset improvements
- Report bugs and issues

## 📚 Additional Resources

### DeepSeek Documentation:
- [Fine-Tuning Guide](https://platform.deepseek.com/docs/fine-tuning)
- [API Reference](https://platform.deepseek.com/docs/api)
- [Best Practices](https://platform.deepseek.com/docs/best-practices)

### Fitness AI Resources:
- Exercise databases and APIs
- Nutrition calculation tools
- Mental health screening tools
- Evidence-based fitness protocols

---

## 🎉 Success Checklist

- [ ] Environment setup complete
- [ ] API keys configured
- [ ] Training dataset generated (10,000 examples)
- [ ] Fine-tuning job created successfully
- [ ] Model training completed
- [ ] Application updated to use fine-tuned model
- [ ] Testing completed with improved responses
- [ ] Fallback system working properly
- [ ] Performance monitoring in place

**Congratulations!** You now have a specialized AI fitness and mental health assistant! 🏆