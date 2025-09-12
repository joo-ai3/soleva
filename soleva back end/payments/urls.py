from django.urls import path
from . import views

urlpatterns = [
    path('methods/', views.PaymentMethodListView.as_view(), name='payment_methods'),
    path('create-intent/', views.CreatePaymentIntentView.as_view(), name='create_payment_intent'),
    path('capture/<str:payment_intent_id>/', views.CapturePaymentView.as_view(), name='capture_payment'),
    path('status/<str:payment_intent_id>/', views.PaymentStatusView.as_view(), name='payment_status'),
    path('refund/', views.RefundRequestView.as_view(), name='refund_request'),
    path('refunds/', views.RefundListView.as_view(), name='refunds'),
    path('transactions/', views.TransactionListView.as_view(), name='transactions'),
    path('transactions/<str:transaction_id>/', views.TransactionDetailView.as_view(), name='transaction_detail'),
    path('webhooks/paymob/', views.PaymobWebhookView.as_view(), name='paymob_webhook'),
    path('webhooks/stripe/', views.StripeWebhookView.as_view(), name='stripe_webhook'),
    path('stats/', views.payment_stats, name='payment_stats'),
]