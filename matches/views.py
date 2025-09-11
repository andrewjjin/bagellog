from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import Tournament, TournamentParticipant, SavedBracket, BracketMatch
from .models import create_bracket_from_session_data, convert_bracket_to_session_data
from players.models import Player


def tournament_list(request):
    """Display a list of all tournaments"""
    tournaments = Tournament.objects.all()
    context = {
        'tournaments': tournaments,
        'user': request.user
    }
    return render(request, 'matches/tournament_list.html', context)


def tournament_detail(request, tournament_id):
    """Display tournament details and allow bracket creation"""
    tournament = get_object_or_404(Tournament, id=tournament_id)
    
    # Check if user has a saved bracket for this tournament
    user_bracket = None
    if request.user.is_authenticated:
        try:
            user_bracket = SavedBracket.objects.get(tournament=tournament, user=request.user)
        except SavedBracket.DoesNotExist:
            pass
    
    # Get participants
    participants = tournament.participants.filter(is_active=True)
    
    context = {
        'tournament': tournament,
        'participants': participants,
        'user_bracket': user_bracket,
        'can_register': tournament.can_user_register(request.user) if request.user.is_authenticated else False
    }
    return render(request, 'matches/tournament_detail.html', context)


@login_required
def create_tournament(request):
    """Create a new tournament"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        max_participants = request.POST.get('max_participants')
        entry_fee = request.POST.get('entry_fee', 0)
        prize_pool = request.POST.get('prize_pool', 0)
        
        try:
            tournament = Tournament.objects.create(
                name=name,
                description=description,
                start_date=start_date,
                end_date=end_date,
                max_participants=int(max_participants),
                entry_fee=float(entry_fee),
                prize_pool=float(prize_pool),
                created_by=request.user
            )
            messages.success(request, f'Tournament "{tournament.name}" created successfully!')
            return redirect('tournament_detail', tournament_id=tournament.id)
        except Exception as e:
            messages.error(request, f'Error creating tournament: {str(e)}')
    
    return render(request, 'matches/create_tournament.html')


@login_required
def register_tournament(request, tournament_id):
    """Register user for a tournament"""
    tournament = get_object_or_404(Tournament, id=tournament_id)
    
    if not tournament.can_user_register(request.user):
        messages.error(request, 'Cannot register for this tournament.')
        return redirect('tournament_detail', tournament_id=tournament_id)
    
    try:
        player = request.user.player
        TournamentParticipant.objects.create(
            tournament=tournament,
            player=player
        )
        messages.success(request, f'Successfully registered for "{tournament.name}"!')
    except Player.DoesNotExist:
        messages.error(request, 'You need to create a player profile first.')
    except Exception as e:
        messages.error(request, f'Registration failed: {str(e)}')
    
    return redirect('tournament_detail', tournament_id=tournament_id)


@login_required
def save_bracket(request, tournament_id):
    """Save user's bracket for a tournament"""
    tournament = get_object_or_404(Tournament, id=tournament_id)
    
    if request.method == 'POST':
        bracket_name = request.POST.get('bracket_name', 'My Bracket')
        bracket_data = request.session.get('bracket_data', [])
        
        if not bracket_data:
            messages.error(request, 'No bracket data to save.')
            return redirect('brackets_view')
        
        try:
            # Delete existing bracket if it exists
            SavedBracket.objects.filter(tournament=tournament, user=request.user).delete()
            
            # Create new bracket
            saved_bracket = create_bracket_from_session_data(
                tournament=tournament,
                user=request.user,
                bracket_data=bracket_data,
                bracket_name=bracket_name
            )
            
            messages.success(request, f'Bracket "{saved_bracket.name}" saved successfully!')
            return redirect('tournament_detail', tournament_id=tournament_id)
            
        except Exception as e:
            messages.error(request, f'Error saving bracket: {str(e)}')
    
    return redirect('brackets_view')


@login_required
def load_bracket(request, tournament_id):
    """Load user's saved bracket into session"""
    tournament = get_object_or_404(Tournament, id=tournament_id)
    
    try:
        saved_bracket = SavedBracket.objects.get(tournament=tournament, user=request.user)
        bracket_data = convert_bracket_to_session_data(saved_bracket)
        
        # Store in session
        request.session['bracket_data'] = bracket_data
        request.session['num_participants'] = tournament.participant_count
        request.session['total_slots'] = len(bracket_data[0]) if bracket_data else 0
        
        messages.success(request, f'Bracket "{saved_bracket.name}" loaded successfully!')
        return redirect('brackets_view')
        
    except SavedBracket.DoesNotExist:
        messages.error(request, 'No saved bracket found for this tournament.')
        return redirect('tournament_detail', tournament_id=tournament_id)


@login_required
def user_brackets(request):
    """Display user's saved brackets"""
    brackets = SavedBracket.objects.filter(user=request.user).select_related('tournament')
    context = {
        'brackets': brackets
    }
    return render(request, 'matches/user_brackets.html', context)


@require_http_methods(["GET"])
def tournament_participants_api(request, tournament_id):
    """API endpoint to get tournament participants"""
    tournament = get_object_or_404(Tournament, id=tournament_id)
    participants = tournament.participants.filter(is_active=True).select_related('player')
    
    data = []
    for participant in participants:
        data.append({
            'id': participant.player.id,
            'name': f"{participant.player.first_name} {participant.player.last_name}",
            'seed_position': participant.seed_position
        })
    
    return JsonResponse({'participants': data})