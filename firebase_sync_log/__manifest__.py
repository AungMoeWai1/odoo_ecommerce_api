# -*- coding: utf-8 -*-
{
    "name": "Firebase Notification for Odoo Ecommerce Order",
    "summary": "Firebase Notification for Odoo Ecommerce Order",
    "description": """
    Notification with related device token using firebase connection
     for Odoo user to send status of order and delivery status.
    """,
    "author": "SMEi",
    "website": "https://www.smeintellect.com",
    "category": "Website",
    "version": "0.1",
    # any module necessary for this one to work correctly
    "depends": ["base", "web", "website_sale"],
    "external_dependencies": {"python": ["firebase_admin"]},
    # always loaded
    "data": ["views/message_noti_views.xml", "security/ir.model.access.csv"],
    # only loaded in demonstration mode
    "installable": True,
    "application": False,
    "auto_install": True,
    "license": "LGPL-3",
}
