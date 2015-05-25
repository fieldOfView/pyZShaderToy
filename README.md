pyZShaderToy
============

Runs a GLSL fragment shader on a raspberry pi fullscreen framebuffer

zshadertoy.py is the ZOCP node for this application. Once running, a more interesting shader can be sent to it over ZOCP.
'''
python3 zshadertoy.py
'''


shadertoy.py contains the ShaderToy class which does the heavy lifting functionality-wise. It can be used standalone to test out shaders, but note that mouse-functionality has been removed):
'''
python3 shadertoy.py example.glsl
'''


pyopengles
----------
Forked from an example project by @benosteen, which in itself is a fork from @peterderivaz's pypopengl bindings
https://github.com/benosteen/pyopengles
https://github.com/peterderivaz/pyopengles
