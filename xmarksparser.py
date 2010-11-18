from HTMLParser import HTMLParser


class XMarksParser(HTMLParser):
    """
    Processes HTML data in Xmarks' format.
    Returns a representation of this data as a python dictionary

    >>> html = u"<dl><dt><a href='www.opera.com'>Opera</a></dt><dl/>"
    >>> parser = XMarksParser()
    >>> parser.feed(html)
    >>> parser.bms
    [{'item_type': 'bookmark', 'properties': {'uri': u'www.opera.com', 'title': u'Opera'}}]
    """

    def __init__(self):
        HTMLParser.__init__(self)
        # The actual result of the parsing
        self.bms = []
        # Run stack for the parsing
        self._item_stack = [self.bms, ]
        # State of the state-machine
        self._state = "start"

    def append_item(self, item):
        """
        Depending on the state of the machine, appends the item either
        to the topmost list of results or in a list under the
        'children' key
        """
        if self._state == "top":
            self._item_stack[-1].append(item)
        elif self._state == "folder":
            parent = self._item_stack[-1]
            if "children" not in parent:
                parent["children"] = []
            parent["children"].append(item)

    def handle_starttag(self, tag, attrs):
        """
        Called on every start tag found
        """

        #Handles the first <dl> that encapsulates all items
        if tag == "dl":
            if self._state == "start":
                self._state = "top"

        # <h3> defines a new folder. The data in it is the title
        elif tag == "h3":
            folder = {
                "item_type": "bookmark_folder",
                "properties": {},
                }

            self.append_item(folder)
            self._item_stack.append(folder)
            self._state = "foldertitle"

        # <a> defines a new bookmark. The href is the URI.
        elif tag == "a":
            bookmark = {
                "item_type": "bookmark",
                "properties": {},
                }
            # Find the href attrib and assign it to URI
            for name, value in attrs:
                if name == "href":
                    bookmark["properties"]["uri"] = value
            self.append_item(bookmark)
            self._state = "bookmark"
            self._item_stack.append(bookmark)

    def handle_endtag(self, tag):
        """
        Called on every end tag found
        """
        # End of bookmark or folder definition.
        if tag in ("dl", "a"):
            item = self._item_stack.pop()

            # In case of missing titles, assign a default one
            if isinstance(item, dict) and "title" not in item["properties"]:
                item["properties"]["title"] = "No Title"

        if tag in ("dl", "a", "h3"):
            if len(self._item_stack) == 1:
                self._state = "top"
            else:
                self._state = "folder"

    def handle_data(self, data):
        """
        Called when data is found inside the tags.
        """
        if self._state in ("foldertitle", "bookmark"):
            self._item_stack[-1]["properties"]["title"] = data
