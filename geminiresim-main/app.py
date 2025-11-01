import base64
import os
import mimetypes
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Create necessary directories
UPLOAD_FOLDER = os.path.join('static', 'images')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def save_binary_file(base64_data, mime_type):
    """Base64 gelen görseli decode edip dosyaya kaydeder"""
    file_extension = mimetypes.guess_extension(mime_type) or ".png"
    file_name = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_FOLDER, file_name)

    # Base64 decode işlemi
    with open(file_path, "wb") as f:
        f.write(base64.b64decode(base64_data))

    return file_name

def generate_image(prompt):
    try:
        client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY"),
        )

        model = "gemini-2.0-flash-exp-image-generation"
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)],
            ),
        ]
        generate_content_config = types.GenerateContentConfig(
            temperature=1,
            top_p=0.95,
            top_k=40,
            max_output_tokens=8192,
            response_modalities=["image", "text"],
            safety_settings=[
                types.SafetySetting(
                    category="HARM_CATEGORY_CIVIC_INTEGRITY",
                    threshold="OFF",
                ),
            ],
            response_mime_type="text/plain",
        )

        # Stream API kullanımı
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            if not chunk.candidates or not chunk.candidates[0].content or not chunk.candidates[0].content.parts:
                continue

            part = chunk.candidates[0].content.parts[0]

            # Görsel geldiğinde
            if part.inline_data:
                inline_data = part.inline_data
                file_name = save_binary_file(inline_data.data, inline_data.mime_type)

                # Debug için
                print(f"✅ Görsel oluşturuldu: {file_name}, MIME: {inline_data.mime_type}")
                return {'success': True, 'file_name': file_name}

            # Metin cevabı varsa (hata durumunda genelde buradan gelir)
            if hasattr(part, 'text') and part.text:
                print(f"⚠️ API Metin Yanıtı: {part.text}")

        return {'success': False, 'error': 'Görsel oluşturulamadı'}

    except Exception as e:
        print(f"❌ Hata: {str(e)}")
        return {'success': False, 'error': str(e)}


@app.route('/')
def index():
    # Get all generated images
    images = []
    if os.path.exists(UPLOAD_FOLDER):
        for filename in os.listdir(UPLOAD_FOLDER):
            if filename.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                images.append(filename)

    # Sort images by creation date (newest first)
    images.sort(key=lambda x: os.path.getmtime(os.path.join(UPLOAD_FOLDER, x)), reverse=True)

    # Pass current year for footer
    now = datetime.now()

    return render_template('index.html', images=images, now=now)


@app.route('/generate', methods=['POST'])
def generate():
    prompt = request.form.get('prompt')
    if not prompt:
        flash('Lütfen bir istem (prompt) girin', 'error')
        return redirect(url_for('index'))

    result = generate_image(prompt)

    if result['success']:
        flash('✅ Görsel başarıyla oluşturuldu!', 'success')
    else:
        flash(f"❌ Görsel oluşturma hatası: {result.get('error', 'Bilinmeyen hata')}", 'error')

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
