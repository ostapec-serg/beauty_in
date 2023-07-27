from datetime import timedelta

from odoo import fields, models, api, _
from odoo.addons.beauty_in import constants as const
from odoo.exceptions import ValidationError


class BeautyInMasterSchedule(models.Model):
    _name = 'beauty.in.master.schedule'
    _description = 'Master Schedule'
    _order = "shift_date"

    shift_date = fields.Date(
        required=True
    )
    day_week = fields.Char(
        string="Day of the week",
        compute="_compute_day_week",
    )
    shift_duration = fields.Selection(
        selection=const.WORK_SHIFT_DURATION,
        required=True,
        default="8"
    )
    location_id = fields.Many2one(
        comodel_name="beauty.in.location",
        required=True
    )
    shift_start_time = fields.Datetime(string="Start time")
    shift_end_time = fields.Datetime(
        compute="_compute_shift_end_time",
        store=True
    )
    master_id = fields.Many2one(
        comodel_name="hr.employee",
        domain=[('employee_type', '=', 'master')],
        ondelete="cascade",
        required=True
    )
    # tz_offset = fields.Char(compute='_compute_tz_offset',
    # string='Timezone offset', invisible=True)
    # TODO Add to calendar view.
    appointments_ids = fields.One2many(
        comodel_name="beauty.in.appointment",
        inverse_name="schedule_id"
    )

    @api.model
    def create(self, vals_list):
        self._is_available_schedule_time(vals_list)
        return super().create(vals_list)

    # def write(self, vals):
    #     """
    #     Updates all records in ``self`` with the provided values.
    #     """
    #  TODO add checking func for location
    # for rec in self:
    #     if vals.get('shift_start_time', ""):
    #         rec._is_available_schedule_time(vals)
    # return super().write(vals)

    @api.onchange('shift_date')
    @api.depends('shift_date')
    def _compute_day_week(self):
        """
        Compute dy of the week based on shift_date field
        """
        if self.shift_date:
            day_week = self.shift_date.strftime('%A')
            self.day_week = day_week.capitalize()
        else:
            self.day_week = None

    # @api.depends('tz')
    # def _compute_tz_offset(self):
    #     for user in self:
    #         user.tz_offset = datetime.datetime.now(
    #         pytz.timezone(user.tz or 'GMT')
    #         ).strftime('%z')

    def name_get(self) -> list:
        """ Build display name """
        return [
            (schedule.id, f"[{schedule.shift_date}, "
                          f"{schedule.master_id.name}]") for schedule in self
        ]

    @api.onchange('shift_start_time', 'shift_duration')
    @api.depends('shift_start_time', 'shift_duration')
    def _compute_shift_end_time(self):
        """
        Computing shift end time depends on
        shift duration and shift start
        """
        for rec in self:
            if rec.shift_start_time and rec.shift_duration:
                shift_duration = int(rec.shift_duration)
                shift_end_delta = timedelta(hours=shift_duration)
                rec.shift_end_time = rec.shift_start_time + shift_end_delta
            else:
                rec.shift_end_time = None

    # TODO Add doctor new schedule checking method.

    @api.onchange('shift_start_time')
    @api.depends('shift_start_time')
    def _get_shift_start_date(self):
        """
        Compute shift_start_time date based on shift_date field
        """
        for rec in self:
            if rec.shift_start_time:
                rec.shift_date = rec.shift_start_time.date()

    def _is_available_schedule_time(self, vals_list):
        dlt = const.delta
        schedule_dtime = fields.Datetime.to_datetime(
            vals_list.get("shift_start_time"))
        master_id = vals_list.get("master_id")
        duration = vals_list.get('shift_duration')
        location_id = vals_list.get('location_id')
        schedule_list = self.get_filtered_schedules(schedule_dtime, master_id)
        new_start = schedule_dtime + dlt
        new_end = schedule_dtime + self.get_duration_dt(duration) + dlt
        # Check if any schedule exist
        for schedule in schedule_list[0]:
            # Checkin whether the specified time does not
            # overlap with existing appointments
            shift_start = schedule.shift_start_time
            shift_end = schedule.shift_end_time
            if shift_start < (new_start or new_end) < shift_end:
                raise ValidationError(
                    _("The new schedule intersects"
                      " with the existing one!"
                      )
                )
        if location_id:
            params = {
                'schedules': schedule_list[1],
                'new_shift_start': new_start,
                'new_shift_end': new_end,
                'location_id': location_id,
            }
            self._check_location_time(params)
        return True

    def get_duration_dt(self, duration):
        duration = timedelta(hours=int(duration))
        return duration

    def _check_location_time(self, params):
        schedules = params['schedules']
        new_shift_start = params['new_shift_start']
        new_shift_end = params['new_shift_end']
        location_id = params['location_id']
        for schedule in schedules:
            # Checkin whether the specified location does not
            # overlap with existing schedules in this location
            shift_start = schedule.shift_start_time
            shift_end = schedule.shift_end_time
            if new_shift_start < (shift_start or shift_end) < new_shift_end:
                loc_id = schedule.location_id.id
                if loc_id == location_id:
                    raise ValidationError(
                        _("Specified location is busy!"
                          " Choose another time or another location!"
                          )
                    )
        return True

    def get_filtered_schedules(self, shift_date, master_id):
        schedules = self.search([
            ('shift_date', '=', shift_date.date())
        ])
        # Getting schedules for current master
        master_schedules = [
            s for s in schedules if s.master_id.id == master_id
        ]
        # Getting schedules for another masters
        masters_schedules = [
            s for s in schedules if s.master_id.id != master_id
        ]
        return [master_schedules, masters_schedules]
