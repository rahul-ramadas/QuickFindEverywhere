import sublime
import sublime_plugin


class QuickFindEverywhereCommand(sublime_plugin.TextCommand):

    def run(self, edit, forward=True):
        search_term_region, is_word = self.extract_search_term()
        if search_term_region is None:
            return

        # If nothing was selected, select the search term to give some visual
        # feedback, particularly for the case where the search doesn't find anything.

        if self.view.sel()[0].empty():
            self.view.sel().clear()
            self.view.sel().add(search_term_region)

        views = self.view.window().views()
        this_view_index, _ = next((i, v) for (i, v) in enumerate(views) if v.id() == self.view.id())

        from_pos = search_term_region.end() if forward else search_term_region.begin()

        search_term = self.view.substr(search_term_region)
        if is_word:
            search_term = '\\b' + search_term + '\\b'

        is_current_view = True
        if forward:
            view_index_iter = range(this_view_index, len(views))
        else:
            view_index_iter = range(this_view_index, -1, -1)

        for i in view_index_iter:
            if not is_current_view:
                from_pos = 0 if forward else views[i].size()
            if forward:
                found_region = self.find_next(views[i], from_pos, search_term, is_word)
            else:
                found_region = self.find_prev(views[i], from_pos, search_term, is_word)
            if found_region is not None:
                self.view.window().focus_view(views[i])
                return
            is_current_view = False

    def region_is_word(self, in_view, region):
        view = in_view
        word_region = view.word(region)
        if word_region.begin() == region.begin() and word_region.end() == region.end():
            return True
        return False

    def find_prev(self, in_view, from_pos, search_term, is_word):
        view = in_view
        result_region = None

        # Since Sublime does not offer an API to perform a text search
        # backwards, we need to get creative.
        # Do a binary search for the search term.

        def is_in_range(begin, end):
            '''
            Check if the word exists in this range and return the
            first region.
            '''
            region = view.find(search_term, begin)
            if region.empty() or region.a == -1 or region.b == -1:
                return None
            if region.end() > end:
                return None
            return region

        def find_mid_point(begin, end):
            '''
            Find the middle point for the binary search. Round up to the
            next word boundary.
            '''
            middle = (begin + end) // 2
            middle = view.find_by_class(middle, True, sublime.CLASS_WORD_END)
            return middle

        lower = 0
        upper = from_pos
        result_region = is_in_range(lower, upper)
        if result_region is None:
            return

        middle = find_mid_point(lower, upper)
        while middle > lower and middle < upper:
            region = is_in_range(middle, upper)
            if region is not None:
                result_region = region
                lower = middle
            else:
                upper = middle
            middle = find_mid_point(lower, upper)

        view.sel().clear()
        view.sel().add(result_region)
        view.show(result_region)
        return result_region

    def find_next(self, in_view, from_pos, search_term, is_word):
        view = in_view

        current_pos = from_pos
        result_region = view.find(search_term, current_pos)

        if result_region.empty() or result_region.a == -1 or result_region.b == -1:
            return

        view.sel().clear()
        view.sel().add(result_region)
        view.show(result_region)
        return result_region

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

        # Don't know what to do with multiple selections.
        if len(sels) != 1:
            return (None, None)

        sel = sels[0]

        # Occasionally, there are these bogus selections.
        if sel.a == -1 or sel.b == -1:
            return (None, None)

        if sel.empty():
            # Select the word under the cursor.
            word_region = view.word(sel)
            return (word_region, True)
        else:
            # Something is already selected. That is probably what we need
            # to search for.
            return (sel, self.region_is_word(view, sel))
