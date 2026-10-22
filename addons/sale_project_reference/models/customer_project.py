from odoo import api, fields, models
from odoo.exceptions import ValidationError

class CustomerProject(models.Model):
    _name = "customer.project"
    _description = "Customer Project"
    _rec_names_search = ["code", "name"]

    name = fields.Char(
        string="Project Name",
        required=True,
    )

    code = fields.Char(
        string="Project Code",
        required=True,
    )

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Customer",
        required=True,
        ondelete="restrict",
    )

    active = fields.Boolean(
        default=True,
    )

    @api.constrains("partner_id")
    def _check_partner_matches_linked_orders(self):
        for project in self:
            inconsistent_order = self.env["sale.order"].sudo().search([
                ("customer_project_id", "=", project.id),
                ("partner_id", "!=", project.partner_id.id),
            ], limit=1)

            if inconsistent_order:
                raise ValidationError(
                    "You cannot change this project's customer "
                    "because it would conflict with a linked "
                    "quotation or sales order."
                )
    @api.depends("code", "name")
    def _compute_display_name(self):
        for project in self:
            code = project.code or ""
            name = project.name or ""

            project.display_name = (
                f"[{code}] {name}" if code else name
            )
