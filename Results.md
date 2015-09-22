The final product seems to work quite well in that it allows one to make windows transparent. However, there are still some problems with representing the window state and stacking order in pycompmgr.

For example, different clients (i.e., windows) fire different series of events when being created, which need to be accounted for in pycompmgr. This implies that some windows in pycompmgr aren't being properly represented, and therefore, the display becomes inconsistent with what the window manager thinks is being displayed.

In particular, it's possible to open a window, and pycompmgr won't display it (although, this is not always the case). It is also possible to mess with the stacking order in pycompmgr, so that clicking a window to focus it might actually appear to focus another window. Similarly, it's possible to close a window but still see it on the display.

With regards to performance, pycompmgr seems to do quite well. Even though it is written in a scripting language, window movement and resizing is, for the most part, fairly smooth (although there are some hiccups occasionally).