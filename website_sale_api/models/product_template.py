"""Models for product templates"""

# pylint:disable=import-error,protected-access,R0913,R0917,R0903,R0914
from odoo import _, fields, models
from odoo.http import request
from odoo.tools import float_is_zero


class ProductTemplate(models.Model):
    """Model for product templates"""

    _inherit = "product.template"

    def _get_combination_info(
        self,
        combination=False,
        product_id=False,
        add_qty=1.0,
        uom_id=False,
        only_template=False,
    ):
        """
        if context of website present, get the value of website
        """
        self.ensure_one()

        if not self.env.context.get("website", False):
            return super()._get_combination_info(
                combination=combination,
                product_id=product_id,
                add_qty=add_qty,
                uom_id=uom_id,
                only_template=only_template,
            )

        combination = combination or self.env["product.template.attribute.value"]

        website = self.env.context.get("website", False)

        uom = self.env["uom.uom"].browse(uom_id) or self.uom_id

        if not product_id and not combination and not only_template:
            combination = self._get_first_possible_combination()

        if only_template:
            product = self.env["product.product"]
        elif product_id:
            product = self.env["product.product"].browse(product_id)
            if combination - product.product_template_attribute_value_ids:
                # If the combination is not fully represented in the given product
                #   make sure to fetch the right product for the given combination
                product = self._get_variant_for_combination(combination)
        else:
            product = self._get_variant_for_combination(combination)

        product_or_template = product or self
        combination = combination or product.product_template_attribute_value_ids

        display_name = product_or_template.with_context(
            display_default_code=False
        ).display_name
        if not product:
            combination_name = combination._get_combination_name()
            if combination_name:
                display_name = f"{display_name} ({combination_name})"

        price_context = product_or_template._get_product_price_context(combination)
        product_or_template = product_or_template.with_context(**price_context)

        combination_info = {
            "combination": combination,
            "product_id": product.id,
            "product_template_id": self.id,
            "display_name": display_name,
            "is_combination_possible": self._is_combination_possible(
                combination=combination
            ),
            **self._get_additionnal_combination_info(
                product_or_template=product_or_template,
                quantity=add_qty or 1.0,
                uom=uom,
                date=fields.Date.context_today(self),
                website=website,
            ),
        }

        if website.google_analytics_key:
            combination_info["product_tracking_info"] = self._get_google_analytics_data(
                product,
                combination_info,
            )

        if (
            product_or_template.type == "combo"
            and website.show_line_subtotals_tax_selection == "tax_included"
            and not all(
                tax.price_include
                for tax in product_or_template.sudo().combo_ids.combo_item_ids.product_id.taxes_id
            )
        ):
            combination_info["tax_disclaimer"] = _(
                "Final price may vary based on selection. Tax will be calculated at checkout."
            )

        return combination_info

    def _get_additionnal_combination_info(
        self, product_or_template, quantity, uom, date, website
    ):
        """Compute additional combination info, based on given parameters.

        :param product_or_template: `product.product` or `product.template` record
            as variant values must take precedence over template values (when we have a variant)
        :param float quantity: requested quantity
        :param uom: `uom.uom` record
        :param date date: today's date, avoids useless calls to today/context_today and harmonize
            behavior
        :param website: `website` record holding the current website of the request (if any),
            or the contextual website (tests, ...)
        :returns: additional product/template information
        :rtype: dict
        """
        if request and hasattr(request, "pricelist"):
            return super()._get_additionnal_combination_info(
                product_or_template, quantity, uom, date, website
            )
        currency = website.currency_id.with_context(self.env.context)

        pricelists = website.pricelist_ids

        # Pricelist price doesn't have to be converted
        pricelist_price, pricelist_rule_id = pricelists[0]._get_product_price_rule(
            product=product_or_template,
            quantity=quantity,
            uom=uom,
            currency=currency,
        )

        price_before_discount = pricelist_price
        pricelist_item = self.env["product.pricelist.item"].browse(pricelist_rule_id)
        if pricelist_item._show_discount_on_shop():
            price_before_discount = pricelist_item._compute_price_before_discount(
                product=product_or_template,
                quantity=quantity or 1.0,
                date=date,
                uom=uom,
                currency=currency,
            )

        has_discounted_price = (
            currency.compare_amounts(price_before_discount, pricelist_price) == 1
        )
        combination_info = {
            "list_price": max(pricelist_price, price_before_discount),
            "price": pricelist_price,
            "has_discounted_price": has_discounted_price,
            "discount_start_date": pricelist_item.date_start,
            "discount_end_date": pricelist_item.date_end,
        }

        if (
            not has_discounted_price
            and product_or_template.compare_list_price
            and self.env["res.groups"]._is_feature_enabled(
                "website_sale.group_product_price_comparison"
            )
        ):
            # depending on product price, should be removed from combination info in the future
            combination_info["compare_list_price"] = (
                product_or_template.currency_id._convert(
                    from_amount=product_or_template.compare_list_price,
                    to_currency=currency,
                    company=self.env.company,
                    date=date,
                    round=False,
                )
            )

        # Apply taxes
        product_taxes = product_or_template.sudo().taxes_id._filter_taxes_by_company(
            self.env.company
        )
        taxes = self.env["account.tax"]
        if product_taxes:
            taxes = request.fiscal_position.map_tax(product_taxes)
            # We do not apply taxes on the compare_list_price value because it's meant to be
            # a strict value displayed as is.
            for price_key in ("price", "list_price"):
                combination_info[price_key] = self._apply_taxes_to_price(
                    combination_info[price_key],
                    currency,
                    product_taxes,
                    taxes,
                    product_or_template,
                    website=website,
                )

        combination_info.update(
            {
                "prevent_zero_price_sale": website.prevent_zero_price_sale
                and float_is_zero(
                    combination_info["price"],
                    precision_rounding=currency.rounding,
                ),
                # additional info to simplify overrides
                "currency": currency,  # displayed currency
                "date": date,
                "product_taxes": product_taxes,  # taxes before fpos mapping
                "taxes": taxes,  # taxes after fpos mapping
            }
        )

        if self.env["res.groups"]._is_feature_enabled(
            "website_sale.group_show_uom_price"
        ):
            price_per_product_uom = uom._compute_price(
                price=combination_info["price"], to_unit=self.uom_id
            )
            combination_info.update(
                {
                    "base_unit_name": product_or_template.base_unit_name,
                    "base_unit_price": product_or_template._get_base_unit_price(
                        price_per_product_uom
                    ),
                }
            )

        if combination_info["prevent_zero_price_sale"]:
            # If price is zero and prevent_zero_price_sale is enabled we don't want to send any
            # price information regarding the product
            combination_info["compare_list_price"] = 0

        return combination_info
