==========
SimpleIDML
==========

.. image:: https://coveralls.io/repos/Starou/SimpleIDML/badge.png
  :target: https://coveralls.io/r/Starou/SimpleIDML

.. image:: https://img.shields.io/pypi/v/simpleidml.svg
  :target: https://pypi.python.org/pypi/SimpleIDML

.. image:: https://img.shields.io/pypi/pyversions/simpleidml.svg
    :target: https://pypi.python.org/pypi/SimpleIDML/
    :alt: Supported Python versions

.. image:: https://img.shields.io/pypi/l/simpleidml.svg
    :target: https://pypi.python.org/pypi/SimpleIDML/
    :alt: License

.. image:: https://travis-ci.org/Starou/SimpleIDML.svg
    :target: https://travis-ci.org/Starou/SimpleIDML
    :alt: Travis C.I.

Installation
============

Use ``pip``:

.. code-block:: bash

    pip install SimpleIDML

Or:

.. code-block:: bash

    python setup.py build
    sudo python setup.py install

Python support
--------------

- Python 3: 3.6+

Any questions?
--------------

https://groups.google.com/forum/#!forum/simpleidml-users

Developers
----------

.. code-block:: bash

    vagrant up
    vagrant ssh
    cd tests
    python runtests.py

What is SimpleIDML?
===================

SimpleIDML is a Python library to manipulate Adobe® InDesign® IDML file. The main purpose being
the ability to compose IDML files together and produce complex documents from simple pieces and
to separate the data from the structure.

The philosophy behind SimpleIDML is to keep separated the content and the structure and to use XML
files to feed your documents by using the XML Structure in InDesign.
Keeping this isolation is important to ease the debugging and to keep track of what is going on.

I urge you to take a look in the *regressiontests* directory for real-world examples.

Uses cases - success story(ies)
===============================

Le Figaro - FigaroClassifieds
-----------------------------

SimpleIDML is used in production at *Le Figaro* aside in-house tools managing the content of
Classifieds Ads magazines like *Propriétés de France* or *Belles Maisons à louer*.
These tools produces XML files describing the page layout (which IDML templates and sub-templates
to use) and the page content.
The XML files feed another tool - the one using SimpleIDML - that compose the final page.

The steps of the (simplified) process of composition are:

1. Get the main IDML template (the page) ;
2. Ad the sub-templates (the ads) into the page template ;
3. Import the content into the final IDML file ;
4. Edit the file in InDesign ;
5. Push the changesets back to the content management application and update the database.

There is a lot of cool features in this application. You can update a part of a page already or
partially composed for example.

Architecture
''''''''''''

These applications are web-applications. The communication is done by web-services feeding a task
queue (RabbitMQ/Celery).

The performances are quite good. Composing a document require a fraction of a second.

What are IDML files?
====================

IDML (*InDesign Markup Language*) files are a Zip archives (Adobe calls them packages) storing
essentially XML files. Adobe made a descent job because those files can completely express the
content of the native (binary) documents.
This is a small revolution in the print world when it comes to automatically process files in both
ways from templates and database (Round-trip) without using proprietary server-edition of
Publishing Software.

What does SimpleIDML do?
========================

Package exploration
-------------------

You can discover the structure of your IDML files:

.. code-block:: python

    >>> from simple_idml import idml
    >>> my_idml_package = idml.IDMLPackage("/path/to/my_main_document.idml")
    >>> my_idml_package.spreads
    [u'Spreads/Spread_ub6.xml', u'Spreads/Spread_ubc.xml', u'Spreads/Spread_uc3.xml']
    >>> my_idml_package.stories
    [u'Stories/Story_u139.xml', u'Stories/Story_u11b.xml',
     u'Stories/Story_u102.xml', u'Stories/Story_ue4.xml']

Some attributes are *lxml.etree* Elements or Documents:

.. code-block:: python

    >>> my_package.font_families
    [<Element FontFamily at 0x1010048c0>,
     <Element FontFamily at 0x101004a50>,
     <Element FontFamily at 0x101004aa0>,
        <Element FontFamily at 0x101004af0>]
    >>> [e.get("Name") for e in my_package.font_families]
    ['Minion Pro', 'Myriad Pro', 'Kozuka Mincho Pro', 'Vollkorn']

    >>> my_package.xml_structure
    <Element Root at 0x101004910>
    >>> from lxml import etree
    >>> # print my_package.xml_structure_pretty() is a shortcut for:
    >>> print etree.tostring(my_package.xml_structure, pretty_print=True)
    <Root Self="di2">
      <article XMLContent="u102" Self="di2i3">
        <Story XMLContent="ue4" Self="di2i3i1">
          <title Self="di2i3i1i1"/>
          <subtitle Self="di2i3i1i2"/>
        </Story>
        <content XMLContent="u11b" Self="di2i3i2"/>
        <illustration XMLContent="u135" Self="di2i3i3"/>
        <description XMLContent="u139" Self="di2i3i4"/>
      </article>
      <article XMLContent="udb" Self="di2i4"/>
      <article XMLContent="udd" Self="di2i5"/>
      <advertise XMLContent="udf" Self="di2i6"/>
    </Root>


