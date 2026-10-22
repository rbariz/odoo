{
    "name": "Sales Project Reference",
    "version": "19.0.1.0.0",
    "summary": "Progressive sales customization for the Odoo lab",
    "author": "Rachid Bariz",
    "license": "LGPL-3",
    "depends": ["sale", "account"],
    "data": [
        "security/ir.model.access.csv",
        "views/sale_order_views.xml",
        "views/account_journal_views.xml",
        "views/customer_project_views.xml",
        "report/saleorder_document_customer_project_report.xml"
    ],
    "installable": True,
    "application": False,
}