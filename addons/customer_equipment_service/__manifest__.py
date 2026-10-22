{
    "name": "Customer Equipment/Intervention",
    "version": "19.0.1.0.0",
    "summary": "Customer equipment tracking and intervention management",
    "author": "Rachid Bariz",
    "license": "LGPL-3",
    "depends": ["sale"],
    "data": [
        "security/ir.model.access.csv",
        "views/customer_equipment_views.xml",
        "views/customer_intervention_views.xml",
        "report/customer_intervention_report.xml",
    ],
    "installable": True,
    "application": False,
}