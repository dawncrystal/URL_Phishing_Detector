import requests
from urllib.parse import urlparse
from datetime import datetime
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

# Testing this funtion to see if it does what it needs to do


test_url = input("Enter a URL to expand: ")
result = expand_url(test_url)

if result:
    print(f"\nFinal URL: {result[-1]['url']}")
    print(f"Total redirects: {len(result) - 1}")
else:
    print("Opssss.....Failed to expand URL")
