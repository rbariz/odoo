from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    """ customer_project_ref = fields.Char(
        string="Customer Project Reference",
    ) """
    customer_project_id = fields.Many2one(
        comodel_name="customer.project",
        string="Customer Project",
        ondelete="restrict",
    )

    """ def action_confirm(self):
        for order in self:
            reference = (order.customer_project_ref or "").strip()

            if not reference:
                raise UserError(
                    "Please enter a customer project reference "
                    "before confirming the quotation."
                )

        return super().action_confirm() """
    def action_confirm(self):
        for order in self:
            if not order.customer_project_id:
                raise UserError(
                    "Please select a customer project "
                    "before confirming the quotation."
                )

        return super().action_confirm()

    """ @api.constrains("state", "customer_project_ref")
    def _check_customer_project_ref(self):
        for order in self:
            reference = (order.customer_project_ref or "").strip()

            if order.state == "sale" and not reference:
                raise ValidationError(
                    "A confirmed sales order must retain "
                    "a valid customer project reference."
                ) """
    @api.constrains("state", "customer_project_id")
    def _check_customer_project_required(self):
        for order in self:
            if order.state == "sale" and not order.customer_project_id:
                raise ValidationError(
                    "A confirmed sales order must retain "
                    "a customer project."
                )

    @api.constrains("partner_id", "customer_project_id")
    def _check_customer_project_partner(self):
        for order in self:
            project = order.customer_project_id

            if project and project.partner_id != order.partner_id:
                raise ValidationError(
                    "The selected project must belong "
                    "to the sales order customer."
                )