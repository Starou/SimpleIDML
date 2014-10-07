==========
SimpleIDML
==========

Installation
============

Use ``pip``:

.. code-block:: bash

    pip install SimpleIDML

Or:

.. code-block:: bash

    python setup.py build
    sudo python setup.py install

Dependencies
------------

- Python >= 2.6
- lxml >= 2.3
- unittest2 if Python < 2.7
- suds (if you want to use the SOAP interface of the InDesign Server.)


What is SimpleIDML ?
====================

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

What are IDML files ?
=====================

IDML (*InDesign Markup Language*) files are a Zip archives (Adobe calls them packages) storing
essentially XML files. Adobe made a descent job because those files can completely express the
content of the native (binary) documents.
This is a small revolution in the print world when it comes to automatically process files in both
ways from templates and database (Round-trip) without using proprietary server-edition of
Publishing Software.

What does SimpleIDML do ?
=========================

Package exploration
-------------------

You can discover the structure of your IDML files::


    >>> from simple_idml import idml
    >>> my_idml_package = idml.IDMLPackage("/path/to/my_main_document.idml")
    >>> my_idml_package.spreads
    [u'Spreads/Spread_ub6.xml', u'Spreads/Spread_ubc.xml', u'Spreads/Spread_uc3.xml']
    >>> my_idml_package.stories
    [u'Stories/Story_u139.xml', u'Stories/Story_u11b.xml', u'Stories/Story_u102.xml', u'Stories/Story_ue4.xml']
    

