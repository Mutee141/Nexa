from django.db import models

# Create your models here.
from django.db import models
from accounts.models import User


class Subscription(models.Model):
    PLAN_CHOICES = [
        ('free',       'Free'),
        ('pro',        'Pro'),
        ('enterprise', 'Enterprise'),
    ]
    STATUS_CHOICES = [
        ('active',    'Active'),
        ('cancelled', 'Cancelled'),
        ('past_due',  'Past Due'),
        ('trialing',  'Trialing'),
    ]

    user                    = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    plan                    = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    status                  = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    stripe_customer_id      = models.CharField(max_length=100, blank=True)
    stripe_subscription_id  = models.CharField(max_length=100, blank=True)
    current_period_end      = models.DateTimeField(null=True, blank=True)
    cancel_at_period_end    = models.BooleanField(default=False)
    created_at              = models.DateTimeField(auto_now_add=True)
    updated_at              = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} — {self.plan}"

    def is_pro(self):
        return self.plan in ['pro', 'enterprise'] and self.status == 'active'

    def is_enterprise(self):
        return self.plan == 'enterprise' and self.status == 'active'

    def get_plan_limits(self):
        limits = {
            'free': {
                'users':    3,
                'projects': 5,
                'ai_calls': 10,
                'storage':  '1 GB',
            },
            'pro': {
                'users':    25,
                'projects': 999,
                'ai_calls': 500,
                'storage':  '50 GB',
            },
            'enterprise': {
                'users':    999,
                'projects': 999,
                'ai_calls': 9999,
                'storage':  'Unlimited',
            },
        }
        return limits.get(self.plan, limits['free'])


class PaymentHistory(models.Model):
    user            = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    stripe_invoice_id = models.CharField(max_length=100, blank=True)
    amount          = models.DecimalField(max_digits=10, decimal_places=2)
    currency        = models.CharField(max_length=10, default='usd')
    status          = models.CharField(max_length=30, default='paid')
    description     = models.CharField(max_length=200, blank=True)
    invoice_url     = models.URLField(blank=True)
    paid_at         = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-paid_at']

    def __str__(self):
        return f"{self.user.email} — ${self.amount}"