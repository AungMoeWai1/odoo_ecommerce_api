"""Controller for handling product ribbons in the e-commerce API."""

# pylint: disable=import-error,too-few-public-methods
from odoo import http
from odoo.exceptions import ValidationError
from ..services.ribbon_service import RibbonService
from .base import BaseAPI


class RibbonController(BaseAPI):
    """API controller for product ribbons."""

    @http.route(
        "/api/product/ribbons",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
    )
    def get_ribbons(self):
        """Fetch all product ribbons."""

        try:
            return self._success(RibbonService().fetch_all_ribbons())

        except ValidationError as e:
            return self._error(
                message=str(e),
                code=400,
            )
