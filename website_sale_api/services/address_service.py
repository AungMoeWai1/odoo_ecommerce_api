"""Service for managing shipping addresses in the Odoo e-commerce API."""

# pylint: disable=too-few-public-methods, import-error,too-many-arguments,too-many-positional-arguments,redefined-builtin,raise-missing-from,consider-using-in
from odoo.exceptions import ValidationError
from odoo.http import request

from ..schemas.address_schema import (
    AddressLine,
    ShippingAddressResponse,
    State,
    StateResponse,
    Township,
    TownshipResponse,
)
from .base_service import BaseService


class ShippingAddressService(BaseService):
    """Service class for managing shipping addresses"""

    def __init__(self):
        super().__init__()
        self.model_name = "res.partner"
        self.website = self._get_current_website()

    def get_state(self, country_id):
        """Get state for a country"""
        states = request.env["res.country.state"].search(
            [("country_id", "=", country_id)]
        )
        return StateResponse(
            country_id=country_id,
            states=[State(id=state.id, name=state.name) for state in states],
        )

    def get_state_townships(self, country_id):
        """get townships excluding a specific country."""
        townships = (request.env["res.township"].sudo().search(
            [("country_id", "=", country_id)]
        ))
        return TownshipResponse(
            country_id=country_id,
            townships=[
                Township(id=tsp.id, name=tsp.name, state_id=tsp.state_id.id)
                for tsp in townships
            ],
        )

    def get_partner_addresses(self, user):
        """get addresses of partner"""
        partner = user.partner_id
        addresses = []
        all_partners = partner | partner.child_ids

        for address in all_partners:
            addresses.append(
                AddressLine(
                    id=address.id,
                    name=address.name,
                    email=address.email,
                    phone=address.phone,
                    street=address.street,
                    city=address.city,
                    zip=address.zip,
                    type=address.type,
                    country=address.country_id.id,
                    state=address.state_id.id,
                    township=address.township_id.id,
                )
            )
        return ShippingAddressResponse(addresses=addresses)

    def create_address(self, user, data):
        """Create a new shipping address for the user"""
        data["parent_id"] = user.partner_id.id
        new_partner = (
            request.env["res.partner"]
            .sudo()
            .with_context(
                {
                    "tracking_disable": True,
                    "no_vat_validation": True,
                }
            )
            .create(data)
        )

        return {"id": new_partner.id, "message": "New Address is created"}

    def update_address(self, user, partner_id, data):
        """Update the user's shipping address with the provided information"""
        if partner_id not in user.child_ids.ids:
            raise ValidationError("Partner not allow")

        address = self.get_record_by_id(partner_id)

        address.write(data)

        return {"id": address.id, "message": "Address updated successfully"}

    def delete_address(self, user, partner_id):
        """Delete the specified shipping address for the user"""
        if partner_id not in user.partner_id.child_ids.ids:
            raise ValidationError("User not found")

        address = self.get_record_by_id(partner_id)
        self._delete(address)

        return {"id": address.id, "message": "Address deleted successfully"}

    def process_address_update(self, user, data):
        """Update the user's shipping address with the provided information"""
        order = self._get_sale_order(self.website.id, user)
        self._write(order, data)
        return {"order_id": order.id, "message": "Address update successfully"}
