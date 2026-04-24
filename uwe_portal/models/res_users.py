# -*- coding: utf-8 -*-
###############################################################################
#
#    UWE Portal Models
#    Copyright (C) 2024 UWE
#
###############################################################################

from odoo import models, fields, api, _


class ResUsers(models.Model):
    """Extend res.users to add Employee Portal User type"""
    _inherit = 'res.users'

    user_type = fields.Selection([
        ('internal', 'Internal User'),
        ('portal', 'Portal User'),
        ('public', 'Public'),
        ('employee_portal', 'Employee Portal User'),
    ], string='User Type', default='internal', required=True,
       help="Internal User: Full system access\n"
            "Portal User: Limited portal access\n"
            "Public: Public user access\n"
            "Employee Portal User: Portal access for employees")

    def _get_type_groups(self):
        return {
            'internal': self.env.ref('base.group_user'),
            'portal': self.env.ref('base.group_portal'),
            'public': self.env.ref('base.group_public', raise_if_not_found=False),
            'employee_portal': self.env.ref('base.group_portal'),
        }

    @api.model
    def create(self, vals):
        user_type = vals.get('user_type', 'internal')
        type_groups = self._get_type_groups()
        employee_portal_group = self.env.ref(
            'uwe_portal.uwe_portal_group_employee_portal', raise_if_not_found=False
        )

        # Build the set of group IDs for the chosen user type
        group_ids = [type_groups[user_type].id] if type_groups.get(user_type) else []
        if user_type == 'employee_portal' and employee_portal_group:
            group_ids.append(employee_portal_group.id)

        if group_ids:
            vals['groups_id'] = [(6, 0, group_ids)]

        return super(ResUsers, self).create(vals)

    def write(self, vals):
        if 'user_type' not in vals:
            return super(ResUsers, self).write(vals)

        type_groups = self._get_type_groups()
        employee_portal_group = self.env.ref(
            'uwe_portal.uwe_portal_group_employee_portal', raise_if_not_found=False
        )
        new_type = vals['user_type']

        # All mutually exclusive base user-type groups
        exclusive_group_ids = {g.id for g in type_groups.values() if g}

        for user in self:
            current_ids = set(user.groups_id.ids)

            # Groups to add for the new type
            add_ids = set()
            target_group = type_groups.get(new_type)
            if target_group:
                add_ids.add(target_group.id)
            if new_type == 'employee_portal' and employee_portal_group:
                add_ids.add(employee_portal_group.id)

            # Remove all exclusive type groups not in add_ids, plus employee_portal when leaving that type
            remove_ids = (exclusive_group_ids - add_ids) & current_ids
            if new_type != 'employee_portal' and employee_portal_group:
                if employee_portal_group.id in current_ids:
                    remove_ids.add(employee_portal_group.id)

            # Only act on groups that actually change
            add_ids -= current_ids

            commands = (
                [(3, gid) for gid in remove_ids] +
                [(4, gid) for gid in add_ids]
            )
            if commands:
                # Single atomic write — constraint fires once on the final valid state
                super(ResUsers, user).write({'groups_id': commands})

        return super(ResUsers, self).write(vals)
