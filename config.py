import os
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class DeepSeekConfig:
    """Configuration for DeepSeek R1 API"""

    api_key: str
    base_url: str = "https://api.deepseek.com/v1"
    model_name: str = "deepseek-r1"
    max_tokens: int = 1000
    temperature: float = 0.7
    timeout: int = 30


@dataclass
class DatabaseConfig:
    """Database configuration"""

    db_path: str = "fitness_ai.db"
    backup_interval: int = 24  # hours
    max_interactions_per_user: int = 1000


@dataclass
class FilterConfig:
    """Content filtering configuration"""

    fitness_keywords: List[str] = None
    mental_health_keywords: List[str] = None
    strict_filtering: bool = True

    def __post_init__(self):
        if self.fitness_keywords is None:
            self.fitness_keywords = [
                "exercise",
                "workout",
                "fitness",
                "training",
                "gym",
                "muscle",
                "strength",
                "cardio",
                "running",
                "cycling",
                "swimming",
                "yoga",
                "pilates",
                "crossfit",
                "bodybuilding",
                "powerlifting",
                "weightlifting",
                "calisthenics",
                "hiit",
                "nutrition",
                "diet",
                "protein",
                "calories",
                "macros",
                "supplements",
                "health",
                "wellness",
                "recovery",
                "sleep",
                "hydration",
                "stretching",
                "flexibility",
                "mobility",
                "injury",
                "rehabilitation",
                "physical therapy",
            ]

        if self.mental_health_keywords is None:
            self.mental_health_keywords = [
                "mental health",
                "stress",
                "anxiety",
                "depression",
                "mood",
                "emotional",
                "wellbeing",
                "mindfulness",
                "meditation",
                "therapy",
                "counseling",
                "self-care",
                "motivation",
                "confidence",
                "self-esteem",
                "burnout",
                "work-life balance",
                "relationships",
                "coping",
                "resilience",
            ]


class ConfigManager:
    """Manage application configuration"""

    def __init__(self):
        self.deepseek_config = self._load_deepseek_config()
        self.database_config = self._load_database_config()
        self.filter_config = self._load_filter_config()

    def _load_deepseek_config(self) -> DeepSeekConfig:
        """Load DeepSeek configuration from environment"""
        return DeepSeekConfig(
            api_key=os.getenv("DEEPSEEK_API_KEY", ""),
            base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
            model_name=os.getenv("DEEPSEEK_MODEL", "deepseek-r1"),
            max_tokens=int(os.getenv("DEEPSEEK_MAX_TOKENS", "1000")),
            temperature=float(os.getenv("DEEPSEEK_TEMPERATURE", "0.7")),
            timeout=int(os.getenv("DEEPSEEK_TIMEOUT", "30")),
        )

    def _load_database_config(self) -> DatabaseConfig:
        """Load database configuration"""
        return DatabaseConfig(
            db_path=os.getenv("DATABASE_PATH", "fitness_ai.db"),
            backup_interval=int(os.getenv("BACKUP_INTERVAL", "24")),
            max_interactions_per_user=int(os.getenv("MAX_INTERACTIONS", "1000")),
        )

    def _load_filter_config(self) -> FilterConfig:
        """Load filter configuration"""
        return FilterConfig(
            strict_filtering=os.getenv("STRICT_FILTERING", "true").lower() == "true"
        )

    def validate_config(self) -> Dict[str, bool]:
        """Validate configuration settings"""
        validation_results = {
            "deepseek_api_key": bool(self.deepseek_config.api_key),
            "database_path": os.path.exists(
                os.path.dirname(self.database_config.db_path) or "."
            ),
            "deepseek_url": self.deepseek_config.base_url.startswith("http"),
            "valid_temperature": 0.0 <= self.deepseek_config.temperature <= 2.0,
            "valid_max_tokens": 1 <= self.deepseek_config.max_tokens <= 4000,
        }

        return validation_results

    def get_system_prompts(self) -> Dict[str, str]:
        """Get system prompts for different modes"""
        return {
            "fitness": """You are a specialized AI fitness coach with expertise in:
- Workout planning and exercise programming
- Proper form and technique guidance
- Injury prevention and recovery
- Progress tracking and goal setting
- Equipment recommendations

Always provide safe, evidence-based advice. If unsure about medical conditions, recommend consulting healthcare professionals.""",
            "nutrition": """You are a knowledgeable nutrition advisor specializing in:
- Meal planning and dietary guidance
- Macronutrient and micronutrient education
- Sports nutrition and supplementation
- Healthy eating habits and lifestyle changes
- Special dietary considerations

Provide practical, science-based nutrition advice. For specific medical dietary needs, recommend consulting registered dietitians.""",
            "mental_health": """You are a compassionate mental health support assistant focused on:
- Stress management and coping strategies
- Motivation and goal-setting support
- Exercise-related anxiety and confidence building
- Work-life balance and wellness
- Mindfulness and self-care practices

Provide empathetic, supportive guidance. For serious mental health concerns, always recommend professional help.""",
        }


# Global configuration instance
config = ConfigManager()
