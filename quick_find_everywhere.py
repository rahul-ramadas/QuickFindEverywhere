import sublime
import sublime_plugin


class QuickFindEverywhereCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        search_term_region, is_word = self.extract_search_term()
        if search_term_region is None:
            return

        self.find_next(search_term_region, is_word)

    def region_is_word(self, region):
        word_region = self.view.word(region)
        if word_region.begin() == region.begin() and word_region.end() == region.end():
            return True
        return False

    def find_next(self, search_term_region, is_word):
        view = self.view
        search_term = view.substr(search_term_region)

        current_pos = search_term_region.end()
        while True:
            result_region = view.find(search_term, current_pos, sublime.LITERAL)
            if result_region.empty() or result_region.a == -1 or result_region.b == -1:
                return

            if not is_word or self.region_is_word(result_region):
                break

            current_pos = result_region.end()

        view.sel().clear()
        view.sel().add(result_region)
        view.show(result_region)

    def extract_search_term(self):
        '''
        Returns a tuple (region, is_word).
            region - region containing the search term.
            is_word - boolean that specifies whether the search
                      term is a word.

        Returns (None, None) if a search term could not be extracted.
        '''

        view = self.view
        sels = view.sel()
        if len(sels) != 1:
            return (None, None)

        sel = sels[0]
        if sel.a == -1 or sel.b == -1:
            return (None, None)

        if sel.empty():
            word_region = view.word(sel)
            return (word_region, True)
        else:
            return (sel, self.region_is_word(sel))
