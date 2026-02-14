# Генерація моделі
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install numpy==1.26.4 tensorflow-macos tensorflow-metal matplotlib azure-eventhub azure-storage-blob
python main.py

# Сгенерує ваги
xxd -i smartiot_model.tflite > model_data.h
