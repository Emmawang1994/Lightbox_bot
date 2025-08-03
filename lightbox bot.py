# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import requests
import time
import os
import sys
import webbrowser
import random

COLLECTION_URL = 'https://lightboxjewelry.com/collections/lab-grown-loose-diamonds/products.json'
CHECK_INTERVAL = 5  # seconds
TEST_MODE = True  # Set True to test alert
SKIP_KEYWORDS = ['Round Brilliant']  # Don't alert for these

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; LightboxMonitor/1.0)'
}

def get_products_from_collection(page=1, retries=3):
    for attempt in range(retries):
        try:
            r = requests.get(f"{COLLECTION_URL}?page={page}", headers=HEADERS, timeout=10)
            if r.status_code != 200:
                print("\nRequest failed with", r.status_code)
                return []
            return r.json().get('products', [])
        except Exception as e:
            print(f"\nError fetching page (attempt {attempt + 1}):", e)
            time.sleep(2 ** attempt + random.uniform(0, 1))  # Exponential backoff
    return []

def variant_available(variant):
    return variant.get("available", False)

def play_sound():
    os.system('say "New diamond in stock"')  # macOS text-to-speech alert

def open_in_chrome(url):
    try:
        # macOS-specific Chrome path; change if needed
        chrome_path = 'open -a "Google Chrome" %s'
        webbrowser.get(chrome_path).open(url)
    except:
        webbrowser.open(url)  # Fallback to default browser

def monitor():
    page = 1
    matches = []
    while True:
        print("Checking TEST_MODE status...")  # Add this to confirm the loop is running

        products = get_products_from_collection(page)
        if not products:
            break
        for product in products:
            skip = any(keyword in product["title"] for keyword in SKIP_KEYWORDS)
            if skip:
                continue
            for variant in product.get("variants", []):
                if variant_available(variant):
                    matches.append({
                        "title": product["title"],
                        "url": f"https://lightboxjewelry.com/products/{product['handle']}?variant={variant['id']}",
                        "variant": variant["title"],
                        "id": variant["id"]
                    })
        page += 1
    return matches

seen_variant_ids = set()

while True:
    if TEST_MODE:
        results = [{
            "title": "Test Diamond",
            "url": "https://lightboxjewelry.com/products/fake-product?variant=123456789",
            "variant": "2 ct test",
            "id": 123456789
        }]
    else:
        results = monitor()

    for item in results:
        print("💎 STOCK FOUND!")
        print(f"-- {item['title']} ({item['variant']}): {item['url']}")
        play_sound()

        if item['id'] not in seen_variant_ids:
            seen_variant_ids.add(item['id'])
            open_in_chrome(item['url'])  # Only opens once per variant

    if not results:
        sys.stdout.write("\r⏳ No stock... Checking again soon. ")
        sys.stdout.flush()

    time.sleep(CHECK_INTERVAL)

