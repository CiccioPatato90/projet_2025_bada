import numpy as np
import pandas as pd
import glob
import re
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle
from utils.XML_Parser import XMLParser

# List of target coefficients
TARGETS = ["CD_clean/d", "CT/a", "CL_clean/bf", "CF/f"]
def extract_altitude(filename):
    # Use regex to find the altitude value
    match = re.search(r"ptd_results/results_Altitude_(\d+)_ISA_", filename)
    if match:
        return int(match.group(1))  # Convert to integer
    else:
        raise ValueError(f"Altitude not found in filename: {filename}")
# Load and preprocess all data
def load_and_preprocess_data(file_list, xml_parser, tags):
    X_all, y_all = [], []
    for file in file_list:
        df = pd.read_csv(file)
        if df.empty:
            continue
        # Input features
        print(file)
        A = extract_altitude(file)
        X = df[["Mass", "CAS"]].values
        # Target coefficients (from XML file or heuristic approach)
        y = np.array([xml_parser.find_tag_coefficients(tag) for tag in tags])
        X_all.append(X)
        X_all.append(A)
        y_all.append(y)
    X_all = np.vstack(X_all)
    y_all = np.vstack(y_all)
    return X_all, y_all

# Fit scalers on the entire dataset
file_list = glob.glob("ptd_results/results_Altitude_*_ISA_*.csv")
xml_parser = XMLParser("reference_dummy_extracted/Dummy-TWIN-plus/Dummy-TWIN-plus.xml")
tags = ["CF/f", "CT/a", "CL_clean/bf", "CD_clean/d"]
X, y = load_and_preprocess_data(file_list, xml_parser, tags)

# Data generator to handle large CSV files efficiently
def data_generator(file_list, batch_size=32):
    while True:
        for file in shuffle(file_list):  # Shuffle files for each epoch
            df = pd.read_csv(file)
            if df.empty:
                continue

            X = df[["Mass", "CAS", "Altitude"]].values
            y = df[TARGETS].values
            X_scaled = scaler_X.transform(X)
            y_scaled = scaler_y.transform(y)
            for i in range(0, len(X_scaled), batch_size):
                yield X_scaled[i:i+batch_size], y_scaled[i:i+batch_size]

# Split data into training and validation sets
train_files, val_files = train_test_split(glob.glob("ptd_results/results_Altitude_*_ISA_*.csv"), test_size=0.2)

# Define neural network model
model = keras.Sequential([
    layers.Dense(128, activation="relu", input_shape=(3,)),
    layers.Dense(128, activation="relu"),
    layers.Dense(len(TARGETS))  # Output for all coefficients
])

# Compile the model
model.compile(optimizer="adam", loss="mse")

# Train using generator
batch_size = 32
epochs = 50
steps_per_epoch = len(train_files) // batch_size
validation_steps = len(val_files) // batch_size

history = model.fit(
    data_generator(train_files, batch_size=batch_size),
    epochs=epochs,
    steps_per_epoch=steps_per_epoch,
    validation_data=data_generator(val_files, batch_size=batch_size),
    validation_steps=validation_steps,
    verbose=1
)

# Prediction function
def predict_coefficients(mass, cas, altitude):
    input_data = np.array([[mass, cas, altitude]])
    input_scaled = scaler_X.transform(input_data)
    predicted_scaled = model.predict(input_scaled)
    predicted = scaler_y.inverse_transform(predicted_scaled)
    return dict(zip(TARGETS, predicted[0]))

# Example prediction
predicted_coefficients = predict_coefficients(60000, 250, 30000)
print("Predicted Coefficients:", predicted_coefficients)