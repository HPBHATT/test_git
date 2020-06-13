from odoo import models
from odoo.addons.http_routing.models.ir_http import unslug
from odoo.addons.http_routing.models.ir_http import is_multilang_url
from odoo.http import request

class irQweb(models.AbstractModel):
    
    _inherit = 'ir.qweb'

    URL_ATTRS = {
        'a':'href',
    }
    
    """
        @param : Tag => set href as per Seo URL
        @return: Attributes of tag
        @description : If tag contains a product or category link , replace that link with related Seo url of product and category
    """
    def _post_processing_att(self, tagName, atts, options):
        atts = super(irQweb, self)._post_processing_att(tagName, atts, options)
        tmp_atts = atts
        try:
            name = self.URL_ATTRS.get(tagName)
            website = request and getattr(request, 'website', None)
            url=None
            if not website and options.get('website_id'):
                website = self.env['website'].browse(options['website_id'])
            if website and website.is_allow_url_rewrite and request and name and atts.get(name) and name in atts and ('/shop/product' in atts.get(name)):
                url=atts.get(name)
                surl = url.split('/')
                langs = [lg[0] for lg in request.env['res.lang'].get_available()]
                if surl[1] in langs:
                    surl = url.split('/',5)
                    surl.pop(1)
                else:
                    surl = url.split('/',4)
                if surl.__len__() < 4:
                    return tmp_atts
                query_url=surl[3].split('?')
                unslug_url = unslug(query_url[0])
                seo = request.env['seo.url'].sudo().search([('product_id','=',unslug_url[1]),('website_id','=',request.website.id),('is_active','=',True)])
                if seo:
                    if surl.__len__() >= 5:
                        re_url = seo[0].url+'/'+surl[surl.__len__()-1]
                    else:
                        re_url = seo[0].url
                    if query_url.__len__() > 1:
                        re_url +='?'+query_url[1]
                    if (len(langs) > 1 ) and is_multilang_url(url, langs):
                        ps = url.split(u'/')
                        if ps[1] in langs:
                            re_url="/"+ps[1]+re_url
                    atts[name] =re_url
            if website and website.is_allow_url_rewrite and request and name and atts.get(name) and name in atts and ('/shop/category' in atts.get(name)):
                url=atts.get(name)
                surl = url.split('/')
                langs = [lg[0] for lg in request.env['res.lang'].get_available()]
                if surl[1] in langs:
                    surl = url.split('/',5)
                    surl.pop(1)
                else:
                    surl = url.split('/',4)
                if surl.__len__() < 4:
                    return tmp_atts
                query_url=surl[3].split('?')
                unslug_url = unslug(query_url[0])
                seo = request.env['seo.url'].sudo().search([('categ_id','=',unslug_url[1]),('website_id','=',request.website.id),('is_active','=',True)])
                if seo:
                    if surl.__len__() >= 5:
                        re_url = seo[0].url+'/'+surl[surl.__len__()-1]
                    else:
                        re_url = seo[0].url
                    if query_url.__len__() > 1:
                        re_url +='?'+query_url[1]
                    if (len(langs) > 1 ) and is_multilang_url(url, langs):
                        ps = url.split(u'/')
                        if ps[1] in langs:
                            re_url="/"+ps[1]+re_url
                    atts[name] =re_url
            return atts    
        except Exception as e:
            return tmp_atts
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
