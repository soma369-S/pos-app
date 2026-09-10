from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect


def login_view(request):
    if request.user.is_authenticated:
        return redirect('frontend:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('frontend:dashboard')
        messages.error(request, 'Invalid username or password.')

    return render(request, 'frontend/login.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('frontend:login')


@login_required
def dashboard(request):
    return render(request, 'frontend/dashboard.html')


@login_required
def customers_page(request):
    return render(request, 'frontend/customers.html')


@login_required
def inventory_page(request):
    return render(request, 'frontend/inventory.html')


@login_required
def loans_page(request):
    return render(request, 'frontend/loans.html')


@login_required
def loan_detail_page(request, loan_id):
    return render(request, 'frontend/loan_detail.html', {'loan_id': loan_id})
