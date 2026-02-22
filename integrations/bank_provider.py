from app.models import BankSyncResponse


class BankingAggregator:
    """Represents bank connectivity via secure aggregator API."""

    provider_name = "secure-bank-aggregator"

    def sync_transactions(self, customer_id: str) -> BankSyncResponse:
        count = max(1, len(customer_id) % 7)
        return BankSyncResponse(
            provider=self.provider_name,
            synced_transactions=count,
            status="success",
        )
