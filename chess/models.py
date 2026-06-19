from django.db import models
from django.contrib.auth.models import AbstractUser

# for password hashing django is using a hash + salt method so it is hard to break through even if there was a possible database leak
class User(AbstractUser):
    current_rating = models.IntegerField(default=1200)

    def update_rating(self, new_rating):
        self.current_rating = new_rating #update to the new rating
        self.save()

    def __str__(self):
        return self.username

class PlayerProfile(models.Model): #PROFILE checker
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    total_games = models.IntegerField(default=0)
    total_wins = models.IntegerField(default=0)
    total_losses = models.IntegerField(default=0)
    favourite_opening = models.CharField(max_length=100, blank=True)

    def update_stats(self, won, opening):
        self.total_games += 1
        if won:
            self.total_wins += 1
        else:
            self.total_losses += 1
        # update favourite opening if this one appears more than current favourite
        if opening and opening != 'Unknown Opening':
            self.favourite_opening = opening
        self.save()

    def __str__(self):
        return f"{self.user.username}'s profile"

class Game(models.Model):
    white_player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='white_games')
    black_player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='black_games')
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='won_games')
    opening_name = models.CharField(max_length=100, blank=True)
    date_played = models.DateTimeField(auto_now_add=True)
    move_history = models.TextField(blank=True)

    def __str__(self):
        return f"{self.white_player} vs {self.black_player}"

class Move(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='moves')
    move_number = models.IntegerField(default=0)
    from_square = models.CharField(max_length=2)
    to_square = models.CharField(max_length=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Move {self.move_number}: {self.from_square} to {self.to_square}"

class OpeningDatabase(models.Model):
    name = models.CharField(max_length=100)
    moves = models.TextField()

    def __str__(self):
        return self.name


