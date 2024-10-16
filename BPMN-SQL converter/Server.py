from flask import Flask, request, jsonify
import os
import parser_to_json  # Предполагаем, что у вас есть модуль parser_to_json
import DatabaseManager
import DataProcessor
import config
import json

app = Flask(__name__)

# Настройка базы данных
db_manager = DatabaseManager.DatabaseManager(
    host=config.HOST,
    database=config.DATABASE,
    user=config.USER,
    password=config.PASSWORD
)


@app.route('/upload', methods=['POST'])
def upload_file():
    """Обработчик для загрузки файла BPMN."""
    if 'file' not in request.files:
        return jsonify({'error': 'Файл не найден'}), 400

    file = request.files['file']

    if file.filename.endswith('.bpmn'):
        # Сохранение файла
        file_path = os.path.join('./uploads', file.filename)
        file.save(file_path)

        # Обработка файла
        try:
            parser_to_json.parser_to_json(file_path, f"./json/{os.path.splitext(file.filename)[0]}.json")
            with open(f"./json/{os.path.splitext(file.filename)[0]}.json", 'r') as f:
                data = json.load(f)

            processor = DataProcessor.DataProcessor(db_manager)
            processor.process_data(data)

            return jsonify({'message': 'Файл успешно обработан'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Неверный тип файла'}), 400


if __name__ == '__main__':
    app.run(debug=True)
