from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'payments'
    verbose_name = 'Payments'

    def ready(self):
        from payments.strategy import PaymentProcessor
        from payments.stripe_provider import stripe_provider
        from payments.bkash_provider import bkash_provider

        PaymentProcessor.register_provider('stripe', stripe_provider)
        PaymentProcessor.register_provider('bkash', bkash_provider)
        PaymentProcessor.set_default('stripe')
