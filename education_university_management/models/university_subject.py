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
from odoo import fields, models


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
