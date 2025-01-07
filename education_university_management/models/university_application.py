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
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class UniversityApplication(models.Model):
    """ For managing student applications to the courses of the university"""
    _name = 'university.application'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Applications for the admission'

    def action_send_mail(self):
        template_id = self.env.ref('education_university_management.email_template_registration_form').id
        template = self.env['mail.template'].browse(template_id)
        print('*********************',template_id)
        template.send_mail(self.id,force_send=True)
        self.state = 'send'

    @api.model
    def create(self, vals):
        """Overriding the create method and assigning
            the sequence for the record"""
        if vals.get('application_no', _('New')) == _('New'):
            vals['application_no'] = self.env['ir.sequence'].next_by_code(
                'university.application') or _('New')
        res = super(UniversityApplication, self).create(vals)
        return res

    name = fields.Char(string='Name', required=True,
                       help="Enter First name of Student")
    middle_name = fields.Char(string='Middle Name',
                              help="Enter Middle name of Student")
    last_name = fields.Char(string='Last Name',
                            help="Enter Last name of Student")
    image = fields.Binary(string='Image',
                          attachment=True,
                          help="Provide the image of the Student")
    academic_year_id = fields.Many2one(
        'university.academic.year',
        string='Academic Year',
        help="Choose Academic year for which the admission is choosing")
    course_id = fields.Many2one(
        'university.course', string="Course",
        required=True,
        help="Enter Course to which the admission is seeking")
    department_ids = fields.Many2many(
        'university.department', string="Department",
        compute="_compute_department_ids",
        help="Enter department to which the admission is seeking")
    department_id = fields.Many2one(
        'university.department', string="Department",
        help="Enter department to which the admission is seeking")
    semester_ids = fields.Many2many('university.semester',
                                    string="Semester",
                                    compute="_compute_semester_ids",
                                    help="Enter semester to which the "
                                         "admission is seeking")
    semester_id = fields.Many2one('university.semester',
                                  string="Semester",
                                  help="Enter semester to which the admission "
                                       "is seeking")
    batch_ids = fields.Many2many('university.batch',
                                 string="Batch", compute="_compute_batch_ids",
                                 help="Enter batch to which the "
                                      "admission is seeking")
    batch_id = fields.Many2one('university.batch', string="Batch",
                               help="Enter batch to which the "
                                    "admission is seeking")
    admission_date = fields.Datetime('Admission Date',
                                     help="Admission Taken date",
                                     default=fields.Datetime.now,
                                     required=True)
    application_no = fields.Char(string='Application  No',
                                 help="Application number of new admission",
                                 readonly=True, related="department_id.compound_name",default=lambda self: _('New'))
    company_id = fields.Many2one('res.company', string='Company',
                                 help="Company of the application",
                                 default=lambda self: self.env.user.company_id)
    email = fields.Char(string="Current email", help="Enter E-mail id for contact purpose")
    phone = fields.Char(string="Mobile 2",
                        help="Enter Phone no. for contact purpose")
    mobile = fields.Char(string="Mobile 1", required=True,
                         help="Enter Mobile num for contact purpose")
    nationality_id = fields.Many2one('res.country',
                                     string='Present nationality', ondelete='restrict',
                                     help="Select the Nationality")
    mother_tongue = fields.Char(string="Mother Tongue",
                                help="Enter Student's Mother Tongue")
    religion = fields.Char(string="Religion",
                           help="My Religion is ")
    caste = fields.Char(string="Caste",
                        help="My Caste is ")
    street = fields.Char(string='Street', help="Enter the street")
    street2 = fields.Char(string='Street2', help="Enter the street2")
    zip = fields.Char(change_default=True, string='ZIP code',
                      help="Enter the Zip Code")
    city = fields.Char(string='City', help="Enter the City name")
    state_id = fields.Many2one("res.country.state", string='State',
                               ondelete='restrict',
                               help="Select the State where you are from")
    country_id = fields.Many2one('res.country', string='Present Country',
                                 ondelete='restrict',
                                 help="Select the Country")
    is_same_address = fields.Boolean(
        string="Permanent Address same as above",
        default=True,
        help="Tick the field if the Present and permanent address is same")
    per_street = fields.Char(string='Street', help="Enter the street")
    per_street2 = fields.Char(string='Street2', help="Enter the street2")
    per_zip = fields.Char(change_default=True, string='ZIP code',
                          help="Enter the Zip Code")
    per_city = fields.Char(string='City', help="Enter the City name")
    per_state_id = fields.Many2one("res.country.state",
                                   string='State', ondelete='restrict',
                                   help="Select the State where you are from")
    per_country_id = fields.Many2one('res.country',
                                     string='Country', ondelete='restrict',
                                     help="Select the Country")
    date_of_birth = fields.Date(string="Date of Birth",
                                help="Enter your DOB")
    guardian_id = fields.Many2one('res.partner', string="Guardian",
                                  domain=[('is_parent', '=', True)],
                                  help="Tell us who will take care of you")
    description = fields.Text(string="Note",
                              help="Description about the application")
    father_name = fields.Char(string="Father", help="My father is")
    mother_name = fields.Char(string="Mother", help="My mother's name is")
    active = fields.Boolean(string='Active', default=True,
                            help="Is the application is active or not")
    document_count = fields.Integer(compute='_compute_document_count',
                                    string='# Documents',
                                    help="Number of documents of application")
    verified_by_id = fields.Many2one('res.users',
                                     string='Verified by',
                                     help="The Document is verified by")
    reject_reason = fields.Many2one('reject.reason',
                                    string='Reject Reason',
                                    help="Application is rejected because")
    gender = fields.Selection(
        [('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
        string='Gender', default='male',
        track_visibility='onchange',
        help="Your Gender is")
    blood_group = fields.Selection(
        [('a+', 'A+'), ('a-', 'A-'), ('b+', 'B+'), ('o+', 'O+'),
         ('o-', 'O-'), ('ab-', 'AB-'), ('ab+', 'AB+')], string='Blood Group',
        default='a+', track_visibility='onchange',
        help="Your Blood Group is")
    state = fields.Selection([('draft', 'Draft'),
                              ('verification', 'Verify'),
                              ('approve', 'Approve'), ('reject', 'Rejected'),
                              ('done', 'Done')], string='State', required=True,
                             default='draft', track_visibility='onchange',
                             help="Status of the application")
    prev_institute = fields.Char('Previous Institute',
                                 help="Previously studied institution",)
    prev_course = fields.Char('Previous Course',
                              help="Previously studied course")
    prev_result = fields.Char('Previous Result',
                              help="Previously studied institution")

    title = fields.Selection(
        [('mr', 'Mr'), ('mrs', 'Mrs'), ('miss', 'Miss'), ('ms', 'Ms')],
        string='Title')
    passport_no = fields.Char(string='Passport Number',
                              help="Enter Passport Number")
    country_issue_id = fields.Many2one('res.country', string='Country of Issue',
                                       ondelete='restrict',
                                       help="Select the Country")
    country_residence_id = fields.Many2one('res.country', string='Country of Residence',
                                           ondelete='restrict',
                                           help="Select the Country")

    address = fields.Char(string='Address', help="Enter the address")
    residance_place = fields.Selection([('yes', 'Yes'), ('no', 'NO')], )
    studied_place = fields.Selection([('yes', 'Yes'), ('no', 'NO')], )
    visa_status = fields.Selection([('work', 'Work'), ('dependent_visa', 'Dependent visa'), ('Visitor', 'Visitor'),
                                    ('student_visit', 'Student Visit')])
    visa_expired = fields.Date(string="Date current visa expires:",
                               help="Enter your visa expired")
    course_ids = fields.One2many('university.med.course', 'app_id', string='Courses')
    academic_ids = fields.One2many('university.academic.qualification', 'academic_id',
                                   string='Academic qualifications ')
    experience_ids = fields.One2many('university.work.experience', 'application_id',
                                   string='Work experience')
    english_requirements = fields.Selection(
        [('ielts', 'IELTS'), ('campridge_toefl', 'CAMBRIDGE TOEFL'), ('pearson_test', 'PEARSON TEST'),
         ('emsat', 'EMSAT'), ('duolingo', 'DUOLINGO')])
    score = fields.Char('Grade / score',)
    date_achieved = fields.Date('Date Achieved',)
    medical_status = fields.Selection([('yes', 'Yes'), ('no', 'NO')], )
    medical_paper = fields.Char(string='If Yes please provide details on a separate sheet of paper.',)
    attachment_ids = fields.Many2many('ir.attachment', string='If Yes please provide details on a separate sheet of paper.')
    # personal_statement_ids = fields.Many2many('ir.attachment',)
    media_type = fields.Selection(
        [('agent', 'Agent'), ('university_website', 'University website'), ('exhibition', 'Exhibition'),
         ('search_engine', 'Search engine'), ('school_visit', 'School Visit')])
    website = fields.Char(string='Website / Online directory listing (please specify)' )
    social_media = fields.Char(string='Social Media website (please specify)')
    other_source = fields.Char(string='Other (please specify)')
    ref_name1 = fields.Char(string='Name')
    ref_name2 = fields.Char(string='Name')
    ref_work1 = fields.Char(string='University/Company')
    ref_work2 = fields.Char(string='University/Company')
    ref_address1 = fields.Char(string='Address')
    ref_address2 = fields.Char(string='Address')
    ref_city1 = fields.Char(string='City')
    ref_city2 = fields.Char(string='City')
    ref_county1 = fields.Char(string='County')
    ref_county2 = fields.Char(string='County')
    ref_postcode1 = fields.Integer(string='Postcode')
    ref_postcode2 =fields.Integer(string='Postcode')
    ref_tel1 = fields.Char(string='Telephone (including international code)')
    ref_tel2 = fields.Char(string='Telephone (including international code)')
    ref_mob1 = fields.Char(string='Mobile (including international code)')
    ref_mob2 = fields.Char(string='Mobile (including international code)')
    ref_email1 = fields.Char(string='Email')
    ref_email2 = fields.Char(string='Email')
    applicant_sign = fields.Binary(string='Signature of Applicant')
    doc_form = fields.Boolean(string='Application Form')
    doc_passport = fields.Boolean(string='Copy of current passport')
    doc_cert = fields.Boolean(string='Copies of your Academic Certificates/Transcripts')
    doc_english = fields.Boolean(string='Copy of your English Language Examination Results')
    doc_visa = fields.Boolean(string='VISA Copy')
    doc_photo = fields.Boolean(string='Personal Photo')
    doc_id = fields.Boolean(string='ID copy')
    user_id = fields.Many2one('res.users', string='Salesperson', readonly=True)
    partner_id = fields.Many2one('res.partner', string='partner', readonly=True)
    sale_id = fields.Many2one('sale.order', string='Sale reference', readonly=True)
    application_type = fields.Selection([('new', 'New'), ('transfered', 'Transfered')], default='new', string="Application Type", required=True)
    last_academic_certificate = fields.Boolean(string='Last Academic Certificate')

    def _compute_document_count(self):
        """Return the count of the documents provided"""
        for rec in self:
            rec.document_count = self.env['university.document'].search_count(
                [('application_ref_id', '=', rec.id)])

    def action_document_view(self):
        """ smart button action of viewing list of documents of application
            :return dict: the list of documents view
        """
        return {
            'name': _('Documents'),
            'domain': [('application_ref_id', '=', self.id)],
            'res_model': 'university.document',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'context': {'default_application_ref_id': self.id}
        }

    def action_send_verification(self):
        """Button action for sending the application for the verification"""
        for rec in self:
            if not self.env['university.document'].search(
                    [('application_ref_id', '=', rec.id)]):
                raise ValidationError(_('No Documents provided'))
            rec.write({
                'state': 'verification'
            })

    def action_verify_application(self):
        """ This method checks the status of documents related to the student
            application. If no documents are provided or if the provided
            documents are not in the 'done' state, it raises a validation error
            Otherwise, it updates the verification status of the application
            and approves it.

            :raises ValidationError: If all documents are not verified or no
                documents are provided.
        """
        for rec in self:
            doc_status = self.env['university.document'].search(
                [('application_ref_id', '=', rec.id)]).mapped('state')
            if doc_status:
                if all(state in 'done' for state in doc_status):
                    rec.write({
                        'verified_by_id': self.env.uid,
                        'state': 'approve'
                    })
                else:
                    raise ValidationError(
                        _('All Documents are not Verified Yet, '
                          'Please complete the verification'))
            else:
                raise ValidationError(_('No Documents provided'))

    def action_reject(self):
        """This method updates the state of the student application to 'reject',
            indicating that the application has been rejected for admission.
        """
        for rec in self:
            rec.write({
                'state': 'reject'
            })

    def action_create_student(self):
        """ This method creates a new student record using the data from the
             application.It populates the student record with the relevant
             information. It also assigns a user login for the student.

            :returns dict: A dictionary containing the information required
                            to open the student form view."""
        for rec in self:
            values = {
                'name': rec.name,
                'last_name': rec.last_name,
                'middle_name': rec.middle_name,
                'application_id': rec.id,
                'student_no': rec.application_no,
                'father_name': rec.father_name,
                'mother_name': rec.mother_name,
                'guardian_id': rec.guardian_id.id,
                'street': rec.street,
                'street2': rec.street2,
                'city': rec.city,
                'state_id': rec.state_id.id,
                'country_id': rec.country_id.id,
                'zip': rec.zip,
                'is_same_address': rec.is_same_address,
                'per_street': rec.per_street,
                'per_street2': rec.per_street2,
                'per_city': rec.per_city,
                'per_state_id': rec.per_state_id.id,
                'per_country_id': rec.per_country_id.id,
                'per_zip': rec.per_zip,
                'gender': rec.gender,
                'date_of_birth': rec.date_of_birth,
                'blood_group': rec.blood_group,
                'nationality_id': rec.nationality_id.id,
                'email': rec.email,
                'mobile': rec.mobile,
                'phone': rec.phone,
                'image_1920': rec.image,
                'is_student': True,
                'religion': rec.religion,
                'caste': rec.caste,
                'mother_tongue': rec.mother_tongue,
                'semester_id': rec.semester_id.id,
                'academic_year_id': rec.academic_year_id.id,
                'company_id': rec.company_id.id,
                'batch_id': rec.batch_id.id,
                'course_id': rec.course_id.id,
            }
            if not rec.is_same_address:
                pass
            else:
                values.update({
                    'per_street': rec.street,
                    'per_street2': rec.street2,
                    'per_city': rec.city,
                    'per_state_id': rec.state_id.id,
                    'per_country_id': rec.country_id.id,
                    'per_zip': rec.zip,
                })
            student = self.env['university.student'].create(values)
            # student.user_id = self.env['res.users'].create({
            #     'name': student.name,
            #     'login': student.email,
            #     'partner_id': student.partner_id.id,
            #     'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])]
            # })
            rec.write({
                'state': 'done'
            })
            return {
                'name': _('Student'),
                'view_mode': 'form',
                'res_model': 'university.student',
                'type': 'ir.actions.act_window',
                'res_id': student.id,
                'context': self.env.context
            }

    @api.depends('course_id')
    def _compute_department_ids(self):
        """ To find the departments in the selected course and assign them
            to department_ids field for setting domain for department_id field
        """
        for rec in self:
            rec.department_ids = self.env['university.department'].search(
                [('course_id', '=',
                  self.course_id.id)]).ids if rec.course_id else False

    @api.depends('department_id')
    def _compute_semester_ids(self):
        """ To find the semester in the selected department and assign them
            to semester_ids field for setting domain for semester_id field"""
        for rec in self:
            rec.semester_ids = self.env['university.semester'].search(
                [('department_id', '=',
                  self.department_id.id)]).ids if rec.department_id else False

    @api.depends('semester_id')
    def _compute_batch_ids(self):
        """ To find the batch in the selected semester and assign them
            to batch_ids field."""
        for rec in self:
            rec.batch_ids = self.env['university.batch'].search(
                [('semester_id', '=',
                  self.semester_id.id)]).ids if rec.semester_id else False

    @api.onchange('date_of_birth')
    def _onchange_date_of_birth(self):
        """ It checks if the provided date of birth makes the person under
            18 years old.
            :raises ValidationError: If the person is under 18."""
        if self.date_of_birth:
            if (fields.date.today().year - self.date_of_birth.year) < 16:
                raise ValidationError(_('Please provide valid date of birth'))

    class UniversityMedCourse(models.Model):
        """Used to managing the courses of university"""
        _name = "university.med.course"
        _description = "University Mediate Courses"
        _inherit = ['mail.thread', 'mail.activity.mixin']

        course_id = fields.Many2one('university.course',
                                    string='Course', )
        app_id = fields.Many2one('university.application',
                                    string='Course', )



    class UniversityAcademicQualification(models.Model):
        _name = "university.academic.qualification"
        _description = "University Acadmic"


        academic_id = fields.Many2one('university.application',
                                      string='Academic',
                                      help="Choose Academic year for which the admission is choosing")
        program = fields.Char(string="program")
        start_date = fields.Date(string="Start Date")
        end_date = fields.Date(string="End Date")
        award_date = fields.Date(string="Date of Award")
        university_id = fields.Many2one('university.config',
                                        string='Name of school')
        result = fields.Char(string="Qualification and Result")
        lang_id = fields.Many2one(
            'res.lang', string='Language Study')

    class UniversityConfig(models.Model):
        _name = 'university.config'

        name = fields.Char(string="University Name")

    class JobTitle(models.Model):
        _name = 'job.title'

        name = fields.Char(string="Job title and nature of work/training")

    class OrganizationName(models.Model):
        _name = 'organization.name'

        name = fields.Char(string="Name of Organization")

    class UniversityWorkExperience(models.Model):
        _name = 'university.work.experience'

        name = fields.Char(string="Work Experience")
        start_date = fields.Date(string="From (mm/yy)")
        end_date = fields.Date(string="To (mm/yy)")
        duty_type = fields.Selection(
        [('part', 'Part time'), ('full', 'Full Time')],
        string='Full- or part-time')
        organization_id = fields.Many2one('organization.name', string='Name of Organization',
                                          ondelete='restrict',
                                          help="Select the Country")
        job_id = fields.Many2one('job.title', string='Job title',
                                 ondelete='restrict', )
        application_id = fields.Many2one('university.application', string='Applicant',
                                         ondelete='restrict', )