..     Licensed to the Apache Software Foundation (ASF) under one
       or more contributor license agreements.  See the NOTICE file
       distributed with this work for additional information
       regarding copyright ownership.  The ASF licenses this file
       to you under the Apache License, Version 2.0 (the
       "License"); you may not use this file except in compliance
       with the License.  You may obtain a copy of the License at

         http://www.apache.org/licenses/LICENSE-2.0

       Unless required by applicable law or agreed to in writing,
       software distributed under the License is distributed on an
       "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
       KIND, either express or implied.  See the License for the
       specific language governing permissions and limitations
       under the License.

**************
Administration
**************

.. contents::
   :local:

.. _site-admin-interface:

Site Admin Interface
====================

Allura has an admin interface at http://MYSITE/nf/admin/  You must be an admin of the
`/p/allura` project on the site to access it.  If you want to use another project to control
admin access, change the :code:`site_admin_project` setting in :file:`development.ini`.

The admin interface allows you to:

* View newly registered projects
* Search for projects
* :ref:`Delete projects <delete-projects>`
* View neighborhood total stats
* Search for users, view user details, update user status, email address, and reset their password
* View background task statuses, and submit new background tasks
* Manage "trove" categories (for user skill choices)
* Subscribe a user to an artifact
* Reclone a repository

Commands, Scripts, and Tasks
============================

Overview
--------

Allura has many commands and scripts that can be run from the server commandline to
administrate Allura.  There are also tasks that can be run through the `taskd` system
in the background.  These tasks can be submitted via the web at
http://MYSITE/nf/admin/task_manager  Some paster scripts have been set up
so that they are runnable as tasks too, giving you the convenience of starting
them through the web and letting `taskd` execute them, rather than from a server
shell.

Commands can be discovered and run via the `paster` command when you are in the
'Allura' directory that has your .ini file.  For example::

     paster help
    ... all commands listed here ...

     paster create-neighborhood --help
    ... specific command help ...

     paster create-neighborhood development.ini myneighborhood myuser ...


Scripts are in the `scripts/` directory and run slightly differently, via `paster script`.  An extra
:kbd:`--` is required to separate script arguments from paster arguments.  Example::

     paster script development.ini ../scripts/create-allura-sitemap.py -- --help
    ... help output ...

     paster script development.ini ../scripts/create-allura-sitemap.py -- -u 100

To run these when using docker, prefix with :code:`docker-compose run taskd` and use :code:`docker-dev.ini` like::

    docker-compose run taskd paster create-neighborhood docker-dev.ini myneighborhood myuser ...

Tasks can be run via the web interface at http://MYSITE/nf/admin/task_manager  You must know
the full task name, e.g. :code:`allura.tasks.admin_tasks.install_app`  You can
optionally provide a username and project and app which will get set on the
current context (`c`).  You should specify what args and kwargs will be passed
as parameters to the task.  They are specified in JSON format on the form.  If you are
running a script via this interface, the `args/kwargs` JSON should be like::

    {
        "args": ["--foo --bar baz"],
        "kwargs": {}
    }

See the listing of :mod:`some available tasks <allura.tasks.admin_tasks>`.


Available scripts and commands are:


create-neighborhood
-------------------

.. program-output:: paster create-neighborhood development.ini --help | fmt -s -w 95
   :shell:


ensure_index
------------

.. program-output:: paster ensure_index development.ini --help


ircbot
------

.. program-output:: paster ircbot development.ini --help


reindex
-------

.. program-output:: paster reindex development.ini --help


set-neighborhood-features
-------------------------

.. program-output:: paster set-neighborhood-features development.ini --help | fmt -s -w 95
   :shell:


set-tool-access
---------------

.. program-output:: paster set-tool-access development.ini --help | fmt -s -w 95
   :shell:


taskd
-----

.. program-output:: paster taskd development.ini --help


taskd_cleanup
-------------

.. program-output:: paster taskd_cleanup development.ini --help | fmt -s -w 95
   :shell:


pull-rss-feeds
--------------

Blog tools may optionally be configured to fetch external RSS feeds.  If that is in place, this command should
be used to fetch all those rss feeds and convert new entries into blog posts.

Requires `html2text`, a GPL library.

::

    cd ../ForgeBlog
    paster pull-rss-feeds development.ini --help


disable_users.py
----------------

*Can be run as a background task using task name:* :code:`allura.scripts.disable_users.DisableUsers`

.. argparse::
    :module: allura.scripts.disable_users
    :func: get_parser
    :prog: paster script development.ini allura/scripts/disable_users.py --


.. _delete-projects-py:

delete_projects.py
------------------

*Can be run as a background task using task name:* :code:`allura.scripts.delete_projects.DeleteProjects`

More convenient way to delete project is :ref:`this site admin page <delete-projects>`. It uses this script under the hood.

.. argparse::
    :module: allura.scripts.delete_projects
    :func: get_parser
    :prog: paster script development.ini allura/scripts/delete_projects.py --


refreshrepo.py
--------------

*Can be run as a background task using task name:* :code:`allura.scripts.refreshrepo.RefreshRepo`

.. argparse::
    :module: allura.scripts.refreshrepo
    :func: get_parser
    :prog: paster script development.ini allura/scripts/refreshrepo.py --


