from django.db import models
from django.contrib.auth.models import User
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


class Tournament(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    max_participants = models.PositiveIntegerField()
    entry_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    prize_pool = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(
        max_length=20,
        choices=[
            ('upcoming', 'Upcoming'),
            ('active', 'Active'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled')
        ],
        default='upcoming'
    )
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tournaments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def participant_count(self):
        """Return the number of registered participants"""
        return self.participants.filter(is_active=True).count()
    
    @property
    def spots_remaining(self):
        """Return the number of spots remaining"""
        return self.max_participants - self.participant_count
    
    @property
    def is_full(self):
        """Check if tournament is full"""
        return self.participant_count >= self.max_participants
    
    @property
    def is_registration_open(self):
        """Check if registration is still open"""
        from django.utils import timezone
        return self.status == 'upcoming' and not self.is_full
    
    def can_user_register(self, user):
        """Check if a user can register for this tournament"""
        if not self.is_registration_open:
            return False
        # Check if user already has a player profile
        try:
            player = user.player
            # Check if player is already registered
            return not self.participants.filter(player=player, is_active=True).exists()
        except:
            return False


class TournamentParticipant(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='participants')
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='tournament_participations')
    registration_date = models.DateTimeField(auto_now_add=True)
    seed_position = models.PositiveIntegerField(null=True, blank=True)  # For bracket seeding
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['tournament', 'player']
    
    def __str__(self):
        return f"{self.player.first_name} {self.player.last_name} - {self.tournament.name}"


class SavedBracket(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='saved_brackets')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_brackets')
    name = models.CharField(max_length=200, default="My Bracket")
    bracket_type = models.CharField(
        max_length=20,
        choices=[
            ('single_elimination', 'Single Elimination'),
            ('double_elimination', 'Double Elimination'),
            ('round_robin', 'Round Robin')
        ],
        default='single_elimination'
    )
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['tournament', 'user']  # One bracket per user per tournament
    
    def __str__(self):
        return f"{self.name} - {self.tournament.name}"
    
    @property
    def match_count(self):
        """Return the total number of matches in this bracket"""
        return self.matches.count()
    
    @property
    def completed_matches(self):
        """Return the number of completed matches"""
        return self.matches.exclude(winner__isnull=True).exclude(winner_name__isnull=True).exclude(winner_name='').count()
    
    @property
    def completion_percentage(self):
        """Return the percentage of matches completed"""
        if self.match_count == 0:
            return 0
        return (self.completed_matches / self.match_count) * 100
    
    @property
    def is_complete(self):
        """Check if the bracket is complete"""
        return self.completed_matches == self.match_count
    
    def get_rounds(self):
        """Return matches organized by rounds"""
        rounds = {}
        for match in self.matches.all():
            if match.round_number not in rounds:
                rounds[match.round_number] = []
            rounds[match.round_number].append(match)
        return rounds
    
    def get_final_winner(self):
        """Get the final winner of the bracket"""
        final_round = self.matches.filter(round_number=self.matches.aggregate(max_round=models.Max('round_number'))['max_round']).first()
        if final_round:
            return final_round.winner or final_round.winner_name
        return None


class BracketMatch(models.Model):
    saved_bracket = models.ForeignKey(SavedBracket, on_delete=models.CASCADE, related_name='matches')
    round_number = models.PositiveIntegerField()
    match_number = models.PositiveIntegerField()  # Position within the round
    team1_player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='bracket_matches_team1', null=True, blank=True)
    team2_player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='bracket_matches_team2', null=True, blank=True)
    team1_name = models.CharField(max_length=200, blank=True)  # For custom team names
    team2_name = models.CharField(max_length=200, blank=True)
    team1_score = models.PositiveIntegerField(null=True, blank=True)
    team2_score = models.PositiveIntegerField(null=True, blank=True)
    winner = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='bracket_match_wins', null=True, blank=True)
    winner_name = models.CharField(max_length=200, blank=True)  # For custom team names
    is_bye = models.BooleanField(default=False)
    match_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['saved_bracket', 'round_number', 'match_number']
        ordering = ['round_number', 'match_number']
    
    def __str__(self):
        team1 = self.team1_name or (f"{self.team1_player.first_name} {self.team1_player.last_name}" if self.team1_player else "TBD")
        team2 = self.team2_name or (f"{self.team2_player.first_name} {self.team2_player.last_name}" if self.team2_player else "TBD")
        return f"Round {self.round_number}, Match {self.match_number}: {team1} vs {team2}"
    
    @property
    def team1_display_name(self):
        """Get the display name for team 1"""
        if self.team1_name:
            return self.team1_name
        elif self.team1_player:
            return f"{self.team1_player.first_name} {self.team1_player.last_name}"
        return "TBD"
    
    @property
    def team2_display_name(self):
        """Get the display name for team 2"""
        if self.team2_name:
            return self.team2_name
        elif self.team2_player:
            return f"{self.team2_player.first_name} {self.team2_player.last_name}"
        return "TBD"
    
    @property
    def winner_display_name(self):
        """Get the display name for the winner"""
        if self.winner_name:
            return self.winner_name
        elif self.winner:
            return f"{self.winner.first_name} {self.winner.last_name}"
        return None
    
    @property
    def is_completed(self):
        """Check if the match is completed"""
        return bool(self.winner or self.winner_name)
    
    @property
    def has_scores(self):
        """Check if the match has scores"""
        return self.team1_score is not None and self.team2_score is not None
    
    def set_winner(self, winner_player=None, winner_name=None):
        """Set the winner of the match"""
        if winner_player:
            self.winner = winner_player
            self.winner_name = ""
        elif winner_name:
            self.winner_name = winner_name
            self.winner = None
        self.save()


