# Tournament and Bracket Management System

This Django application now includes a comprehensive tournament and bracket management system that allows users to create tournaments, register participants, and save their bracket predictions.

## Features

### 🏆 Tournament Management
- Create tournaments with custom details (name, dates, participants, prizes)
- Tournament status tracking (upcoming, active, completed, cancelled)
- Participant registration and management
- Entry fees and prize pool management

### 📊 Bracket System
- Save bracket predictions tied to specific tournaments
- Support for single elimination tournaments
- Track match results and winners
- Bracket completion percentage tracking
- Public/private bracket visibility

### 👥 User Management
- User authentication required for bracket saving
- One bracket per user per tournament
- Player profiles linked to Django User model

## Models Overview

### Tournament
- **Purpose**: Represents a tournament with all its details
- **Key Fields**: name, description, start_date, end_date, max_participants, entry_fee, prize_pool, status
- **Relationships**: Created by User, has many Participants and SavedBrackets

### TournamentParticipant
- **Purpose**: Links players to tournaments
- **Key Fields**: tournament, player, seed_position, registration_date
- **Relationships**: Belongs to Tournament and Player

### SavedBracket
- **Purpose**: Stores user's bracket predictions for a tournament
- **Key Fields**: tournament, user, name, bracket_type, is_public
- **Relationships**: Belongs to Tournament and User, has many BracketMatches

### BracketMatch
- **Purpose**: Individual matches within a bracket
- **Key Fields**: round_number, match_number, team1/team2 names/players, scores, winner
- **Relationships**: Belongs to SavedBracket

### TournamentResult
- **Purpose**: Final results and standings for tournaments
- **Key Fields**: final_position, points_earned, prize_amount
- **Relationships**: Links Tournament and SavedBracket

## Usage Examples

### 1. Creating a Tournament

```python
from matches.models import Tournament
from django.contrib.auth.models import User

# Create a tournament
tournament = Tournament.objects.create(
    name="Spring Championship 2024",
    description="Annual spring tournament",
    start_date=timezone.now() + timedelta(days=7),
    end_date=timezone.now() + timedelta(days=10),
    max_participants=16,
    entry_fee=25.00,
    prize_pool=500.00,
    created_by=user
)
```

### 2. Registering Participants

```python
from matches.models import TournamentParticipant

# Register a player for a tournament
participant = TournamentParticipant.objects.create(
    tournament=tournament,
    player=player,
    seed_position=1
)
```

### 3. Saving a Bracket

```python
from matches.models import create_bracket_from_session_data

# Convert session bracket data to saved bracket
saved_bracket = create_bracket_from_session_data(
    tournament=tournament,
    user=user,
    bracket_data=session_bracket_data,
    bracket_name="My Championship Bracket"
)
```

### 4. Loading a Bracket

```python
from matches.models import convert_bracket_to_session_data

# Convert saved bracket back to session format
bracket_data = convert_bracket_to_session_data(saved_bracket)
```

## URL Patterns

- `/matches/tournaments/` - List all tournaments
- `/matches/tournaments/create/` - Create new tournament
- `/matches/tournaments/<id>/` - Tournament details
- `/matches/tournaments/<id>/register/` - Register for tournament
- `/matches/tournaments/<id>/save-bracket/` - Save bracket to tournament
- `/matches/tournaments/<id>/load-bracket/` - Load saved bracket
- `/matches/my-brackets/` - User's saved brackets

## Integration with Existing Bracket System

The new tournament system integrates seamlessly with your existing bracket generation:

1. **Generate Bracket**: Use the existing `/brackets/` page to create brackets
2. **Save to Tournament**: Select a tournament and save your bracket
3. **Load Bracket**: Load saved brackets back into the bracket editor
4. **Track Progress**: View completion percentage and match results

## Admin Interface

All models are registered in Django admin with custom configurations:
- Tournament management with filtering and search
- Participant management with tournament filtering
- Bracket management with user and tournament filtering
- Match management with round and tournament filtering

## Helper Methods

### Tournament Methods
- `participant_count` - Number of registered participants
- `spots_remaining` - Available spots
- `is_full` - Check if tournament is full
- `is_registration_open` - Check if registration is still open
- `can_user_register(user)` - Check if user can register

### SavedBracket Methods
- `match_count` - Total number of matches
- `completed_matches` - Number of completed matches
- `completion_percentage` - Percentage of matches completed
- `is_complete` - Check if bracket is complete
- `get_rounds()` - Get matches organized by rounds
- `get_final_winner()` - Get the final winner

### BracketMatch Methods
- `team1_display_name` - Display name for team 1
- `team2_display_name` - Display name for team 2
- `winner_display_name` - Display name for winner
- `is_completed` - Check if match is completed
- `has_scores` - Check if match has scores
- `set_winner()` - Set the winner of the match

## Database Migrations

The system includes migrations for all new models:
- `0004_tournament_savedbracket_tournamentresult_and_more.py`

Run migrations with:
```bash
python manage.py migrate
```

## Next Steps

1. **Create Tournaments**: Use the admin interface or create tournament form
2. **Register Players**: Players can register for tournaments
3. **Generate Brackets**: Use the existing bracket generator
4. **Save Brackets**: Save brackets to specific tournaments
5. **Track Results**: Monitor tournament progress and results

The system is now ready for tournament management and bracket saving functionality!
