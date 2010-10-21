from HTMLParser import HTMLParser

class XMarksParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self._bms = None
        self._current_f = None
        self._state = ''

    def handle_starttag(self, tag, attrs):
        if tag == 'h3':
            self._state = 'foldertitle'
        elif tag == 'a':
            self._state = 'bookmark'
            href_attrs = [pair[1] for pair in attrs if pair[0] == 'href']
            self._bookmark_url = href_attrs[0]

    def handle_endtag(self, tag):
        if tag == 'h3':
            f = {'type': 'folder',
                 'title': self._data,
                 'children': [],
                 'parent_folder': self._current_folder()}
            self._current_folder()['children'].append(f)
            self._current_f = f
            self._state = ''
        if tag == 'a':
            self._current_folder()['children'].\
                append({'type': 'bookmark',
                        'title': self._data,
                        'url': self._bookmark_url})
            self._state = ''
        if tag == 'dl':
            self._current_f = self._current_folder()['parent_folder']

    def handle_data(self, data):
        if self._state == 'foldertitle' or self._state == 'bookmark':
            self._data = data

    def bookmarks(self):
        if self._bms is None:
            self._bms = {'type': 'folder',
                         'parent_folder': None,
                         'children': []}
        return self._bms

    def _current_folder(self):
        if self._current_f is None:
            self._current_f = self.bookmarks()
        return self._current_f
