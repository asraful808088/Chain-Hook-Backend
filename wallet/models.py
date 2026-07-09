import random
from datetime import timedelta

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone



class TimeStampedModel(models.Model):
    create_date_time = models.DateTimeField(auto_now_add=True, verbose_name="Date Created")
    update_date_time = models.DateTimeField(auto_now=True, verbose_name="Last Updated")

    class Meta:
        abstract = True


class Wallet(models.Model):

    CURRENCY_CHOICES = [
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('JPY', 'Japanese Yen'),
        ('GBP', 'British Pound'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wallet',
        verbose_name="User",
        help_text="The user who owns this wallet"
    )

    USD = models.DecimalField(
        max_digits=15, decimal_places=2, default=0.00,
        verbose_name="US Dollar", validators=[MinValueValidator(0)]
    )
    EUR = models.DecimalField(
        max_digits=15, decimal_places=2, default=0.00,
        verbose_name="Euro", validators=[MinValueValidator(0)]
    )
    JPY = models.DecimalField(
        max_digits=15, decimal_places=2, default=0.00,
        verbose_name="Japanese Yen", validators=[MinValueValidator(0)]
    )
    GBP = models.DecimalField(
        max_digits=15, decimal_places=2, default=0.00,
        verbose_name="British Pound", validators=[MinValueValidator(0)]
    )

    preferred_currency = models.CharField(
        max_length=3, choices=CURRENCY_CHOICES, default='USD',
        verbose_name="Preferred Currency",
        help_text="User's preferred currency for display"
    )

    is_active = models.BooleanField(
        default=True, verbose_name="Is Active",
        help_text="Whether this wallet is active"
    )

    update_date_time = models.DateTimeField(auto_now=True, verbose_name="Last Updated")
    create_date_time = models.DateTimeField(auto_now_add=True, verbose_name="Date Created")

    class Meta:
        db_table = 'wallet'
        verbose_name = "Wallet"
        verbose_name_plural = "Wallets"
        ordering = ['-create_date_time']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['preferred_currency']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.user.email} - USD: {self.USD}, EUR: {self.EUR}, JPY: {self.JPY}, GBP: {self.GBP}"

    def get_balance(self, currency_code):
        currency_code = currency_code.upper()
        if hasattr(self, currency_code):
            return getattr(self, currency_code)
        return None

    def add_balance(self, currency_code, amount):
        currency_code = currency_code.upper()
        if hasattr(self, currency_code) and amount > 0:
            current = getattr(self, currency_code)
            setattr(self, currency_code, current + amount)
            self.save()
            return True
        return False

    def subtract_balance(self, currency_code, amount):
        currency_code = currency_code.upper()
        if hasattr(self, currency_code) and amount > 0:
            current = getattr(self, currency_code)
            if current >= amount:
                setattr(self, currency_code, current - amount)
                self.save()
                return True
            return False
        return False

    def transfer_balance(self, from_currency, to_currency, amount):
        if amount <= 0:
            return False, "Amount must be positive"
        if self.subtract_balance(from_currency, amount):
            if self.add_balance(to_currency, amount):
                return True, "Transfer successful"
            self.add_balance(from_currency, amount)
            return False, "Transfer failed"
        return False, "Insufficient balance"

    def get_total_balance_in_usd(self, exchange_rates=None):
        if exchange_rates is None:
            exchange_rates = {'EUR': 1.09, 'JPY': 0.0068, 'GBP': 1.27}
        total = float(self.USD)
        for currency, rate in exchange_rates.items():
            if hasattr(self, currency):
                total += float(getattr(self, currency)) * rate
        return round(total, 2)

    def get_all_balances(self):
        return {
            'USD': float(self.USD), 'EUR': float(self.EUR),
            'JPY': float(self.JPY), 'GBP': float(self.GBP),
        }

    @classmethod
    def create_for_user(cls, user, **kwargs):
        return cls.objects.create(
            user=user,
            USD=kwargs.get('USD', 0.00),
            EUR=kwargs.get('EUR', 0.00),
            JPY=kwargs.get('JPY', 0.00),
            GBP=kwargs.get('GBP', 0.00),
            preferred_currency=kwargs.get('preferred_currency', 'USD')
        )


def generate_payment_address():
    block = lambda: f"{random.randint(0, 9999):04d}"
    return f"CH-WAL-{block()}-{block()}-{block()}"


