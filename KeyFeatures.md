Since a lot of the work involved in this project was to get a compositing manager up and running, the only feature I had time to implement was window opacity (which is adjustable, in real time).

In particular, getting the compositing manager up and running means accurately storing window state and stacking order so that it corresponds to the window manager's vision of window state and stacking order. For example, when a window is minimized, pycompmgr must reflect that by not drawing it to the screen, or when a window is moved in the stacking order (i.e., brought to focus), pycompmgr must draw the window in the appropriate order.

As for opacity, it works by reading a `_`NET\_WM\_WINDOW\_OPACITY property on a given window. (This property isn't part of any standard, but is used by multiple compositing managers.) It can be changed in the same way that any other property on a window can be changed, however, a utility exists that specifically changes `_`NET\_WM\_WINDOW\_OPACITY. That utility is [transset-df](http://forchheimer.se/transset-df/). In particular, at the project demo, I bound these commands to my mouse wheel so that I could change the opacity in real time:

`transset-df -p --max 1.0 --inc 0.05`

`transset-df -p --min 0.1 --dec 0.05`

With the former on the "up" and the latter on the "down" motions of the scroll wheel. The first command says to increment the opacity by 5% and never let it go over 1. The second command says to decrement the opacity by 5% and never let it go below 0.1. The reason for 0.1 instead of 0, is that when the window is completely transparent (i.e., no opacity), it is invisible.

While I mentioned that `_`NET\_WM\_WINDOW\_OPACITY is not a standard, these same commands work with xcompmgr and unagi to modify the transparency of a window.

A screenshot of window opacity in action (click on the image for a full view):

![![](http://pytyle.com/images/opacity-thumb.jpg)](http://pytyle.com/images/opacity.jpg)