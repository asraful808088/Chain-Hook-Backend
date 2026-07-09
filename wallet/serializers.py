from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Wallet, Transaction, CurrencyPriceHistory

User = get_user_model()


class WalletSerializer(serializers.ModelSerializer):
    """
    Serializer for Wallet model
    """
    user = serializers.StringRelatedField(read_only=True)
    total_balance_usd = serializers.SerializerMethodField()
    
    class Meta:
        model = Wallet
        fields = [
            'id',
            'user',
            'USD',
            'EUR',
            'JPY',
            'GBP',
            'preferred_currency',
            'is_active',
            'total_balance_usd',
            'create_date_time',
            'update_date_time'
        ]
        read_only_fields = ['id', 'create_date_time', 'update_date_time']
    
    def get_total_balance_usd(self, obj):
        return obj.get_total_balance_in_usd()


class TransactionSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = ['id', 'entity', 'date', 'method', 'status', 'amount', 'create_date_time']

    def get_date(self, obj):
        local_dt = timezone.localtime(obj.transaction_date)
        return local_dt.strftime('%b %d, %H:%M')

    def get_amount(self, obj):
        entity = obj.entity.upper()
        amount_val = float(obj.amount)

        SYMBOLS = {
            'USD': '$',
            'EUR': '€',
            'GBP': '£',
            'JPY': '¥',
        }

        # Case 1: Conversion (Internal FX Swap)
        if "CONVERSION" in entity or "FX" in entity:
            parts = obj.entity.split()
            from_cur = 'USD'
            to_cur = 'EUR'
            if len(parts) >= 3:
                from_cur = parts[0].upper()
                to_cur = parts[2].upper()

            symbol_from = SYMBOLS.get(from_cur, '$')
            symbol_to = SYMBOLS.get(to_cur, '€')

            # Fetch rates to compute target converted amount
            rates = CurrencyPriceHistory.objects.first()
            if not rates:
                rates_dict = {'EUR': 0.92, 'JPY': 148.50, 'GBP': 0.79, 'USD': 1.00}
            else:
                rates_dict = {
                    'USD': float(rates.USD),
                    'EUR': float(rates.EUR),
                    'JPY': float(rates.JPY),
                    'GBP': float(rates.GBP),
                }

            rate_from = rates_dict.get(from_cur, 1.0)
            rate_to = rates_dict.get(to_cur, 1.0)
            
            rate = rate_to / rate_from
            converted = amount_val * 0.996 * rate

            formatted_from = f"{symbol_from}{amount_val:,.2f}"
            formatted_to = f"{symbol_to}{converted:,.2f}"
            return f"-{formatted_from} (+{formatted_to})"

        # Check if transaction is credit or debit
        is_credit = False
        if "TRANSFER FROM" in entity or "PAYOUT" in entity or "RECEIVED" in entity:
            is_credit = True

        # Extract currency code from method
        cur_code = None
        for code in SYMBOLS.keys():
            if f"({code})" in obj.method:
                cur_code = code
                break
        
        if not cur_code:
            if hasattr(obj.user, 'wallet'):
                cur_code = obj.user.wallet.preferred_currency
            else:
                cur_code = 'USD'

        symbol = SYMBOLS.get(cur_code, '$')
        sign = '+' if is_credit else '-'
        return f"{sign}{symbol}{amount_val:,.2f}"


class CurrencyPriceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrencyPriceHistory
        fields = ['id', 'USD', 'EUR', 'JPY', 'GBP', 'create_date_time']
