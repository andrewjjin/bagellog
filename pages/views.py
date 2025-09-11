from django.shortcuts import render
import math

# Create your views here.
def home_view(request, *args, **kwargs):
    print("user: ", request.user)
    return render(request, "home.html", {})

def devils_discount_view(request):
    """View for the devils-discount page with file upload"""
    return render(request, "devils_discount.html", {})

def medical_bill_view(request):
    """View for displaying the fake medical bill with dynamic discount"""
    # Handle discount reset
    if request.GET.get('reset_discount'):
        request.session['discount_percentage'] = 75
        return render(request, "medical_bill.html", get_bill_context(request))
    
    # Initialize or decrease discount
    if 'discount_percentage' not in request.session:
        # First visit - set to 75%
        request.session['discount_percentage'] = 75
    else:
        # Subsequent visits - decrease by 10% until 0%
        current_discount = request.session['discount_percentage']
        if current_discount > 0:
            request.session['discount_percentage'] = max(0, current_discount - 10)
    
    return render(request, "medical_bill.html", get_bill_context(request))

def get_bill_context(request):
    """Helper function to prepare bill context with discount calculations"""
    original_amount = 578.62
    discount_percentage = request.session.get('discount_percentage', 0)
    discount_amount = original_amount * (discount_percentage / 100)
    final_amount = original_amount - discount_amount
    
    return {
        'patient_name': 'John Smith',
        'patient_id': 'PT-2024-001',
        'date_of_service': 'January 15, 2024',
        'provider': 'St. Mary\'s Medical Center',
        'original_amount': f'${original_amount:.2f}',
        'discount_percentage': discount_percentage,
        'discount_amount': f'${discount_amount:.2f}',
        'final_amount': f'${final_amount:.2f}',
        'has_discount': discount_percentage > 0
    }

def brackets_view(request):
    """View for creating single-elimination tournament brackets"""
    context = {}
    
    # Add available tournaments for bracket saving
    if request.user.is_authenticated:
        from matches.models import Tournament
        available_tournaments = Tournament.objects.filter(status='upcoming')
        context['available_tournaments'] = available_tournaments
    
    if request.method == 'POST':
        if 'submit_scores' in request.POST:
            # Handle score submission
            bracket_data = request.session.get('bracket_data', [])            
            if bracket_data:
                # Process scores and update bracket
                bracket_data = process_scores(request.POST, bracket_data)
                request.session['bracket_data'] = bracket_data
                context['bracket_data'] = bracket_data
                context['participants'] = request.session.get('participants', [])
                context['num_participants'] = request.session.get('num_participants', 0)
                context['total_slots'] = request.session.get('total_slots', 0)
                context['show_scores'] = True
            else:
                context['error'] = "No bracket data found. Please generate a bracket first."
        else:
            # Handle initial bracket generation
            num_participants = request.POST.get('num_participants', '').strip()
            
            if num_participants:
                try:
                    num_participants = int(num_participants)
                    if num_participants > 0:
                        # Generate bracket with empty slots
                        bracket_data = generate_empty_bracket(num_participants)
                        
                        # Store in session for score updates
                        request.session['bracket_data'] = bracket_data
                        request.session['num_participants'] = num_participants
                        request.session['total_slots'] = len(bracket_data[0])
                        
                        context['bracket_data'] = bracket_data
                        context['num_participants'] = num_participants
                        context['total_slots'] = len(bracket_data[0])
                    else:
                        context['error'] = "Number of participants must be positive"
                except ValueError:
                    context['error'] = "Number of participants must be a valid integer"
    else:
        # GET request - check if we have existing bracket data
        bracket_data = request.session.get('bracket_data', [])
        if bracket_data:
            context['bracket_data'] = bracket_data
            context['num_participants'] = request.session.get('num_participants', 0)
            context['total_slots'] = request.session.get('total_slots', 0)
            context['show_scores'] = True
    
    return render(request, "brackets.html", context)

