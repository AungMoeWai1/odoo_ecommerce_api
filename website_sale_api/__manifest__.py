{
    "name": "Website Sale API",
    "version": "1.0",
    "summary": "REST API for website sale in Odoo 19",
    "category": "website",
    "author": "SME Intellect",
    "website": "https://www.smeintellect.com",
    "license": "LGPL-3",
    "depends": ["web", "product", "website_sale", "website_sale_wishlist"],
    "external_dependencies": {"python": ["PyJWT", "pydantic"]},
    "data": [],
    "installable": True,
    "application": False,
}