``xml_structure`` attribute is a representation of the XML Structure of your InDesign XML-ready
document (The one you want to use to populate the content with data from an external XML file
having the same structure).


Build package
-------------

There is a convenient script to create a IDML package from a flat directory called
*simpleidml_create_package_from_dir.py* which should be in your PATH.


Compose document
----------------

**Important**: You should always use a ``with`` context when using side-effect methods on
``IDMLPackage`` instances returning new instances.


For example, the following is bad because ``my_doc`` initial instance reference is lost and
the associated file cannot be properly closed. This may rise an exception on Windows platform
if you try to ``os.unlink()`` an unclosed file.

.. code-block:: python

    from simple_idml import idml
    my_doc = idml.IDMLPackage("/path/to/my_main_document.idml")
    my_doc = my_doc.prefix("main")

Instead, use:

.. code-block:: python

    from simple_idml import idml
    my_doc = idml.IDMLPackage("/path/to/my_main_document.idml")
    with my_doc.prefix("main") as f:
        # some code.

Insert elements
'''''''''''''''

Using the XML Structure you can ask SimpleIDML to insert into a document at a XML tag the content
of another XML tag from another document. The tag paths are expressed using XPath_ syntax.
Note that you should always make a copy of your idml files before altering them with
``shutil.copy2(src, dst)`` for instance and prefix your document before using ``insert_idml()``
to avoid reference collisions.

.. code-block:: python

    >>> from simple_idml import idml
    >>> idml_main = idml.IDMLPackage("/path/to/my_main_document.idml")
    >>> idml_module = idml.IDMLPackage("/path/to/my_small_document.idml")

    >>> with idml_main.prefix("main") as p_idml_main, \
    >>>      idml_module.prefix("article") as p_idml_article:

    >>>     with p_idml_main.insert_idml(p_idml_article, at="/Root/article[3]",
                                         only="/Root/module[1]") as f:
    >>>         f.stories
    ['Stories/Story_article1u188.xml', 'Stories/Story_article1u19f.xml',
     'Stories/Story_article1u1db.xml', 'Stories/Story_mainu102.xml',
     'Stories/Story_mainu11b.xml', 'Stories/Story_mainu139.xml',
     'Stories/Story_mainue4.xml']


    >>>         print f.xml_structure_pretty()
    <Root Self="maindi2">
      <article XMLContent="mainu102" Self="maindi2i3">
        <Story XMLContent="mainue4" Self="maindi2i3i1">
          <title Self="maindi2i3i1i1"/>
          <subtitle Self="maindi2i3i1i2"/>
        </Story>
        <content XMLContent="mainu11b" Self="maindi2i3i2"/>
        <illustration XMLContent="mainu135" Self="maindi2i3i3"/>
        <description XMLContent="mainu139" Self="maindi2i3i4"/>
      </article>
      <article XMLContent="mainudb" Self="maindi2i4"/>
      <article Self="maindi2i5">
        <module XMLContent="article1u1db" Self="article1di3i12">
          <main_picture XMLContent="article1u182" Self="article1di3i12i1"/>
          <headline XMLContent="article1u188" Self="article1di3i12i2"/>
          <Story XMLContent="article1u19f" Self="article1di3i12i3">
            <article Self="article1di3i12i3i2"/>
            <informations Self="article1di3i12i3i1"/>
          </Story>
        </module>
      </article>
      <advertise XMLContent="mainudf" Self="maindi2i6"/>
    </Root>


Combine pages
'''''''''''''

You may need to gather pages from severals documents into a single one:

.. code-block:: python

    >>> edito_idml_file = IDMLPackage("magazineA-edito.idml")
    >>> courrier_idml_file = IDMLPackage("magazineA-courrier-des-lecteurs.idml")

    >>> # Always start by prefixing packages to avoid collision.
    >>> with edito_idml_file.prefix("edito") as p_edito,\
    >>>      courrier_idml_file.prefix("courrier") as p_courrier:
    >>>     len(edito_idml_file.pages)
    2

    >>>     new_idml = p_edito.add_page_from_idml(p_courrier,
    ...                                           page_number=1,
    ...                                           at="/Root",
    ...                                           only="/Root/page[1]")
    >>>     len(new_idml.pages)
    3

    # The XML Structure has integrated the new file.
    >>>     print etree.tostring(new_idml.xml_structure, pretty_print=True)
    <Root Self="editodi2">
      <page Self="editodi2ib">
        <article Self="editodi2ibif">
          <Story XMLContent="editoue4" Self="editodi2ibifi1f">
            <title Self="editodi2ibifi1fi1"/>
            <subtitle Self="editodi2ibifi1fi2"/>
          </Story>
          <content XMLContent="editou11b" Self="editodi2ibifi1e"/>
        </article>
      </page>
      <page Self="editodi2i10">
        <advertise XMLContent="editou1de" Self="editodi2i10i23"/>
      </page>
      <page Self="courrierdi2ib">
        <title XMLContent="courrieru1b2" Self="courrierdi2ibi34"/>
        <article XMLContent="courrieru1c9" Self="courrierdi2ibi33"/>
        <article XMLContent="courrieru1e0" Self="courrierdi2ibi32"/>
        <article XMLContent="courrieru1fb" Self="courrierdi2ibi31"/>
        <article XMLContent="courrieru212" Self="courrierdi2ibi30"/>
      </page>
    </Root>


There is a convenient method to add several pages at once:

.. code-block:: python

    >>> edito_idml_file = IDMLPackage("magazineA-edito.idml")
    >>> courrier_idml_file = IDMLPackage("magazineA-courrier-des-lecteurs.idml")
    >>> bloc_notes_idml_file = IDMLPackage("magazineA-bloc-notes.idml")

    >>> with edito_idml_file.prefix("edito") as p_edito,\
    >>>      courrier_idml_file.prefix("courrier") as p_courrier,\
    >>>      bloc_notes_idml_file.prefix("blocnotes") as p_bloc_notes:

    >>>     packages_to_add = [
    ...         (p_courrier, 1, "/Root", "/Root/page[1]"),
    ...         (p_bloc_notes, 1, "/Root", "/Root/page[1]"),
    ...     ]

    >>>     new_idml = p_edito.add_pages_from_idml(packages_to_add)
    >>>     len(new_idml.pages)
    4
    >>>     new_idml.spreads
    ['Spreads/Spread_editoub6.xml',
     'Spreads/Spread_editoubc.xml',
     'Spreads/Spread_editoubd.xml']


Import/Export XML
-----------------

Exporting as XML:

.. code-block:: python

    >>> idml_file = IDMLPackage("path/to/file.idml")
    >>> print idml_file.export_xml()
    <Root>
        <module>
            <main_picture/>
            <headline>Hello world!</headline>
            <Story>
                <article>Lorem ipsum dolor sit amet, ...</article>
                <informations>Lorem ipsum dolor sit amet,</informations>
            </Story>
        </module>
    </Root>

You can as well import XML file into your InDesign® documents. The following rules applies:

- A node having the attribute ``simpleidml-setcontent="false"`` will not update the content of the
  corresponding element into the idml document (but its children will be updated).
- A node having the attribute ``simpleidml-ignorecontent"true"`` will not update the content of the
  corresponding element into the idml document **and** its children.
- A node having the attribute ``simpleidml-setcontent="delete"`` will remove the corresponding
  element into the idml document (Story and Spread elements).
- A node having the attribute ``simpleidml-setcontent="remove-previous-br"`` will remove the new-line
  characters before the element.
- You can mix several flags using a comma (i.e.: ``simpleidml-setcontent="delete,remove-previous-br"``)
- In a *ignorecontent* context the content of a child node can be turned on with the
  ``simpleidml-forcecontent="true"`` flag.
- Images references are passed by the *href* attribute. An empty value will remove the
  corresponding page items into the document.
- Nested tag will be created if they are mapped with a *character-style*.
- The style applied to the newly created tag is a combinaison of the parent character-styles and
  the mapped one.

Please take a look into the tests for in-depth examples.

Import PDF
----------

A block can be used as a placeholder for a PDF file:

.. code-block:: python

    >>> with IDMLPackage("my_package.idml") as idml_file:
    >>>     with idml_file.import_pdf("file:/path/to/file.pdf", at="/Root/modules/module[2]", crop="PDFCrop") as f:
    >>>         f.export_xml()

The ``crop`` parameter should be one of the ``PDFCrop_EnumValue`` from the IDML Specification
(``"CropArt"``, ``"CropPDF"``, ``"CropTrim"``, ``"CropBleed"``, ``"CropMedia"``,
``"CropContentVisibleLayers"``, ``"CropContentAllLayers"``, ``"CropContent"``).
It defaults to ``CropContentVisibleLayers````

Use InDesign server SOAP interface to convert a file
----------------------------------------------------

This require an *InDesign Server* and a readable/writable working directory.
The same directory must be accessible by the client either by the filesystem or
over FTP.

The ``formats`` parameter is a list (of dicts) of formats and parameters you want
your file to be exported into.
The supported output formats are ``jpeg``, ``idml``, ``pdf``, ``indd`` and
``zip`` (a zipped InDesign Package).

Export parameters are provided using the ``params`` key. Use
``simpleidml_indesign_save_as.py --help`` for a list of supported parameters.

The response is a list of binary strings matching ``formats`` provided:

.. code-block:: python

    from simple_idml.indesign import indesign

    response = indesign.save_as("/path_to_file.idml", [{"fmt": "indd"}],
                                "http://url-to-indesign-server:port",
                                "/path/to/client/workdir",
                                "/path/to/indesign-server/workdir")[0]
    with open("my_file.indd", "wb+") as f:
        f.write(response)

    response = indesign.save_as("/path_to_file.indd", [{"fmt": "idml"}],
                                "http://url-to-indesign-server:port",
                                "/path/to/client/workdir",
                                "/path/to/indesign-server/workdir")[0]
    with open("my_file.idml", "wb+") as f:
        f.write(response)

    response = indesign.save_as("/path_to_file.indd", [{
                                    "fmt": "pdf",
                                    "params": {"colorSpace": "CMYK"},
                                }],
                                "http://url-to-indesign-server:port",
                                "/path/to/client/workdir",
                                "/path/to/indesign-server/workdir")[0]
    with open("my_file.pdf", "wb+") as f:
        f.write(response)

    pdf_response, jpeg_response, zip_response = indesign.save_as(
                                    "/path_to_file.indd",
                                    [{"fmt": "pdf"}, {"fmt": "jpeg"}, {"fmt": "zip"}],
                                    "http://url-to-indesign-server:port",
                                    "/path/to/client/workdir",
                                    "/path/to/indesign-server/workdir")

To convert an InDesign Package, use ``indesign.export_package_as()`` instead.

If the InDesign Server instance runs on a Windows machine, set the
``indesign_server_path_style`` parameter to ``"windows"``.

If the client access to the working directory *via* FTP, you must specify that
in the ``ftp_params`` parameter:

.. code-block:: python

    {
        'auth': ("ftp://ftp.foo.org", "user_account", "s3cret-pa55word"),
        'passive': False,
        'keepalive': True,         # False by default (optional)
        'keepalive_interval': 30,  # set socket.TCP_KEEPINTVL (optional)
        'keepalive_idle': 45,      # set socket.TCP_KEEPIDLE  (optional)
        'polite': False,           # Unilaterally close ftp connection (optional)
    }

A script (``simpleidml_indesign_save_as.py``) that wraps these functions is
installed in your PATH.

Revisions
=========

1.1.3
-----

- Catch and log exceptions to the InDesign Server when setting options in
  export.jsx. Thanks to @kylehodgson for the contribution.

1.1.2
-----

New features
''''''''''''

- Add ``indesign.export_package_as()`` to convert an InDesign Package.

1.1.1
-----

New features
''''''''''''

- Add the possiblity to remove new-line characters when importing XML by using the flag
  ``simpleidml-setcontent="remove-previous-br"``.

1.1.0
-----

Removed Python 2 support.

New features
''''''''''''

- Add the possiblity to remove elements when importing XML by using the flag
  ``simpleidml-setcontent="delete"``.
- The ``PDFCrop`` attribute is now parametrable when using ``import_pdf()``.
- ``IDMLPackage.add_note(note, author, at=path)`` added.

1.0.5
-----

Bug fixes
'''''''''

