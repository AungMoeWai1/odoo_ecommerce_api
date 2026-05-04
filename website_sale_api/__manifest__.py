{
    "name": "Website Sale API",
    "version": "1.0",
    "summary": "REST API for website sale in odoo 19",
    "category": "website",
    "author": "https://www.smeintelle.com",
    "website": "https://www.smeintelle.com",
    "license": "LGPL-3",
    "depends": ["web", "product", "website_sale"],
    "external_dependencies": {
        "python": ["PyJWT", "pydantic"],
    },
    "data": [],
    "installable": True,
    "application": False,
}
