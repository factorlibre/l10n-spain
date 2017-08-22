.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

======================================================================
Suministro Inmediato de Información en el IVA - Facturas simplificadas
======================================================================

Ampliación módulo para la presentación inmediata del IVA para la gestión de facturas simplificadas.


Installation
============

Sin requisitos especiales.

Configuration
=============

Para configurar este módulo necesitas:

 * En la configuración de las posiciones fiscales, indicar si se requiere NIF. Esto hará
que al procesar por SII las facturas, el mensaje enviado a hacienda sea de una forma u otra (simplificada o normal).

 * En el formulario de la compañía establecer el límite máximo para facturas simplificadas (a día de hoy jun2017
   400€ o 3000€). Si no se indica no se podrá usar SII para aquellas posiciones fiscales que no tengan el check
   de NIF marcado (la posición fiscal implica que se utilizará para facturas simplificadas).

Usage
=====

Cuando se valida una factura automáticamente envia la comunicación al servidor
de AEAT. Este tipo de comunicación varía si la posición fiscal asocida a la factura requiere el uso de NIF/CIF
o no lo requiere.

Si la posición fiscal no está indicada, se entiende que la factura es ordinaria, indicando la necesidad de tener NIF/CIF
indicado para el cliente asociado a la misma.


Known issues / Roadmap
======================

* No incluye el procesado desde el POS/TPV, sólo facturas directas.

* Tipos de facturas y estado actual:

   * Facturas emitidas simplificadas F2:

      * Se incluyen los impuestos desglosados, lo que no es requisito en todos los casos
      (simplemente usa el resto del estándar).

      * Se eliminan los datos de la contraparte en el envío a SII.

   * Facturas emitidas simplificadas rectificativas (R5):

      * Funcionando. El asistente estándar de las rectificativas ya incluye lo necesario.

   * Límite máximo legal para importes totales (impuestos incluidos) controlado e indicado
      en el formulario de la compañía, avisando del error en el retorno SII de la factura.

Bug Tracker
===========



Credits
=======

Images
------


Contributors
------------

* Juanjo Algaz - Santa Fixie S.L. <jalgaz@gmail.com>

Funders
-------

The development of this module has been financially supported by:

* Santa Fixie S.L.

Maintainer
----------
