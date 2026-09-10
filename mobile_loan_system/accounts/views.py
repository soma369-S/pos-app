from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect

from rest_framework import viewsets, status, permissions
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CustomerProfile
from .serializers import CustomerProfileSerializer, CustomerRegistrationSerializer


# ---------------------------------------------------------------------------
# DRF API views
# ---------------------------------------------------------------------------

class RegisterAPIView(APIView):
    """POST /api/accounts/register/ -> creates User + CustomerProfile, returns auth token."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = CustomerRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = serializer.save()
        token, _ = Token.objects.get_or_create(user=profile.user)
        return Response(
            {
                'token': token.key,
                'profile': CustomerProfileSerializer(profile).data,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginAPIView(APIView):
    """POST /api/accounts/login/ with {username, password} -> returns auth token."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        token, _ = Token.objects.get_or_create(user=user)
        data = {'token': token.key}
        if hasattr(user, 'profile'):
            data['profile'] = CustomerProfileSerializer(user.profile).data
        return Response(data)


class CustomerProfileViewSet(viewsets.ModelViewSet):
    """
    Staff can list/manage all customer profiles.
    A logged-in customer can only see & update their own profile.
    """
    serializer_class = CustomerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return CustomerProfile.objects.all().order_by('-created_at')
        return CustomerProfile.objects.filter(user=user)

    @action(detail=False, methods=['get'])
    def me(self, request):
        profile = getattr(request.user, 'profile', None)
        if not profile:
            return Response({'detail': 'No customer profile for this user.'}, status=404)
        return Response(CustomerProfileSerializer(profile).data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def verify(self, request, pk=None):
        """Staff endpoint: mark a customer's KYC as verified."""
        profile = self.get_object()
        profile.is_verified = True
        profile.save(update_fields=['is_verified'])
        return Response(CustomerProfileSerializer(profile).data)


# ---------------------------------------------------------------------------
# Template-based frontend views
# ---------------------------------------------------------------------------

def register_view(request):
    if request.method == 'POST':
        data = request.POST
        serializer = CustomerRegistrationSerializer(data={
            'username': data.get('username'),
            'email': data.get('email'),
            'password': data.get('password'),
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name'),
            'phone_number': data.get('phone_number'),
            'address': data.get('address'),
            'city': data.get('city'),
            'state': data.get('state'),
            'pincode': data.get('pincode'),
            'id_proof_type': data.get('id_proof_type'),
            'id_proof_number': data.get('id_proof_number'),
            'monthly_income': data.get('monthly_income') or None,
        })
        if serializer.is_valid():
            profile = serializer.save()
            login(request, profile.user)
            messages.success(request, "Account created successfully. Welcome!")
            return redirect('home')
        else:
            for field, errs in serializer.errors.items():
                for e in errs:
                    messages.error(request, f"{field}: {e}")
    return render(request, 'accounts/register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        messages.error(request, "Invalid username or password.")
    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def dashboard_view(request):
    profile = getattr(request.user, 'profile', None)
    orders = profile.orders.all().order_by('-created_at') if profile else []
    loans = profile.loans.all().order_by('-applied_at') if profile else []
    return render(request, 'accounts/dashboard.html', {
        'profile': profile,
        'orders': orders,
        'loans': loans,
    })
