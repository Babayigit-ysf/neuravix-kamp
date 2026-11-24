import json
import math
import matplotlib.pyplot as plt


class GorevNoktasi:
    def __init__(self, ad, aciklama, enlem, boylam):
        self.ad = ad
        self.aciklama = aciklama
        self.enlem = enlem
        self.boylam = boylam

    def __str__(self):
        return f"{self.ad} ({self.aciklama}) -> Enlem: {self.enlem}, Boylam: {self.boylam}"


def gorevleri_yukle(dosya_yolu):
    noktalar = []
    try:
        with open(dosya_yolu, "r", encoding="utf-8") as dosya:
            veri = json.load(dosya)
    except FileNotFoundError:
        print(f"Hata: '{dosya_yolu}' dosyası bulunamadı. Dosya yolunu kontrol et.")
        return []
    except json.JSONDecodeError:
        print(f"Hata: '{dosya_yolu}' geçerli bir JSON/GeoJSON dosyası değil.")
        return []

    for ozellik in veri.get("features", []):
        props = ozellik.get("properties", {})
        coords = ozellik.get("geometry", {}).get("coordinates", [])

        # GeoJSON'da sıra [boylam, enlem] şeklindedir
        boylam = coords[0]
        enlem = coords[1]

        ad = props.get("name","İsimsiz") 
        aciklama = props.get("description","-")

        noktalar.append(GorevNoktasi(ad, aciklama, enlem, boylam))

    return noktalar


def haversine(n1, n2):
    R = 6_371_000  # Dünya yarıçapı (metre)

    lat1 = math.radians(n1.enlem)
    lat2 = math.radians(n2.enlem)
    d_lat = math.radians(n2.enlem - n1.enlem)
    d_lon = math.radians(n2.boylam - n1.boylam)

    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(d_lon / 2) ** 2
    )
    d = 2 * R * math.asin(math.sqrt(a))
    return d


def en_yakin_nokta(enlem, boylam, noktalar):
    if not noktalar:
        return None, 0.0

    konum = GorevNoktasi("Mevcut Konum", "-", enlem, boylam)
    en_yakin = noktalar[0]
    en_kisa_mesafe = haversine(konum, noktalar[0])

    for nokta in noktalar[1:]:
        mesafe = haversine(konum, nokta)
        if mesafe < en_kisa_mesafe:
            en_kisa_mesafe = mesafe
            en_yakin = nokta

    return en_yakin, en_kisa_mesafe


def rotayi_ciz(noktalar):
    if not noktalar:
        return

    boylamlar = [n.boylam for n in noktalar]
    enlemler = [n.enlem for n in noktalar]

    plt.figure(figsize=(8, 6))
    plt.plot(boylamlar, enlemler, marker="o", linestyle="-", color="blue")

    for n in noktalar:
        plt.annotate(
            n.ad,
            (n.boylam, n.enlem),
            textcoords="offset points",
            xytext=(5, 5),
            fontsize=9,
        )

    plt.title("Görev Noktaları Rotası")
    plt.xlabel("Boylam")
    plt.ylabel("Enlem")
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def ozet_kaydet(noktalar, ardisik_mesafeler, toplam_mesafe, cikti_dosyasi="rota_ozeti.json"):
    ozet = {
        "nokta_sayisi": len(noktalar),
        "toplam_mesafe_metre": round(toplam_mesafe, 2),
        "noktalar": [
            {
                "ad": n.ad,
                "aciklama": n.aciklama,
                "enlem": n.enlem,
                "boylam": n.boylam,
            }
            for n in noktalar
        ],
        "ardisik_mesafeler": ardisik_mesafeler,
    }

    with open(cikti_dosyasi, "w", encoding="utf-8") as dosya:
        json.dump(ozet, dosya, ensure_ascii=False, indent=4)

    print(f"\nRota özeti '{cikti_dosyasi}' dosyasına kaydedildi.")