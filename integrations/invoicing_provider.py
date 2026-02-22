from app.models import InvoiceRequest, InvoiceResponse


class ApprovedThirdPartyInvoicing:
    """Represents an approved invoicing provider integration."""

    provider_name = "approved-third-party"

    def create_invoice(self, payload: InvoiceRequest) -> InvoiceResponse:
        external_id = f"INV-{payload.customer_id}-{int(payload.amount * 100)}"
        return InvoiceResponse(
            provider=self.provider_name,
            external_invoice_id=external_id,
            status="created",
        )
