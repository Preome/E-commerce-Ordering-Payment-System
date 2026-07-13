from abc import ABC, abstractmethod
import logging

logger = logging.getLogger('payments')


class PaymentProvider(ABC):
    """Abstract base class for all payment providers (Strategy Pattern)."""

    @abstractmethod
    def create_payment(self, order, **kwargs):
        pass

    @abstractmethod
    def confirm_payment(self, transaction_id, **kwargs):
        pass

    @abstractmethod
    def verify_payment(self, transaction_id):
        pass

    @abstractmethod
    def process_webhook(self, payload):
        pass

    @abstractmethod
    def get_provider_name(self):
        pass


class PaymentProcessor:
    """Context class that uses a PaymentProvider strategy."""

    _providers = {}
    _default_provider = None

    @classmethod
    def register_provider(cls, name, provider_instance):
        cls._providers[name] = provider_instance
        logger.info(f"Registered payment provider: {name}")

    @classmethod
    def set_default(cls, name):
        if name not in cls._providers:
            raise ValueError(f"Provider '{name}' not registered")
        cls._default_provider = name

    @classmethod
    def get_provider(cls, name=None):
        provider_name = name or cls._default_provider
        if provider_name not in cls._providers:
            raise ValueError(
                f"Payment provider '{provider_name}' not found. "
                f"Available: {list(cls._providers.keys())}"
            )
        return cls._providers[provider_name]

    @classmethod
    def create_payment(cls, order, provider_name=None, **kwargs):
        provider = cls.get_provider(provider_name)
        logger.info(f"Creating {provider.get_provider_name()} payment for order {order.id}")
        return provider.create_payment(order, **kwargs)

    @classmethod
    def confirm_payment(cls, provider_name, transaction_id, **kwargs):
        provider = cls.get_provider(provider_name)
        return provider.confirm_payment(transaction_id, **kwargs)

    @classmethod
    def verify_payment(cls, provider_name, transaction_id):
        provider = cls.get_provider(provider_name)
        return provider.verify_payment(transaction_id)

    @classmethod
    def process_webhook(cls, provider_name, payload):
        provider = cls.get_provider(provider_name)
        return provider.process_webhook(payload)

    @classmethod
    def available_providers(cls):
        return list(cls._providers.keys())
