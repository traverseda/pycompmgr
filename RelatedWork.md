There are a few other window manager agnostic compositing managers out there.

## [unagi](http://projects.mini-dweeb.org/projects/unagi) ##
A compositing manager written with XCB. It is quite new, and unstable. However, unagi was invaluable in helping to teach me how to write a compositing manager using XCB (or xpyb).

## [xcompmgr](http://cgit.freedesktop.org/xorg/app/xcompmgr/) ##
A "proof of concept" compositing manager developed by the same person who wrote the protocol specification for the Composite X extension. It is widely used for simple effects (opacity and drop shadows), and is generally considered inefficient. It also uses Xlib. xcompmgr played a minor role in helping me to build my own compositing manager.

## [Cairo Composite Manager](http://cairo-compmgr.tuxfamily.org/) ##
I have not investigated or tried this compositing manager quite yet, although it looks to be replacing xcompmgr as the go-to compositing manager for users with window managers that do not have built-in compositing managers (like Openbox, Fluxbox, etc.)