from django.contrib import admin
from .models import Match, Tournament, TournamentParticipant, SavedBracket, BracketMatch, TournamentResult


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'start_date', 'end_date', 'max_participants', 'created_by']
    list_filter = ['status', 'start_date', 'created_at']
    search_fields = ['name', 'description']
    date_hierarchy = 'start_date'


@admin.register(TournamentParticipant)
class TournamentParticipantAdmin(admin.ModelAdmin):
    list_display = ['player', 'tournament', 'seed_position', 'registration_date', 'is_active']
    list_filter = ['tournament', 'is_active', 'registration_date']
    search_fields = ['player__first_name', 'player__last_name', 'tournament__name']


@admin.register(SavedBracket)
class SavedBracketAdmin(admin.ModelAdmin):
    list_display = ['name', 'tournament', 'user', 'bracket_type', 'is_public', 'created_at']
    list_filter = ['bracket_type', 'is_public', 'tournament', 'created_at']
    search_fields = ['name', 'tournament__name', 'user__username']


@admin.register(BracketMatch)
class BracketMatchAdmin(admin.ModelAdmin):
    list_display = ['saved_bracket', 'round_number', 'match_number', 'team1_name', 'team2_name', 'winner_name']
    list_filter = ['round_number', 'saved_bracket__tournament', 'is_bye']
    search_fields = ['team1_name', 'team2_name', 'winner_name']


@admin.register(TournamentResult)
class TournamentResultAdmin(admin.ModelAdmin):
    list_display = ['tournament', 'saved_bracket', 'final_position', 'points_earned', 'prize_amount', 'is_final']
    list_filter = ['tournament', 'final_position', 'is_final']
    search_fields = ['tournament__name', 'saved_bracket__name']


admin.site.register(Match)