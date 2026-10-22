from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError


class CustomerIntervention(models.Model):
    _name = "customer.intervention"
    _description = "Customer Intervention"

    name = fields.Char(
        string="Intervention Name",
        required=True,
    )

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Customer",
        required=True,
        ondelete="restrict",
    )

    equipment_id = fields.Many2one(
        comodel_name="customer.equipment",
        string="Equipment",
        ondelete="restrict",
    )

    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("cancel", "Cancelled"),
        ],
        string="Status",
        default="draft",
        required=True,
    )

    def action_confirm(self):
        for intervention in self:
            if intervention.state != "draft":
                raise UserError(
                    "Only draft interventions can be confirmed."
                )

            if not intervention.equipment_id:
                raise UserError(
                    "Please select an equipment "
                    "before confirming the intervention."
                )

        self.write({"state": "confirmed"})
        return True
    def action_cancel(self):
        for intervention in self:
            if intervention.state not in ("draft", "confirmed"):
                raise UserError(
                    "Only draft or confirmed interventions "
                    "can be cancelled."
                )

        self.write({"state": "cancel"})
        return True
    def action_reset_to_draft(self):
        for intervention in self:
            if intervention.state != "cancel":
                raise UserError(
                    "Only cancelled interventions "
                    "can be reset to draft."
                )

        self.write({"state": "draft"})
        return True


    @api.constrains("partner_id", "equipment_id")
    def _check_customer_equipment_partner(self):
        for intervention in self:
            equipment = intervention.equipment_id

            if equipment and equipment.partner_id != intervention.partner_id:
                raise ValidationError(
                    "The selected equipment must belong "
                    "to the intervention customer."
                )

    @api.constrains("state", "equipment_id")
    def _check_customer_equipment_required(self):
        for intervention in self:
            if (intervention.state == "confirmed" and not intervention.equipment_id):
                raise ValidationError(
                    "A confirmed intervention must retain "
                    "a customer equipment."
                )
    def write(self, vals):
        if "state" in vals:
            allowed_transitions = {
                "draft": {"confirmed", "cancel"},
                "confirmed": {"cancel"},
                "cancel": {"draft"},
            }

            target_state = vals["state"]

            for intervention in self:
                current_state = intervention.state

                if target_state == current_state:
                    continue

                if target_state not in allowed_transitions.get(
                    current_state, set()
                ):
                    raise ValidationError(
                        f"Transition from '{current_state}' "
                        f"to '{target_state}' is not allowed."
                    )

        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        default_state = None

        for vals in vals_list:
            if "state" in vals:
                initial_state = vals["state"]
            else:
                if default_state is None:
                    default_state = self.default_get(["state"]).get("state")

                initial_state = default_state

            if initial_state != "draft":
                raise ValidationError(
                    "An intervention must be created in draft."
                )

        return super().create(vals_list)