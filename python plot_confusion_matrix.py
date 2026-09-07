import numpy as np
import os
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import load_model
from tensorflow.keras.utils import to_categorical

# --- 1. CONFIGURATION ---
MODEL_PATH = 'final_forthesis_bidirectionallstm_and_encoders_exercise_classifier_model.h5'
DATA_PATH = "processed_data"
ACTIONS = ["barbell biceps curl", "push-up", "shoulder press", "squat"]
SEQUENCE_LENGTH = 30

def load_processed_data():
    """
    Loads data from the processed_data folder using the same logic 
    as your training script.
    """
    sequences, labels = [], []
    for action_idx, action in enumerate(ACTIONS):
        action_path = os.path.join(DATA_PATH, action)
        if not os.path.exists(action_path):
            continue
            
        for sequence_file in os.listdir(action_path):
            if sequence_file.endswith('.npy'):
                res = np.load(os.path.join(action_path, sequence_file))
                # Create sequences with the same logic as your training
                step_size = 5 # Matches your optimized_train.py logic
                for i in range(0, len(res) - SEQUENCE_LENGTH + 1, step_size):
                    window = res[i : i + SEQUENCE_LENGTH]
                    sequences.append(window)
                    labels.append(action_idx)
    
    return np.array(sequences), to_categorical(np.array(labels)).astype(int)

def main():
    # --- 2. LOAD DATA & MODEL ---
    print("Loading data...")
    X, y = load_processed_data()
    
    if len(X) == 0:
        print("Error: No data found in 'processed_data'. Please run the processing script first.")
        return

    # Feature Scaling (Crucial: Must match training scaling)
    print("Scaling features...")
    scaler = StandardScaler()
    n_samples, n_timesteps, n_features = X.shape
    X_scaled = scaler.fit_transform(X.reshape(-1, n_features)).reshape(n_samples, n_timesteps, n_features)

    # Split Data (Using same seed '42' to ensure we test on the same data subset)
    # Note: We split twice to match your training script's logic
    X_temp, X_test, y_temp, y_test = train_test_split(X_scaled, y, test_size=0.15, random_state=42, stratify=y)
    
    print(f"Loading model from {MODEL_PATH}...")
    try:
        model = load_model(MODEL_PATH)
    except Exception as e:
        print(f"Error loading model: {e}")
        return

    # --- 3. PREDICT ---
    print("Running predictions...")
    y_pred = model.predict(X_test)
    y_pred_classes = np.argmax(y_pred, axis=1)
    y_true = np.argmax(y_test, axis=1)

    # --- 4. GENERATE CONFUSION MATRIX ---
    cm = confusion_matrix(y_true, y_pred_classes)
    
    # Plotting
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=ACTIONS, 
                yticklabels=ACTIONS)
    
    plt.title('Confusion Matrix - Exercise Recognition')
    plt.ylabel('Actual Label')
    plt.xlabel('Predicted Label')
    
    # Save the plot
    plt.tight_layout()
    plt.savefig('confusion_matrix.png')
    print("\n✅ Confusion Matrix saved as 'confusion_matrix.png'")
    
    # Print Text Report
    print("\n--- Classification Report ---")
    print(classification_report(y_true, y_pred_classes, target_names=ACTIONS))

if __name__ == "__main__":
    main()