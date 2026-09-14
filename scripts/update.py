import os
import re
from datetime import datetime, timezone
from urllib.parse import urlparse
import requests

# Takip edilecek kök domainler veya sabit yönlendirici servisler
# Bu adresler genellikle kullanıcıyı en güncel aynaya (mirror) yönlendirir
TRACKING_SEEDS = [
    "https://hdfilmcehennemi.life",
    "https://hdfilmcehennemi.net",
    "https://dizipal.com",
    "https://fullhdfilmizlesene.de",
    "https://filmmodu.org",
    "https://sezonlukdizi.vip",
]

OUTPUT_FILE = "blocklist.txt"
STATIC_FILE = "static_rules.txt"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

def resolve_domain(url):
    """Verilen URL'nin yönlendiği son nihai domain adını döndürür."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
        final_url = response.url
        domain = urlparse(final_url).netloc.lower()
        
        # 'www.' önekini kaldır
        if domain.startswith("www."):
            domain = domain[4:]
            
        # Geçerli bir alan adı formatında olup olmadığını kontrol et
        if domain and "." in domain and not domain.startswith("localhost"):
            return domain
    except Exception as e:
        print(f"[HATA] {url} çözümlenemedi: {e}")
    return None

def main():
    discovered_domains = set()

    print("Yönlendirmeler taranıyor...")
    for seed in TRACKING_SEEDS:
        domain = resolve_domain(seed)
        if domain:
            print(f"[BULUNDU] {seed} -> {domain}")
            discovered_domains.add(domain)

    # Statik kuralları oku
    static_rules = []
    if os.path.exists(STATIC_FILE):
        with open(STATIC_FILE, "r", encoding="utf-8") as f:
            static_rules = [line.strip() for line in f if line.strip()]

    # Dinamik kuralları AdGuard DNS formatına dönüştür: ||domain^
    dynamic_rules = [f"||{domain}^" for domain in sorted(discovered_domains)]

    # Tüm kuralları birleştir ve mükerrerleri kaldır (sıralamayı koruyarak)
    all_rules = list(dict.fromkeys(static_rules + dynamic_rules))

    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # AdGuard Header oluştur
    header = f"""!
! Title: Dynamic Pirate Video & Streaming DNS Blocklist
! Description: Auto-updated AdGuard DNS filter tracking illegal streaming sites & mirrors.
! Version: 1.0
! Last modified: {now_iso}
! Total Rules: {len(all_rules)}
!
"""

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(header)
        for rule in all_rules:
            f.write(f"{rule}\n")

    print(f"\nİşlem tamamlandı! Toplam {len(all_rules)} kural '{OUTPUT_FILE}' dosyasına yazıldı.")

if __name__ == "__main__":
    main()