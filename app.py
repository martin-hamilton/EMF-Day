import app
import requests
import ujson
import math
from events.input import Buttons, BUTTON_TYPES
from app_components import clear_background
# import EMF logo as bitmap - not working yet
#from . import emf2024-logo-dark-small as emf2024-logo
#from tildagonos import tildagonos

class EMF_Day(app.App):
    def __init__(self):
        self.button_states = Buttons(self)
        # we'll fetch the current UK time from here - could be localised by our IP address
        self.url = "http://worldtimeapi.org/api/timezone/Europe/London"
        # placeholder text in case URL fetch takes a long time / times out
        self.slurptxt = "EMF\nDay"
        # 9am on 31st May 2024...
        self.day_one = 1717142400
        # so we can check if display output rendered and avoid re-doing
        self.rendered = False

    def update(self, delta):
        if self.button_states.get(BUTTON_TYPES["CANCEL"]):
            self.button_states.clear()
            self.minimise()

        if self.rendered == False:
            # go off and fetch the time - could also be done via NTP, could use RTC
            self.slurptxt = timeslurp(self.url, self.day_one)
            # set this flag so we don't keep fetching/drawing every 0.05s
            self.rendered = True

    def draw(self, ctx):
        clear_background(ctx)
        ctx.save()
        #diagonal linear gradient in EMF style guide colours
        ctx.linear_gradient(-120,-120,240,240)
        ctx.add_stop(0.0, (175,201,68), 1.0)
        ctx.add_stop(0.2, (82,131,41), 1.0)
        ctx.add_stop(0.4, (33,48,24), 1.0)
        ctx.rectangle(-120, -120, 240, 240)
        ctx.fill()
        # yellow circle around the edge of the screen
        ctx.rgb(255,234,0).arc(0,0,120,0,2*math.pi, True).stroke()
        # display text messages
        ctx.font_size += 24
        ctx.text_align = ctx.CENTER
        ctx.rgb(255,255,255).move_to(75,-10).text(f"{self.slurptxt}")
        # can't show images directly yet via ctx.image due to a firmware bug
        #ctx.image("/emf2024-logo-dark-small.png",-120,-120,240,240)
        # this might work instead... (uses output of imgtobitmap.py)
        #tildgonos.tft.bitmap(emf2024-logo,-50,-50)
        ctx.restore()

def timeslurp(url,day_one):
    # fetch the current time
    res = requests.get(url).text
    # convert to JSON data structure
    res_j = ujson.loads(res)
    # this field gives us Unix epoch time in seconds since Jan 1st 1970
    ut = res_j['unixtime']
    # compute the number of days difference between the two epoch times
    emf_day = ((int(ut) - day_one) / 86400) + 1
    # format nicely for display
    s = "It's EMF\nday %d" % (round(emf_day))
    return(s)

__app_export__ = EMF_Day