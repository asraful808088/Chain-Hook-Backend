from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
import secrets


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        import random
        from decimal import Decimal
        from django.utils import timezone
        from datetime import timedelta
        from wallet.models import Wallet, Transaction, UserCurrency

        Wallet.objects.create(
            user=user,
            USD=Decimal('50000.00'),
            EUR=Decimal('2400.00'),
            JPY=Decimal('180000.00'),
            GBP=Decimal('1500.00'),
            preferred_currency='USD',
            is_active=True
        )

        UserCurrency.objects.create(
            user=user,
            USD=Decimal('50000.00'),
            EUR=Decimal('2400.00'),
            JPY=Decimal('180000.00'),
            GBP=Decimal('1500.00'),
            max_lmt=Decimal('50000.00'),
            use_lmt=Decimal('0.00'),
        )

        now = timezone.now()
        seed_transactions = [
            {'entity': 'Goldman Sachs Payout',   'method': 'SWIFT Verified (USD)',   'status': 'completed',  'amount': Decimal('12400.00'), 'days_ago': 1},
            {'entity': 'Stripe Payout',           'method': 'Automated API (USD)',    'status': 'completed',  'amount': Decimal('3200.00'),  'days_ago': 2},
            {'entity': 'CloudFlare API',          'method': 'Automated API (USD)',    'status': 'completed',  'amount': Decimal('450.00'),   'days_ago': 3},
            {'entity': 'EUR to USD Conversion',   'method': 'Internal FX Swap (EUR)', 'status': 'completed', 'amount': Decimal('2000.00'),  'days_ago': 4},
            {'entity': 'AWS Services',            'method': 'Credit Card (USD)',      'status': 'failed',     'amount': Decimal('120.00'),   'days_ago': 5},
            {'entity': 'Netflix Subscription',    'method': 'Auto-Debit (USD)',       'status': 'completed',  'amount': Decimal('15.99'),    'days_ago': 6},
            {'entity': 'Transfer from Revolut',   'method': 'SEPA Transfer (EUR)',    'status': 'completed',  'amount': Decimal('1500.00'),  'days_ago': 8},
            {'entity': 'USD to GBP Conversion',   'method': 'Internal FX Swap (USD)', 'status': 'completed', 'amount': Decimal('1500.00'),  'days_ago': 10},
            {'entity': 'Payoneer Transfer',       'method': 'Wire Transfer (USD)',    'status': 'completed',  'amount': Decimal('2800.00'),  'days_ago': 12},
            {'entity': 'Shopify Payout',          'method': 'Automated API (USD)',    'status': 'pending',    'amount': Decimal('4200.00'),  'days_ago': 14},
            {'entity': 'Google AdSense',          'method': 'Wire Transfer (USD)',    'status': 'completed',  'amount': Decimal('890.50'),   'days_ago': 16},
            {'entity': 'Azure Cloud Services',    'method': 'Credit Card (USD)',      'status': 'completed',  'amount': Decimal('340.00'),   'days_ago': 18},
            {'entity': 'USD to JPY Conversion',   'method': 'Internal FX Swap (USD)', 'status': 'completed', 'amount': Decimal('5000.00'),  'days_ago': 19},
            {'entity': 'TransferWise Payout',     'method': 'SEPA Transfer (EUR)',    'status': 'completed',  'amount': Decimal('1200.00'),  'days_ago': 21},
            {'entity': 'Binance Withdrawal',      'method': 'Wire Transfer (USD)',    'status': 'pending',    'amount': Decimal('3500.00'),  'days_ago': 23},
        ]

        txs = []
        for tx in seed_transactions:
            t_date = now - timedelta(days=tx['days_ago'])
            offset_minutes = random.randint(-120, 120)
            t_date = t_date + timedelta(minutes=offset_minutes)
            txs.append(Transaction(
                user=user,
                entity=tx['entity'],
                transaction_date=t_date,
                method=tx['method'],
                status=tx['status'],
                amount=tx['amount'],
            ))
        Transaction.objects.bulk_create(txs)

        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_admin') is not True:
            raise ValueError('Superuser must have is_admin=True.')
        
        return self.create_user(email, password, **extra_fields)



