Globals
=======

Jinja2 `globals <https://jinja.palletsprojects.com/en/3.1.x/templates/#list-of-global-functions>`_ are
often data or functions that do not are not :doc:`filters </usage/templating/filters>` or :doc:`tests </usage/templating/tests>`.

In addition to Jinja2's built-in globals, Betty provides the following:

``app`` (:py:class:`betty.app.App`)
    The currently running Betty application.
``project`` (:py:class:`betty.project.Project`)
    The project the template is being rendered for.
``today`` (:py:class:`betty.date.Date`)
    The current date.
