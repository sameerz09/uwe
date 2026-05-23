# -*- coding: utf-8 -*-
###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Jumana Jabin MP (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from odoo import api, fields, models


class UniversitySubject(models.Model):
    """For managing subjects of every courses"""
    _name = 'university.subject'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "University Subjects"

    name = fields.Char(string="Subject", help="Name of the subject")
    is_language = fields.Boolean(string="Language",
                                 help="Tick if this subject is a language")
    is_lab = fields.Boolean(string="Lab", help="Tick if this subject is a Lab")
    code = fields.Char(string="Code", help="Enter the Subject Code")
    type = fields.Selection(
        [('compulsory', 'Compulsory'), ('elective', 'Elective')],
        string='Type', default="compulsory",
        help="Choose the type of the subject")
    weightage = fields.Float(string='Weightage', default=1.0,
                             help="Enter the weightage for this subject")
    description = fields.Text(string='Description',
                              help="Description about the subject")
    parent_subject_id = fields.Many2one('university.subject', string="Parent",
                                        help="Parent subject of this subject")
    is_theory = fields.Boolean(string="Theoritical")
    subject_style = fields.Selection([('campus', 'Campus'), ('online', 'Online')], string='Style', default='campus', required=True)
    pass_mark = fields.Float(string='Pass Mark', help="Enter the pass mark for this subject")
    active = fields.Boolean(default=True)
    timetable_count = fields.Integer(string="Timetables", compute='_compute_timetable_batch_student_count')
    batch_count = fields.Integer(string="Batches", compute='_compute_timetable_batch_student_count')
    student_count = fields.Integer(string="Students", compute='_compute_timetable_batch_student_count')

    def _get_timetable_ids(self, subject_id):
        """Return distinct timetable IDs that include this subject from both schedule line models."""
        lines = self.env['timetable.schedule.line'].search([('subject', '=', subject_id)])
        timetable_ids = set(lines.mapped('timetable_id').ids)

        uwa_lines = self.env['uwa.timetable.schedule.line'].search([
            '|', '|', '|', '|', '|', '|',
            ('monday_subject', '=', subject_id),
            ('tuesday_subject', '=', subject_id),
            ('wednesday_subject', '=', subject_id),
            ('thuresday_subject', '=', subject_id),
            ('friday_subject', '=', subject_id),
            ('saturday_subject', '=', subject_id),
            ('sunday_subject', '=', subject_id),
        ])
        timetable_ids |= set(uwa_lines.mapped('timetable_id').ids)
        return list(timetable_ids)

    def _compute_timetable_batch_student_count(self):
        for subject in self:
            timetable_ids = subject._get_timetable_ids(subject.id)
            timetables = self.env['university.timetable'].browse(timetable_ids)
            batch_ids = timetables.mapped('batch_id').ids

            subject.timetable_count = len(timetable_ids)
            subject.batch_count = len(set(batch_ids))
            subject.student_count = self.env['university.student'].search_count(
                [('batch_id', 'in', batch_ids)]
            )

    def action_open_timetables(self):
        self.ensure_one()
        timetable_ids = self._get_timetable_ids(self.id)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Timetables',
            'res_model': 'university.timetable',
            'view_mode': 'list,form',
            'domain': [('id', 'in', timetable_ids)],
        }

    def action_open_batches(self):
        self.ensure_one()
        timetable_ids = self._get_timetable_ids(self.id)
        timetables = self.env['university.timetable'].browse(timetable_ids)
        batch_ids = list(set(timetables.mapped('batch_id').ids))
        return {
            'type': 'ir.actions.act_window',
            'name': 'Batches',
            'res_model': 'university.batch',
            'view_mode': 'list,form',
            'domain': [('id', 'in', batch_ids)],
        }

    def action_open_students(self):
        self.ensure_one()
        timetable_ids = self._get_timetable_ids(self.id)
        timetables = self.env['university.timetable'].browse(timetable_ids)
        batch_ids = list(set(timetables.mapped('batch_id').ids))
        student_ids = self.env['university.student'].search(
            [('batch_id', 'in', batch_ids)]
        ).ids
        return {
            'type': 'ir.actions.act_window',
            'name': 'Students',
            'res_model': 'university.student',
            'view_mode': 'list,form',
            'domain': [('id', 'in', student_ids)],
        }