class User(AbstractBaseUser, PermissionsMixin):
    
    name = models.CharField(max_length=255, verbose_name="Full Name")
    email = models.EmailField(
        unique=True, 
        max_length=255, 
        verbose_name="Email Address"
    )
    password = models.CharField(max_length=128)
    
    is_staff = models.BooleanField(
        default=False,
        verbose_name="Staff Status",
        help_text="Designates whether the user can log into this admin site."
    )
    
    is_admin = models.BooleanField(
        default=False,
        verbose_name="Admin Status",
        help_text="Designates whether the user has all permissions."
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active Status",
        help_text="Designates whether this user should be treated as active."
    )
    
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to.'
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.'
    )
    
    update_date_time = models.DateTimeField(
        auto_now=True,
        verbose_name="Last Updated"
    )
    
    create_date_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date Created"
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    
    objects = UserManager()
    
    class Meta:
        db_table = 'users'
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ['-create_date_time']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_staff']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.email})"
    
    def get_full_name(self):
        return self.name
    
    def get_short_name(self):
        return self.name.split()[0] if self.name else self.email
    
    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, app_label):
        return self.is_admin
    
    @property
    def is_superuser(self):
        return self.is_admin
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    


class Client(models.Model):
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='clients',
        verbose_name="User",
        help_text="The user who owns this client"
    )
    
    api_key = models.CharField(
        max_length=255,
        unique=True,
        blank=True,
        null=True,
        verbose_name="API Key",
        help_text="Unique API key for client authentication"
    )
    
    base_url = models.CharField(
        max_length=500,
        verbose_name="Base URL",
        help_text="Base URL of the client application"
    )
    
    for_login = models.BooleanField(
        default=False,
        verbose_name="For Login",
        help_text="Designates whether this client is used for login"
    )
    
    for_payment = models.BooleanField(
        default=False,
        verbose_name="For Payment",
        help_text="Designates whether this client is used for payment"
    )
    
    name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Client Name",
        help_text="Name of the client application"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Is Active",
        help_text="Whether this client is active"
    )
    
    update_date_time = models.DateTimeField(
        auto_now=True,
        verbose_name="Last Updated"
    )
    
    create_date_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date Created"
    )
    
    class Meta:
        db_table = 'client'
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        ordering = ['-create_date_time']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['base_url']),
            models.Index(fields=['api_key']),
            models.Index(fields=['is_active']),
            models.Index(fields=['for_login']),
            models.Index(fields=['for_payment']),
        ]
    
    def __str__(self):
        return f"{self.name or 'Client'} - {self.user.email}"
    
    def save(self, *args, **kwargs):
        if not self.api_key:
            self.api_key = self.generate_api_key()
        super().save(*args, **kwargs)
    
    def generate_api_key(self):
        return secrets.token_urlsafe(32)
    
    def regenerate_api_key(self):
        self.api_key = self.generate_api_key()
        self.save(update_fields=['api_key', 'update_date_time'])
        return self.api_key
    
    def get_login_url(self):
        if self.for_login:
            return self.base_url
        return None

    def get_payment_url(self):
        if self.for_payment:
            return self.base_url
        return None



class UserActivityLog(models.Model):
    
    ACTION_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('payment', 'Payment'),
        ('transfer', 'Transfer'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('create', 'Create'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='activities',
        verbose_name="User"
    )
    
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name="Action"
    )
    
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name="IP Address"
    )
    
    user_agent = models.TextField(
        blank=True,
        verbose_name="User Agent"
    )
    
    details = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Details"
    )
    
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Timestamp"
    )
    
    class Meta:
        db_table = 'user_activity_log'
        verbose_name = "User Activity Log"
        verbose_name_plural = "User Activity Logs"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'action']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.action} - {self.timestamp}"