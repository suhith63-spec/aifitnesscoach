import streamlit as st
import random

# Exercise database with variations for each muscle group
exercises = {
    "Back": [
        "Deadlifts",
        "Pull-ups",
        "Lat Pulldowns",
        "Bent Over Rows",
        "Single Arm Rows",
        "T-Bar Rows",
        "Seated Cable Rows",
        "Face Pulls",
        "Trap Shrugs",
        "Hyperextensions",
        "Good Mornings",
        "Reverse Flys",
        "Rack Pulls",
        "Inverted Rows",
        "Renegade Rows",
    ],
    "Triceps": [
        "Tricep Dips",
        "Close-Grip Bench Press",
        "Overhead Tricep Extension",
        "Skull Crushers",
        "Tricep Kickbacks",
        "Rope Pushdowns",
        "Diamond Push-ups",
        "Bench Dips",
        "EZ Bar Extensions",
        "Reverse Grip Pushdowns",
        "French Press",
        "Tricep Push-ups",
        "JM Press",
        "Cable Extensions",
        "Parallel Bar Dips",
    ],
    "Biceps": [
        "Barbell Curls",
        "Hammer Curls",
        "Preacher Curls",
        "Concentration Curls",
        "EZ Bar Curls",
        "Incline Dumbbell Curls",
        "Zottman Curls",
        "Cable Curls",
        "Spider Curls",
        "Drag Curls",
        "Rope Curls",
        "Reverse Curls",
        "Resistance Band Curls",
        "Chin-ups",
        "Cross Body Curls",
    ],
    "Chest": [
        "Bench Press",
        "Incline Bench Press",
        "Decline Bench Press",
        "Push-ups",
        "Chest Flys",
        "Cable Crossovers",
        "Pec Deck Machine",
        "Dumbbell Press",
        "Incline Dumbbell Press",
        "Decline Dumbbell Press",
        "Chest Dips",
        "Landmine Press",
        "Machine Chest Press",
        "Svend Press",
        "Resistance Band Flys",
    ],
    "Abs": [
        "Crunches",
        "Planks",
        "Russian Twists",
        "Leg Raises",
        "Bicycle Crunches",
        "V-Ups",
        "Mountain Climbers",
        "Hanging Leg Raises",
        "Ab Rollouts",
        "Flutter Kicks",
        "Toe Touches",
        "Side Planks",
        "Cable Crunches",
        "Woodchoppers",
        "Dragon Flags",
    ],
    "Legs": [
        "Squats",
        "Front Squats",
        "Deadlifts",
        "Leg Press",
        "Lunges",
        "Romanian Deadlifts",
        "Bulgarian Split Squats",
        "Calf Raises",
        "Leg Extensions",
        "Leg Curls",
        "Step-Ups",
        "Hack Squats",
        "Sumo Deadlifts",
        "Hip Thrusts",
        "Glute Bridges",
    ],
}

# Schedule for split workouts
split_workouts = {
    "Push-Pull-Legs": ["Chest", "Back", "Legs", "Rest", "Chest", "Back", "Legs"],
    "Upper-Lower": ["Upper", "Lower", "Rest", "Upper", "Lower", "Rest", "Rest"],
}


# Generate workout plan
def generate_workout_plan(
    level,
    num_exercises=5,
    split_type=None,
    muscle_group=None,
    cardio_time=20,
    functional_time=20,
):
    plan = {}

    if split_type and split_type in split_workouts:
        schedule = split_workouts[split_type]
    elif muscle_group:
        schedule = [muscle_group] * 6 + ["Rest"]
    else:
        schedule = [
            "Chest",
            "Back",
            "Legs",
            "Rest",
            "Chest",
            "Back",
            "Legs",
        ]  # Default schedule

    for day, muscle in enumerate(schedule):
        if muscle == "Rest":
            plan[f"Day {day + 1} ({muscle})"] = ["Take a Rest Day"]
        elif muscle == "Cardio":
            plan[f"Day {day + 1} (Cardio)"] = [f"Cardio: {cardio_time} min"]
        elif muscle == "Functional":
            plan[f"Day {day + 1} (Functional)"] = [
                f"Functional Training: {functional_time} min"
            ]
        else:
            selected_muscle_groups = (
                ["Chest", "Back", "Triceps", "Biceps", "Legs", "Abs"]
                if muscle == "Upper"
                else ["Legs", "Abs"]
            )
            selected_exercises = []
            for mg in selected_muscle_groups:
                selected_exercises.extend(
                    random.sample(exercises[mg], min(num_exercises, len(exercises[mg])))
                )
            plan[f"Day {day + 1} ({muscle})"] = selected_exercises
    return plan


# Streamlit UI
def smart_workout_ui():
    """Advanced smart workout planner with comprehensive questionnaire"""
    
    # Check if advanced planner is available
    try:
        from advanced_workout_planner import advanced_workout_planner_ui
        advanced_workout_planner_ui()
        return
    except ImportError:
        st.error("Advanced workout planner not available. Using basic version.")
    
    # Fallback to basic planner
    st.title("Smart Workout Planner")
    st.info("💡 This is the basic version. For a truly personalized plan based on 15 foundational questions, please ensure the advanced planner is available.")

    # User preferences
    level = st.selectbox(
        "Select your fitness level", ["Beginner", "Intermediate", "Advanced"]
    )
    workout_type = st.radio(
        "Choose your workout style", ["Split Workout", "Single Muscle Group"]
    )
    cardio_time = st.slider("Select Cardio Duration (minutes)", 10, 60, 20)
    functional_time = st.slider(
        "Select Functional Training Duration (minutes)", 10, 60, 20
    )

    if workout_type == "Split Workout":
        split_type = st.selectbox(
            "Select Split Type", ["Push-Pull-Legs", "Upper-Lower"]
        )
        num_exercises = st.slider("Select number of exercises per day", 3, 7, 5)
        muscle_group = None
    else:
        muscle_group = st.selectbox(
            "Select Muscle Group", ["Back", "Triceps", "Biceps", "Chest", "Abs", "Legs"]
        )
        num_exercises = st.slider("Select number of exercises for the day", 3, 7, 5)
        split_type = None

    if st.button("Generate Basic Workout Plan"):
        workout_plan = generate_workout_plan(
            level, num_exercises, split_type, muscle_group, cardio_time, functional_time
        )
        st.subheader("Your Basic Workout Plan")
        for day, exercises_list in workout_plan.items():
            st.subheader(day)
            for exercise in exercises_list:
                st.write(f"- {exercise}")
        
        st.info("💡 **Upgrade to Advanced Planner**: Get a truly personalized plan based on your specific goals, schedule, equipment, and fitness history with our 15-question assessment.")


if __name__ == "__main__":
    smart_workout_ui()