Some attributes are *lxml.etree* Elements or Documents::

    >>> my_package.font_families
    [<Element FontFamily at 0x1010048c0>, <Element FontFamily at 0x101004a50>, <Element FontFamily at 0x101004aa0>,
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


Insert elements
'''''''''''''''

Using the XML Structure you can ask SimpleIDML to insert into a document at a XML tag the content
of another XML tag from another document. The tag paths are expressed using XPath_ syntax.
Note that you should always make a copy of your idml files before altering them with
``shutil.copy2(src, dst)`` for instance and prefix your document before using ``insert_idml()``
to avoid reference collisions.

::


    >>> from simple_idml import idml
    >>> idml_main = idml.IDMLPackage("/path/to/my_main_document.idml")
    >>> idml_module = idml.IDMLPackage("/path/to/my_small_document.idml")

    >>> idml_main = idml_main.prefix("main")
    >>> idml_article = idml_module.prefix("article")

    >>> idml_main = idml_main.insert_idml(idml_article, at="/Root/article[3]", only="/Root/module[1]")
    >>> idml_main.stories
    ['Stories/Story_article1u188.xml', 'Stories/Story_article1u19f.xml', 'Stories/Story_article1u1db.xml', 
     'Stories/Story_mainu102.xml', 'Stories/Story_mainu11b.xml', 'Stories/Story_mainu139.xml', 'Stories/Story_mainue4.xml']


    >>> print idml_main.xml_structure_pretty()
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

You may need to gather pages from severals documents into a single one::

    >>> edito_idml_file = IDMLPackage("magazineA-edito.idml")
    >>> courrier_idml_file = IDMLPackage("magazineA-courrier-des-lecteurs.idml")

    >>> # Always start by prefixing packages to avoid collision.
    >>> edito_idml_file = edito_idml_file.prefix("edito")
    >>> courrier_idml_file = courrier_idml_file.prefix("courrier")
    >>> len(edito_idml_file.pages)
    2

    >>> new_idml = edito_idml_file.add_page_from_idml(courrier_idml_file,
    ...                                               page_number=1,
    ...                                               at="/Root",
    ...                                               only="/Root/page[1]")
    >>> len(new_idml.pages)
    3

    # The XML Structure has integrated the new file.
    >>> print etree.tostring(new_idml.xml_structure, pretty_print=True)
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


There is a convenient method to add several pages at once::

    >>> edito_idml_file = IDMLPackage("magazineA-edito.idml")
    >>> courrier_idml_file = IDMLPackage("magazineA-courrier-des-lecteurs.idml")
    >>> bloc_notes_idml_file = IDMLPackage("magazineA-bloc-notes.idml")

    >>> edito_idml_file = edito_idml_file.prefix("edito")
    >>> courrier_idml_file = courrier_idml_file.prefix("courrier")
    >>> bloc_notes_idml_file = bloc_notes_idml_file.prefix("blocnotes")

    >>> packages_to_add = [
    ...     (courrier_idml_file, 1, "/Root", "/Root/page[1]"),
    ...     (bloc_notes_idml_file, 1, "/Root", "/Root/page[1]"),
    ... ]

    >>> new_idml = edito_idml_file.add_pages_from_idml(packages_to_add)
    >>> len(new_idml.pages)
    4
    >>> new_idml.spreads
    ['Spreads/Spread_editoub6.xml', 'Spreads/Spread_editoubc.xml', 'Spreads/Spread_editoubd.xml']


Import/Export XML
-----------------

Exporting as XML:

.. code-block:: python

    >>> idml_file = IDMLPackage("path/to/file.idml")
    >>> print idml_file.export_xml()
    ... <Root>
    ...     <module>
    ...         <main_picture/>
    ...         <headline>Hello world!</headline>
    ...         <Story>
    ...             <article>Lorem ipsum dolor sit amet, ...</article>
    ...             <informations>Lorem ipsum dolor sit amet,</informations>
    ...         </Story>
    ...     </module>
    ... </Root>

You can as well import XML file into your InDesign® documents. The following rules applies:

- A node having the attribute ``simpleidml-setcontent="false"`` will not update the content of the
  corresponding element into the idml document (but its children will be updated).
- A node having the attribute ``simpleidml-ignorecontent"true"`` will not update the content of the
  corresponding element into the idml document **and** its children.
- In a *ignorecontent* context the content of a child node can be turned on with the
  ``simpleidml-forcecontent="true"`` flag.
- Images references are passed by the *href* attribute. An empty value will remove the
  corresponding page items into the document.
- Nested tag will be created if they are mapped with a *character-style*.
- The style applied to the newly created tag is a combinaison of the parent character-styles and
  the mapped one.

Please take a look into the tests for in-depth examples.

Use InDesign server SOAP interface to convert a file
----------------------------------------------------

This require an InDesign Server and a directory that it can access in read/write.
The ``formats`` parameter is a list of formats you want your file to be exported into.
The supported formats are ``jpeg``, ``idml``, ``pdf``, ``indd`` and ``zip`` (this one
returning a zipped InDesign package).

Here some snippets:

.. code-block:: python

    from simple_idml.indesign import indesign

    response = indesign.save_as("/path_to_file.idml", ["indd"],
                                "http://url-to-indesign-server:port",
                                "/path/to/indesign-server/workdir")[0]
    with open("my_file.indd", "w+") as f:
        f.write(response)

    response = indesign.save_as("/path_to_file.indd", ["idml"],
                                "http://url-to-indesign-server:port",
                                "/path/to/indesign-server/workdir")[0]
    with open("my_file.idml", "w+") as f:
        f.write(response)

    response = indesign.save_as("/path_to_file.indd", ["pdf"],
                                "http://url-to-indesign-server:port",
                                "/path/to/indesign-server/workdir")[0]
    with open("my_file.pdf", "w+") as f:
        f.write(response)

The response is a list of string because you can pass a list of formats
and so generate several exports in a row (if performances matter):

.. code-block:: python

    from simple_idml.indesign import indesign
    pdf_response, jpeg_response, zip_response = indesign.save_as(
                                    "/path_to_file.indd",
                                    ["pdf", "jpeg", "zip"],
                                    "http://url-to-indesign-server:port",
                                    "/path/to/indesign-server/workdir")



Revisions
=========

0.91.6
------

New features
''''''''''''

Add the ``simpleidml-ignorecontent`` and ``simpleidml-forcecontent`` tags (XML attributes) allowing one
to carefully exclude a node and its children during the import XML process.

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
