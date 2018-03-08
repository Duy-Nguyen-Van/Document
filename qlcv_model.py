# -*- coding: utf-8 -*-
from odoo import models, fields,api
from datetime import datetime
# import os
# import re
# import json
# import base64
# import logging
# import mimetypes
#
# from odoo import _
# from odoo import models, api, fields
# from odoo.tools import ustr
# from odoo.tools.mimetypes import guess_mimetype
# from odoo.exceptions import ValidationError, AccessError

from odoo.addons.muk_dms.models import dms_base

class Document(models.Model):
     _name = 'doc.task'
     _description = 'Document'
     _inherit = ['mail.thread','muk_dms.file']
     filename = fields.Char('Name',required=True)
     number = fields.Char('Number',required=True)
     sign_date = fields.Datetime('Sign Date')
     sent_date = fields.Datetime('Sent Date')
     arrived_date = fields.Datetime('Arrived Date',default=datetime.today())
     # composer_id = fields.Many2one('hr.employee' , 'Composer')
     # approver_id = fields.Many2one('hr.employee' , 'Approver')
     # sender_id = fields.Many2one('hr.employee' , 'Sender')
     organization = fields.Many2one('res.partner','Organization',required=True)
     department_id = fields.Many2one('hr.department' , 'Department')
     type = fields.Char('Type',required=True, default='Arrived', readonly=True)
     otherinfor = fields.Text('Notes')
     # type_id = fields.Many2one('doc.type','Type',required=True)
     # data = fields.Binary(
     #     string='File',
     #     )
     data = fields.Many2one('muk_dms.file','File')
     # filename = fields.Char(
     #     string="Filename",
     #     required=True)
     state = fields.Selection([
          ('draft','Draft'),
          ('sent','Email Sent'),
          ('done','Done'),
          ('cancel','Cancelled'),
     ],string='Document Status', readonly=True, copy=False, store=True, default='draft')
     tag = fields.Many2many('tag.doc', string='Tag')

     @api.multi
     def action_document_send(self):
         '''
         This function opens a window to compose an email, with the edi sale template message loaded by default
         '''
         self.ensure_one()
         attachment = {
             'name': ("%s" % self.name),
             'datas': self.data.content,
             'datas_fname': self.name,
             'res_model': 'doc.task',
             'type': 'binary'
         }
         id = self.env['ir.attachment'].create(attachment)
         email_template = self.env.ref('islabdocument.email_template_doc')
         email_template.attachment_ids = False
         email_template.attachment_ids = [(4,id.id)]
         ir_model_data = self.env['ir.model.data']
         try:
             template_id = ir_model_data.get_object_reference('islabdocument', 'email_template_doc')[1]
         except ValueError:
             template_id = False
         try:
             compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
         except ValueError:
             compose_form_id = False
         ctx = dict()
         ctx.update({
             'default_model': 'doc.task',
             'default_res_id': self.ids[0],
             'default_use_template': bool(template_id),
             'default_template_id': template_id,
             'default_composition_mode': 'comment',
             'mark_so_as_sent': True,
         })
         return {
             'type': 'ir.actions.act_window',
             'view_type': 'form',
             'view_mode': 'form',
             'res_model': 'mail.compose.message',
             'views': [(compose_form_id, 'form')],
             'view_id': compose_form_id,
             'target': 'new',
             'context': ctx,
         }

     @api.multi
     def action_convert(self):
          for doc in self:
               doc.state = 'done'

     @api.multi
     def action_cancel(self):
         for doc in self:
             doc.state = 'cancel'

     @api.multi
     def print_document(self):
        result = self.pool.get('data').get_pdf(cr, uid, [0], data, context=ctx)

     # def notify_change(self, values, refresh=False, operation=None):
     #     super(Document, self).notify_change(values, refresh, operation)
     #     if "index_files" in values:
     #         self._compute_index()
     #     if "save_type" in values:
     #         self._update_reference_type()
     #
     # def trigger_computation_up(self, fields):
     #     self.directory.trigger_computation(fields)
     #
     # def trigger_computation(self, fields, refresh=True, operation=None):
     #     super(Document, self).trigger_computation(fields, refresh, operation)
     #     values = {}
     #     if "settings" in fields:
     #         values.update(self.with_context(operation=operation)._compute_settings(write=False))
     #     if "path" in fields:
     #         values.update(self.with_context(operation=operation)._compute_path(write=False))
     #         values.update(self.with_context(operation=operation)._compute_relational_path(write=False))
     #     if "extension" in fields:
     #         values.update(self.with_context(operation=operation)._compute_extension(write=False))
     #     if "mimetype" in fields:
     #         values.update(self.with_context(operation=operation)._compute_mimetype(write=False))
     #     if "index_content" in fields:
     #         values.update(self.with_context(operation=operation)._compute_index(write=False))
     #     if values:
     #         self.write(values);
     #         if "settings" in fields:
     #             self.notify_change({'save_type': self.settings.save_type})
     #
     #     # ----------------------------------------------------------
     #     # Read, View
     #     # ----------------------------------------------------------
     #
     # def _compute_settings(self, write=True):
     #     if write:
     #         for record in self:
     #             record.settings = record.directory.settings
     #     else:
     #         self.ensure_one()
     #         return {'settings': self.directory.settings.id}
     #
     # def _compute_extension(self, write=True):
     #     if write:
     #         for record in self:
     #             record.extension = os.path.splitext(record.filename)[1]
     #     else:
     #         self.ensure_one()
     #         return {'extension': os.path.splitext(self.filename)[1]}
     #
     # def _compute_mimetype(self, write=True):
     #     def get_mimetype(record):
     #         mimetype = mimetypes.guess_type(record.filename)[0]
     #         if (not mimetype or mimetype == 'application/octet-stream') and record.content:
     #             mimetype = guess_mimetype(base64.b64decode(record.content))
     #         return mimetype or 'application/octet-stream'
     #
     #     if write:
     #         for record in self:
     #             record.mimetype = get_mimetype(record)
     #     else:
     #         self.ensure_one()
     #         return {'mimetype': get_mimetype(self)}
     #
     # def _compute_path(self, write=True):
     #     if write:
     #         for record in self:
     #             record.path = "%s%s" % (record.directory.path, record.filename)
     #     else:
     #         self.ensure_one()
     #         return {'path': "%s%s" % (self.directory.path, self.filename)}
     #
     # def _compute_relational_path(self, write=True):
     #     def get_relational_path(record):
     #         path = json.loads(record.directory.relational_path)
     #         path.append({
     #             'model': record._name,
     #             'id': record.id,
     #             'name': record.filename})
     #         return json.dumps(path)
     #
     #     if write:
     #         for record in self:
     #             record.relational_path = get_relational_path(record)
     #     else:
     #         self.ensure_one()
     #         return {'relational_path': get_relational_path(self)}
     #
     # def _compute_index(self, write=True):
     #     def get_index(record):
     #         type = record.mimetype.split('/')[0] if record.mimetype else record._compute_mimetype(write=False)[
     #             'mimetype']
     #         index_files = record.settings.index_files if record.settings else record.directory.settings.index_files
     #         if type and type.split('/')[0] == 'text' and record.content and index_files:
     #             words = re.findall("[^\x00-\x1F\x7F-\xFF]{4,}", base64.b64decode(record.content))
     #             return ustr("\n".join(words))
     #         else:
     #             return None
     #
     #     if write:
     #         for record in self:
     #             record.index_content = get_index(record)
     #     else:
     #         self.ensure_one()
     #         return {'index_content': get_index(self)}
     #
     # def _compute_content(self):
     #     for record in self:
     #         record.content = record._get_content()
     #
     # @api.depends('custom_thumbnail')
     # def _compute_thumbnail(self):
     #     for record in self:
     #         if record.custom_thumbnail:
     #             record.thumbnail = record.with_context({}).custom_thumbnail
     #         else:
     #             extension = record.extension and record.extension.strip(".") or ""
     #             path = os.path.join(_img_path, "file_%s.png" % extension)
     #             if not os.path.isfile(path):
     #                 path = os.path.join(_img_path, "file_unkown.png")
     #             with open(path, "rb") as image_file:
     #                 record.thumbnail = base64.b64encode(image_file.read())
     #
     # # ----------------------------------------------------------
     # # Create, Update, Delete
     # # ----------------------------------------------------------
     #
     # @api.constrains('filename')
     # def _check_name(self):
     #     if not self.check_name(self.filename):
     #         raise ValidationError("The file name is invalid.")
     #     childs = self.directory.files.mapped(lambda rec: [rec.id, rec.filename])
     #     duplicates = [rec for rec in childs if rec[1] == self.filename and rec[0] != self.id]
     #     if duplicates:
     #         raise ValidationError("A file with the same name already exists.")
     #
     # def _after_create(self, vals):
     #     record = super(Document, self)._after_create(vals)
     #     record._check_recomputation(vals)
     #     return record
     #
     # def _after_write_record(self, vals, operation):
     #     vals = super(Document, self)._after_write_record(vals, operation)
     #     self._check_recomputation(vals, operation)
     #     return vals
     #
     # def _check_recomputation(self, values, operation=None):
     #     fields = []
     #     if 'filename' in values:
     #         fields.extend(['extension', 'mimetype', 'path'])
     #     if 'directory' in values:
     #         fields.extend(['settings', 'path'])
     #     if 'content' in values:
     #         fields.extend(['index_content'])
     #     if fields:
     #         self.trigger_computation(fields)
     #     self._check_reference_values(values)
     #     if 'size' in values:
     #         self.trigger_computation_up(['size'])
     #
     # def _inverse_content(self):
     #     for record in self:
     #         if record.content:
     #             content = record.content
     #             directory = record.directory
     #             settings = record.settings if record.settings else directory.settings
     #             reference = record.reference
     #             if reference:
     #                 record._update_reference_content(content)
     #             else:
     #                 reference = record._create_reference(
     #                     settings, directory.path, record.filename, content)
     #             record.reference = "%s,%s" % (reference._name, reference.id)
     #             record.size = len(base64.b64decode(content))
     #         else:
     #             record._unlink_reference()
     #             record.reference = None
     #
     # @api.returns('self', lambda value: value.id)
     # def copy(self, default=None):
     #     self.ensure_one()
     #     default = dict(default or [])
     #     names = self.directory.files.mapped('filename')
     #     default.update({'filename': self.unique_name(self.filename, names, self.extension)})
     #     vals = self.copy_data(default)[0]
     #     if 'reference' in vals:
     #         del vals['reference']
     #     if not 'content' in vals:
     #         vals.update({'content': self.content})
     #     new = self.with_context(lang=None).create(vals)
     #     self.copy_translations(new)
     #     return new
     #
     # def _before_unlink_record(self):
     #     super(Document, self)._before_unlink_record()
     #     self._unlink_reference()
     #
     # # ----------------------------------------------------------
     # # Reference
     # # ----------------------------------------------------------
     #
     # def _create_reference(self, settings, path, filename, content):
     #     self.ensure_one()
     #     self.check_access('create', raise_exception=True)
     #     if settings.save_type == 'database':
     #         return self.env['muk_dms.data_database'].sudo().create({'data': content})
     #     return None
     #
     # def _update_reference_content(self, content):
     #     self.ensure_one()
     #     self.check_access('write', raise_exception=True)
     #     self.reference.sudo().update({'content': content})
     #
     # def _update_reference_type(self):
     #     self.ensure_one()
     #     self.check_access('write', raise_exception=True)
     #     if self.reference and self.settings.save_type != self.reference.type():
     #         reference = self._create_reference(self.settings, self.directory.path, self.filename, self.content)
     #         self._unlink_reference()
     #         self.reference = "%s,%s" % (reference._name, reference.id)
     #
     # def _check_reference_values(self, values):
     #     self.ensure_one()
     #     self.check_access('write', raise_exception=True)
     #     if 'content' in values:
     #         self._update_reference_content(values['content'])
     #     if 'settings' in values:
     #         self._update_reference_type()
     #
     # def _get_content(self):
     #     self.ensure_one()
     #     self.check_access('read', raise_exception=True)
     #     return self.reference.sudo().content() if self.reference else None
     #
     # def _unlink_reference(self):
     #     self.ensure_one()
     #     self.check_access('unlink', raise_exception=True)
     #     if self.reference:
     #         self.reference.sudo().delete()
     #         self.reference.sudo().unlink()


