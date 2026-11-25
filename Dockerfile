# Öğrenci Harcama Takip - Docker imajı
FROM python:3.12-slim

# Python'un .pyc dosyası yazmasını ve çıktıyı tamponlamasını kapat
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Önce bağımlılıklar: kod değişince bu katman önbellekten gelir, build hızlanır
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Uygulamayı root olmayan bir kullanıcıyla çalıştır; veritabanı instance/ klasöründe
RUN useradd --create-home uygulama \
    && mkdir -p /app/instance \
    && chown -R uygulama /app
USER uygulama

EXPOSE 8000

# Konteyner ayakta mı? Ana sayfa yanıt veriyorsa sağlıklı sayılır
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/')" || exit 1

# Üretim için Flask'ın geliştirme sunucusu yerine gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "app:app"]
