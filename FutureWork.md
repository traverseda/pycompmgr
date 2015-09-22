One of the great things about this project is that I can continue to develop it indefinitely. There are loads of visual effects that I could add, in addition to increasing performance, and using a different rendering library (instead of the X Render extension).

But first...

## Fix window representation in pycompmgr ##

Before moving on, it would be imperative to make pycompmgr be more accurate in representing the window stacking order and state, as it is known by the window manager.

## Increase performance ##

There are still some areas in which performance can be increased. In particular, when a damage event occurs, it tell us the region that has changed. It would be more efficient to find a way to re-paint just that region, instead of the entire screen.

## More visual effects ##

In addition to opacity, there are a litany of other visual effects that could be added. This includes, but is certainly not limited to: expose, drop shadows, and wobbly windows. As well as special effects when a window changes state (disappears, minimized, maximized, etc.).

## Use a different rendering library ##

The only other rendering library that is used in place of the X Render extension is OpenGL. I could certainly use that instead of, or in addition to, the X Render extension.