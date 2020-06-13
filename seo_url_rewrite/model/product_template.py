from odoo import api, fields, models, _
from odoo.exceptions import UserError

class productTemplate(models.Model):
    _inherit = ["product.template"]
    
    seo_url_ids = fields.One2many('seo.url', 'product_id','seo url')
    
    # Creates a seo url when Products created
    def create(self,vals):
        res = super(productTemplate, self).create(vals)
        websites= self.env['website'].sudo().search([])
        if res.website_id:
            websites= res.website_id
        for website in websites:
            if website.is_allow_url_rewrite:
                if res.seo_url_ids and res.seo_url_ids.filtered(lambda r:r.website_id.id == website.id):
                    continue
                else:
                    seo_obj = self.env['seo.url'].sudo()
                    seo_obj.create_seo_url(product_id=res,website_id=website)
        return res
    
    # When any custom change in url , it checked for custom url validation and update seo url,
    # Also update the url while any changes in website_id and product name
    def write(self, vals):
        SeoUrl = self.env['seo.url'].sudo()
        if 'seo_url_ids' in vals.keys():
            for seo_url in vals.get('seo_url_ids'):
                if seo_url.__len__() >=3 and seo_url[2]:
                    url= seo_url[2].get('url')
                    if url:
                        is_valid_url=SeoUrl.is_valid_url(res_id=seo_url[1],url=url)
                        if not is_valid_url:
                            raise UserError(_("SEO URL is not valid , URL  contains some string start with '/' also allow just '-' with URL and must not end with '/' Example : '/ipod' or '/Imac-hd'"))
        res = super(productTemplate, self).write(vals)
        if self.website_id:
            seo_urls = self.seo_url_ids.filtered(lambda r : r.website_id.id != self.website_id.id)
            if seo_urls:
                seo_urls.sudo().unlink()
            seo_urls = self.seo_url_ids.filtered(lambda r : r.website_id.id in self.website_id.id)
            if not seo_urls and self.website_id.is_allow_url_rewrite:
                SeoUrl.create_seo_url(product_id=self,website_id=self.website_id)
        else:
            websites= self.env['website'].sudo().search([('is_allow_url_rewrite','=',True)])
            for website in websites:
                seo_urls = self.seo_url_ids.filtered(lambda r : r.website_id.id == website.id)
                if not seo_urls:
                    SeoUrl.create_seo_url(product_id=self,website_id=website)
        if 'name' in vals.keys() and self.seo_url_ids:
            for seo_url in self.seo_url_ids:
                self.env['website'].update_seo_url(seo_url_id=seo_url)
        return res