- Fixed ``indesign.save_as()`` in Python 3 where the jsx file was opened
  in text mode instead of binary.

1.0.3
-----

- Use setuptools instead of distutils for a better integration with Pypi.

1.0.0
-----

New features
''''''''''''

- Added support for Python 3

Backward incompatibilities
''''''''''''''''''''''''''

- Removed support for Python 2.6

0.92.9
------

New features
''''''''''''

- Added ``simpleidml_indesign_profiles.py`` script to list the available joboptions
  files on the InDesign Server using the SOAP interface.

Bug fixes
'''''''''

- Fix working directory cleaning of the SOAP server when an exception is raised.
  ``indesign.save_as()`` may be backward incompatible since the returned list
  may contains some ``None`` (instead of raising an exception before returning
  anything).
- Give the list of available profiles (joboptions files) on the InDesign Server
  if the given 'pdfExportPresetName' is not found.

Backward incompatibilities
''''''''''''''''''''''''''

- ``indesign.close_all_documents()`` has been replace the ``CloseAllDocuments`` class
  and its ``.execute()`` method.
- Some util functions that wrap the basic file manipulations to manage the case of
  a ftp access to those files have been moved from indesign.py to a new ftp.py module.

0.92.8
------

New features
''''''''''''

- Added ``IDMLPackage.import_pdf()`` method.


Bug fixes
'''''''''

