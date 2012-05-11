== Raspberry Pi 3d demo. ==

This uses the peterderivaz's bindings to the EGL and OpenGLES libraries to draw 3d graphics from inside Python with hardware acceleration (via ctypes and ctypes.CDLL)

I wrote the 'Hello_*' scripts as a learning tool for myself and they are quite rough around the edges. I would appreciate any feedback/patches to make them better!

=== 01_Hello_Triangle.py ===

A large red triangle.

This script shows the minimum setup required to use OpenGL ES 2.0, from getting a display, loading shaders, linking and creating a (small) Vertex Buffer Object (VBO) for the triangle.

=== 02_Hello_Rotating_Triangle.py ===

A large triangle, but this time, you can rotate it using the m and n keys. The rotation of the triangle is done within the shader.

=== 03_Hello_Moving_Triangle.py ===

Extension of 02, showing how to translate a set of vertices. 

=== 04_Hello_Aspect_Ratio ===

How to correct the aspect ratio of the rendering to match that of the display.

-------------------------------

=== GLSL 'sandbox' ===

"glsl_heroku_env.py" is an attempt to provide some support to running the shader examples from @mrdoob's GLSL sandbox: http://glsl.heroku.com/

Usage:

Run a shader stored in a file:
python glsl_heroku_env.py raymarch.glsl

Interactive:
python -i glsl_heroku_env.py

>>> frag = """
uniform float time;
uniform vec2 mouse;
uniform vec2 resolution;

void main()
{

	vec2 position = -1.0 + 2.0 * (gl_FragCoord.xy / resolution.xy);
	position.x *= resolution.x / resolution.y;
	
	position += vec2(cos(time * 0.25), sin(time * 0.5)) * 0.8;

	vec3 colour = vec3(0.0);
	
	float u = sqrt(dot(position, position));
	float v = atan(position.y, position.x);
	
	float t = time + 1.0 / u;
	
	float val = smoothstep(0.0, 1.0, sin(5.0 * (time + sin(1.0*u * 3.7)) + 10.0 * v) + cos(t * 10.0));
	
	colour = vec3(val / 0.1, val, 0.0) + (0.9 - val) * vec3(0.05, 0.05, 0.05);
	colour *= clamp(u / 1.0, 0.0, 1.0);
	
	gl_FragColor = vec4(colour, 1.0);

}
"""
>>> run_shader(f)
Compiled GL_VERTEX_SHADER shader
Compiled GL_FRAGMENT_SHADER shader

[NB Press Ctrl-C to quit the render and get back to the commandline]


-------------------------------

Forked from @peterderivaz's pyopengles bindings, which have been made into a loadable module in pyopengles.

-------------------------------
