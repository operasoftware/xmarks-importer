from __future__ import with_statement

import sys
import json

from pyoperalink.auth import OAuth
from pyoperalink.datatypes import BookmarkFolder
from pyoperalink.client import LinkClient, OPERA_LINK_URL

import xmarksparser

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

auth = OAuth('0pkSfFbxApCMWoXKi0n67FgNxe2anNSq',
             'DUHLAnWClwT89HVrJwsSOLpOUrn1lYSk')

try:
    with open('access_token.txt', 'r') as token_file:
        a_t = token_file.readline().rstrip()
        a_t_s = token_file.readline().rstrip()
        auth.set_access_token(a_t, a_t_s)
except IOError:
    url = auth.get_authorization_url()
    print "Now go to:\n%s\nand type here the verifier code you get:" % (url)
    verifier = raw_input()
    if verifier == "":
        print "You need to write the verifier code. Please try again."
        sys.exit(1)
    token = auth.get_access_token(verifier)
    with open('access_token.txt', 'w') as token_file:
        token_file.write("%s\n%s\n" % (token.key, token.secret))

client = LinkClient(auth)


def import_bookmarks(auth, folder_id, bookmark_tree):
    raw_client = auth.Client(auth._consumer, auth.access_token)
    headers = {
        "Accept:": "application/json",
        "Content-Type": "application/json",
        }
    method = "POST"
    url = OPERA_LINK_URL + "/bookmark/%s/import/" % folder_id
    body = json.dumps(bookmark_tree)
    resp, content = raw_client.request(url, method, body=body, headers=headers)

    if resp["status"] == "200":
        print "Xmarks import completed successfully"
    else:
        print "Something went wrong"
        print resp
        print content

# Try to find previous import folder
import_folder = None
for entry in client.get_bookmarks():
    if isinstance(entry, BookmarkFolder) and entry.title == 'Xmarks':
        import_folder = entry

if import_folder is None:
    import_folder = BookmarkFolder(title='Xmarks')
    client.add(import_folder)

import_bookmarks(auth, import_folder.id, parser.bms)
