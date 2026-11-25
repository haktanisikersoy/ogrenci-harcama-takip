# Öğrenci Harcama Takip

[![CI](https://github.com/haktanisikersoy/ogrenci-harcama-takip/actions/workflows/ci.yml/badge.svg)](https://github.com/haktanisikersoy/ogrenci-harcama-takip/actions/workflows/ci.yml)

## Proje Hakkında
Üniversite öğrencileri çoğu zaman sınırlı bir bütçeyle yaşıyor ve ay sonunda paranın nereye gittiğini bilmiyor. Bu uygulama, öğrencilerin harcamalarını kategoriye göre kaydetmesini, aylık harcama özetini görmesini, bütçe limitini takip etmesini ve düzenli abonelik ödemelerini kaçırmamasını sağlar.

**Kimin için:** Harçlık, burs veya part-time gelirle geçinen ve bütçesini kontrol altında tutmak isteyen üniversite öğrencileri.

## Proje Panosu
🔗 **[Öğrenci Harcama Takip - Pano](https://github.com/users/haktanisikersoy/projects/1/views/1)**

Görevler GitHub Projects üzerinde **Yapılacak → Devam Ediyor → Tamamlandı** sütunlarıyla takip edilmektedir. Her kartta görevin açıklaması ve kabul kriterleri bulunur. Tamamlanan kartlar, ilgili Pull Request'e bağlıdır (kartı açınca sağdaki **Development** bölümünde görünür).

## Kullanılan Teknolojiler
- **Python 3.9+** ve **Flask** (web uygulaması)
- **SQLite** (veritabanı, ek kurulum gerektirmez)
- **pytest** (otomatik testler) ve **ruff** (lint/format kontrolü)
- **GitHub Actions** (her push ve PR'da lint, test ve Docker kontrolü)
- **Docker** ve **gunicorn** (konteyner ile çalıştırma)

## Kurulum ve Çalıştırma

### Gereksinimler
- **Python 3.9 veya üzeri** — sürümü kontrol etmek için: `python3 --version` (Windows: `python --version`)
- **Git** — yoksa repo sayfasındaki **Code → Download ZIP** ile indirip klasörü açabilirsiniz

### Yöntem 1: Python ile (önerilen)

**macOS / Linux**
```bash
git clone https://github.com/haktanisikersoy/ogrenci-harcama-takip.git
cd ogrenci-harcama-takip
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

**Windows (PowerShell veya Komut İstemi)**
```bash
git clone https://github.com/haktanisikersoy/ogrenci-harcama-takip.git
cd ogrenci-harcama-takip
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Tarayıcıda **http://127.0.0.1:5000** adresini açın. Uygulama boş bir veritabanıyla başlar (`instance/harcamalar.db` ilk çalıştırmada otomatik oluşur). Durdurmak için terminalde **Ctrl + C**.

### Yöntem 2: Docker ile
Bilgisayarınızda Docker kuruluysa (Python kurulumu gerekmez):
```bash
docker build -t ogrenci-harcama-takip .
docker run --rm -p 8000:8000 ogrenci-harcama-takip
```
Tarayıcıda **http://localhost:8000** adresini açın. (macOS/Linux kısayolu: `make docker-run`)

### Testler ve lint
```bash
pytest            # otomatik testler
ruff check .      # lint kontrolü
make check        # lint + testler birlikte (macOS/Linux)
```

### Olası sorunlar ve çözümleri

| Sorun | Çözüm |
|---|---|
| macOS'ta sayfa **"403 Forbidden"** veriyor | 5000 portunu AirPlay kullanıyor. Uygulamayı `flask --app app run --port 5001` ile başlatıp **http://127.0.0.1:5001** adresini açın. |
| **"Address already in use"** / port dolu | Aynı komutla başka bir port kullanın: `flask --app app run --port 5001` |
| `python3: command not found` | Windows'ta `python3` yerine `python` yazın. Python yüklü değilse python.org'dan 3.9+ sürümünü kurun. |
| Windows PowerShell'de `activate` komutu **"running scripts is disabled"** hatası veriyor | Önce `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` çalıştırın, sonra tekrar `.venv\Scripts\activate` yazın. (Ya da Komut İstemi'nde `.venv\Scripts\activate.bat` kullanın.) |
| `ModuleNotFoundError: No module named 'flask'` | Sanal ortam etkin değil. `activate` komutunu çalıştırıp `pip install -r requirements.txt` adımını tekrarlayın. |
| Denemeleri sıfırdan başlatmak istiyorum | Uygulamayı durdurup `instance/harcamalar.db` dosyasını silin; bir sonraki çalıştırmada boş veritabanı oluşur. |
| Docker'da 8000 portu dolu | `docker run --rm -p 8080:8000 ogrenci-harcama-takip` ile çalıştırıp **http://localhost:8080** adresini açın. |

## Geliştirilen Özellikler ve Nasıl Denenir

### ✅ 1. Harcama Ekleme — [#1](https://github.com/haktanisikersoy/ogrenci-harcama-takip/issues/1)
1. Ana sayfadaki formda tutar (ör. `120,50`), kategori, açıklama ve tarih girip **Harcama Ekle**'ye basın.
2. **Beklenen:** Harcama, formun altındaki tabloda görünür.
3. Tutar alanını boş bırakın veya `-50` yazıp tekrar deneyin.
4. **Beklenen:** Kırmızı bir hata mesajı görünür ve kayıt eklenmez.

### ✅ 2. Aylık Kategori Özeti — [#2](https://github.com/haktanisikersoy/ogrenci-harcama-takip/issues/2)
1. Farklı kategorilerde ve farklı aylarda (ör. biri bu ay, biri geçen ay) birkaç harcama ekleyin.
2. Ana sayfadaki **📊 Aylık kategori özetini gör** bağlantısına tıklayın.
3. **Beklenen:** Seçili ay için her kategorinin adedi, toplam tutarı ve en altta **Genel Toplam** görünür.
4. Listeden başka bir ay seçip **Göster**'e basın.
5. **Beklenen:** Yalnızca o aya ait harcamalar listelenir; diğer aylar özete dahil edilmez.

### Ek özellikler

| Özellik | Nasıl denenir |
|---|---|
| **Harcama silme** — [#3](https://github.com/haktanisikersoy/ogrenci-harcama-takip/issues/3) | Listede bir harcamanın yanındaki **Sil** butonuna basıp onaylayın; kayıt listeden ve aylık özetten kalkar. |
| **Aylık bütçe limiti uyarısı** — [#4](https://github.com/haktanisikersoy/ogrenci-harcama-takip/issues/4) | Ana sayfada limite ör. `500` yazıp **Limiti Kaydet**'e basın. Bu ayki harcamalar limiti aşınca çubuk kırmızıya döner ve uyarı çıkar. |
| **Abonelik takibi** — [#12](https://github.com/haktanisikersoy/ogrenci-harcama-takip/issues/12) | **🔁 Aboneliklerim** sayfasında ödeme günü 2-3 gün sonrasına denk gelen bir abonelik ekleyin; 🔔 rozetiyle vurgulanır ve ana sayfada uyarı görünür. |
| **CI (GitHub Actions)** — [#5](https://github.com/haktanisikersoy/ogrenci-harcama-takip/issues/5) | Repodaki **Actions** sekmesinde her push/PR için lint ve test sonuçları görülür. |
| **Docker** — [#6](https://github.com/haktanisikersoy/ogrenci-harcama-takip/issues/6) | Yukarıdaki *Yöntem 2*. CI, her PR'da imajı oluşturup uygulamanın konteynerde açıldığını da kontrol eder. |

## Geliştirme Süreci
- Her görev panoda bir kart (issue) olarak tanımlandı ve kabul kriterleri yazıldı.
- Her görev ayrı bir branch'te (`feature/...`) geliştirildi ve Pull Request ile `main`'e birleştirildi. PR açıklamasındaki `Closes #N` ifadesi PR'ı ilgili karta bağlar.
- Kabul kriterleri doğrulandıktan sonra PR birleştirildi ve kart **Tamamlandı** sütununa taşındı.
- Her PR'da GitHub Actions; lint (ruff), testler (pytest) ve Docker imajı kontrollerini otomatik çalıştırır.

## Proje Yapısı
```
├── app.py                     # Flask uygulaması (sayfalar ve iş kuralları)
├── abonelik.py                # Abonelik ödeme tarihi hesaplamaları
├── templates/
│   ├── index.html             # Harcama ekleme, listeleme ve bütçe
│   ├── ozet.html              # Aylık kategori özeti
│   └── abonelikler.html       # Abonelik takibi
├── tests/                     # pytest testleri
├── .github/workflows/ci.yml   # GitHub Actions (lint, test, Docker)
├── Dockerfile
├── Makefile                   # make check, make docker-run vb.
├── pyproject.toml             # ruff ayarları
└── requirements.txt
```
