import numpy as np
import cv2
import mediapipe as mp
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Bidirectional, Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.optimizers import Adam

def process_videos_to_landmarks():
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.7, min_tracking_confidence=0.7)
    
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
                # Multiple overlapping sequences for data augmentation
                step_size = 5  # More overlap = more data
                for i in range(0, len(res) - SEQUENCE_LENGTH + 1, step_size):
                    window = res[i : i + SEQUENCE_LENGTH]
                    sequences.append(window)
                    labels.append(action_idx)
    
    return np.array(sequences), to_categorical(np.array(labels)).astype(int)

def build_optimized_bilstm_model(input_shape, num_classes):
    model = Sequential([
        Bidirectional(LSTM(128, return_sequences=True, dropout=0.2, recurrent_dropout=0.2), input_shape=input_shape),
        BatchNormalization(),
        
        Bidirectional(LSTM(256, return_sequences=True, dropout=0.2, recurrent_dropout=0.2)),
        BatchNormalization(),
        
        Bidirectional(LSTM(128, return_sequences=True, dropout=0.2, recurrent_dropout=0.2)),
        BatchNormalization(),
        
        Bidirectional(LSTM(64, return_sequences=False, dropout=0.2, recurrent_dropout=0.2)),
        BatchNormalization(),
        
        Dense(256, activation='relu'),
        Dropout(0.5),
        BatchNormalization(),
        
        Dense(128, activation='relu'),
        Dropout(0.3),
        
        Dense(64, activation='relu'),
        Dropout(0.2),
        
        Dense(num_classes, activation='softmax')
    ])
    
    model.compile(
        optimizer=Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['categorical_accuracy']
    )
    
    return model

def main():
    print("Starting Optimized BiLSTM Training...")
    
    # Process videos
    print("Processing videos...")
    process_videos_to_landmarks()
    
    # Load data
    print("Loading data...")
    X, y = load_processed_data()
    
    if len(X) == 0:
        print("No data found!")
        return
    
    print(f"Dataset shape: {X.shape}")
    
    # Feature scaling
    scaler = StandardScaler()
    n_samples, n_timesteps, n_features = X.shape
    X_scaled = scaler.fit_transform(X.reshape(-1, n_features)).reshape(n_samples, n_timesteps, n_features)
    
    # Split data with stratification
    X_temp, X_test, y_temp, y_test = train_test_split(X_scaled, y, test_size=0.15, random_state=42, stratify=y)
    X_train, X_val, y_train, y_val = train_test_split(X_temp, y_temp, test_size=0.18, random_state=42, stratify=y_temp)
    
    print(f"Train: {X_train.shape}, Val: {X_val.shape}, Test: {X_test.shape}")
    
    # Build model
    model = build_optimized_bilstm_model(input_shape=(30, n_features), num_classes=y.shape[1])
    print(model.summary())
    
    # Callbacks for best performance
    callbacks = [
        EarlyStopping(patience=20, restore_best_weights=True, monitor='val_categorical_accuracy'),
        ModelCheckpoint('best_model.h5', save_best_only=True, monitor='val_categorical_accuracy'),
        ReduceLROnPlateau(patience=10, factor=0.5, min_lr=1e-7)
    ]
    
    # Train
    print("Training...")
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=200,
        batch_size=16,
        callbacks=callbacks,
        verbose=1
    )
    
    # Evaluate
    test_loss, test_accuracy = model.evaluate(X_test, y_test, verbose=0)
    print(f"\nFINAL TEST ACCURACY: {test_accuracy:.4f} ({test_accuracy*100:.2f}%)")
    
    # Detailed evaluation
    y_pred = model.predict(X_test)
    y_pred_classes = np.argmax(y_pred, axis=1)
    y_true_classes = np.argmax(y_test, axis=1)
    
    actions = ["barbell biceps curl", "push-up", "shoulder press", "squat"]
    print("\nClassification Report:")
    print(classification_report(y_true_classes, y_pred_classes, target_names=actions))
    
    # Save
    model.save('final_forthesis_bidirectionallstm_and_encoders_exercise_classifier_model.h5')
    print("Model saved!")

if __name__ == "__main__":
    main()