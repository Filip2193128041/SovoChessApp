import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SovoChessApp.settings')
django.setup()

from chess.models import User, Game

users = [
    {'username': 'Magnus', 'rating': 2820},
    {'username': 'Hikaru', 'rating': 2800},
    {'username': 'Fabiano', 'rating': 2795},
    {'username': 'Wesley', 'rating': 2760},
    {'username': 'Hans', 'rating': 2750},
]

for u in users:
    user = User.objects.create_user(username=u['username'], password='chess1234')
    user.current_rating = u['rating']
    user.save()
    print(f"Created: {u['username']}")

print("Done!")