class UserCurrency(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='currency_account',
    )

    USD = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, validators=[MinValueValidator(0)])
    EUR = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, validators=[MinValueValidator(0)])
    JPY = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, validators=[MinValueValidator(0)])
    GBP = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, validators=[MinValueValidator(0)])

    max_lmt = models.DecimalField(
        max_digits=15, decimal_places=2, default=0.00,
        verbose_name="Maximum Limit",
        help_text="Maximum allowed balance/spend limit"
    )
    use_lmt = models.DecimalField(
        max_digits=15, decimal_places=2, default=0.00,
        verbose_name="Used Limit",
        help_text="Amount of the limit already used"
    )

    payment_address = models.CharField(
        max_length=255,
        blank=True,
        unique=True,
        editable=False,
        verbose_name="Payment Address",
    )

    class Meta:
        db_table = 'currency'
        verbose_name = "User Currency"
        verbose_name_plural = "User Currencies"
        indexes = [
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"UserCurrency(user_id={self.user_id})"

    def save(self, *args, **kwargs):
        if not self.payment_address:
            self.payment_address = self._generate_unique_payment_address()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_unique_payment_address():
        while True:
            candidate = generate_payment_address()
            if not UserCurrency.objects.filter(payment_address=candidate).exists():
                return candidate


class CardBase(TimeStampedModel):
    user_currency = models.ForeignKey(
        UserCurrency,
        on_delete=models.CASCADE,
        related_name="%(class)ss",
    )
    number = models.CharField(max_length=19)
    cvc = models.CharField(max_length=4)
    exp = models.CharField(max_length=5, help_text="Format: MM/YY")
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def __str__(self):
        masked = f"**** **** **** {self.number[-4:]}" if len(self.number) >= 4 else "****"
        return f"{self.__class__.__name__}({masked})"


class PremiumCard(CardBase):
    class Meta:
        db_table = 'premium_cards'
        verbose_name = "Premium Card"
        verbose_name_plural = "Premium Cards"


class StandardCard(CardBase):
    class Meta:
        db_table = 'standard_cards'
        verbose_name = "Standard Card"
        verbose_name_plural = "Standard Cards"


class VirtualCard(CardBase):
    class Meta:
        db_table = 'virtual_cards'
        verbose_name = "Virtual Card"
        verbose_name_plural = "Virtual Cards"


class CurrencyPriceHistoryManager(models.Manager):
    def seed_if_empty(self, rows=50):
        if self.exists():
            return []

        base_rates = {'EUR': 0.92, 'JPY': 148.50, 'GBP': 0.79}
        now = timezone.now()

        objs = [
            CurrencyPriceHistory(
                USD=1.000000,
                EUR=round(base_rates['EUR'] * random.uniform(0.97, 1.03), 6),
                JPY=round(base_rates['JPY'] * random.uniform(0.97, 1.03), 6),
                GBP=round(base_rates['GBP'] * random.uniform(0.97, 1.03), 6),
            )
            for _ in range(rows)
        ]
        created = self.bulk_create(objs)

        for i, obj in enumerate(created):
            ts = now - timedelta(minutes=30 * (rows - i))
            obj.create_date_time = ts
            obj.update_date_time = ts
        self.bulk_update(created, ['create_date_time', 'update_date_time'])
        return created

    def get_latest_price_history(self, limit=50):
        self.seed_if_empty(rows=limit)

        now = timezone.now()
        history = list(self.order_by('-create_date_time')[:limit])

        if not history:
            return []

        latest = history[0]
        if now - latest.create_date_time >= timedelta(minutes=30):
            new_eur = round(float(latest.EUR) * random.uniform(0.985, 1.015), 6)
            new_jpy = round(float(latest.JPY) * random.uniform(0.985, 1.015), 6)
            new_gbp = round(float(latest.GBP) * random.uniform(0.985, 1.015), 6)

            new_entry = self.create(
                USD=1.000000,
                EUR=new_eur,
                JPY=new_jpy,
                GBP=new_gbp,
            )
            history.insert(0, new_entry)

            all_entries = list(self.order_by('-create_date_time'))
            if len(all_entries) > limit:
                ids_to_keep = [x.id for x in all_entries[:limit]]
                self.exclude(id__in=ids_to_keep).delete()
                history = all_entries[:limit]

        return history



class CurrencyPriceHistory(TimeStampedModel):
    USD = models.DecimalField(max_digits=15, decimal_places=6, default=1.00)
    EUR = models.DecimalField(max_digits=15, decimal_places=6, default=0.00)
    JPY = models.DecimalField(max_digits=15, decimal_places=6, default=0.00)
    GBP = models.DecimalField(max_digits=15, decimal_places=6, default=0.00)

    objects = CurrencyPriceHistoryManager()

    class Meta:
        db_table = 'currency_price_history'
        verbose_name = "Currency Price History"
        verbose_name_plural = "Currency Price History"
        ordering = ['-create_date_time']

    def __str__(self):
        return f"Rates @ {self.create_date_time:%Y-%m-%d %H:%M}"


class Transaction(TimeStampedModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transactions',
    )
    entity = models.CharField(max_length=255) 
    transaction_date = models.DateTimeField()
    method = models.CharField(max_length=100)  
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0)])

    class Meta:
        db_table = 'transactions'
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
        ordering = ['-transaction_date']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['status']),
            models.Index(fields=['transaction_date']),
        ]

    def __str__(self):
        return f"Transaction(user_id={self.user_id}, amount={self.amount}, status={self.status})"