from django.core.management.base import BaseCommand
from store.models import Category, Book
from store.google_books import fetch_books_from_google, parse_book_data, CATEGORY_QUERIES


CATEGORIES_CONFIG = [
    {'name': 'Fiction', 'icon': '📖', 'tag_line': 'STORIES UNBOUND', 'order': 1},
    {'name': 'Science', 'icon': '🔬', 'tag_line': 'BEYOND LIMITS', 'order': 2},
    {'name': 'Fantasy', 'icon': '🧝', 'tag_line': 'REALMS REBORN', 'order': 3},
    {'name': 'Mystery', 'icon': '🕵️', 'tag_line': 'DARK SECRETS', 'order': 4},
    {'name': 'History', 'icon': '🏛️', 'tag_line': 'PAST ECHOES', 'order': 5},
    {'name': 'Biography', 'icon': '👤', 'tag_line': 'TIMELESS LIVES', 'order': 6},
    {'name': 'Self-Help', 'icon': '🌟', 'tag_line': 'RISE HIGHER', 'order': 7},
    {'name': 'Non-Fiction', 'icon': '📰', 'tag_line': 'REAL STORIES', 'order': 8},
]


class Command(BaseCommand):
    help = 'Seed categories and fetch books from Google Books API'

    def add_arguments(self, parser):
        parser.add_argument('--books', type=int, default=10, help='Books per category (max 40)')
        parser.add_argument('--clear', action='store_true', help='Clear existing books first')

    def handle(self, *args, **options):
        books_per_cat = min(options['books'], 40)

        if options['clear']:
            self.stdout.write('Clearing existing books...')
            Book.objects.all().delete()

        # Create categories
        self.stdout.write('Creating categories...')
        for cfg in CATEGORIES_CONFIG:
            cat, created = Category.objects.get_or_create(
                name=cfg['name'],
                defaults={
                    'icon': cfg['icon'],
                    'tag_line': cfg['tag_line'],
                    'order': cfg['order'],
                }
            )
            if created:
                self.stdout.write(f'  ✓ Created category: {cat.name}')

        # Fetch books per category
        total_created = 0
        for cat_config in CATEGORIES_CONFIG:
            category = Category.objects.get(name=cat_config['name'])
            query = CATEGORY_QUERIES.get(cat_config['name'], cat_config['name'])
            self.stdout.write(f'\nFetching {books_per_cat} books for {category.name}...')

            items = fetch_books_from_google(query, max_results=books_per_cat)
            created_count = 0

            for item in items:
                book_data = parse_book_data(item, category.name)
                gb_id = book_data.get('google_books_id')

                if not gb_id:
                    continue

                if Book.objects.filter(google_books_id=gb_id).exists():
                    continue

                book_data['category'] = category
                try:
                    Book.objects.create(**book_data)
                    created_count += 1
                    total_created += 1
                except Exception as e:
                    self.stdout.write(f'  ⚠ Error saving book: {e}')

            self.stdout.write(f'  ✓ Added {created_count} books to {category.name}')

        self.stdout.write(self.style.SUCCESS(f'\n✅ Done! Total books created: {total_created}'))
