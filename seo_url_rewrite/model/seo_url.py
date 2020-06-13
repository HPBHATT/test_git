from odoo import api, fields, models, _
from odoo.addons.http_routing.models.ir_http import slugify
import re
from odoo.exceptions import ValidationError
from odoo.http import request


class seoUrl(models.Model):

    _name = 'seo.url'
    _description = 'Seo URL'
    _rec_name = 'url'
    
    apply_for  = fields.Selection([('product', 'Product'), ('category', 'Category')], string='SEO For', required=True)
    product_id = fields.Many2one('product.template',string="Product")
    categ_id = fields.Many2one('product.public.category', string="Category")
    url = fields.Char(string='URL',translate=True, required=True)
    website_id = fields.Many2one('website', string="Website")
    is_active = fields.Boolean(string='Active',default=True)
    
    _sql_constraints = [
        ('uniq_url_website', 'unique(url,website_id)','URL Must Be Unique Per Website'),
    ]
    
    #match the url pattern with regular expression 
    @api.constrains('url')
    def validate_url(self):
        for obj in self:
            if re.match("^(\/){1}([a-z0-9&_\.-]+)?((\/)?([a-z0-9&_\.-]+))$", obj.url) == None:
                raise ValidationError("Set url is not valid")
        return True
    
    
    #checked for url is valid or not
    #page url and seo url not be same 
    #seo url not same as odoo  base url E.x /shop/cart is not acceptable
    def is_valid_url(self,res_id=None,url=None):
        seo_url=self.sudo().browse(res_id)
        router = request.httprequest.app.get_db_router(request.db)
        inc=0
        for rule in router.iter_rules():
            if rule.rule == url:
                return False
        if self.env['seo.url'].with_context(active_test=False).sudo().search([('id','!=',seo_url.id),('url', '=', url),('website_id','in',(False,seo_url.website_id.id))]) or self.env['website.page'].with_context(active_test=False).sudo().search([('url', '=', url),('website_id','in',(False,seo_url.website_id.id))]) or url.split('/').__len__() > 3:
            return False
        else:
            return True
    
    #If generated url is same as other url then then this method return a unique url
    def get_unique_path(self,url,website_id=None):
        inc = 0
        url_temp = url
        while self.env['seo.url'].with_context(active_test=False).sudo().search([('url', '=', url_temp),('website_id','in',(False,website_id.id))]) or self.env['website.page'].with_context(active_test=False).sudo().search([('url', '=', url_temp),('website_id','in',(False,website_id.id))] ):
            inc += 1
            url_temp = url + (inc and "-%s" % inc or "")
        return url_temp

    #return the seo url for product and category
    def get_seo_url(self,product_id=None,categ_id=None,website_id=website_id):
        seo_url =None
        if product_id:
            seo_url = "/%s" % slugify(product_id.name or '').strip().strip('-')
        if categ_id:
            seo_url = "/%s" % slugify(categ_id.name or '').strip().strip('-')
        router = request.httprequest.app.get_db_router(request.db)
        inc=0
        for rule in router.iter_rules():
            if rule.rule == seo_url:
                inc += 1
                seo_url = seo_url + (inc and "-%s" % inc or "")
        return seo_url
    
    #creates unique a seo url for products and category
    def create_seo_url(self,product_id=None,categ_id=None,website_id=None):
        seo_url = self.get_seo_url(product_id=product_id,categ_id=categ_id,website_id=website_id)
        if self.env['seo.url'].sudo().search([('url','=',seo_url),('website_id.id','=',website_id.id)]):
                seo_url = self.env['seo.url'].get_unique_path(url=seo_url,website_id=website_id)
        if categ_id:
            categ_id=categ_id.id
        if product_id:
            product_id=product_id.id
        vals = {
                'product_id': product_id,
                'url': seo_url,
                'website_id':website_id.id,
                'is_active': True,
                'categ_id':categ_id,
                'apply_for':'product'
                }
        self.create(vals)
       
    
    