- Fix ``bleedMarks`` in export.jsx.

0.92.7
------

Bug fixes
'''''''''

- FillTint wasn't managed.
- Force ``lxml < 4`` in dependencies.

0.92.6
------

Bug fixes
'''''''''

- Catch errors when InDesign SOAP server fails to complete a task and raise
  an exception.

0.92.5
------

Bug fixes
'''''''''

- Handle <PDF> in `IDMLPackage._get_item_translation_for_insert()`

0.92.4
------

Bug fixes
'''''''''

- Fix issue #11: Parent CharacterStyle not applied in import_xml() in some cases.

0.92.2
------

New features
''''''''''''

- More ftp parameters for `indesign.save_as()` function. Hardcoded socket parameters are now
  modifiable. And you can set the flag `polite` to `False` if you encounter hanging problem
  on `ftp.quit()` as I do. Being unpolite calls an unilateral and rude `ftp.close()`.
  Please upgrade your code with explicite values if you rely on the previous default
  behavior.

0.92.1
------

Bug fixes
'''''''''

- ``indesign.save_as()`` uses a dedicated temporary working directory to avoid
  concurrent access on files.
- Added a logger to ``indesign.save_as()`` ('simpleidml.indesign') and some debug messages.
- Fixed hanging ``ftp.retrbinary()`` in ``indesign.save_as()`` calls by tuning the socket.

0.91.8
------

New features
''''''''''''

- Added support for PDF export presets in ``indesign.save_as()``.

0.91.7
------

New features
''''''''''''

- Added ``IMDLPackage.merge_layers(with_name)`` (Refs#7).
- Added a new script ``simpleidml_indesign_close_all_documents.py``.

Bug fixes
'''''''''

