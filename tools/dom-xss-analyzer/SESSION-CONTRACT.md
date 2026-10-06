# R2 — HTTP oturum ve gönderim sözleşmesi

6 Ekim 2026. HTTP prototipi için R2 kabulü; browser'a oturum aktarımı R3'te.

## Hedefe özel oturum kontrolü

Login yanıtı/cookie/header kurulumu tek başına kullanıcı veya rol kanıtı değildir.
`--auth-check check.json`, mevcut HTTP oturumuyla bir GET yapar; HTTP 200,
JSON Content-Type ve her beklenen JSONPath değerinin türüyle birlikte eşleşmesini
ister. Login HTML'i, 401/403, eksik alan veya yanlış hesap/rol taramayı exit 2
ile durdurur. Auth-flow, form login, manuel cookie veya header ile kullanılabilir.

Örnek (yalnız yetkili yerel lab adresini kullan):

```json
{"url":"http://127.0.0.1:8080/api/me","expect":{"$.user":"alice","$.role":"reader"}}
```

```console
python dxadyn.py http://127.0.0.1:8080/search?q=test --auth-flow login.json --auth-check check.json --session-role reader --json-out result.json --html result.html
```

JSON/HTML meta'da `session_check=passed|failed|not-requested` ve operatörün
`session_role` etiketi yer alır. Beklenen/gerçek hesap değerleri rapora yazılmaz.
Kontrol dosyası hedefe özel hazırlanır: anonim bir endpoint'in daima aynı
JSON'u vermesi yanlış bir sözleşme olabilir. Bu özellik genel yetki analizi
veya privilege escalation kanıtı üretmez; R1 `role_verified` alanı false kalır.
Kontrol taramadan önce bir kez yapılır; sonradan sona eren oturum 401/403
olaylarıyla görünür, otomatik yeniden login yapılmaz. Ayrı süreçte oturum korunmaz.
`--dom --auth-check` reddedilir; doğrulanmış HTTP oturumu browser'a aktarılmış sayılmaz.

## Rate, CSRF ve eşzamanlılık

`--rate 0` sınırsızdır; negatif/NaN/infinity reddedilir. Pozitif fractional
rate desteklenir: 0.5/s bir ilk isteğe izin verir, sonra token başına 2 saniye.
Kapasite max(1, rate), sürekli refill; kayan bir saniyelik mutlak kota değildir.

Bir süreçte tek opener/cookie jar bulunduğundan HTTP işlemleri yeniden girişli
oturum kilidiyle sıralanır. `--parallel` işleri kuyruğa alabilir ama HTTP hız
artışı sağlamaz. Form token fetch+submit, header refresh+submit, auth/flow
adımları ve stored submit+read aynı oturumda birbirine giremez. Stored-auto
her canary için submit→crawl tamamlar; sonra sıradakini gönderir. Sayfa
sayaçları canary başına toplamdır; eski toplu crawl'a göre daha fazla GET yapar.

`--csrf-refresh URL --csrf-header NAME` HTTP fetch ve flow gönderimlerinde
her yazma öncesi token yeniler; token yoksa/refresh başarısızsa yazma yapılmaz.
Stored form `--csrf-field NAME` ile tek kullanımlık alanı alır; token yoksa
göndermez. CSRF'siz form için açıkça `--csrf-field ""` kullanılır. Form ve
header CSRF aynı stored formda birlikte seçilemez; header için form alanını
devre dışı bırak. Farklı field/header token çiftleri henüz desteklenmez.

Zaman aşımı/bağlantı hatası, 401/403 engellemesi, 429 ve 5xx ortak raporda
error/skip olaylarıdır; boş findings bu olayları silmez. Token değerleri
auth-check hatalarında yer almaz. Genel origin/redirect sınırı, proxy ve
callback işletimi R9'dadır; bu kapanış onların tamamlandığı iddiası değildir.

## Zorunlu regresyonlar

`test_auth_guards.py`, `test_r2_contract.py`, mevcut JSON/CSRF/flow testleri
ve R1 negatif örnekleri ana test paketindedir. CI'da R1/R2 negatif kontrol
adımı ayrıca zorunludur; continue-on-error kullanmaz. Gerçek CI çalışmasının
başarısı yerel test sonucuyla karıştırılmaz. Kabul matrisi:
[R2 kapanışı](../../audit/2026-10-06-r2/R2-KAPANIS.md).
