import numpy as np
import cv2
import mediapipe as mp
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Bidirectional, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.utils import to_categorical
import pickle
import matplotlib.pyplot as plt
import seaborn as sns

def process_videos_to_landmarks():
    """Process videos and extract pose landmarks"""
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)
    
    DATA_PATH = r"D:\Fitness-AI-Trainer-With-Automatic-Exercise-Recognition-and-Counting-main\dataset\final_kaggle_with_additional_video"
    output_path = "processed_data"
    actions = ["barbell biceps curl", "push-up", "shoulder press", "squat"]
    
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    for action in actions:
        action_path = os.path.join(DATA_PATH, action)
        if not os.path.exists(action_path):
            continue
            
        if not os.path.exists(os.path.join(output_path, action)):
            os.makedirs(os.path.join(output_path, action))
        
        print(f"Processing {action}...")
        for video_name in os.listdir(action_path):
            if video_name.lower().endswith(('.mp4', '.avi', '.mov')):
                video_path = os.path.join(action_path, video_name)
                output_file = os.path.join(output_path, action, os.path.splitext(video_name)[0] + ".npy")
                
                if os.path.exists(output_file):
                    continue
                    
                cap = cv2.VideoCapture(video_path)
                landmarks_list = []
                
                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    image.flags.writeable = False
                    results = pose.process(image)
                    
                    if results.pose_landmarks:
                        landmarks = []
                        for landmark in results.pose_landmarks.landmark:
                            landmarks.extend([landmark.x, landmark.y, landmark.z, landmark.visibility])
                        landmarks_list.append(landmarks)
                
                cap.release()
                if landmarks_list:
                    np.save(output_file, np.array(landmarks_list))
                    print(f"  Saved {video_name}")
    
    pose.close()
    print("Video processing complete!")

def load_processed_data():
    """Load processed landmark data and create sequences"""
    SEQUENCE_LENGTH = 30
    DATA_PATH = "processed_data"
    actions = ["barbell biceps curl", "push-up", "shoulder press", "squat"]
    
    sequences, labels = [], []
    for action_idx, action in enumerate(actions):
        action_path = os.path.join(DATA_PATH, action)
        if not os.path.exists(action_path):
            continue
            
        for sequence_file in os.listdir(action_path):
            if sequence_file.endswith('.npy'):
                res = np.load(os.path.join(action_path, sequence_file))
                for i in range(len(res) - SEQUENCE_LENGTH + 1):
                    window = res[i : i + SEQUENCE_LENGTH]
                    sequences.append(window)
                    labels.append(action_idx)
    
    return np.array(sequences), to_categorical(np.array(labels)).astype(int)

def build_bilstm_model(input_shape, num_classes):
    """Build bidirectional LSTM model"""
    model = Sequential([
        Bidirectional(LSTM(64, return_sequences=True, activation='relu'), input_shape=input_shape),
        Dropout(0.2),
        Bidirectional(LSTM(128, return_sequences=True, activation='relu')),
        Dropout(0.2),
        Bidirectional(LSTM(64, return_sequences=False, activation='relu')),
        Dense(64, activation='relu'),
        Dense(32, activation='relu'),
        Dense(num_classes, activation='softmax')
    ])
    
    model.compile(
        optimizer='Adam',
        loss='categorical_crossentropy',
        metrics=['categorical_accuracy']
    )
    
    return model



def main():
    print("Starting BiLSTM Exercise Classification Training...")
    
    # Step 1: Process videos to landmarks
    print("Step 1: Processing videos to pose landmarks...")
    process_videos_to_landmarks()
    
    # Step 2: Load processed data
    print("Step 2: Loading processed data...")
    X, y = load_processed_data()
    
    if len(X) == 0:
        print("No data found! Check your dataset path.")
        return
    
    print(f"Dataset shape: {X.shape}")
    print(f"Labels shape: {y.shape}")
    
    # Step 3: Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print(f"Training set: {X_train.shape}")
    print(f"Test set: {X_test.shape}")
    
    # Step 4: Build and train model
    model = build_bilstm_model(input_shape=(30, X.shape[2]), num_classes=y.shape[1])
    print(model.summary())
    
    print("Training model...")
    history = model.fit(X_train, y_train, epochs=50, batch_size=32, validation_data=(X_test, y_test))
    
    # Step 5: Evaluate
    test_loss, test_accuracy = model.evaluate(X_test, y_test, verbose=0)
    print(f"\nFINAL TEST ACCURACY: {test_accuracy:.4f} ({test_accuracy*100:.2f}%)")
    
    # Step 6: Save model
    model.save('final_forthesis_bidirectionallstm_and_encoders_exercise_classifier_model.h5')
    print("Model saved successfully!")

if __name__ == "__main__":
    main()