import sublime_plugin


class QuickFindEverywhereCommand(sublime_plugin.WindowCommand):

    def run(self):
        search_term, is_word = self.extract_search_term()
        print(self.window.active_view().substr(search_term))

    def extract_search_term(self):
        '''
        Returns a tuple (region, is_word).
            region - region containing the search term.
            is_word - boolean that specifies whether the search
                      term is a word.
        '''

        view = self.window.active_view()
        sels = view.sel()
        if len(sels) != 1:
            return None

        sel = sels[0]
        if sel.a == -1 or sel.b == -1:
            return None

        if sel.empty():
            word_region = view.word(sel)
            return (word_region, True)
        else:
            return (sel, False)
