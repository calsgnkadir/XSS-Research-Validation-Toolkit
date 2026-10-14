# R5/K01 — yeni venv ile yerel tekrar (14 Ekim 2026)

Bu kayıt yalnız projenin kendi, her kontrolde yeni 127.0.0.1 portunda çalışan disposable K01 fixture'ına aittir. Başlangıç kaynak commit'i fed161026d4272468b856f309801b866144a2f0f. Çalışma ağacındaki K01 kodu bu commit'in Git blob baytlarıyla birebir eşleşti. Diğer agent'ların benchmark dosyalarındaki eşzamanlı değişiklikler bu koşuya girmedi.

## Kurulum ve komut

Yeni .dxa/r5-k01-venv-20261014-a Python 3.10.11 venv'i oluşturuldu. cases/k01-stored-comment/requirements-proof.txt içindeki sabit playwright==1.63.0, pip önbelleğinden bu venv'e yüklendi. Kurulu Chrome 155.0.8059.79 kullanıldı; yeni browser indirmesi yapılmadı. Platform Windows.

    py -3.10 -m venv .dxa/r5-k01-venv-20261014-a
    .dxa\r5-k01-venv-20261014-a\Scripts\python.exe -m pip install -r cases/k01-stored-comment/requirements-proof.txt
    .dxa\r5-k01-venv-20261014-a\Scripts\python.exe cases/k01-stored-comment/prove.py --browser "C:\Program Files\Google\Chrome\Application\chrome.exe" --output .dxa/r5-k01-proof-20261014-a

Çıktı dizini koşu öncesi yoktu. CLI exit 0 ve **5/5** kontrol bildirdi. Bağımsız çıktı incelemesi beş farklı loopback fixture portunun koşudan sonra bağlantı kabul etmediğini, her vakada tam bir POST olduğunu, aynı CID/payload'ın kullanıldığını, kaynak hashlerini ve fix diff'ini doğruladı. [Makine kabulü](acceptance.json) kaynak ve 12 kanıt üyesinin SHA-256 değerlerini içerir.

## Gözlem

| Kontrol | Beklenen CID execution | Gözlenen | HTTP bot kanıtı |
|---|---:|---:|---|
| Ham HTML, JS açık | Evet | Evet | Reflection |
| Ham HTML, JS kapalı | Hayır | Hayır | Reflection |
| HTML escaping sonrası aynı payload | Hayır | Hayır | Candidate |
| JSON-only yanıt | Hayır | Hayır | JSON-only reflection |
| Normal uygulama dialog'u | Hayır | Hayır | Candidate |

[Proof klasöründe](proof/result.json) tam sentetik request/response, vaka JSON'u ve [fix diff](proof/fix.diff) bulunur. Dosyalar paylaşım öncesi yerel kullanıcı yolu ve credential dizgileri açısından denetlendi; yalnız rastgele test CID'si ve geçici loopback portları taşır. Browser gözlemi vaka özeldir. Botun HTTP bulguları execution-confirmed yapılmadı.

Bu, **aynı Windows makinesinde yeni Python ortamıyla** yapılan tekrardır. Bağımsız ikinci kişi veya farklı işletim sistemi kabulü yapılmadı. Ayrı doğrulanmış kullanıcı rolleri ve gerçek ürün/CVE iddiası yoktur. Negatif browser penceresi yalnız bu senkron fixture'ın 500 ms gözlem süresidir. R5 genel “başka biri temiz ortamda” maddesi bu tek kayıtla kapatılmamalıdır.

Paylaşılan proof/fix.diff, renderer kaynaklarının birebir diff çıktısıdır;
boş bağlam satırlarında kaynak diff formatının son boşluğu vardır. Varsayılan
git diff --check yalnız bu iki satırı işaretler; hashli fixture kanıtı
değiştirilmedi.
