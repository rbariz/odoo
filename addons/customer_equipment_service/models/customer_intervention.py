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

    equipment_code = fields.Char(
        string="Equipment Code",
        related="equipment_id.code",
        readonly=True,
        store=False,
    )

    equipment_code_at_confirmation = fields.Char(
        string="Equipment Code at Confirmation",
        readonly=True,
        copy=False,
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
        if "equipment_code_at_confirmation" in vals:
            raise ValidationError(
                "The equipment code at confirmation "
                "cannot be edited directly."
            )

        target_state = vals.get("state")

        if "state" in vals:
            allowed_transitions = {
                "draft": {"confirmed", "cancel"},
                "confirmed": {"cancel"},
                "cancel": {"draft"},
            }

            for intervention in self:
                if target_state == intervention.state:
                    continue

                if target_state not in allowed_transitions.get(
                    intervention.state, set()
                ):
                    raise ValidationError(
                        f"Transition from '{intervention.state}' "
                        f"to '{target_state}' is not allowed."
                    )

        if target_state != "confirmed":
            return super().write(vals)

        for intervention in self:
            record_vals = dict(vals)

            if intervention.state != "confirmed":
                if "equipment_id" in vals:
                    equipment = self.env["customer.equipment"].browse(
                        vals["equipment_id"]
                    )
                else:
                    equipment = intervention.equipment_id

                record_vals["equipment_code_at_confirmation"] = (
                    equipment.code
                )

            super(CustomerIntervention, intervention).write(record_vals)

        return True

    @api.model_create_multi
    def create(self, vals_list):
        defaults = self.default_get([
            "state",
            "equipment_code_at_confirmation",
        ])

        for vals in vals_list:
            initial_state = vals.get(
                "state", defaults.get("state")
            )
            initial_code = vals.get(
                "equipment_code_at_confirmation",
                defaults.get("equipment_code_at_confirmation"),
            )

            if initial_state != "draft":
                raise ValidationError(
                    "An intervention must be created in draft."
                )

            if initial_code:
                raise ValidationError(
                    "The equipment code at confirmation "
                    "must be empty when creating an intervention."
                )

        return super().create(vals_list)

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        if (
            self.state == "draft"
            and self.equipment_id
            and self.partner_id != self.equipment_id.partner_id
        ):
            self.equipment_id = False