class TournamentResult(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='results')
    saved_bracket = models.ForeignKey(SavedBracket, on_delete=models.CASCADE, related_name='tournament_result')
    final_position = models.PositiveIntegerField()  # 1st, 2nd, 3rd, etc.
    points_earned = models.PositiveIntegerField(default=0)
    prize_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_final = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['tournament', 'saved_bracket']
    
    def __str__(self):
        return f"{self.tournament.name} - {self.saved_bracket.name} - Position {self.final_position}"


# Utility functions for bracket management
def create_bracket_from_session_data(tournament, user, bracket_data, bracket_name="My Bracket"):
    """
    Create a SavedBracket and BracketMatch objects from session bracket data
    """
    # Create the saved bracket
    saved_bracket = SavedBracket.objects.create(
        tournament=tournament,
        user=user,
        name=bracket_name,
        bracket_type='single_elimination'
    )
    
    # Create matches from bracket data
    for round_idx, round_matches in enumerate(bracket_data):
        for match_idx, match_data in enumerate(round_matches):
            BracketMatch.objects.create(
                saved_bracket=saved_bracket,
                round_number=round_idx,
                match_number=match_idx,
                team1_name=match_data.get('team1', ''),
                team2_name=match_data.get('team2', ''),
                team1_score=match_data.get('score1'),
                team2_score=match_data.get('score2'),
                winner_name=match_data.get('winner', ''),
                is_bye=match_data.get('team1') == 'BYE' or match_data.get('team2') == 'BYE'
            )
    
    return saved_bracket


def convert_bracket_to_session_data(saved_bracket):
    """
    Convert a SavedBracket back to session data format for compatibility
    """
    bracket_data = []
    rounds = saved_bracket.get_rounds()
    
    for round_num in sorted(rounds.keys()):
        round_matches = []
        for match in rounds[round_num]:
            match_data = {
                'team1': match.team1_display_name,
                'team2': match.team2_display_name,
                'score1': match.team1_score,
                'score2': match.team2_score,
                'winner': match.winner_display_name,
                'match_id': f"match_{round_num}_{match.match_number}"
            }
            round_matches.append(match_data)
        bracket_data.append(round_matches)
    
    return bracket_data
