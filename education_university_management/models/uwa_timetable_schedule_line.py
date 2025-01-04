from odoo import api, fields, models, _


class UwaTimeScheduleLine(models.Model):
    _name = 'uwa.timetable.schedule.line'


    time_from = fields.Float(string='From', help="Start and End time of Period.", required=True)
    friday_subject = fields.Many2one('university.subject',
                              string='Friday',
                              help="Select the subject to schedule timetable")
    saturday_subject = fields.Many2one('university.subject',
                              string='Saturday',
                              help="Select the subject to schedule timetable")
    sunday_subject = fields.Many2one('university.subject',
                              string='Sunday',
                              help="Select the subject to schedule timetable")
    monday_subject = fields.Many2one('university.subject',
                                     string='Monday',
                                        help="Select the subject to schedule timetable")
    tuesday_subject = fields.Many2one('university.subject',
                                        string='Tuesday',
                                            help="Select the subject to schedule timetable")
    wednesday_subject = fields.Many2one('university.subject',
                                        string='Wednesday',
                                        help="Select the subject to schedule timetable")
    thuresday_subject = fields.Many2one('university.subject',
                                        string='Thursday',
                                        help="Select the subject to schedule timetable")
    timetable_id = fields.Many2one('university.timetable',
                                   required=True, string="Timetable",
                                   help="Relation to university.timetable")