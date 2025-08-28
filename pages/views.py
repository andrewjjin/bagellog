from django.shortcuts import render

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