def generate_empty_bracket(num_participants):
    """
    Generate a single-elimination tournament bracket with empty slots for team names
    Returns a list of rounds, where each round is a list of matches
    """
    # Find the next power of 2
    next_power_of_2 = 2 ** math.ceil(math.log2(num_participants))
    
    # Create the bracket with empty slots
    bracket = []
    
    # First round (seeding round)
    first_round = []
    total_slots = next_power_of_2
    
    # Calculate BYE distribution
    byes_needed = total_slots - num_participants
    byes_per_quarter = byes_needed // 4
    extra_byes = byes_needed % 4
    
    # Create seeding positions
    positions = list(range(total_slots))
    
    # Distribute BYEs evenly across quarters
    bye_positions = []
    quarter_size = total_slots // 4
    
    for quarter in range(4):
        quarter_byes = byes_per_quarter + (1 if quarter < extra_byes else 0)
        if quarter_byes > 0:
            # Distribute BYEs within this quarter
            start_pos = quarter * quarter_size
            for i in range(quarter_byes):
                bye_pos = start_pos + (i * 2) + 1
                if bye_pos < start_pos + quarter_size:
                    bye_positions.append(bye_pos)
    
    # Create first round matches
    for i in range(0, total_slots, 2):
        pos1, pos2 = i, i + 1
        
        if pos1 in bye_positions:
            match = {
                'team1': 'BYE',
                'team2': '',  # Empty slot for team name input
                'winner': '',  # Will be filled when team name is entered
                'score1': None,
                'score2': None,
                'match_id': f"match_0_{len(first_round)}"
            }
        elif pos2 in bye_positions:
            match = {
                'team1': '',  # Empty slot for team name input
                'team2': 'BYE',
                'winner': '',  # Will be filled when team name is entered
                'score1': None,
                'score2': None,
                'match_id': f"match_0_{len(first_round)}"
            }
        else:
            match = {
                'team1': '',  # Empty slot for team name input
                'team2': '',  # Empty slot for team name input
                'winner': None,  # No auto-winner for non-BYE matches
                'score1': None,
                'score2': None,
                'match_id': f"match_0_{len(first_round)}"
            }
        
        first_round.append(match)
    
    bracket.append(first_round)
    
    # Generate subsequent rounds with empty matches
    current_round = first_round
    round_num = 1
    while len(current_round) > 1:
        next_round = []
        for i in range(0, len(current_round), 2):
            if i + 1 < len(current_round):
                match = {
                    'team1': None,
                    'team2': None,
                    'winner': None,
                    'score1': None,
                    'score2': None,
                    'match_id': f"match_{round_num}_{len(next_round)}"
                }
                next_round.append(match)
            else:
                # Handle odd number of teams in round
                match = {
                    'team1': None,  # Will be filled from previous round winner
                    'team2': None,
                    'winner': None,
                    'score1': None,
                    'score2': None,
                    'match_id': f"match_{round_num}_{len(next_round)}"
                }
                next_round.append(match)
        
        bracket.append(next_round)
        current_round = next_round
        round_num += 1
    
    return bracket

def _advance_winner_to_next_round(bracket_data, round_idx, match_idx, winner):
    """Helper function to advance a winner to the next round"""
    if round_idx < len(bracket_data) - 1:
        next_round_idx = round_idx + 1
        next_match_idx = match_idx // 2
        
        if next_match_idx < len(bracket_data[next_round_idx]):
            next_match = bracket_data[next_round_idx][next_match_idx]
            if match_idx % 2 == 0:  # First team in pair
                next_match['team1'] = winner
            else:  # Second team in pair
                next_match['team2'] = winner
            
            print(f"DEBUG: Advanced BYE winner {winner} to next round match {next_match['match_id']}")

def process_scores(request_data, bracket_data):
    """Process submitted scores and update bracket winners"""
    print(f"DEBUG: Processing scores. Request data keys: {list(request_data.keys())}")
    
    for round_idx, round_matches in enumerate(bracket_data):
        for match_idx, match in enumerate(round_matches):
            match_id = match['match_id']
            
            # Get team names from form (for first round only)
            if round_idx == 0:  # First round
                team1_key = f"team1_{match_id}"
                team2_key = f"team2_{match_id}"
                
                if team1_key in request_data:
                    match['team1'] = request_data[team1_key].strip()
                if team2_key in request_data:
                    match['team2'] = request_data[team2_key].strip()
                
                # Handle BYE logic for first round
                if match['team1'] == 'BYE' and match['team2']:
                    match['winner'] = match['team2']
                    # Advance BYE winner to next round
                    _advance_winner_to_next_round(bracket_data, round_idx, match_idx, match['winner'])
                elif match['team2'] == 'BYE' and match['team1']:
                    match['winner'] = match['team1']
                    # Advance BYE winner to next round
                    _advance_winner_to_next_round(bracket_data, round_idx, match_idx, match['winner'])
            
            # Get scores from form
            score1_key = f"score1_{match_id}"
            score2_key = f"score2_{match_id}"
            
            print(f"DEBUG: Checking match {match_id} - score1_key: {score1_key}, score2_key: {score2_key}")
            
            if score1_key in request_data and score2_key in request_data:
                try:
                    score1 = int(request_data[score1_key]) if request_data[score1_key] else None
                    score2 = int(request_data[score2_key]) if request_data[score2_key] else None
                    
                    print(f"DEBUG: Match {match_id} - score1: {score1}, score2: {score2}")
                    
                    if score1 is not None and score2 is not None:
                        match['score1'] = score1
                        match['score2'] = score2
                        
                        # Determine winner
                        if score1 > score2:
                            match['winner'] = match['team1']
                        elif score2 > score1:
                            match['winner'] = match['team2']
                        else:
                            match['winner'] = 'Tie'  # Handle ties if needed
                        
                        print(f"DEBUG: Match {match_id} winner: {match['winner']}")
                        
                        # Update next round if this isn't the final round
                        _advance_winner_to_next_round(bracket_data, round_idx, match_idx, match['winner'])
                
                except ValueError:
                    print(f"DEBUG: Invalid score input for match {match_id}")
                    pass  # Invalid score input
    
    return bracket_data
