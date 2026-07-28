{
    "name": "Website Sale API",
    "version": "1.0",
    "summary": "REST API for website sale in Odoo 19",
    "category": "website",
    "author": "SME Intellect",
    "website": "https://www.smeintellect.com",
    "license": "LGPL-3",
    "depends": ["web", "product", "website_sale", "stock", "website_sale_wishlist"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_township_views.xml",
        "views/res_partner_views.xml",
        "views/address_templates.xml",
        "views/delivery_carrier_views.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_sale_api/static/src/interactions/**/*",
        ]
    },
    "installable": True,
    "application": False,
}
