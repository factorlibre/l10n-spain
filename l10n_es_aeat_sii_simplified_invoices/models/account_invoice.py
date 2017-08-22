# -*- coding: utf-8 -*-
# Copyright 2017 Santa Fixie SL - Juanjo Algaz <jalgaz@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openerp import _, api, exceptions, fields, models
from openerp.tools.float_utils import float_round

_logger = logging.getLogger(__name__)

try:
    from openerp.addons.connector.queue.job import job
    from openerp.addons.connector.session import ConnectorSession
except ImportError:
    _logger.debug('Can not `import connector`.')
    import functools

    def empty_decorator_factory(*argv, **kwargs):
        return functools.partial
    job = empty_decorator_factory


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'


    def _vat_required(self):
        """
        Return fiscal position vat_required value or False for no fiscal position
        :return: True or False
        """
        res = True
        if self.fiscal_position and not self.fiscal_position.vat_required:
            res = False
        return res


    @api.multi
    def _get_sii_identifier(self):
        """Get the SII structure for a partner identifier depending on the
        conditions of the invoice.
        """
        self.ensure_one()
        if not self._vat_required():
            return {}
        else:
            return super(AccountInvoice, self)._get_sii_identifier()

    @api.multi
    def _sii_check_exceptions(self):
        """Inheritable method for exceptions control when sending SII invoices.
        """
        self.ensure_one()
        if (not self.fiscal_position and not self.partner_id.vat) or \
            (self.fiscal_position and self.fiscal_position.vat_required and not
                self.partner_id.vat):
            raise exceptions.Warning(
                _("The partner has not a VAT configured.")
            )
        if not self.company_id.chart_template_id:
            raise exceptions.Warning(_(
                'You have to select what account chart template use this'
                ' company.'))
        if not self.company_id.sii_enabled:
            raise exceptions.Warning(
                _("This company doesn't have SII enabled.")
            )
        if not self._vat_required():
            if not self.company_id.max_amount_total_simplified_invoice:
                raise exceptions.Warning(
                    _("The company does not have the maximum amount indicated for simplified "
                      "invoices (company form).")
                )
            if self.amount_total > self.company_id.max_amount_total_simplified_invoice:
                raise exceptions.Warning(
                    _("This invoice can not be simplified type, the amount total is above the "
                      "limit (company form).")
                )

    @api.multi
    def _get_sii_invoice_dict_out(self, cancel=False):
        """Build dict with data to send to AEAT WS for invoice types:
        out_invoice and out_refund.

        :param cancel: It indicates if the dictionary if for sending a
          cancellation of the invoice.
        :return: invoices (dict) : Dict XML with data for this invoice.
        """
        inv_dict = super(AccountInvoice, self)._get_sii_invoice_dict_out(cancel=cancel)
        if not self._vat_required():
            # es simplificada:
            if self.type == 'out_invoice':
                # factura simplificada
                tipo_factura = 'F2'
            elif self.type == 'out_refund':
                # factura simplificada
                tipo_factura = 'R5'
                # se requiere redondear por si el sistema no tiene establecido
                # a 2 dígitos los valores para account
                if 'FacturaExpedida' in inv_dict:
                    factExp = inv_dict['FacturaExpedida']
                    if 'ImporteRectificacion' in factExp:
                        importeRect = factExp['ImporteRectificacion']
                        if 'CuotaRectificada' in importeRect:
                            importeRect['CuotaRectificada'] = round(importeRect['CuotaRectificada'], 2)
                        if 'BaseRectificada' in importeRect:
                            importeRect['BaseRectificada'] = round(importeRect['BaseRectificada'], 2)
            if 'FacturaExpedida' in inv_dict:
                if 'TipoFactura' in inv_dict['FacturaExpedida']:
                    inv_dict['FacturaExpedida']['TipoFactura'] = tipo_factura
                if 'Contraparte' in inv_dict['FacturaExpedida']:
                    del inv_dict['FacturaExpedida']['Contraparte']
        return inv_dict
