import requests
from urllib.parse import urlparse
from datetime import datetime
from difflib import SequenceMatcher
#import re


# This function is to expand the short urls
# It takes a  short url as a parameter


def expand_url(short_url):
    """Follow redirects to find the final destination URL"""
    print(f"[....] Expanding: {short_url}")

    history = []
    current_url = short_url
    redirect_count = 0
    max_redirects = 5

    # Headers to look like a real browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        while redirect_count < max_redirects:
            # Don't automatically follow redirects (Pausing a bit )
            response = requests.get(current_url, allow_redirects=False, timeout=10, headers=headers)

            # Save this step
            history.append({
                'url': current_url,
                'status': response.status_code
            })

            # Check if this is a redirect
            if response.status_code in [301, 302, 303, 307, 308]:
                next_url = response.headers.get('Location')

                if not next_url:
                    break

                # Handles the e relative redirects
                if not next_url.startswith('http'):
                    parsed = urlparse(current_url)
                    next_url = f"{parsed.scheme}://{parsed.netloc}{next_url}"

                current_url = next_url
                print(f"[....] Redirecting to: {current_url}")
                redirect_count += 1
            else:
                # Since there is  no more redirects, this is  the final destination
                # To verify .. This is to do a final GET to get the final status
                final_response = requests.get(current_url, timeout=10, headers=headers)
                history.append({
                    'url': current_url,
                    'status': final_response.status_code,
                    'final': True
                })
                break

        return history

    except requests.exceptions.RequestException as e:
        print(f"[--] Error: {e}")
        return history


def check_domain_reputation(domain):
    """Now ...checking  if domain looks suspicious"""
    domain_lower = domain.lower()

    # List of known URL shorteners (red flag)
    KNOWN_URL_SHORTENERS = {
        "bit.ly",
        "tinyurl.com",
        "t.co",
        "goo.gl",
        "ow.ly",
        "is.gd",
        "v.gd",
        "buff.ly",
        "adf.ly",
        "cutt.ly",
        "rebrand.ly",
        "shorturl.at",
        "t.ly",
        "tiny.cc",
        "lnkd.in",
        "rb.gy",
        "bl.ink",
        "soo.gd",
        "s2r.co",
        "shorte.st",
        "cli.re",
        "fur.ly",
        "mcaf.ee",
        "su.pr",
        "ity.im",
        "qr.ae",
        "trib.al",
        "amzn.to",
        "youtu.be",
        "ift.tt",
        "geni.us",
        "bit.do",
        "short.io",
        "cutt.us",
        "u.to",
        "x.co",
        "po.st",
        "smarturl.it",
        "linktr.ee",
    }
    for shortener in KNOWN_URL_SHORTENERS:
        if shortener in domain_lower:
            return 'WARNING', f"Uses URL shortener: {shortener}"

    # Check for typosquatting like instead of Google it is Go0gle and the others
    KNOWN_BRANDS = {
        "google", "gmail", "youtube", "microsoft", "windows", "office", "outlook", "apple", "icloud",
        "facebook", "instagram", "whatsapp", "messenger", "x", "twitter", "linkedin", "tiktok", "snapchat", "discord", "reddit",
        "amazon", "ebay", "walmart", "etsy", "aliexpress",
        "paypal", "stripe", "wise", "venmo", "cashapp", "zelle", "coinbase", "binance",
        "wellsfargo", "chase", "bankofamerica", "citibank", "capitalone", "hsbc", "barclays",
        "dropbox", "onedrive", "box", "zoom", "slack", "notion",
        "netflix", "spotify", "disney", "hulu",
        "fedex", "ups", "dhl", "usps",
        "norton", "mcafee",
        "github", "gitlab",
    }
    parsed = urlparse(domain if '://' in domain else f'http://{domain}')
    domain_name = parsed.netloc.lower()

    for brand in KNOWN_BRANDS:
        score = SequenceMatcher(None, domain_name, brand).ratio() * 100

        if score >= 85 and domain_name != brand:
            return (
                "DANGER",
                f"Possible typosquatting of '{brand}' "
                f"(similarity {int(score)}%)."
            )

    # Check for weird Top Level Domains
    parsed = urlparse(domain if '://' in domain else f'http://{domain}')
    tld = parsed.netloc.split('.')[-1]
    RISKY_TLDS = {
        "tk", "ml", "ga", "cf", "gq",
        "xyz", "top", "club", "online", "site", "website", "space", "click", "stream", "work", "live", "buzz",
        "win", "bid", "loan", "download", "party", "review", "trade", "science", "account", "support", "cam",
        "country", "men", "date", "racing", "cricket",
        "zip", "mov", "rest", "quest", "kim", "fit", "help", "monster", "link", "host", "pro", "info"}

    if tld in RISKY_TLDS:
        return 'CAUTION', f"Unusual TLD: .{tld} (this is usually used  in phishing)"

    return 'CLEAN', "No immediate red flags"

# Testing the domain reputation functiom


url = input("Enter a URL or domain: ").strip()
status, message = check_domain_reputation(url)

print("\n=== Result ===")
print(f"Status : {status}")
print(f"Reason : {message}")

# Testing this funtion to see if it does what it needs to do


test_url = input("Enter a URL to expand: ")
result = expand_url(test_url)

if result:
    print(f"\nFinal URL: {result[-1]['url']}")
    print(f"Total redirects: {len(result) - 1}")
else:
    print("Opssss.....Failed to expand URL")
