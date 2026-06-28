from django.shortcuts import render
import stripe
import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from django.utils import timezone
from .models import Subscription, PaymentHistory
from accounts.models import User
from accounts.decorators import admin_required

def get_or_create_subscription(user):
    sub, _ = Subscription.objects.get_or_create(user=user)
    return sub


# ---- Public pricing page ----
def pricing_page(request):
    return render(request, 'billing/pricing.html')


# ---- Billing dashboard ----
@login_required
def billing_dashboard(request):
    sub = get_or_create_subscription(request.user)
    payments = PaymentHistory.objects.filter(user=request.user)[:10]
    context = {
        'sub':       sub,
        'payments':  payments,
        'limits':    sub.get_plan_limits(),
        'pub_key':   settings.STRIPE_PUBLISHABLE_KEY,
    }
    return render(request, 'billing/dashboard.html', context)


# ---- Create Stripe Checkout Session ----
@login_required
def create_checkout_session(request, plan):
    price_map = {
        'pro':        settings.STRIPE_PRO_PRICE_ID,
        'enterprise': settings.STRIPE_ENTERPRISE_PRICE_ID,
    }
    price_id = price_map.get(plan)
    if not price_id:
        messages.error(request, 'Invalid plan selected.')
        return redirect('billing_dashboard')

    price_id = price_id.strip()
    sub = get_or_create_subscription(request.user)

    try:
        # Dynamically fetch active price ID if a Product ID (prod_...) is configured
        if price_id.startswith('prod_'):
            prices = stripe.Price.list(product=price_id, active=True, limit=1)
            if prices.data:
                price_id = prices.data[0].id
            else:
                messages.error(request, f'No active price found for product {price_id}.')
                return redirect('billing_dashboard')

        # Get or create Stripe customer
        if sub.stripe_customer_id:
            customer_id = sub.stripe_customer_id
        else:
            customer = stripe.Customer.create(
                email=request.user.email,
                name=request.user.get_full_name() or request.user.email,
                metadata={'user_id': request.user.pk},
            )
            customer_id = customer.id
            sub.stripe_customer_id = customer_id
            sub.save()

        # Create checkout session
        site_url = request.build_absolute_uri('/').rstrip('/')
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[{'price': price_id, 'quantity': 1}],
            mode='subscription',
            success_url=f"{site_url}/billing/success/?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{site_url}/billing/",
            metadata={
                'user_id': request.user.pk,
                'plan':    plan,
            },
        )
        return redirect(session.url)

    except stripe.error.StripeError as e:
        messages.error(request, f'Payment error: {str(e)}')
        return redirect('billing_dashboard')


# ---- Success page after payment ----
@login_required
def checkout_success(request):
    session_id = request.GET.get('session_id')
    if session_id:
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            plan    = session.metadata.get('plan', 'pro')
            sub     = get_or_create_subscription(request.user)
            sub.plan   = plan
            sub.status = 'active'
            sub.stripe_subscription_id = session.subscription or ''
            sub.save()
            messages.success(request, f'Welcome to NexaOps {plan.title()}! Your subscription is now active.')
        except Exception:
            pass
    return render(request, 'billing/success.html')


# ---- Cancel subscription ----
@admin_required
@login_required
def cancel_subscription(request):
    if request.method == 'POST':
        sub = get_or_create_subscription(request.user)
        try:
            if sub.stripe_subscription_id:
                stripe.Subscription.modify(
                    sub.stripe_subscription_id,
                    cancel_at_period_end=True,
                )
                sub.cancel_at_period_end = True
                sub.save()
                messages.success(request, 'Subscription cancelled. You can use Pro features until the end of your billing period.')
            else:
                sub.plan   = 'free'
                sub.status = 'active'
                sub.save()
                messages.success(request, 'Subscription cancelled.')
        except stripe.error.StripeError as e:
            messages.error(request, f'Error: {str(e)}')
    return redirect('billing_dashboard')


# ---- Stripe Webhook ----
@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload    = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session  = event['data']['object']
        user_id  = session['metadata'].get('user_id')
        plan     = session['metadata'].get('plan', 'pro')
        try:
            user = User.objects.get(pk=user_id)
            sub  = get_or_create_subscription(user)
            sub.plan   = plan
            sub.status = 'active'
            sub.stripe_subscription_id = session.get('subscription', '')
            sub.save()
        except User.DoesNotExist:
            pass

    elif event['type'] == 'invoice.payment_succeeded':
        invoice    = event['data']['object']
        customer_id = invoice.get('customer')
        try:
            sub = Subscription.objects.get(stripe_customer_id=customer_id)
            PaymentHistory.objects.create(
                user=sub.user,
                stripe_invoice_id=invoice.get('id', ''),
                amount=invoice.get('amount_paid', 0) / 100,
                currency=invoice.get('currency', 'usd'),
                status='paid',
                description=f"NexaOps {sub.plan.title()} Plan",
                invoice_url=invoice.get('hosted_invoice_url', ''),
            )
        except Subscription.DoesNotExist:
            pass

    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        try:
            sub = Subscription.objects.get(
                stripe_subscription_id=subscription['id']
            )
            sub.plan   = 'free'
            sub.status = 'active'
            sub.cancel_at_period_end = False
            sub.save()
        except Subscription.DoesNotExist:
            pass

    elif event['type'] == 'invoice.payment_failed':
        invoice     = event['data']['object']
        customer_id = invoice.get('customer')
        try:
            sub = Subscription.objects.get(stripe_customer_id=customer_id)
            sub.status = 'past_due'
            sub.save()
        except Subscription.DoesNotExist:
            pass

    return HttpResponse(status=200)