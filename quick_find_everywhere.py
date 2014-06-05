import sublime
import sublime_plugin


class QuickFindEverywhereCommand(sublime_plugin.TextCommand):

    def run(self, edit, forward=True):
        search_term_region, is_word = self.extract_search_term()
        if search_term_region is None:
            return

        if forward:
            self.find_next(search_term_region, is_word)
        else:
            self.find_prev(search_term_region, is_word)

    def region_is_word(self, region):
        word_region = self.view.word(region)
        if word_region.begin() == region.begin() and word_region.end() == region.end():
            return True
        return False

    def find_prev(self, search_term_region, is_word):
        view = self.view
        current_line = view.line(search_term_region.begin())
        must_be_before = search_term_region.begin()
        search_term = view.substr(search_term_region)

        def find_last_in_line(current_line, must_be_before):
            current_region = None
            from_position = current_line.begin()
            while True:
                next_region = view.find(search_term, from_position, sublime.LITERAL)

                if next_region.empty() or next_region.a == -1 or next_region.b == -1:
                    break

                if next_region.end() <= must_be_before:
                    if not is_word or self.region_is_word(next_region):
                        current_region = next_region
                    from_position = next_region.end()
                else:
                    break

            return current_region

        while True:
            result_region = find_last_in_line(current_line, must_be_before)
            if result_region is not None:
                break
            if current_line.begin() == 0:
                break
            current_line = view.line(current_line.begin() - 1)
            must_be_before = current_line.end()

        if result_region is None:
            return

        view.sel().clear()
        view.sel().add(result_region)
        view.show(result_region)

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
