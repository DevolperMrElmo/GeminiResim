# Gemini AI Görsel Üretici

Bu uygulama, Gemini AI API kullanarak metinden görsel üretmenizi sağlayan kullanıcı dostu bir web arayüzü sunar.

## Özellikler

> Girilen prompt üzerinden görsel üretme
> Resposive arayüz
> Üretilen görselleri localde kaydetme
> Görsellere tıklayarak büyütme
> Çeşitli animasyonlar

/Kurulum\

1 = Gerekli paketleri yükleyin:

```bash
pip install -r requirements.txt
```

2 = `.env` dosyasını oluşturun ve Gemini API anahtarınızı ekleyin:

```
GEMINI_API_KEY=sizin_api_anahtariniz
```

/Kullanım\

1 = Uygulamayı başlatın:

```bash
python app.py
```

2 = Tarayıcınızda `http://127.0.0.1:5000` adresine gidin
3 = Sol taraftaki alana prompt yazın ve "Görsel Oluştur" düğmesine tıklayın
4 = Oluşturulan görseli hem localden hemde sağdaki galeride görüntüleyin

## Teknik Detaylar

- Flask web çerçevesi
- Tailwind CSS (CDN üzerinden)
- Google Gemini AI API
- Responsive tasarım 
