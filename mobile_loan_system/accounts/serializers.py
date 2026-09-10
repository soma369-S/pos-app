from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import CustomerProfile


class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class CustomerProfileSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)

    class Meta:
        model = CustomerProfile
        fields = [
            'id', 'user', 'phone_number', 'address', 'city', 'state', 'pincode',
            'id_proof_type', 'id_proof_number', 'monthly_income', 'credit_score',
            'is_verified', 'created_at',
        ]
        read_only_fields = ['credit_score', 'is_verified', 'created_at']


class CustomerRegistrationSerializer(serializers.Serializer):
    """
    Handles creating the User + CustomerProfile together in one API call,
    so the mobile app / frontend only needs a single registration request.
    """
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, validators=[validate_password])
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)

    phone_number = serializers.CharField(max_length=15)
    address = serializers.CharField()
    city = serializers.CharField(max_length=100)
    state = serializers.CharField(max_length=100, required=False, allow_blank=True)
    pincode = serializers.CharField(max_length=10, required=False, allow_blank=True)
    id_proof_type = serializers.ChoiceField(choices=CustomerProfile._meta.get_field('id_proof_type').choices)
    id_proof_number = serializers.CharField(max_length=50)
    monthly_income = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        profile = CustomerProfile.objects.create(
            user=user,
            phone_number=validated_data['phone_number'],
            address=validated_data['address'],
            city=validated_data['city'],
            state=validated_data.get('state', ''),
            pincode=validated_data.get('pincode', ''),
            id_proof_type=validated_data['id_proof_type'],
            id_proof_number=validated_data['id_proof_number'],
            monthly_income=validated_data.get('monthly_income'),
        )
        return profile
