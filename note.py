#!/usr/bin/env python
import os, sys, time, sqlite3, logging, datetime, subprocess    # bad style
from optparse import OptionParser
from tempfile import NamedTemporaryFile

NOTESDIR = os.path.abspath(os.path.expanduser("~/.mynote"))
DBPATH = os.path.join(NOTESDIR, "notes.dat")
HEADER = "|      | Date       | Time     | Note\n" + '-' * 38

ADDMODE, EDITMODE, LISTMODE, REPORTMODE = range(4)

def main():
    p = OptionParser(description='A SIMPLE note taking utility', epilog='2012-09-22', version='%prog 0.1')
    p.add_option('-v', '--verbose', action='store_true', help='verbose mode')
    p.add_option('-a', '--add', action='store_true', help='add new note (DEFAULT mode)')
    p.add_option('-e', '--edit', action='store_true', help='edit existing note')
    p.add_option('-l', '--list', dest="list_all", action='store_true', help='list notes')
    p.add_option('-r', '--report', action='store_true', help='list ALL notes, ever')
    p.add_option('-d', '--date', metavar="YYYY-MM-DD", help='specify date (DEFAULT=today)')
    p.set_defaults(verbose=False, add=False, edit=False,
            list_all=False, report=False, date=str(datetime.date.today()))
    (options, args) = p.parse_args()

    level = (logging.ERROR, logging.DEBUG)[options.verbose]
    logging.basicConfig(level=level, format='%(message)s')

    mode = (ADDMODE, EDITMODE)[options.edit]
    mode = (mode, LISTMODE)[options.list_all]
    mode = (mode, REPORTMODE)[options.report]

    if not os.path.isdir(NOTESDIR):     # create user notes dir if it doesn't exist
        os.makedirs(NOTESDIR)
    if not os.path.isfile(DBPATH):      # create db if it doesn't exist
        query("create table notes (id INTEGER PRIMARY KEY AUTOINCREMENT, note TEXT, stamp INTEGER)", ())
    try:
        when = int(time.mktime(datetime.datetime.strptime(options.date, "%Y-%m-%d").timetuple()))    # python > 2.4
    except:
        error("Can't parse option date")

    actions = [add_note, edit_note, list_notes, list_notes]
    actions[mode]((when, 0)[mode == REPORTMODE], (86400, sys.maxint)[mode == REPORTMODE])

def error(msg):
    logging.error(msg)
    sys.exit(1)

def query(statement, parameters):
    conn = sqlite3.connect(DBPATH)
    result = None
    with sqlite3.connect(DBPATH) as conn:
        cur = conn.cursor()
        cur.execute(statement, parameters)
        result = cur.fetchall()
        cur.close()
        conn.commit()
    return result

def user_input(prompt):
    with NamedTemporaryFile(suffix=".rst", delete=False) as fobj:
        name = fobj.name
        fobj.write(prompt)
    editor = os.getenv("EDITOR", "vim")
    if subprocess.call([editor, name]) != 0:    # spawn editor
        error("Could not open text editor")
    with open(name) as fobj:
        note = fobj.read()  # read what user wrote to the tempfile in their editor
    os.unlink(name) # delete temporary file
    # strip extra newline... not sure where it comes from
    note = (note, note[:-1])[len(note) > 0 and note[-1] == '\n']
    return note

def show_notes(query_results):
    options = list()
    for row in query_results:
        options.append(row[0])
        dt = datetime.datetime.fromtimestamp(row[2])
        lines = row[1].splitlines()
        note = (lines[0], lines[0] + ' (cont...)')[len(lines) > 1]
        print("| %4d | %s | %s | %s" % (len(options), dt.date(), dt.time(), note))
    return options

def list_notes(when, delta):
    print(HEADER)
    show_notes(query("select * from notes where stamp between ? and ?", (when, when + delta)))

def edit_note(when, delta):
    print(HEADER)
    options = show_notes(query("select * from notes where stamp between ? and ?", (when, when + delta)))
    try:
        choice = int(raw_input("Choice? "))     # int() cast will raise ValueError on bad cast
        if choice > len(options) or choice < 1:     # these wouldn't normally cause ValueErrors
            raise ValueError
    except ValueError:
        error("Not a valid option")
    note = query("select note from notes where id = ?", (options[choice - 1], ))[0][0]
    edited_note = user_input(note)
    query("update notes set note = ? where id = ?", (edited_note, options[choice - 1], ))

def add_note(when, delta):  # delta not used
    note = user_input("")
    t = when + (int(time.time()) - when) % 86400    # convert date to date+time
    if note != "" and note is not None:
        query("insert into notes(note, stamp) values(?, ?)", (note, t))

if __name__ == "__main__":
    main()
