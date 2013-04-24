import signal, time, curses

class curses_screen:
  def __enter__(self):
    self.stdscr = curses.initscr()
    curses.start_color()
    curses.cbreak()
    curses.noecho()
    curses.curs_set(0)
    self.stdscr.keypad(1)
    return self.stdscr
  
  def __exit__(self,a,b,c):
    curses.nocbreak()
    self.stdscr.keypad(0)
    curses.echo()
    curses.endwin()
  
  
class Window:
  def __init__(self, screen):
    self.screen = screen
    self.windowratio = 0.25
    (self.h, self.w) = self.screen.getmaxyx()
    #signal.signal(signal.SIGWINCH, self.sizehandler)

    left_startx = 1
    left_starty = 1
    left_width = int(self.w*self.windowratio) - 2*left_startx
    left_height = self.h-left_starty*2
    self.leftwin  = curses.newwin(left_height, left_width, left_starty, left_startx)
    
    right_startx = left_startx + left_width + 2
    right_starty = 1
    right_width = self.w - right_startx - 1
    right_height = self.h-right_starty*2
    self.rightwin  = curses.newwin(right_height, right_width, right_starty, right_startx)
    
    self.screen.timeout(10)
    
  def resize(self):
    left_startx = 1
    left_starty = 1
    left_width = int(self.w*self.windowratio) - 2*left_startx
    left_height = self.h-left_starty*2
    self.leftwin.resize(left_height, left_width)
    self.leftwin.mvwin(left_starty, left_startx)
    
    right_startx = left_startx + left_width + 2
    right_starty = 1
    right_width = self.w - right_startx - 1
    right_height = self.h-right_starty*2
    self.rightwin.resize(right_height, right_width)
    self.rightwin.mvwin(right_starty, right_startx)
    
  def render(self):
    event = self.screen.getch()
    if event == curses.KEY_RESIZE:
      (self.h, self.w) = self.screen.getmaxyx()
      self.resize()
    
    self.screen.erase()
    self.screen.vline(0, int(self.windowratio*self.w), '|', self.h)
    self.screen.noutrefresh()

    self.leftwin.erase()
    for i in range(1,10):
      self.leftwin.addstr(i, 2, 'hello ' + str(i))
    self.leftwin.noutrefresh()
    
    self.rightwin.erase()
    self.rightwin.addstr(i, 2, 'Size: ' + str(self.w) + ', ' + str(self.h))
    for i in range(1,10):
      self.rightwin.addstr(i, 2, 'goodbye ' + str(i))
    self.rightwin.noutrefresh()
    
    
    curses.doupdate()
  
  
with curses_screen() as screen:
  window = Window(screen)

  while True:
    window.render()
    time.sleep(100)
