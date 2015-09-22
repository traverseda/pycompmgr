Arguably, for this project, the primary goal was to get some kind of compositing effect working. However, as I began to get an effect working (in particular, opacity), it became evident that performance was indeed going to be a factor.

Performance for a compositing manager is extremely important, because effects ought not to disrupt a user's experience--and a lagging or slow-moving window is certainly going to achieve that. For example, when working on the opacity effect for pycompmgr, one needs to consider how often to re-paint the contents of the visible screen.

At first, it might seem enough to respond to a window's events. That is, when a window is moved or resized, update the screen with the new contents and size of a window. However, what happens when working inside a window? Since we are compositing the contents of all windows, we are responsible for updating the screen. That means there could be a disconnect between what the user sees and what is actually going on in the window. For example, you might type an entire sentence into a text editor before actually seeing the sentence appear to your screen.

To remedy this problem, a Damage extension for X was developed. In particular, Damage allows us to listen to a particular window for "damage" events--or when particular portions of the window are changed. Therefore, whenever a window fires a damage event, we update the screen.

However, we now may have the problem of updating the screen too much. This might have the effect of moving a window with your mouse, only to have the window follow your mouse 3 seconds later. (Similarly to resizing.)

I identified the bottleneck as related to my event processing queue (i.e., the code that checks for a new event and responds to it). In particular, I was blocking until I found one event, then re-paint, then check for another event. When **many** damage events are fired in a small time period, a significant performance penalty is incurred (since we're repainting after every damage event).

To work around this, I changed the event processing to empty out the _entire_ event queue, respond to each of those events, and _then_ re-paint the screen. So if 50 damage events are fired in a very short time period, pycompmgr will read in all 50 damage events, process them, and then re-paint the screen.

With a single effect, opacity, this approach works quite well. The screen is updated frequently enough so that the user isn't experiencing a disconnect between what the user sees and what is actually there, but it is also updated sparsely enough so that window moving/resizing is fairly smooth.