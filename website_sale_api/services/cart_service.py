"""Service for handling cart-related business logic."""

# pylint:disable=import-error,broad-exception-caught,protected-access
import json

from odoo.exceptions import ValidationError
from odoo.http import request

from ..schemas.cart_schema import CartItemResponse, CartResponse
from .base_service import BaseService


class CartService(BaseService):
    """Service for cart-related operations"""

    def __init__(self, env=None):
        super().__init__(env)
        self.model_name = "sale.order"
        self.website = self._get_current_website()

    def get_current_cart(self, user):
        """Get current cart/sale order for the user"""
        order = self._get_sale_order(self.website.id, user)
        if not order:
            return {"message": "No order found"}

        cart_items = self._build_cart_items(order)
        if not cart_items:
            return {"message": "No cart items found"}

        return self._build_cart_response(order, cart_items)

    def _build_cart_items(self, order):
        """Build cart items list from order lines"""
        return [
            CartItemResponse(
                line_id=line.id,
                product_id=line.product_template_id.id,
                product_variant_id=line.product_id.id,
                variant_name=line.product_id.name,
                product_name=line.product_template_id.name,
                image_url=self._get_image_url("product.product", line.product_id.id),
                quantity=int(line.product_uom_qty),
                unit_price=round(line.price_unit, 2),
                subtotal=line.price_subtotal,
            )
            for line in order.order_line
            if not line.is_delivery
        ]

    def _build_cart_response(self, order, cart_items):
        """Build cart response object"""
        return CartResponse(
            order_id=order.id,
            items=cart_items,
            untax_total=order.amount_untaxed,
            total=order.amount_total,
            currency=order.currency_id.name,
            items_count=len(cart_items),
            discount=0,
            shipping_fee=0,
        )

    def add_to_cart(self, user):
        """Add product to cart"""
        values = self._parse_request_data()
        order = self._get_or_create_cart(user)
        result = self._add_product_to_order(order, values["product_id"], values["qty"])
        if result["line_id"]:
            return {
                "status": "success",
                "id": order.id,
                "message": "Product added to cart",
            }
        raise ValidationError("Product can't added to cart.")

    def delete_cart_item(self, line_id, user):
        """Delete item from cart"""
        order = self._get_or_create_cart(user)
        line = order.order_line.filtered(lambda l: l.id == line_id)
        if not line:
            raise ValidationError(f"Order line {line_id} not found.")
        line.unlink()
        return {
            "status": "success",
            "id": line_id,
            "message": "Order line deleted successfully",
        }

    # ==================== Private Helper Methods ====================
    def _parse_request_data(self):
        """Parse JSON data from request"""
        return json.loads(request.httprequest.data)

    def _get_or_create_cart(self, user):
        """Get existing cart or create new one"""
        order = self._get_sale_order(self.website.id, user)
        return order or self._create_new_order(user)

    def _create_new_order(self, user):
        """Create a new sale order (cart)"""
        return self._create(
            data={
                "partner_id": user.partner_id.id,
                "state": "draft",
                "website_id": self.website.id,
            }
        )

    def _add_product_to_order(self, order, product_id, quantity):
        """Add product to order with proper context"""
        return order.with_context(skip_cart_verification=True)._cart_add(
            product_id, quantity
        )
