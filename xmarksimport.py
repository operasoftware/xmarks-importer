from __future__ import with_statement

import sys
import xmarksparser

from pyoperalink.auth import OAuth
from pyoperalink.request import LinkClient
from pyoperalink.datatypes import Bookmark, BookmarkFolder

if len(sys.argv) != 2:
    print "xmarksimport.py imports an HTML bookmark file to your Link account."
    print "The bookmarks will be importer to a folder called 'Xmarks'"
    print "The format of the file should be the export format Xmarks uses."
    print "USAGE: xmarksimport.py <mybookmarks.html>"
    sys.exit(1)

bookmark_file = sys.argv[1]

with open(bookmark_file) as bookmark_file:
    content = bookmark_file.read()
    parser = xmarksparser.XMarksParser()
    parser.feed(content.decode('utf-8'))

# ---------------------------------
# import pprint
# pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(parser.bookmarks())
# ---------------------------------

auth = OAuth('0pkSfFbxApCMWoXKi0n67FgNxe2anNSq',
             'DUHLAnWClwT89HVrJwsSOLpOUrn1lYSk')

try:
    with open('access_token.txt', 'r') as token_file:
        a_t = token_file.readline().rstrip()
        a_t_s = token_file.readline().rstrip()
        auth.set_access_token(a_t, a_t_s)
except IOError:
    url = auth.get_authorization_url()
    print "Now go to:\n\n%s\n\nand type here the verifier code you get:" % (url)
    verifier = raw_input()
    if verifier == "":
        print "You need to write the verifier code. Please try again."
        sys.exit(1)
    token = auth.get_access_token(verifier)
    with open('access_token.txt', 'w') as token_file:
        token_file.write("%s\n%s\n" % (token.key, token.secret))

client = LinkClient(auth)

def import_bookmarks(client, import_folder, source_bookmark_folder):
    for bm_data in source_bookmark_folder['children']:
        if bm_data['type'] == 'bookmark':
            print ">> Bookmark '%s' => '%s'" % \
                (bm_data['title'], bm_data['url'])
            bm = Bookmark(title=bm_data['title'], uri=bm_data['url'])
            client.add_to_folder(bm, import_folder)
        elif bm_data['type'] == 'folder':
            print "Folder '%s'" % \
                (bm_data['title'],)
            bmf = BookmarkFolder(title=bm_data['title'])
            client.add_to_folder(bmf, import_folder)
            import_bookmarks(client, bmf, bm_data)

# Try to find previous import folder
import_folder = None
for entry in client.get_bookmarks():
    if isinstance(entry, BookmarkFolder) and entry.title == 'Xmarks':
        import_folder = entry

if import_folder is None:
    import_folder = BookmarkFolder(title='Xmarks')
    client.add(import_folder)


import_bookmarks(client, import_folder, parser.bookmarks())
