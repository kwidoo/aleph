from flask import Flask, jsonify, request
import json
import os

app = Flask(__name__)

TRANSLATION_FILE = './translations/translations.json'

@app.route('/translations', methods=['GET'])
def get_translations():
    """Fetch all translations."""
    if os.path.exists(TRANSLATION_FILE):
        with open(TRANSLATION_FILE, 'r', encoding='utf-8') as f:
            translations = json.load(f)
        return jsonify(translations)
    return jsonify({}), 200

@app.route('/translations', methods=['POST'])
def update_translation():
    """Update a translation key."""
    data = request.json
    key = data.get('key')
    value = data.get('value')

    if not key or not value:
        return jsonify({'error': 'Key and value are required'}), 400

    translations = {}
    if os.path.exists(TRANSLATION_FILE):
        with open(TRANSLATION_FILE, 'r', encoding='utf-8') as f:
            translations = json.load(f)

    translations[key] = value

    with open(TRANSLATION_FILE, 'w', encoding='utf-8') as f:
        json.dump(translations, f, indent=4, ensure_ascii=False)

    return jsonify({'message': 'Translation updated successfully'}), 200

@app.route('/translations/import', methods=['POST'])
def import_translations():
    """Import translations from a file."""
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file provided'}), 400

    translations = json.load(file)
    with open(TRANSLATION_FILE, 'w', encoding='utf-8') as f:
        json.dump(translations, f, indent=4, ensure_ascii=False)

    return jsonify({'message': 'Translations imported successfully'}), 200

@app.route('/translations/export', methods=['GET'])
def export_translations():
    """Export translations to a file."""
    if os.path.exists(TRANSLATION_FILE):
        with open(TRANSLATION_FILE, 'r', encoding='utf-8') as f:
            translations = json.load(f)
        return jsonify(translations)
    return jsonify({}), 200

if __name__ == '__main__':
    app.run(debug=True)