class Document_Sent(models.Model):
     _inherit = 'doc.task'
     _name = 'doc.sent'
     type = fields.Char('Type', required=True, default='Sent', readonly=True)
     composer_id = fields.Many2one('hr.employee', 'Composer')
     approver_id = fields.Many2one('hr.employee', 'Approver')
     sender_id = fields.Many2one('hr.employee', 'Sender')
     state = fields.Selection([
          ('draft', 'Draft'),
          ('email','Email Sent'),
          ('published', 'Published'),
          ('sent', 'Sent'),
          ('done', 'Done'),
          ('cancel', 'Cancelled'),
     ], string='Document Status', readonly=True, copy=False, store=True, default='draft')

     @api.multi
     def action_document_send(self):
         '''
         This function opens a window to compose an email, with the edi sale template message loaded by default
         '''
         self.ensure_one()
         attachment = {
             'name': ("%s" % self.name),
             'datas': self.data.content,
             'datas_fname': self.name,
             'res_model': 'doc.sent',
             'type': 'binary'
         }
         id = self.env['ir.attachment'].create(attachment)
         email_template = self.env.ref('islabdocument.email_template_sent')
         email_template.attachment_ids = False
         email_template.attachment_ids = [(4, id.id)]
         ir_model_data = self.env['ir.model.data']
         try:
             template_id = ir_model_data.get_object_reference('islabdocument', 'email_template_sent')[1]
         except ValueError:
             template_id = False
         try:
             compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
         except ValueError:
             compose_form_id = False
         ctx = dict()
         ctx.update({
             'default_model': 'doc.sent',
             'default_res_id': self.ids[0],
             'default_use_template': bool(template_id),
             'default_template_id': template_id,
             'default_composition_mode': 'comment',
             'mark_so_as_sent': True,
         })
         return {
             'type': 'ir.actions.act_window',
             'view_type': 'form',
             'view_mode': 'form',
             'res_model': 'mail.compose.message',
             'views': [(compose_form_id, 'form')],
             'view_id': compose_form_id,
             'target': 'new',
             'context': ctx,
         }

     @api.multi
     def action_confirm(self):
          for doc in self:
              if doc.state == 'email':
                   doc.state = 'published'
              elif doc.state == 'published':
                   doc.state = 'sent'
              elif doc.state == 'sent':
                   doc.state = 'done'

     @api.multi
     def action_cancel(self):
          for doc in self:
               doc.state = 'cancel'

     @api.multi
     def import_file(self, cr, uid, ids, context=None):
          fileobj = TemporaryFile('w+')
          fileobj.write(base64.decodestring(data))
          # your treatment
          return True

class Tag(models.Model):
     _name = 'tag.doc'
     _description = 'Document Tag'
     name = fields.Char('Tag Name')

class MailComposeMessageArrived(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.multi
    def send_mail(self, auto_commit=False):
        if self._context.get('default_model') == 'doc.task' and self._context.get('default_res_id') and self._context.get('mark_so_as_sent'):
            order = self.env['doc.task'].browse([self._context['default_res_id']])
            if order.state == 'draft':
                order.state = 'sent'
            self = self.with_context(mail_post_autofollow=True)
        return super(MailComposeMessageArrived, self).send_mail(auto_commit=auto_commit)

class MailComposeMessageSent(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.multi
    def send_mail(self, auto_commit=False):
        if self._context.get('default_model') == 'doc.sent' and self._context.get('default_res_id') and self._context.get('mark_so_as_sent'):
            order = self.env['doc.sent'].browse([self._context['default_res_id']])
            if order.state == 'draft':
                order.state = 'email'
            self = self.with_context(mail_post_autofollow=True)
        return super(MailComposeMessageSent, self).send_mail(auto_commit=auto_commit)

