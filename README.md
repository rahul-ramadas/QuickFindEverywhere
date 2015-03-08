QuickFindEverywhere
=====================

Sublime Text 3 plugin that provides a convenient command to quickly jump to the next or previous occurence of the selected text, or the word under the cursor if nothing is selected, from among all open files.

Key Bindings
------------

There are no bindings out-of-the-box. Bind the command to a convenient shortcut by adding the following to your key bindings:
```
    {
        "command": "quick_find_everywhere",
        "args": { "forward": true },
        "keys": [ "ctrl+'" ]
    },
    {
        "command": "quick_find_everywhere",
        "args": { "forward": false  },
        "keys": [ "ctrl+;" ]
    }
```

Installation
------------

`git clone` into your packages directory.
