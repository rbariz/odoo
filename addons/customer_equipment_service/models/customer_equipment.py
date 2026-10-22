from odoo import api, fields, models
from odoo.exceptions import ValidationError


class CustomerEquipment(models.Model):
    _name = "customer.equipment"
    _description = "Customer Equipment"
    _rec_names_search = ["code", "name"]

    name = fields.Char(
        string="Equipment Name",
        required=True,
    )

    code = fields.Char(
        string="Equipment Code",
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

    intervention_count = fields.Integer(
        string="Intervention Count",
        compute="_compute_intervention_count",
    )

    confirmed_intervention_count = fields.Integer(
        string="Confirmed Intervention Count",
        compute="_compute_confirmed_intervention_count",
    )

    intervention_ids = fields.One2many(
        comodel_name="customer.intervention",
        inverse_name="equipment_id",
        string="Interventions",
    )

    def action_view_interventions(self):
        self.ensure_one()

        action = self.env["ir.actions.act_window"]._for_xml_id(
            "customer_equipment_service.action_customer_intervention"
        )
        action["domain"] = [
            ("equipment_id", "=", self.id),
        ]

        action["context"] = dict(
            self.env.context,
            default_equipment_id=self.id,
            default_partner_id=self.partner_id.id,
            lock_equipment_customer=True,
        )

        return action

    def action_view_confirmed_interventions(self):
        self.ensure_one()

        action = self.env["ir.actions.act_window"]._for_xml_id(
            "customer_equipment_service.action_customer_intervention"
        )
        action["domain"] = [
            ("equipment_id", "=", self.id),
            ("state", "=", "confirmed"),
        ]
        action["context"] = dict(
            self.env.context,
            default_equipment_id=self.id,
            default_partner_id=self.partner_id.id,
            lock_equipment_customer=True,
        )

        return action




    @api.constrains("partner_id")
    def _check_partner_matches_linked_interventions(self):
        for equipment in self:
            inconsistent_intervention = self.env["customer.intervention"].sudo().search([
                ("equipment_id", "=", equipment.id),
                ("partner_id", "!=", equipment.partner_id.id),
            ], limit=1)

            if inconsistent_intervention:
                raise ValidationError(
                    "You cannot change this equipment's customer "
                    "because it would conflict with a linked intervention."
                )

    @api.depends("code", "name")
    def _compute_display_name(self):
        for equipment in self:
            code = equipment.code or ""
            name = equipment.name or ""

            equipment.display_name = (
                f"[{code}] {name}" if code else name
            )

    @api.depends("intervention_ids")
    def _compute_intervention_count(self):
        for equipment in self:
            equipment.intervention_count = len(equipment.intervention_ids)

    @api.depends("intervention_ids.state")
    def _compute_confirmed_intervention_count(self):
        groups = self.env["customer.intervention"]._read_group(
            domain=[
                ("equipment_id", "in", self.ids),
                ("state", "=", "confirmed"),
            ],
            groupby=["equipment_id"],
            aggregates=["__count"],
        )

        counts = {
            equipment.id: count
            for equipment, count in groups
        }

        for equipment in self:
            equipment.confirmed_intervention_count = counts.get(
                equipment.id, 0
            )
