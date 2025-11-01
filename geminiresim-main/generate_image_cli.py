#!/usr/bin/env python3
import base64
import os
import mimetypes
import sys
from datetime import datetime
from google import genai
from google.genai import types
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

def save_binary_file(file_name, data):
    # Dosya adında geçersiz karakter varsa temizle
    file_name = ''.join(c for c in file_name if c.isalnum() or c in ['_', '-', ' ']).strip()
    if not file_name:
        file_name = f"image_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    f = open(file_name, "wb")
    f.write(data)
    f.close()
    
    return file_name

def generate(prompt, output_name=None):
    try:
        print(f"İstem: '{prompt}'")
        print("Görsel oluşturuluyor...")
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("Hata: GEMINI_API_KEY çevre değişkeni bulunamadı. Lütfen .env dosyasını kontrol edin.")
            return False
            
        client = genai.Client(
            api_key=api_key,
        )

        model = "gemini-2.0-flash-exp-image-generation"
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=prompt),
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
                    threshold="OFF",  # Off
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
                inline_data = chunk.candidates[0].content.parts[0].inline_data
                file_extension = mimetypes.guess_extension(inline_data.mime_type)
                
                # Kullanıcı belirli bir isim verdiyse kullan, yoksa varsayılan
                if output_name:
                    file_name = output_name
                    if file_extension and not file_name.endswith(file_extension):
                        file_name = f"{file_name}{file_extension}"
                else:
                    # Boşlukları alt tire ile değiştir ve ilk 30 karakteri al
                    auto_name = prompt.replace(' ', '_')[:30].lower()
                    file_name = f"{auto_name}{file_extension}"
                
                complete_name = save_binary_file(file_name, inline_data.data)
                
                print(f"Başarılı! '{complete_name}' dosyası oluşturuldu. (MIME Türü: {inline_data.mime_type})")
                return True
            else:
                if hasattr(chunk, 'text') and chunk.text:
                    print(f"API Yanıtı: {chunk.text}")
        
        print("Hata: Görsel oluşturulamadı.")
        return False
            
    except Exception as e:
        print(f"Hata: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Kullanım: python generate_image_cli.py \"<prompt>\" [output_file_name]")
        print("Örnek: python generate_image_cli.py \"Güneş batarken dağların üzerinde uçan bir kartal\" kartal_gorseli")
        sys.exit(1)
        
    prompt = sys.argv[1]
    output_name = sys.argv[2] if len(sys.argv) > 2 else None
    
    generate(prompt, output_name) 