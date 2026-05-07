import os
import shutil
import azure_helper
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models

DEVICE_ID = azure_helper.DEVICE_ID

def train_and_upload(self):
        if len(self.buffer) < self.seq_len + 50:
            populate_values_for_quick_calibration(self, self.buffer)
            print(f"[WARNING] Not enough data for proper calibration. Populated buffer with {len(self.buffer)} samples.")

        print(f"[INFO] Starting training with {len(self.buffer)} samples.")

        raw_data = np.array(self.buffer)
        self.min_vals = raw_data.min(axis=0)
        self.max_vals = raw_data.max(axis=0)
        norm_data = (raw_data - self.min_vals) / (self.max_vals - self.min_vals + 1e-7)

        sequences = []
        for i in range(len(norm_data) - self.seq_len):
            sequences.append(norm_data[i : i + self.seq_len].flatten())

        train_x = np.array(sequences, dtype=np.float32)
        input_dim = self.seq_len * self.features

        model = models.Sequential([
            layers.Input(shape=(input_dim,)),
            layers.Dense(8, activation='relu'),
            layers.Dense(4, activation='relu'),
            layers.Dense(8, activation='relu'),
            layers.Dense(input_dim, activation='sigmoid')
        ])

        model.compile(optimizer='adam', loss='mse')

        model.fit(train_x, train_x, epochs=50, batch_size=16, validation_split=0.1, verbose=1)

        reconstructions = model.predict(train_x)
        mse = np.mean(np.square(train_x - reconstructions), axis=1)
        threshold = np.percentile(mse, 98)

        if os.path.exists(self.temp_model_path):
            shutil.rmtree(self.temp_model_path)
        model.export(self.temp_model_path)

        try:
            converter = tf.lite.TFLiteConverter.from_saved_model(self.temp_model_path)
            converter.optimizations = [tf.lite.Optimize.DEFAULT]

            def representative_dataset():
                for i in range(min(100, len(train_x))):
                    yield [train_x[i:i+1]]

            converter.representative_dataset = representative_dataset
            converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
            converter.inference_input_type = tf.int8
            converter.inference_output_type = tf.int8

            tflite_model_bytes = converter.convert()

            azure_helper.upload_model_to_blob(tflite_model_bytes, DEVICE_ID, threshold, self.min_vals, self.max_vals)

            print(f"[SUCCESS] Model uploaded. Norm Threshold: {threshold:.6f}")
            azure_helper.update_device_twin(DEVICE_ID, float(threshold))

        except Exception as e:
            print(f"[ERROR] Upload failed: {e}")
        finally:
            if os.path.exists(self.temp_model_path):
                shutil.rmtree(self.temp_model_path)

# in case of calibration was invoked without enough data,
# we can created test data based on data provided by user
# noise in this case must be based on persent, for example 5%
def populate_values_for_quick_calibration(self, values, noise_percent=0.05):
    target_size = self.seq_len + 100
    missing = target_size - len(values)

    if missing <= 0:
        print(f"[INFO] Buffer already has enough samples: {len(values)}")
        return

    if len(values) == 0:
        raise ValueError("Cannot populate calibration data from empty buffer.")

    values_np = np.array(values, dtype=np.float32)

    if values_np.ndim != 2 or values_np.shape[1] != self.features:
        raise ValueError(f"Expected shape (n, {self.features}), got {values_np.shape}")

    print(f"[INFO] Generating {missing} synthetic samples with {noise_percent * 100:.1f}% noise")

    for _ in range(missing):
        base_sample = values_np[np.random.randint(0, len(values_np))].copy()

        noise_scale = np.abs(base_sample) * noise_percent

        noise_scale = np.maximum(noise_scale, np.array([1.0, 0.1, 0.1], dtype=np.float32))

        synthetic = base_sample + np.random.normal(0, noise_scale, size=self.features)


        synthetic[0] = max(0, round(synthetic[0]))   # light
        synthetic[1] = round(synthetic[1], 1)        # temp
        synthetic[2] = round(synthetic[2], 1)        # humidity

        self.buffer.append(synthetic.tolist())

    print(f"[INFO] Population complete. New buffer size: {len(self.buffer)}")