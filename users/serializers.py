from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Client

# ==========================================
# USER SERIALIZERS
# ==========================================

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model - Read-only
    """
    
    class Meta:
        model = User
        fields = [
            'id', 'name', 'email', 'is_staff', 'is_admin', 
            'is_active', 'create_date_time', 'update_date_time'
        ]
        read_only_fields = ['id', 'create_date_time', 'update_date_time']


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new users
    """
    
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password]
    )
    
    class Meta:
        model = User
        fields = ['name', 'email', 'password']
    
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data.get('name', '')
        )
        return user


# ==========================================
# CLIENT SERIALIZERS
# ==========================================

class ClientSerializer(serializers.ModelSerializer):
    """
    Serializer for Client model - Full CRUD
    """
    
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        source='user', 
        write_only=True
    )
    
    class Meta:
        model = Client
        fields = [
            'id', 'user', 'user_id', 'name', 'api_key', 
            'base_url', 'for_login', 'for_payment', 
            'is_active', 'create_date_time', 'update_date_time'
        ]
        read_only_fields = [
            'id', 'api_key', 'create_date_time', 'update_date_time'
        ]
    
    def create(self, validated_data):
        """
        Create a new client with auto-generated API key
        """
        validated_data.pop('api_key', None)  # Remove if accidentally passed
        return super().create(validated_data)


class ClientUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating client (excluding API key)
    """
    
    class Meta:
        model = Client
        fields = [
            'name', 'base_url', 'for_login', 'for_payment', 'is_active'
        ]
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ClientRegenerateKeySerializer(serializers.Serializer):
    """
    Serializer for regenerating API key
    """
    
    client_id = serializers.IntegerField()
    
    def validate(self, data):
        try:
            client = Client.objects.get(pk=data['client_id'])
            data['client'] = client
        except Client.DoesNotExist:
            raise serializers.ValidationError("Client not found")
        return data