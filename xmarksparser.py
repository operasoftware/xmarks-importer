from HTMLParser import HTMLParser

class XMarksParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.bms = []
        self._item_stack = [self.bms, ]
        self._state = "start"

    def append_item(self, item):
        # In the root, we simply append the item,
        # otherwise we have to add to to children
        if self._state == "top":
            self._item_stack[-1].append(item)
        elif self._state == "folder":
            parent = self._item_stack[-1]
            if "children" not in parent:
                parent["children"] = []
            parent["children"].append(item)


    def handle_starttag(self, tag, attrs):
        if tag == "dl":
            if self._state == "start":
                self._state = "top"

        elif tag == "h3":
            folder = {
                "item_type": "bookmark_folder",
                "properties": {},
                }

            self.append_item(folder)
            self._item_stack.append(folder)
            self._state = "foldertitle"

        elif tag == "a":
            bookmark = {
                "item_type": "bookmark",
                "properties": {},
                }
            for name, value in attrs:
                if name == "href":
                    bookmark["properties"]["uri"] = value
            self.append_item(bookmark)
            self._state = "bookmark"
            self._item_stack.append(bookmark)

    def handle_endtag(self, tag):
        if tag in ("dl", "a"):
            self._item_stack.pop()

        if tag in ("dl", "a", "h3"):
            if len(self._item_stack) == 1:
                self._state = "top"
            else:
                self._state = "folder"

    def handle_data(self, data):
        if self._state in ("foldertitle", "bookmark"):
            self._item_stack[-1]["properties"]["title"] = data
