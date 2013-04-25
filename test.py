import curses

COLOR_NORMAL   = 1
COLOR_FINISHED = 2
COLOR_FAILED   = 3

class curses_screen:
  def __enter__(self):
    self.stdscr = curses.initscr()
    curses.start_color()
    curses.cbreak()
    curses.noecho()
    curses.curs_set(0)
    self.stdscr.keypad(1)
    curses.init_pair(COLOR_NORMAL, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(COLOR_FINISHED, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(COLOR_FAILED, curses.COLOR_RED, curses.COLOR_BLACK)
    return self.stdscr
  
  def __exit__(self,a,b,c):
    curses.nocbreak()
    self.stdscr.keypad(0)
    curses.echo()
    curses.endwin()

def debug(stdscr):
    curses.nocbreak()
    stdscr.keypad(0)
    curses.echo()
    curses.endwin()
    import pdb; pdb.set_trace()

######################################################################
class DataLine:
  def __init__(self, data = {}):
    self.data = data
  
  def render(self, window, y, x, maxx, fmt):
    if x > maxx: return
    
    currx = x
    for d in self.data:
      currfmt = fmt
      if d.has_key('fmt'): currfmt |= d['fmt']
      window.addstr(y, currx, d['str'][0:max(0,maxx-currx-1)], currfmt)
      currx += len(d['str'])
      if currx >= maxx: return
  
######################################################################
class ScrollPane:
  def __init__(self, parent, height, width, y, x):
    self.parent = parent
    self.window = parent.subwin(height, width, y, x)
    self.selected = 0
    self.topvisible = 0
    self.height = height
    self.width  = width
    
  def resize(self, height, width):
    if height < 2: return
    self.window.resize(height, width)
    self.height = height
    self.width  = width
  
  def move(self, y, x):
    if self.height < 3: return
    self.window.mvwin(y, x)
    
  def setData(self, data):
    """ Set the data to be displayed. Data should be a list of dictionaries with keys 'string' and an optional key 'format' """
    self.data = data
  
  def render(self):
    if self.height < 3: return
    self.window.erase()
    
    for i, d in enumerate(self.data[self.topvisible:self.topvisible+self.height]):
      fmt = curses.A_NORMAL
      if i+self.topvisible == self.selected:
        fmt = curses.A_REVERSE
      d.render(self.window, i, 2, self.width, fmt)
      
    self.window.noutrefresh()
    
  def setTopVisible(self, topvisible):
    self.topvisible = min(len(self.data), max(0, topvisible))
    
  def setSelected(self, selected):
    self.selected = min(len(self.data), max(0, selected))
    if self.selected < self.topvisible:
      self.setTopVisible(self.selected)
    elif self.selected > self.topvisible+self.height-1:
      self.setTopVisible(self.selected-self.height+1)

class Window:
  def __init__(self, screen):
    self.screen = screen
    self.windowratio = 0.25
    (self.h, self.w) = self.screen.getmaxyx()

    left_startx = 1
    left_starty = 1
    left_width = int(self.w*self.windowratio) - 2*left_startx
    left_height = self.h-left_starty*2
    self.leftscroll = ScrollPane(screen, left_height, left_width, left_starty, left_startx)
    
    right_startx = left_startx + left_width + 2
    right_starty = 1
    right_width = self.w - right_startx - 1
    right_height = self.h-right_starty*2
    self.rightwin  = curses.newwin(right_height, right_width, right_starty, right_startx)
    
    self.screen.timeout(10)
    self.lastevent = 0
    
  def resize(self):
    left_startx = 1
    left_starty = 1
    left_width = int(self.w*self.windowratio) - 2*left_startx
    left_height = self.h-left_starty*2
    self.leftscroll.resize(left_height, left_width)
    self.leftscroll.move(left_starty, left_startx)
    
    #right_startx = left_startx + left_width + 2
    #right_starty = 1
    #right_width = self.w - right_startx - 1
    #right_height = self.h-right_starty*2
    #self.rightwin.resize(right_height, right_width)
    #self.rightwin.mvwin(right_starty, right_startx)
    
  def render(self):
    event = self.screen.getch()
    if event == curses.KEY_UP or event == ord('k'):
      self.leftscroll.setSelected(self.leftscroll.selected - 1)
    elif event == curses.KEY_DOWN or event == ord('j'):
      self.leftscroll.setSelected(self.leftscroll.selected + 1)
    elif event == curses.KEY_RESIZE:
      (self.h, self.w) = self.screen.getmaxyx()
      self.resize()
    elif event == 21:
      self.leftscroll.setSelected(self.leftscroll.selected - 10)
    elif event == 4:
      self.leftscroll.setSelected(self.leftscroll.selected + 10)
    
    if event != -1: self.lastevent = event
    
    self.screen.erase()
    self.screen.vline(0, int(self.windowratio*self.w), '|', self.h)
    self.screen.noutrefresh()



    self.leftscroll.setData([DataLine([{'str': 'My Precious ' + str(x)}, {'str': ' Amazing', 'fmt':  curses.color_pair(COLOR_NORMAL)}]) for x in range(0,100)])

    self.leftscroll.render()
    #self.leftwin.erase()
    #for i in range(1,10):
    #  self.leftwin.addstr(i, 2, 'hello ' + str(i))
    #self.leftwin.noutrefresh()
    
    #self.rightwin.erase()
    #self.rightwin.addstr(i, 2, 'Size: ' + str(self.w) + ', ' + str(self.h))
    #for i in range(1,10):
    #  self.rightwin.addstr(i, 2, 'goodbye ' + str(i))
    #self.rightwin.noutrefresh()
    
    
    curses.doupdate()
  
if __name__ == '__main__': 
  with curses_screen() as screen:
    window = Window(screen)

    while True:
      window.render()
