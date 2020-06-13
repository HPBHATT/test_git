from odoo import api, fields, models, _

class res_config_settings(models.TransientModel):

    _inherit = 'res.config.settings'

    is_allow_url_rewrite = fields.Boolean(related="website_id.is_allow_url_rewrite", string="Enable SEO Friendly URL",readonly=False)
    
   
    #Notification while Seo Url will create an delete
    @api.onchange('is_allow_url_rewrite')
    def on_change_is_allow_url_rewrite(self):
        if self.is_allow_url_rewrite and self._context.get('is_click'):
            return {'warning': {
            'title': 'Set SEO Friendly URL',
            'message': 'By enabling this feature, It will rewrites SEO friendly URL for product & category'}}
        else:
            if self._context.get('is_click'):
                return {'warning': {
                'title': 'Unset SEO Friendly URL',
                'message': 'By disabling this feature, It will removes SEO friendly URL for product & category'}}