from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import fields, models


class BeautyInServiceReportWizard(models.TransientModel):
    _name = 'beauty.in.service.report.wizard'
    _description = 'Create report'

    disease_id = fields.Many2one(
        comodel_name="beauty.in.service",
    )
    disease_count = fields.Integer()


class HrHospitalHospitalReportWizard(models.TransientModel):
    _name = 'hr.hospital.hospital.report.wizard'
    _description = 'Create report'

    report_date = fields.Date(string="Report date")

    def create_report(self):
        """
        Create record for `hr.hospital.hospital.report.wizard`
        model
        """
        self.ensure_one()
        delta = relativedelta(months=1, day=1)
        report_date = fields.Date.to_date(self.report_date)
        start_date = datetime(report_date.year, report_date.month, 1)
        end_date = datetime(report_date.year, report_date.month, 1) + delta
        search_domain = ["&", ("diagnosis_date", ">=", start_date.date()),
                              ("diagnosis_date", "<", end_date.date())]
        disease_ids = set()
        result = dict()
        diagnoses_list = self.env[
            'hr.hospital.diagnosis'
        ].search(search_domain)
        for diagnoses in diagnoses_list:
            disease_ids.add(diagnoses.disease_id)
        for disease in disease_ids:
            disease_count = diagnoses_list.search_count(
                [("disease_id", "=", disease.id)]
            )
            result[disease] = disease_count
        for key, val in result.items():
            self.env[
                "hr.hospital.disease.report.wizard"
            ].create({'disease_id': key.id, 'disease_count': val})
