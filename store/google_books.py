import requests
import random
from decimal import Decimal
from django.conf import settings


GOOGLE_BOOKS_BASE = "https://www.googleapis.com/books/v1/volumes"

CATEGORY_QUERIES = {
    'Fiction': 'subject:fiction bestseller',
    'Science': 'subject:science technology',
    'Fantasy': 'subject:fantasy epic',
    'Mystery': 'subject:mystery thriller detective',
    'History': 'subject:history world',
    'Biography': 'subject:biography autobiography',
    'Self-Help': 'subject:self-help personal development',
    'Non-Fiction': 'subject:nonfiction popular',
}

PRICE_RANGES = {
    'Fiction': (199, 499),
    'Science': (299, 799),
    'Fantasy': (249, 599),
    'Mystery': (199, 449),
    'History': (299, 699),
    'Biography': (249, 549),
    'Self-Help': (199, 499),
    'Non-Fiction': (249, 599),
}


def fetch_books_from_google(query, max_results=20, start_index=0):
    """Fetch books from Google Books API."""
    params = {
        'q': query,
        'maxResults': min(max_results, 40),
        'startIndex': start_index,
        'printType': 'books',
        'langRestrict': 'en',
        'key': settings.GOOGLE_BOOKS_API_KEY,
    }
    try:
        response = requests.get(GOOGLE_BOOKS_BASE, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get('items', [])
    except requests.RequestException as e:
        print(f"Google Books API error: {e}")
        return []


def parse_book_data(item, category_name):
    """Parse a Google Books API item into a dict."""
    info = item.get('volumeInfo', {})
    img_links = info.get('imageLinks', {})

    # Get high-res cover
    cover_url = (
        img_links.get('extraLarge') or
        img_links.get('large') or
        img_links.get('medium') or
        img_links.get('thumbnail', '')
    )
    # Upgrade to HTTPS only — keep zoom=1 so edge=curl stays intact.
    # "edge=curl" in a Google Books URL proves it has a real scanned front cover.
    if cover_url:
        cover_url = cover_url.replace('http://', 'https://')

    price_min, price_max = PRICE_RANGES.get(category_name, (199, 499))
    price = Decimal(random.randint(price_min, price_max))
    original = price + Decimal(random.randint(50, 200)) if random.random() > 0.4 else None

    rating = round(random.uniform(3.5, 5.0), 1)

    authors = ', '.join(info.get('authors', ['Unknown Author']))

    return {
        'google_books_id': item.get('id'),
        'title': info.get('title', 'Untitled')[:300],
        'authors': authors[:300],
        'description': info.get('description', '')[:2000],
        'cover_image_url': cover_url,
        'price': price,
        'original_price': original,
        'rating': rating,
        'page_count': info.get('pageCount'),
        'published_date': info.get('publishedDate', ''),
        'publisher': info.get('publisher', '')[:200],
        'is_featured': random.random() > 0.7,
        'is_bestseller': random.random() > 0.8,
    }


def search_google_books(query, max_results=24):
    """Search books by any query string for the search page."""
    params = {
        'q': query,
        'maxResults': max_results,
        'printType': 'books',
        'langRestrict': 'en',
        'orderBy': 'relevance',
        'key': settings.GOOGLE_BOOKS_API_KEY,
    }
    try:
        response = requests.get(GOOGLE_BOOKS_BASE, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        items = data.get('items', [])
        results = []
        for item in items:
            info = item.get('volumeInfo', {})
            img_links = info.get('imageLinks', {})
            cover_url = img_links.get('thumbnail', '')
            if cover_url:
                cover_url = cover_url.replace('http://', 'https://')
            results.append({
                'id': item.get('id'),
                'title': info.get('title', 'Untitled')[:200],
                'authors': ', '.join(info.get('authors', ['Unknown'])),
                'cover': cover_url,
                'description': info.get('description', '')[:300],
                'category': info.get('categories', ['General'])[0] if info.get('categories') else 'General',
                'price': random.randint(199, 799),
                'rating': round(random.uniform(3.5, 5.0), 1),
                'info_link': info.get('infoLink', f'https://books.google.com/books?id={item.get("id", "")}'),
            })
        return results
    except Exception as e:
        print(f"Search error: {e}")
        return []
