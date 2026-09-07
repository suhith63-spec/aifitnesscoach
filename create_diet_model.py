import numpy as np
import pandas as pd
import pickle
from sklearn.linear_model import LinearRegression


def create_diet_model():
    # Generate a synthetic dataset
    np.random.seed(42)
    calories = np.random.randint(1000, 3500, 500)
    preference = np.random.randint(0, 2, 500)  # 0 for Veg, 1 for Non-Veg
    target_calories = calories + (preference * 200) + np.random.randint(-100, 100, 500)

    # Create DataFrame
    data = pd.DataFrame(
        {
            "Calories": calories,
            "Preference": preference,
            "TargetCalories": target_calories,
        }
    )

    # Train the model
    X = data[["Calories", "Preference"]]
    y = data["TargetCalories"]
    model = LinearRegression()
    model.fit(X, y)

    # Save the model
    with open("diet_model.pkl", "wb") as f:
        pickle.dump(model, f)

    print("Diet model created and saved as 'diet_model.pkl'")


if __name__ == "__main__":
    create_diet_model()
