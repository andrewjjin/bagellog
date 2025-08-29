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
            # Handle initial bracket generation
            participants = request.POST.get('participants', '').strip()
            num_participants = request.POST.get('num_participants', '').strip()
            
            if participants and num_participants:
                try:
                    num_participants = int(num_participants)
                    if num_participants > 0:
                        # Parse participants (comma-separated or newline-separated)
                        participant_list = [p.strip() for p in participants.replace('\n', ',').split(',') if p.strip()]
                        
                        if len(participant_list) >= num_participants:
                            # Generate bracket
                            bracket_data = generate_bracket(participant_list[:num_participants])
                            
                            # Store in session for score updates
                            request.session['bracket_data'] = bracket_data
                            request.session['participants'] = participant_list[:num_participants]
                            request.session['num_participants'] = num_participants
                            request.session['total_slots'] = len(bracket_data[0])
                            
                            context['bracket_data'] = bracket_data
                            context['participants'] = participant_list[:num_participants]
                            context['num_participants'] = num_participants
                            context['total_slots'] = len(bracket_data[0])
                        else:
                            context['error'] = f"Not enough participants provided. Need {num_participants}, got {len(participant_list)}"
                    else:
                        context['error'] = "Number of participants must be positive"
                except ValueError:
                    context['error'] = "Number of participants must be a valid integer"
    
    return render(request, "brackets.html", context)

def generate_bracket(participants):
    """
    Generate a single-elimination tournament bracket
    Returns a list of rounds, where each round is a list of matches
    """
    num_participants = len(participants)
    
    # Find the next power of 2
    next_power_of_2 = 2 ** math.ceil(math.log2(num_participants))
    
    # Create the bracket with BYE slots
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
                'team2': participants[positions[pos2]] if positions[pos2] < num_participants else 'BYE',
                'winner': participants[positions[pos2]] if positions[pos2] < num_participants else 'BYE',
                'score1': None,
                'score2': None,
                'match_id': f"match_{len(first_round)}_0"
            }
        elif pos2 in bye_positions:
            match = {
                'team1': participants[positions[pos1]] if positions[pos1] < num_participants else 'BYE',
                'team2': 'BYE',
                'winner': participants[positions[pos1]] if positions[pos1] < num_participants else 'BYE',
                'score1': None,
                'score2': None,
                'match_id': f"match_{len(first_round)}_0"
            }
        else:
            team1 = participants[positions[pos1]] if positions[pos1] < num_participants else 'BYE'
            team2 = participants[positions[pos2]] if positions[pos2] < num_participants else 'BYE'
            match = {
                'team1': team1,
                'team2': team2,
                'winner': None,  # No auto-winner for non-BYE matches
                'score1': None,
                'score2': None,
                'match_id': f"match_{len(first_round)}_0"
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
                    'team1': current_round[i]['winner'],
                    'team2': None,
                    'winner': current_round[i]['winner'],
                    'score1': None,
                    'score2': None,
                    'match_id': f"match_{round_num}_{len(next_round)}"
                }
                next_round.append(match)
        
        bracket.append(next_round)
        current_round = next_round
        round_num += 1
    
    return bracket

def process_scores(request_data, bracket_data):
    """Process submitted scores and update bracket winners"""
    for round_idx, round_matches in enumerate(bracket_data):
        for match_idx, match in enumerate(round_matches):
            match_id = match['match_id']
            
            # Get scores from form
            score1_key = f"score1_{match_id}"
            score2_key = f"score2_{match_id}"
            
            if score1_key in request_data and score2_key in request_data:
                try:
                    score1 = int(request_data[score1_key]) if request_data[score1_key] else None
                    score2 = int(request_data[score2_key]) if request_data[score2_key] else None
                    
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
                        
                        # Update next round if this isn't the final round
                        if round_idx < len(bracket_data) - 1:
                            next_round_idx = round_idx + 1
                            next_match_idx = match_idx // 2
                            
                            if next_match_idx < len(bracket_data[next_round_idx]):
                                next_match = bracket_data[next_round_idx][next_match_idx]
                                if match_idx % 2 == 0:  # First team in pair
                                    next_match['team1'] = match['winner']
                                else:  # Second team in pair
                                    next_match['team2'] = match['winner']
                
                except ValueError:
                    pass  # Invalid score input
    
    return bracket_data