- In ``IDMLPackage.insert_idml()``, Elements from the same layer (but not tagged in the structure)
  are now added in the Spread of the document of destination.
- Better support for Windows platform.
- Fixed character style mapping with tag when using insert_idml.
- Fixed Export XML in some edge case.
- Added parameters to ``simpleidml_indesign_save_as`` when exporting to PDF.

Backward incompatibilities
''''''''''''''''''''''''''

- ``indesign.save_as()`` formats parameters is now a list of dictionaries.

0.91.6
------

New features
''''''''''''

- Add the ``simpleidml-ignorecontent`` and ``simpleidml-forcecontent`` tags (XML attributes)
  allowing one to carefully exclude a node and its children during the import XML process.
- ``indesign.save_as()`` now works with a client working directory over a FTP.
  This require ``wget`` to be on your system if you want to create zip packages.


Backward incompatibilities
''''''''''''''''''''''''''

- ``indesign.save_as()`` require both a client workdir and a server workdir parameter.

0.91.5.5
--------

Bugfixes
''''''''

- <EPS> elements in Spread weren't handled correctly.
- All spread elements were added in the destination package when using ``insert_idml()``.


0.91.3
------

New features
''''''''''''

Add a SOAP client to call a InDesign server to get INDD file and export in various
formats.

0.91.2
------

New features
''''''''''''

- Ticket #20 - Suffix layers.

Backward incompatibilities
''''''''''''''''''''''''''

- Ticket #22 - IDMLPackage.import_xml() parameter is a XML string and not a file object.

Bugfixes
''''''''

Tickets #19, #21 (orphan layers), #23 (AssertXMLEqual), #24 (import_xml() failure).


.. _XPath: http://en.wikipedia.org/wiki/XPath
