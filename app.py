import app
import math
import ntptime
import time
from events.input import Buttons, BUTTON_TYPES
from tildagonos import tildagonos
from app_components import clear_background

class EMF_Day(app.App):    

    def setup_leds(self):
        return [
            (228, 0, 0),
            (228, 0, 0),
            (255,140, 0),
            (255,140, 0),
            (255, 237, 0),
            (255, 237, 0),
            (0,128,38),
            (0,128,38),
            (36, 64, 142),
            (36, 64, 142),
            (115, 41, 130),
            (115, 41, 130),
        ]

    def display_infos(self, ctx, x, y, msg):
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

        # display text message
        ctx.font_size += 24
        ctx.text_align = ctx.CENTER
        ctx.rgb(255,255,255).move_to(x,y).text(msg)
        ctx.restore() 
        return

    def __init__(self):
        print("into init()")
        
        self.button_states = Buttons(self)        
        self.day_one = 1717142400
        self.leds = self.setup_leds()

#         print("connecting to wifi")
#        
#         try:
#              wifi.connect()
#              self.connected = True
#              print("connected to wifi")
#         except:
#              print("wifi connection error")
#              self.connected = False

        self.connected = True # XXX we should actually check if we managed to connect

        if self.connected:
            print("now trying our luck with NTP")
            ntptime.settime() # XXX can we tell if this actually worked? will it throw an exception if not?
            self.ntp = True # XXX but is it really?
        else:
            self.ntp = False
            
#         if (time.time() + 94684800) <= self.day_one:
#             print("ntp failed")
#             self.ntp = False
#         else:
#             print("ntp succeeded")
#             self.ntp = True

        # XXX we should only do this if we are connected and NTP worked...
        print("calculating days since EMF 2024 day one")
        self.now = time.time() + 946684800
        # how many days between then and now?
        self.emf_days = int((self.now - self.day_one) / 86400) + 1
            
        print("emf_days: %d" % (self.emf_days))
        self.emf_day = 1
        self.days_per_led = math.ceil(self.emf_days / 12) # we have 12 LEDs, don't we?
        print("days per led: %d" % (self.days_per_led))
        self.multiplier = 1
        self.day_to_col = self.emf_days / 255
        
    def update(self, delta):
        print("into update()")

        if not self.ntp:
            print("ntp failed - exiting")
            self.button_states.clear()
            self.minimise()

        if self.button_states.get(BUTTON_TYPES["CANCEL"]):
            print("setting up cancel button")
            self.button_states.clear()
            self.minimise()

        if self.emf_day > self.emf_days:
            print("winding the clock back...")
            self.emf_day = 1
            self.multiplier = 1

        if self.emf_days % self.emf_day is 0:
            self.multiplier = self.multiplier * 2 # faster!

        self.emf_day = self.emf_day + self.multiplier

        if self.emf_day > self.emf_days:
            self.emf_day = self.emf_days
            
    def draw(self, ctx):
        print("into draw()")
        #clear_background(ctx)

        if not self.connected:
            self.display_infos(ctx, 85, -10, 'Uh-oh :-(')
            time.sleep(10)
            return

#         if not self.ntp:
#             self.display_infos(ctx, 85, -10, 'Failed to\nget time :-(')
#             time.sleep(5)
            
        # print it nicely
        print("it's EMF day %d" % (self.emf_day))
        self.s = "It's EMF\nday %d" % (self.emf_day)

        # display text message
        self.display_infos(ctx, 85, -10, f"{self.s}")

        # let's show our progress fractionally
        l = math.ceil(self.emf_day / self.days_per_led)
        
        # oh wait, there are LEDs on the back too :-)
        back_led = math.ceil(12+(l/2))

        print("frobbing up to led %d" % (l))
        for f in range(0,l):
            # light up some leds to represent progress
            print("frobbing led %d, emf_day %d (out of %d days), multiplier %d, back_led %d" % (f, self.emf_day, self.emf_days, self.multiplier, back_led))
            tildagonos.leds[f] = self.leds[f]
            tildagonos.leds[back_led] = (0, 125, 0)
        
        tildagonos.leds[l] = (0, 125, 0)
        tildagonos.leds.write()
        ctx.restore()

        # reset the clock back to day one if we go too far
        if self.emf_day >= self.emf_days:
            self.emf_day = 1

        # let the multiplier creep up because it's fun
        if self.multiplier < self.emf_days:
            return

        # pause then reset the multiplier if it's getting out of hand
        self.multiplier = 1
        for f in range(0,18):
            tildagonos.leds[f] = (0, 255, 0)
            tildagonos.leds.write()
        time.sleep(10)
        for f in range(0,18):
            tildagonos.leds[f] = (0, 0, 0)
            tildagonos.leds.write()

__app_export__ = EMF_Day