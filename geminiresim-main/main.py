import base64
import os
import mimetypes
from google import genai
from google.genai import types
from dotenv import load_dotenv  # .env dosyasını yüklemek için

# .env dosyasını yükle
load_dotenv()

def save_binary_file(file_name, data):
    with open(file_name, "wb") as f:
        f.write(data)


def generate(prompt):
    client = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY"),  # API anahtarı buradan okunacak
    )

    model = "gemini-2.0-flash-exp-image-generation"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt),  # Kullanıcıdan alınan prompt burada kullanılıyor
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192,
        response_modalities=[
            "image",
            "text",
        ],
        safety_settings=[
            types.SafetySetting(
                category="HARM_CATEGORY_CIVIC_INTEGRITY",
                threshold="OFF",
            ),
        ],
        response_mime_type="text/plain",
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if not chunk.candidates or not chunk.candidates[0].content or not chunk.candidates[0].content.parts:
            continue
        
        if chunk.candidates[0].content.parts[0].inline_data:
            file_name = input("Dosya adı girin (uzantı olmadan): ")
            inline_data = chunk.candidates[0].content.parts[0].inline_data
            file_extension = mimetypes.guess_extension(inline_data.mime_type)
            
            if file_extension:
                full_file_name = f"{file_name}{file_extension}"
                save_binary_file(full_file_name, inline_data.data)
                print(f"Dosya başarıyla kaydedildi: {full_file_name}")
            else:
                print("Dosya türü algılanamadı.")
                
        else:
            print("Metin çıktısı alındı:")
            print(chunk.text)


if __name__ == "__main__":
    prompt = input("Lütfen bir istem (prompt) girin: ")
    generate(prompt)
