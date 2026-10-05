# HTTP kanıt modeli — 5 Ekim 2026

Reflected form/link, header, stored, stored-auto ve flow yanıtları ortak
`_finding()` üreticisini ve Content-Type sınıflandırmasını kullanır.
Ham marker veya `-breakout` varyant adı JavaScript çalışmasını ya da bağlamdan
çıkmayı ispatlamaz. HTML bağlamı tahmini ayrıca korunur.

| Gözlem | `severity` alanındaki sınıflandırma | Kanıt |
|---|---|---|
| HTML/XHTML/SVG yanıtında ham marker | `html-reflection` | `reflection` |
| Markup yanıtında yalnız tırnak gözlemi | `attribute-reflection` | `reflection` |
| JSON veya `+json` yanıtındaki yansıma | `json-only` | `reflection` |
| Bildirilmiş diğer Content-Type içindeki yansıma | `non-html-reflection` | `reflection` |
| Content-Type eksik | `unknown-type-reflection` | `reflection` |
| Flow'da marker yok/encoded | `-` | `candidate` |
| Eşleşen blind ağ isteği | `resource-callback` | `resource-callback` |

`severity` tarihsel alan adıdır; değerler CVSS veya açıklık etkisi değildir.
`confidence` yansıma gözleminin sinyalidir, açıklık doğrulama güveni değildir.
Eksik Content-Type'tan MIME sniffing sonucu çıkarılmaz. JSON/text daha sonra
başka bir DOM sink'ine taşınabilir; burada yalnız alınan HTTP yanıtı sınıflandırılır.

## Ortak alanlar ve çıktı

HTTP finding'leri `schema_version=1`, rastgele `finding_id`, `canary_id`, URL,
method/param, variant, context, content_type, reflection, evidence_level,
`triage=unreviewed`, `session_role=unspecified` taşır. Kimlik aynı sonuç nesnesinin
HTML/JSON eşleştirmesi içindir; tekrar taramalar arasında sabit değildir.
Stored kayıtta gönderim hedefi/yöntemi ve okuma URL'si/kodu ayrıca bulunur.

Mevcut HTTP tarama komutuna şu seçenekler eklenebilir:

```console
--json-out .dxa/findings.json --html .dxa/findings.html
```

Çıktı klasörünü önceden oluştur. JSON zarfı `schema_version`, `mode`, `findings`,
`events`, `meta` ve `skipped_submits` sayacını içerir. İki çıktı aynı finding listesini
kullanır; HTML'de finding/attempt kimliği gösterilir. Flow'un auth/vars sözlüğü
JSON raporuna kopyalanmaz. Ortak exporter bilinen header/cookie alanlarını ve
URL kullanıcı/query/fragment değerlerini maskeler. Path/rol/operatör verisi yine
hassas olabilir; paylaşım kopyası ayrıca incelenmelidir.

## Uyumluluk ve kalan iş

- Yeni HTTP sonuçlarında `executable`, `breakout-req`, `attr-breakout` üretilmez.
  Bu etiketleri okuyan tüketiciler yeni gözlem sınıflarına geçmelidir.
- Eski arşiv HTML'leri değiştirilmedi. Tarihsel etiketler güncel proof değildir.
- `context_executes()` eski çağıranlar için kalan bağlam sezgisidir;
  artık sınıflandırmada kullanılmaz ve kanıt fonksiyonu değildir.
- Statik/DOM/journal adapter'ları da [R1 sözleşmesini](EVIDENCE-CONTRACT.md) kullanır.
- Rol etiketi doğrulanmış kimlik değildir; farklı veya bilinmeyen sink/rol birleştirilmez.
- `events` hata/atlama/info kayıtlarını ayrı taşır. İstek ve auth davranışını düzeltmek R2'dir.
- Flow CLI'nin 0 dönüş kodu açıklık kanıtlamaz; mevcut komut davranışı korundu.

## Tekrar doğrulama

```console
python -m pytest tools/dom-xss-analyzer/test_http_evidence.py -q
```

Yedi Content-Type örneği beş HTTP yolunda karşılaştırılır. Yanlış bağlamda kalan
üç ham breakout marker'ı execution sayılmaz. Ayrı CLI sürecindeki yerel JSON
echo fixture'ı console/JSON/HTML tutarlılığını kontrol eder. Bunlar browser
execution testleri değildir; gerçek execution doğrulaması R3'te açık kalır.
