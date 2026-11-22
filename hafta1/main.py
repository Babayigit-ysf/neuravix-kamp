import argparse
from pathlib import Path
from gorev import (
    en_yakin_nokta,
    gorevleri_yukle,
    haversine,
    ozet_kaydet,
    rotayi_ciz,
)

def main():
    varsayilan_dosya = Path(__file__).parent / "kombinasyon_001.geojson"

    parser = argparse.ArgumentParser(
        description="GeoJSON görev noktalarını okur ve rota mesafelerini hesaplar."
    )
    parser.add_argument(
        "dosya",
        nargs="?",
        default=str(varsayilan_dosya),
        help="Okunacak GeoJSON dosyasının yolu",
    )
    args = parser.parse_args()

    noktalar = gorevleri_yukle(args.dosya)
    if not noktalar:
        return

    print("--- Görev Noktaları ---")
    for n in noktalar:
        print(n)

    print("\n--- Ardışık Mesafeler ---")
    toplam_mesafe = 0.0
    ardisik_mesafeler = []

    for i in range(len(noktalar) - 1):
        n1 = noktalar[i]
        n2 = noktalar[i + 1]
        mesafe = haversine(n1, n2)
        toplam_mesafe += mesafe
        print(f"{n1.ad} -> {n2.ad}: {mesafe:.2f} metre")

        ardisik_mesafeler.append({
            "baslangic": n1.ad,
            "bitis": n2.ad,
            "mesafe_metre": round(mesafe, 2),
        })

    print(f"\nToplam rota uzunluğu: {toplam_mesafe:.2f} metre")

    print("\n--- En Yakın Nokta Testi ---")
    test_enlem = noktalar[0].enlem + 0.0005
    test_boylam = noktalar[0].boylam + 0.0005

    yakin, yakin_mesafe = en_yakin_nokta(test_enlem, test_boylam, noktalar)
    print(f"Test konumuna en yakın nokta: {yakin.ad} ({yakin_mesafe:.2f} metre)")

    ozet_kaydet(noktalar, ardisik_mesafeler, toplam_mesafe)
    rotayi_ciz(noktalar)


if __name__ == "__main__":
    main()