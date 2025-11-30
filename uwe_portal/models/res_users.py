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

    @api.model
    def create(self, vals):
        """Set groups based on user type"""
        user_type = vals.get('user_type', 'internal')
        portal_group = self.env.ref('base.group_portal')
        
        if user_type == 'employee_portal':
            # For employee portal users, ensure portal group and employee portal group are added
            employee_portal_group = self.env.ref('uwe_portal.uwe_portal_group_employee_portal', raise_if_not_found=False)
            group_ids_to_add = [portal_group.id]
            if employee_portal_group:
                group_ids_to_add.append(employee_portal_group.id)
            
            if 'groups_id' not in vals:
                vals['groups_id'] = [(6, 0, group_ids_to_add)]
            else:
                # Check if portal group is already included
                group_ids = vals.get('groups_id', [])
                portal_included = False
                
                # Check existing groups
                for item in group_ids:
                    if isinstance(item, tuple):
                        if item[0] == 6 and len(item) == 3:  # (6, 0, [ids])
                            if portal_group.id in item[2]:
                                portal_included = True
                                break
                        elif item[0] == 4 and item[1] == portal_group.id:  # (4, id)
                            portal_included = True
                            break
                
                if not portal_included:
                    # Add portal group and employee portal group
                    if group_ids and isinstance(group_ids[0], tuple) and group_ids[0][0] == 6:
                        # Update existing (6, 0, [ids])
                        existing_ids = group_ids[0][2] if len(group_ids[0]) == 3 else []
                        vals['groups_id'] = [(6, 0, list(set(existing_ids + group_ids_to_add)))]
                    else:
                        # Add portal group
                        if not group_ids:
                            vals['groups_id'] = [(6, 0, group_ids_to_add)]
                        else:
                            for gid in group_ids_to_add:
                                group_ids.append((4, gid))
                            vals['groups_id'] = group_ids
        elif user_type == 'portal':
            # For portal users, ensure portal group is added
            if 'groups_id' not in vals:
                vals['groups_id'] = [(6, 0, [portal_group.id])]
            else:
                # Check if portal group is already included
                group_ids = vals.get('groups_id', [])
                portal_included = False
                
                # Check existing groups
                for item in group_ids:
                    if isinstance(item, tuple):
                        if item[0] == 6 and len(item) == 3:  # (6, 0, [ids])
                            if portal_group.id in item[2]:
                                portal_included = True
                                break
                        elif item[0] == 4 and item[1] == portal_group.id:  # (4, id)
                            portal_included = True
                            break
                
                if not portal_included:
                    # Add portal group
                    if group_ids and isinstance(group_ids[0], tuple) and group_ids[0][0] == 6:
                        # Update existing (6, 0, [ids])
                        existing_ids = group_ids[0][2] if len(group_ids[0]) == 3 else []
                        vals['groups_id'] = [(6, 0, list(set(existing_ids + [portal_group.id])))]
                    else:
                        # Add portal group
                        if not group_ids:
                            vals['groups_id'] = [(6, 0, [portal_group.id])]
                        else:
                            group_ids.append((4, portal_group.id))
                            vals['groups_id'] = group_ids
        
        return super(ResUsers, self).create(vals)

    def write(self, vals):
        """Update groups when user type changes"""
        if 'user_type' in vals:
            portal_group = self.env.ref('base.group_portal')
            public_group = self.env.ref('base.group_public', raise_if_not_found=False)
            
            for user in self:
                if vals['user_type'] == 'employee_portal':
                    # Add portal group
                    if portal_group.id not in user.groups_id.ids:
                        user.write({'groups_id': [(4, portal_group.id)]})
                    # Add employee portal user group (to identify and hide portal menus)
                    employee_portal_group = self.env.ref('uwe_portal.uwe_portal_group_employee_portal', raise_if_not_found=False)
                    if employee_portal_group and employee_portal_group.id not in user.groups_id.ids:
                        user.write({'groups_id': [(4, employee_portal_group.id)]})
                    # Remove public group if exists
                    if public_group and public_group.id in user.groups_id.ids:
                        user.write({'groups_id': [(3, public_group.id)]})
                elif vals['user_type'] == 'portal':
                    # Ensure portal group is added
                    if portal_group.id not in user.groups_id.ids:
                        user.write({'groups_id': [(4, portal_group.id)]})
                    # Remove employee portal user group if exists
                    employee_portal_group = self.env.ref('uwe_portal.uwe_portal_group_employee_portal', raise_if_not_found=False)
                    if employee_portal_group and employee_portal_group.id in user.groups_id.ids:
                        user.write({'groups_id': [(3, employee_portal_group.id)]})
                    # Remove internal groups if any
                    internal_groups = user.groups_id.filtered(
                        lambda g: g.category_id.xml_id == 'base.module_category_human_resources'
                    )
                    if internal_groups:
                        user.write({'groups_id': [(3, g.id) for g in internal_groups]})
                    # Remove public group if exists
                    if public_group and public_group.id in user.groups_id.ids:
                        user.write({'groups_id': [(3, public_group.id)]})
                elif vals['user_type'] == 'public':
                    # Add public group
                    if public_group and public_group.id not in user.groups_id.ids:
                        user.write({'groups_id': [(4, public_group.id)]})
                    # Remove portal group if exists
                    if portal_group.id in user.groups_id.ids:
                        user.write({'groups_id': [(3, portal_group.id)]})
                    # Remove internal groups if any
                    internal_groups = user.groups_id.filtered(
                        lambda g: g.category_id.xml_id == 'base.module_category_human_resources'
                    )
                    if internal_groups:
                        user.write({'groups_id': [(3, g.id) for g in internal_groups]})
                elif vals['user_type'] == 'internal':
                    # Remove portal group if exists
                    if portal_group.id in user.groups_id.ids:
                        user.write({'groups_id': [(3, portal_group.id)]})
                    # Remove employee portal user group if exists
                    employee_portal_group = self.env.ref('uwe_portal.uwe_portal_group_employee_portal', raise_if_not_found=False)
                    if employee_portal_group and employee_portal_group.id in user.groups_id.ids:
                        user.write({'groups_id': [(3, employee_portal_group.id)]})
                    # Remove public group if exists
                    if public_group and public_group.id in user.groups_id.ids:
                        user.write({'groups_id': [(3, public_group.id)]})
        
        return super(ResUsers, self).write(vals)


