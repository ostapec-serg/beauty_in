from odoo import api, fields, models
from odoo.addons.beauty_in import constants as const


class BeautyLocation(models.Model):
    _name = "beauty.in.location"
    _description = "Beauty Locations"
    _parent_name = "parent_id"
    _parent_store = True
    _order = 'complete_name, id'
    _rec_name = 'complete_name'
    _rec_names_search = ['complete_name', 'barcode']
    _check_company_auto = True

    state = fields.Selection(
        selection=const.STATE_LIST,
        default="draft",
    )
    name = fields.Char('Location Name', required=True)
    complete_name = fields.Char(
        "Full Location Name", compute='_compute_complete_name',
        recursive=True, store=True
    )
    parent_id = fields.Many2one(
        comodel_name='beauty.in.location', string='Parent Location',
        index=True, ondelete='cascade', check_company=True,
        help="The parent location that includes this location. Example : "
             "The 'Dispatch Zone' is the 'Gate 1' parent location."
    )
    child_ids = fields.One2many(
        comodel_name='beauty.in.location', inverse_name='parent_id',
        string='Contains'
    )
    available_service_ids = fields.Many2many(
        comodel_name="beauty.in.beauty.specialty",
        column1="location_id", column2="specialty_id",

    )
    comment = fields.Html('Additional Information')
    parent_path = fields.Char(index=True, unaccent=False)
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env.company, index=True,
        help='Let this field empty if '
             'this location is shared between companies'
    )
    barcode = fields.Char(copy=False)
    active = fields.Boolean(
        default=True,
        help="By unchecking the active field, "
             "you may hide a location without deleting it."
    )
    appointment_ids = fields.One2many(
        comodel_name="beauty.in.appointment",
        inverse_name="location_id"
    )
    today_appointment_ids = fields.One2many(
        comodel_name="beauty.in.appointment",
        inverse_name="location_id",
        domain=[("appointment_date", '=', fields.Date.today())]
    )

    @api.model
    def create(self, vals_list: dict) -> dict:
        """ Creates new records for the model """
        vals_list['state'] = "active"
        return super().create(vals_list)

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for location in self:
            if location.parent_id:
                location.complete_name = '%s/%s' % (
                    location.parent_id.complete_name, location.name
                )
            else:
                location.complete_name = location.name
