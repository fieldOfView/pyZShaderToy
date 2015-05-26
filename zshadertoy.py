#!/usr/bin/python3

from zocp import ZOCP
import socket
import logging

from shadertoy import ShaderToy

class ShaderToyNode(ZOCP):
    # Constructor
    def __init__(self, nodename):
        super(ShaderToyNode, self).__init__(nodename)

        self.shadertoy = ShaderToy()
        self.shadertoy.setupEGL()
        self.fragment_shader = self.shadertoy.empty_frag
        self.timeoffset = self.shadertoy.timeoffset
        self.mouse = [self.shadertoy.mouse.x, self.shadertoy.mouse.y]

        self.register_string("Fragment shader", self.fragment_shader, 'rws')
        self.register_vec2f("Mouse", self.mouse, 'rws')
        self.start()

        while True:
            try:
                self.run_once()
                self.shadertoy.draw()
            except (KeyboardInterrupt, SystemExit):
                break

        self.shadertoy.stop()
        self.stop()


    
    def on_modified(self, peer, name, data, *args, **kwargs):
        if self._running and peer:
            for key in data:
                if 'value' in data[key]:
                    self.receive_value(key)


    def on_peer_signaled(self, peer, name, data, *args, **kwargs):
        if self._running and peer:
            for sensor in data[2]:
                if(sensor):
                    self.receive_value(sensor)


    def receive_value(self, key):
        new_value = self.capability[key]['value']

        if key == "Fragment shader":
            if new_value != self.fragment_shader:
                self.fragment_shader = new_value
                self.shadertoy.loadShader(self.fragment_shader)
        elif key == "Mouse":
            if new_value != self.mouse:
                self.mouse = new_value
                self.shadertoy.mouse.x = self.mouse[0]
                self.shadertoy.mouse.y = self.mouse[1]

        
if __name__ == '__main__':
    zl = logging.getLogger("zocp")
    zl.setLevel(logging.DEBUG)

    z = ShaderToyNode("shadertoy@%s" % socket.gethostname())
    print("FINISH")
