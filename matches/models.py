from django.db import models

from players.models import Player


class Match(models.Model):
    class Meta:
        verbose_name_plural = "matches"
    team1player1 = models.ForeignKey(Player, related_name='matches_as_team1player1', on_delete=models.CASCADE)
    team1player2 = models.ForeignKey(Player, related_name='matches_as_team1player2', on_delete=models.CASCADE)
    team1_game_score = models.IntegerField(blank=True, null=True)
    team2player1 = models.ForeignKey(Player, related_name='matches_as_team2player1', on_delete=models.CASCADE)
    team2player2 = models.ForeignKey(Player, related_name='matches_as_team2player2', on_delete=models.CASCADE)
    team2_game_score = models.IntegerField(blank=True, null=True)
