# -*- coding: utf-8 -*-
# License, author and contributors information in:
# __openerp__.py file at the root folder of this module.

from openerp import api, models, fields
from dateutil.relativedelta import relativedelta


class Period(models.Model):
    _name = 'period'
    _description = 'Period'

    name = fields.Char(
        string='Name'
    )
    seconds = fields.Integer(
        string='Seconds',
        translate=True
    )
    minutes = fields.Integer(
        string='Minutes',
        translate=True
    )
    hours = fields.Integer(
        string='Hours',
        translate=True
    )
    days = fields.Integer(
        string='Days',
        translate=True
    )
    weeks = fields.Integer(
        string='Weeks',
        translate=True
    )
    months = fields.Integer(
        string='Months',
        translate=True
    )
    years = fields.Integer(
        string='Years',
        translate=True
    )

    @api.multi
    def next(self, date):
        if isinstance(date, str):
            date = fields.Datetime.from_string(date)

        return date + relativedelta(
            years=self.years,
            months=self.months,
            days=self.days,
            weeks=self.weeks,
            hours=self.hours,
            minutes=self.minutes,
            seconds=self.seconds)
