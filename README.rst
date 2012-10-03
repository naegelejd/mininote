**********
mininote
**********

A 90-line note-taking tool

Goals
========

- Improve my productivity by organizing ALL of my notes.
- Write a useful command-line tool in < 100 lines of code
- Attempt to follow most of `PEP-8 <http://www.python.org/dev/peps/pep-0008/>_`
  (Some of my lines are way over 80 chars, I import everything
  on one line... whatever)

Installation
=============
symbolically link ``note.py`` to ``/usr/local/bin/note``, or similar

Usage
======

#. run ``note`` on command line to add a new note
#. run ``note -h`` to see other options

Design
=======

Command-Line Tool
------------------
Basic options

-  help
-  version
-  list notes
-  edit notes

Editor
-------
The tool spawns either the editor specified by the
``$EDITOR`` environment variable, or ``vim``

Backend
--------
sqlite3 (bundled with Python)

extremely dumb schema::

    table notes
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        note TEXT,
        stamp INTEGER
    )

