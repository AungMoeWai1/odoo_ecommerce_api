"""Controller for handling invoice-related API endpoints in the Odoo eCommerce module."""

# pylint: disable=too-few-public-methods,import-error

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request

from ..services.invoice_service import InvoiceService
from ..services.token_service import JWTService
from .base import BaseAPI


class InvoiceController(BaseAPI):
    """API controller for handling invoice-related requests"""

    @http.route(
        "/api/invoices",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
    )
    @JWTService.jwt_required()
    def get_invoices(self, **kwargs):
        """Retrieve a list of invoice with pagination and sorting"""
        try:
            user = request.authenticated_user
            result = InvoiceService().get_invoices(user=user, kwargs=kwargs)
            return self._success(result)
        except ValidationError as e:
            return self._error(str(e), code=400)

    @http.route(
        "/api/invoices/<int:invoice_id>",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
    )
    @JWTService.jwt_required()
    def get_invoice(self, invoice_id):
        """Retrieve an invoice with pagination and sorting"""
        try:
            user = request.authenticated_user
            result = InvoiceService().get_invoice_detail(
                user=user, invoice_id=invoice_id
            )
            return self._success(result, wrap_in_data=True)
        except ValidationError as e:
            return self._error(message=str(e), code=400)
