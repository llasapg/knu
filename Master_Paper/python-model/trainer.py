import os
import shutil
import azure_helper
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models

DEVICE_ID = azure_helper.DEVICE_ID

def train_and_upload(self):
        if len(self.buffer) < self.seq_len + 50:
            print(f"[!] Not enough data: {len(self.buffer)}")
            return

        raw_data = np.array(self.buffer)
        self.min_vals = raw_data.min(axis=0)
        self.max_vals = raw_data.max(axis=0)
        norm_data = (raw_data - self.min_vals) / (self.max_vals - self.min_vals + 1e-7)

        sequences = []
        for i in range(len(norm_data) - self.seq_len):
            sequences.append(norm_data[i : i + self.seq_len].flatten())

        train_x = np.array(sequences)
        input_dim = self.seq_len * self.features

        model = models.Sequential([
            layers.Input(shape=(input_dim,)),
            layers.Dense(8, activation='relu'),
            layers.Dense(4, activation='relu'),
            layers.Dense(8, activation='relu'),
            layers.Dense(input_dim, activation='linear')
        ])

        model.compile(optimizer='adam', loss='mse')
        model.fit(train_x, train_x, epochs=60, batch_size=16, validation_split=0.1, verbose=1)

        reconstructions = model.predict(train_x)
        mse = np.mean(np.square(train_x - reconstructions), axis=1)
        threshold = np.percentile(mse, 98)

        if os.path.exists(self.temp_model_path):
            shutil.rmtree(self.temp_model_path)
        model.export(self.temp_model_path)

        try:
            converter = tf.lite.TFLiteConverter.from_saved_model(self.temp_model_path)
            converter.optimizations = [tf.lite.Optimize.DEFAULT]
            tflite_model_bytes = converter.convert()

            azure_helper.upload_model_to_blob(tflite_model_bytes, self.temp_model_path, DEVICE_ID)

            print(f"[SUCCESS] Model uploaded. Norm Threshold: {threshold:.6f}")
            azure_helper.update_device_twin(DEVICE_ID, threshold)

        except Exception as e:
            print(f"[ERROR] Upload failed: {e}")
        finally:
            if os.path.exists(self.temp_model_path):
                shutil.rmtree(self.temp_model_path)