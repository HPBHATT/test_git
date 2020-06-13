from odoo.addons.website.models.ir_http import sitemap_qs2dom
from odoo.osv.expression import FALSE_DOMAIN
from odoo import api, fields, models, _
from odoo.http import request

 
class website(models.Model):
    _inherit = "website"
     
    is_allow_url_rewrite = fields.Boolean(string="Enable SEO Friendly url")
   
    #update the seo url while product name or category name will changes
    def update_seo_url(self,seo_url_id=None):
        seo_obj=self.env['seo.url'].sudo()
        url=seo_obj.get_seo_url(product_id=seo_url_id.product_id,categ_id=seo_url_id.categ_id,website_id=seo_url_id.website_id)
        inc = 0
        url_temp = url
        while self.env['seo.url'].with_context(active_test=False).sudo().search([('id','!=',seo_url_id.id),('url', '=', url_temp),('website_id','in',(False,seo_url_id.website_id.id))]) or self.env['website.page'].with_context(active_test=False).sudo().search([('url', '=', url_temp),('website_id','in',(False,seo_url_id.website_id.id))] ):
            inc += 1
            url_temp = url + (inc and "-%s" % inc or "")
        seo_url_id.sudo().write({'url':url_temp})
        return True
    
    #while creating new website or set seo_url true form res configure it creates seo url for respective websites 
    def create_update_seo(self,website=None,values=None): 
        if website.is_allow_url_rewrite:
            SeoUrl = self.env['seo.url'].sudo()
            objects = self.env['product.template'].sudo().search([('website_id','in',(False,website.id))])
            if objects:
                for object in objects:
                    if (object.website_id and  object.website_id != website) or object.seo_url_ids.filtered(lambda r:r.website_id.id == website.id):
                        continue
                    else:
                        SeoUrl.create_seo_url(product_id=object,website_id=website)

            objects = self.env['product.public.category'].sudo().search([('website_id','in',(False,website.id))])
            if objects:
                for object in objects:
                    if (object.website_id and  object.website_id != website) or object.seo_url_ids.filtered(lambda r:r.website_id.id == website.id):
                        continue
                    else:
                        SeoUrl.create_seo_url(categ_id=object,website_id=website)
        else:
            self._cr.execute("DELETE FROM seo_url WHERE website_id=%s", (website.id,))
        Attachment = request.env['ir.attachment'].sudo()
        dom = [('url', 'like', '/sitemap'), ('type', '=', 'binary')]
        sitemaps = Attachment.search(dom)
        sitemaps.unlink()
    
    #create or delete a seo url while changing value of is_allow_url_rewrite
    def write(self, values):
        result = super(website, self).write(values)
        if 'is_allow_url_rewrite' in values.keys():
            self.create_update_seo(website=self[0],values=values)
        return result     
    
    
    #while creates a page from website if page url and seo url would be same then it return the unique url
    def get_unique_path(self, page_url):
        """ Given an url, return that url suffixed by counter if it already exists
            :param page_url : the url to be checked for uniqueness
        """
        inc = 0
        # we only want a unique_path for website specific.
        # we need to be able to have /url for website=False, and /url for website=1
        # in case of duplicate, page manager will allow you to manage this case
        domain_static = [('website_id', '=', self.get_current_website().id)]  # .website_domain()
        page_temp = page_url
        while self.env['website.page'].with_context(active_test=False).sudo().search([('url', '=', page_temp)] + domain_static) or self.env['seo.url'].with_context(active_test=False).sudo().search([('url', '=', page_temp)] + domain_static):
            inc += 1
            page_temp = page_url + (inc and "-%s" % inc or "")
        return page_temp
    
    
    
    ##Generate a sitemap as per seo url 
    def enumerate_pages(self, query_string=None, force=False):
        """ Available pages in the website/CMS. This is mostly used for links
            generation and can be overridden by modules setting up new HTML
            controllers for dynamic pages (e.g. blog).
            By default, returns template views marked as pages.
            :param str query_string: a (user-provided) string, fetches pages
                                     matching the string
            :returns: a list of mappings with two keys: ``name`` is the displayable
                      name of the resource (page), ``url`` is the absolute URL
                      of the same.
            :rtype: list({name: str, url: str})
        """

        router = request.httprequest.app.get_db_router(request.db)
        # Force enumeration to be performed as public user
        url_set = set()

        sitemap_endpoint_done = set()

        for rule in router.iter_rules():
            if 'sitemap' in rule.endpoint.routing:
                if rule.endpoint in sitemap_endpoint_done:
                    continue
                sitemap_endpoint_done.add(rule.endpoint)

                func = rule.endpoint.routing['sitemap']
                if func is False:
                    continue
                for loc in func(self.env, rule, query_string):
                    yield loc
                continue

            if not self.rule_is_enumerable(rule):
                continue

            converters = rule._converters or {}
            if query_string and not converters and (query_string not in rule.build([{}], append_unknown=False)[1]):
                continue
            values = [{}]
            # converters with a domain are processed after the other ones
            convitems = sorted(
                converters.items(),
                key=lambda x: (hasattr(x[1], 'domain') and (x[1].domain != '[]'), rule._trace.index((True, x[0]))))

            for (i, (name, converter)) in enumerate(convitems):
                newval = []
                for val in values:
                    query = i == len(convitems) - 1 and query_string
                    if query:
                        r = "".join([x[1] for x in rule._trace[1:] if not x[0]])  # remove model converter from route
                        query = sitemap_qs2dom(query, r, self.env[converter.model]._rec_name)
                        if query == FALSE_DOMAIN:
                            continue
                    for value_dict in converter.generate(uid=self.env.uid, dom=query, args=val):
                        newval.append(val.copy())
                        value_dict[name] = value_dict['loc']
                        del value_dict['loc']
                        newval[-1].update(value_dict)
                values = newval

            for value in values:
                domain_part, url = rule.build(value, append_unknown=False)
                if not query_string or query_string.lower() in url.lower():
                    website=False
                    if value.get('current_website_id'):
                        website = self.sudo().search([('id','=',value.get('current_website_id')),('is_allow_url_rewrite','=',True)])
                    if website:
                        if 'category' in value.keys() and value.get('category') :
                            categ_id=self.env['product.public.category'].sudo().browse(value.get('category')[0])
                            if categ_id.seo_url_ids:
                                seo_urls = categ_id.seo_url_ids.filtered(lambda r:r.website_id.id == website.id)
                                if seo_urls and seo_urls[0].is_active:
                                    url=seo_urls[0].url
                        if 'product' in value.keys() and value.get('product'):
                            product_id=self.env['product.template'].sudo().browse(value.get('product')[0])
                            if product_id.seo_url_ids:
                                seo_urls = product_id.seo_url_ids.filtered(lambda r:r.website_id.id == website.id)
                                if seo_urls and seo_urls[0].is_active:
                                    url=seo_urls[0].url
                    page = {'loc': url}
                    for key, val in value.items():
                        if key.startswith('__'):
                            page[key[2:]] = val
                    if url in ('/sitemap.xml',):
                        continue
                    if url in url_set:
                        continue
                    url_set.add(url)
                    yield page

        # '/' already has a http.route & is in the routing_map so it will already have an entry in the xml
        domain = [('url', '!=', '/')]
        if not force:
            domain += [('website_indexed', '=', True)]
            # is_visible
            domain += [('website_published', '=', True), '|', ('date_publish', '=', False), ('date_publish', '<=', fields.Datetime.now())]

        if query_string:
            domain += [('url', 'like', query_string)]

        pages = self.get_website_pages(domain)

        for page in pages:
            record = {'loc': page['url'], 'id': page['id'], 'name': page['name']}
            if page.view_id and page.view_id.priority != 16:
                record['__priority'] = min(round(page.view_id.priority / 32.0, 1), 1)
            if page['write_date']:
                record['__lastmod'] = page['write_date'].date()
            yield record