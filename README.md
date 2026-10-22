# Odoo Community 19 — Custom Modules

Modules developed by Rachid Bariz.

## Modules

### Sales Project Reference

Extends Sales with customer projects:

- customer project model, views, menus and access rights;
- project selection filtered by customer;
- project required for sales order confirmation;
- server-side customer/project consistency checks;
- project displayed on the quotation/order report;
- selected Sales and Accounting label customizations.

Technical name: `sale_project_reference`

### Customer Equipment Service

Tracks customer equipment and interventions:

- equipment records with archiving and code/name search;
- intervention workflow: Draft, Confirmed and Cancelled;
- server-side creation and transition controls;
- customer/equipment consistency checks;
- intervention counters and filtered navigation buttons;
- contextual creation from equipment;
- QWeb intervention report with PDF output.

Technical name: `customer_equipment_service`

## Requirements

- Odoo Community 19.0
- PostgreSQL and Python dependencies compatible with Odoo 19
- wkhtmltopdf 0.12.6 with patched Qt for PDF reports

Both modules depend on Odoo Sales.
`sale_project_reference` also declares a dependency on Accounting.

## Installation

1. Clone this repository.
2. Add its absolute `addons` directory to the Odoo `addons_path`.
3. Restart Odoo and update the Apps list.
4. Install the required module.

Test installation and updates on a separate database before production use.

## Project Status

Educational project tested in a local Windows environment.

Manual tests cover workflows, consistency checks, access rights,
searches and reports. Automated tests, fresh-database installation,
concurrency and comprehensive multi-company behavior remain to be validated.

## Repository Scope

This repository contains custom module source code and project documentation.
Personal guides, credentials, databases, filestore and local
runtime configuration are excluded.