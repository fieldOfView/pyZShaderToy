pyZShaderToy
============

This node runs a GLSL fragment shader on a raspberry pi fullscreen framebuffer. It should accept many of the simpler pixel shader examples from http://glslsandbox.com. 
Note that it is very possible to crash the Raspberry Pi VideCore GPU with complex shaders, requiring a reboot of the Raspberry Pi.

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
