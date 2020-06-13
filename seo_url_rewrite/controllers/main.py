from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website.controllers.main import Website

class seoUrlRewrite(WebsiteSale,Website):
    
    """
        @param : token => SEO URL
        @return: render request related to SEO URL
    """
    @http.route(['/<string:token>','/<string:token>/page/<int:page>'], type='http', auth="public", website=True, multilang=True)
    def GetUrlData(self,token,token2=None,page=0,**kwargs):
        url='/'+token
        if token2:
            url = url + '/' +token2
        page_resouce = request.env['seo.url'].sudo().search([('url','=',url),('website_id.id','=',request.website.id)],limit=1)
        if page_resouce and page_resouce.product_id:
            if page_resouce.product_id.is_published:
                product_object = WebsiteSale()
                return product_object.product(page_resouce.product_id, **kwargs)
            else:
                return request.render("website.404")
        elif page_resouce and page_resouce.categ_id:
            if page_resouce.categ_id.website_published:
                shop_object = WebsiteSale()
                return shop_object.shop(category=page_resouce.categ_id, page=page, **kwargs)
            else:
                return request.render("website.404")
        else:
            website_page = request.env['ir.http']._serve_page()
            if website_page:
                return website_page
            else:
                raise request.not_found()

