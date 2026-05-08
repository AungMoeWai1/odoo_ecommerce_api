"""Service for managing shipping addresses in the Odoo e-commerce API."""

# pylint: disable=too-few-public-methods, import-error,too-many-arguments,too-many-positional-arguments,redefined-builtin,raise-missing-from,consider-using-in
from odoo.http import request
from odoo.exceptions import ValidationError
from ..schemas.address_schema import ShippingAddressResponse, AddressLine


class ShippingAddressService:
    """Service class for managing shipping addresses"""

    def _get_country(self, country):
        """Helper method to retrieve country record by name"""
        if not country:
            return False

        country_rec = (
            request.env["res.country"].sudo().search([("name", "=", country)], limit=1)
        )
        if not country_rec:
            raise ValidationError(f"Country '{country}' not found")

        return country_rec

    def create_shipping_address(
        self, user, name, email, phone, street, city, zip, country
    ):
        """Create a new shipping address for the user"""
        partner = user.partner_id
        if not partner:
            raise ValidationError("Partner not found")

        country_rec = False
        if country:
            country_rec = self._get_country(country)

        shipping_vals = {
            "type": "delivery",
            "parent_id": partner.id,
            "name": name,
            "email": email,
            "phone": phone,
            "street": street,
            "city": city,
            "zip": zip,
            "country_id": country_rec.id if country_rec else False,
        }
        missing = [field for field, value in shipping_vals.items() if not value]
        if missing:
            raise ValidationError(f"Missing required field(s): {', '.join(missing)}")

        request.env["res.partner"].sudo().create(shipping_vals)

        return self.get_shipping_address(user)

    def get_shipping_address(self, user):
        """Get the user's shipping address information"""

        partner = user.partner_id
        if not partner:
            raise ValidationError("Partner not found")

        addresses = []

        all_partners = partner | partner.child_ids

        for address in all_partners:
            addresses.append(
                AddressLine(
                    id=address.id,
                    name=address.name,
                    phone=address.phone,
                    street=address.street,
                    city=address.city,
                    zip=address.zip,
                    type=address.type,
                    is_parent=(address.id == partner.id),
                    country={
                        "id": address.country_id.id if address.country_id else None,
                        "name": address.country_id.name if address.country_id else None,
                    },
                )
            )

        return ShippingAddressResponse(partner_id=partner.id, addresses=addresses)

    def update_shipping_address(
        self,
        user,
        partner_id,
        name,
        email,
        phone,
        street,
        city,
        zip,
        country,
    ):
        """Update the user's shipping address with the provided information"""
        partner = user.partner_id
        if not partner:
            raise ValidationError("Partner not found")

        partner_id = int(partner_id)
        address = request.env["res.partner"].sudo().browse(partner_id)

        if not address.exists():
            raise ValidationError("Address not found")

        if address != partner and address.parent_id != partner:
            raise ValidationError("Unauthorized address")

        vals = {
            "name": name,
            "email": email,
            "phone": phone,
            "street": street,
            "city": city,
            "zip": zip,
        }

        vals = {k: v for k, v in vals.items() if v is not None}

        if country:
            country_rec = self._get_country(country)
            vals["country_id"] = country_rec.id

        address.write(vals)

        return self.get_shipping_address(user)

    def delete_shipping_address(self, user, partner_id):
        """Delete the specified shipping address for the user"""

        partner = user.partner_id
        if not partner:
            raise ValidationError("User not found")

        address = request.env["res.partner"].sudo().browse(partner_id)
        if not address.exists():
            raise ValidationError("Shipping Address not found")

        if address.id == partner.id and address.type == "contact":
            raise ValidationError("Main contact address cannot be deleted")

        address.write({"active": False})

        return self.get_shipping_address(user)


def get_shipping_address_service():
    """Factory method to get an instance of ShippingAddressService"""
    return ShippingAddressService()
