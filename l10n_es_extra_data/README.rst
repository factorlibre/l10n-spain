===========
Datos Extra
===========

.. 
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! This file is generated by oca-gen-addon-readme !!
   !! changes will be overwritten.                   !!
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! source digest: sha256:d9c5af58130b5f957e98d2afac60280030de0ed02c8ce58f6340c3b1d59da1dc
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-OCA%2Fl10n--spain-lightgray.png?logo=github
    :target: https://github.com/OCA/l10n-spain/tree/11.0/l10n_es_extra_data
    :alt: OCA/l10n-spain
.. |badge4| image:: https://img.shields.io/badge/weblate-Translate%20me-F47D42.png
    :target: https://translation.odoo-community.org/projects/l10n-spain-11-0/l10n-spain-11-0-l10n_es_extra_data
    :alt: Translate me on Weblate
.. |badge5| image:: https://img.shields.io/badge/runboat-Try%20me-875A7B.png
    :target: https://runboat.odoo-community.org/builds?repo=OCA/l10n-spain&target_branch=11.0
    :alt: Try me on Runboat

|badge1| |badge2| |badge3| |badge4| |badge5|

Módulo que nos permite configurar cualquier cambio del plan contable en la
version 11.0 de la localización española, ya que Odoo no permite modificaciones
en versiones no mantenidas.

**Table of contents**

.. contents::
   :local:

Usage
=====

Instalar el módulo y ejecutar el actualizador del plan contable disponible en
el módulo *account_chart_update*.

Changelog
=========

11.0.2.1.0 (2023-02-20)
~~~~~~~~~~~~~~~~~~~~~~~

* Backport [[13.0][FIX] l10n_es: Includes new food taxes reduction](https://github.com/odoo/odoo/pull/108868)

Se mantiene el uso de los impuestos de alimentos en v11.

En posteriores versiones se renombran de la siguiente manera:

.. code-block:: xml

    ("account_tax_template_p_iva0_a", "account_tax_template_p_iva0_s_bc")
    ("account_tax_template_p_iva5_a", "account_tax_template_p_iva5_bc")
    ("account_tax_template_p_iva0_ic_a", "account_tax_template_p_iva0_ic_bc")
    ("account_tax_template_p_iva5_ic_a", "account_tax_template_p_iva5_ic_bc")
    ("account_tax_template_p_iva0_ia", "account_tax_template_p_iva0_ibc")
    ("account_tax_template_p_iva5_ia", "account_tax_template_p_iva5_ibc")
    ("account_tax_template_p_req0625", "account_tax_template_p_req062")
    ("account_tax_template_s_iva0_a", "account_tax_template_s_iva0b")
    ("account_tax_template_s_iva5_a", "account_tax_template_s_iva5b")
    ("account_tax_template_s_req0625", "account_tax_template_s_req062")

11.0.1.0.0 (2022-08-10)
~~~~~~~~~~~~~~~~~~~~~~~

* [NEW] Module backported to v11. Añadido nuevo impuesto del 5% de las eléctricas.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/l10n-spain/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us to smash it by providing a detailed and welcomed
`feedback <https://github.com/OCA/l10n-spain/issues/new?body=module:%20l10n_es_extra_data%0Aversion:%2011.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Do not contact contributors directly about support or help with technical issues.

Credits
=======

Authors
~~~~~~~

* Trey (www.trey.es)

Contributors
~~~~~~~~~~~~

* `Trey Kilobytes de Soluciones SL <https://www.trey.es>`__:

  * Vicent Cubells

* `Acysos SL <https://www.acysos.es>`__:

  * Ignacio Ibeas

* `FactorLibre <http://factorlibre.com>`__:

  * Luis J. Salvatierra

* `APSL - Nagarro <https://apsl.tech>`__:

  * Miquel Pascual 
  * Bernat Obrador
  * Miquel Alzanilles

Maintainers
~~~~~~~~~~~

This module is maintained by the OCA.

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

.. |maintainer-cubells| image:: https://github.com/cubells.png?size=40px
    :target: https://github.com/cubells
    :alt: cubells

Current `maintainer <https://odoo-community.org/page/maintainer-role>`__:

|maintainer-cubells| 

This module is part of the `OCA/l10n-spain <https://github.com/OCA/l10n-spain/tree/11.0/l10n_es_extra_data>`_ project on GitHub.

You are welcome to contribute. To learn how please visit https://odoo-community.org/page/Contribute.
