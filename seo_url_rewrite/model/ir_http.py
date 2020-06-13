# -*- coding: utf-8 -*-
from werkzeug.routing import NotFound

from odoo import models
from odoo.http import request

class IrHttp(models.AbstractModel):
    _inherit = ['ir.http']
    
    @classmethod
    def _find_handler(cls, return_rule=False):
        path = request.httprequest.path.split('/')
        if path[1] in [lg.code for lg in cls._get_languages()]:
            raise NotFound()
        return super(IrHttp, cls)._find_handler(return_rule=return_rule)