reindex_projects.py
-------------------

*Can be run as a background task using task name:* :code:`allura.scripts.reindex_projects.ReindexProjects`

.. argparse::
    :module: allura.scripts.reindex_projects
    :func: get_parser
    :prog: paster script development.ini allura/scripts/reindex_projects.py --


reindex_users.py
----------------

*Can be run as a background task using task name:* :code:`allura.scripts.reindex_users.ReindexUsers`

.. argparse::
    :module: allura.scripts.reindex_users
    :func: get_parser
    :prog: paster script development.ini allura/scripts/reindex_users.py --


create-allura-sitemap.py
------------------------

*Cannot currently be run as a background task.*

.. argparse::
    :file: ../../scripts/create-allura-sitemap.py
    :func: parser
    :prog: paster script development.ini ../scripts/create-allura-sitemap.py --


publicize-neighborhood.py
-------------------------

*Cannot currently be run as a background task.*

.. argparse::
    :file: ../../scripts/publicize-neighborhood.py
    :func: parser
    :prog: paster script development.ini ../scripts/publicize-neighborhood.py --


scrub-allura-data.py
--------------------

*Cannot currently be run as a background task.*

.. argparse::
    :file: ../../scripts/scrub-allura-data.py
    :func: parser
    :prog: paster script development.ini ../scripts/scrub-allura-data.py --


teamforge-import.py
-------------------

*Cannot currently be run as a background task.*

Extract data from a TeamForge site (via its web API), and import directly into Allura.  There are some hard-coded
and extra functions in this script, which should be removed or updated before being used again.
Requires running: :command:`pip install suds` first. ::

    usage: paster script development.ini ../scripts/teamforge-import.py -- --help


Site Notifications
==================

Allura has support for site-wide notifications that appear below the site header,
but there is currently no UI for managing them.  They can easily be inserted via
manual mongo queries, however:

.. code-block:: console

    > db.site_notification.insert({
    ... active: true,
    ... impressions: 10,
    ... content: 'You can now reimport exported project data.'
    ... })

This will create a notification that will be shown for 10 page views or until the
user closes it manually.  An `impressions` value of 0 will show the notification
indefinitely (until closed).  The notification content can contain HTML.  Only the
most recent notification will be shown, unless it has `active:false`, in which case
no notification will be shown.

.. _delete-projects:

Deleting projects
=================

Site administrators can delete projects using web interface. This is running
:ref:`delete_projects.py script <delete-projects-py>` under the hood. You can
access it choosing "Delete projects" from the left sidebar on the :ref:`site
admin interface <site-admin-interface>`.

**Be careful, projects and all related data are actually deleted from the database!**

Just copy and paste URLs of the project you want to delete into "Projects"
field, separated by newlines. You can also use :code:`nbhd_prefix/project_shortname`
or just :code:`project_shortname` format, e.g.


.. code-block:: text

  http://MYSITE/p/test3/wiki/
  p/test2
  test

will delete projects :code:`test3`, :code:`test2` and :code:`test`.

**NOTE:** if you omit neighborhood prefix project will be matched only if
project with such short name are unique across all neighborhoods, i.e. if you
have project with short name :code:`test` in :code:`p2` neighborhood and
project with the same short name in :code:`p` neighborhood project will not be
deleted. In this case you should specify neighborhood explicitly to
disambiguate it.

The "Reason" field allows you to specify a reason for deletion, which will be logged to disk.

"Disable all project members" checkbox disables all users belonging to groups
"Admin" and "Developer" in these projects. The reason will be also recorded in
the users' audit logs if this option is checked.

After clicking "Delete" you will see a confirmation page. It shows which
projects are going to be deleted and which are failed to parse, so you can go
back and edit your input.

Using Projects and Tools
========================

We currently don't have any further documentation for basic operations of managing
users, projects, and tools on Allura.  However, SourceForge has help docs that cover
these functions https://sourceforge.net/p/forge/documentation/Docs%20Home/  Note
that this documentation also covers some SourceForge features that are not part of Allura.


.. _public_api:

Public API Documentation
========================

All url endpoints are prefixed with /rest/ and the path to the project and tool.

For example, in order to access a wiki installed in the 'test' project with the mount point 'docs' the API endpoint would be /rest/p/test/docs.

`Explore Allura's REST API documentation here. <https://anypoint.mulesoft.com/apiplatform/forge-allura/#/portals/organizations/86c00a85-31e6-4302-b36d-049ca5d042fd/apis/32370/versions/33732>`_
You can also try the API live there.

Client Scripts
==============

Allura includes some client scripts that demonstrate use of the Allura REST API and do not have to be run
from an Allura environment.  They do require some python packages to be installed, though.


wiki-copy.py
------------

.. program-output:: python ../../scripts/wiki-copy.py --help | sed 's/Usage: /Usage: python scripts\//'
    :shell:


new_ticket.py
-------------

Illustrates creating a new ticket, using the simple OAuth Bearer token.

.. argparse::
    :file: ../../scripts/new_ticket.py
    :func: get_parser
    :prog: python scripts/new_ticket.py


wiki-post.py
------------

.. program-output:: python ../../scripts/wiki-post.py --help | sed 's/Usage: /Usage: python scripts\//'
    :shell:
