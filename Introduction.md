pycompmgr is a compositing manager written in Python (using Python 2.7) and the X Python Binding (xpyb). xpyb is the Python version of XCB, which is a low-level transport layer designed to communicate with an X server.

A composting manager is a tool used to manipulate windows in off-screen storage, and then paint those effects to the screen. Traditionally, windows are directly painted to the screen, without any intermediary steps.

In X, this is achieved using the Composite extension. The extension allows one to tell the X server to redirect all windows to some off screen storage--which implies a promise on our behalf that we will draw the windows to the screen.

Usually, there are two manifestations of a compositing manager in X: a window manager agnostic compositing manager, and a compositing manager built inside a window manager. pycompmgr falls in to the former category.

pycompmgr was developed on Openbox, however, it appears to partially work with KWin (KDE's window manager), when KWin's compositing effects are disabled.