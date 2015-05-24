from pyopengles import *

example_frag = """precision mediump float;
uniform float time_ms;
uniform vec2 mouse;
uniform vec2 resolution;

void main( void ) {
	float mouse_charge = 10.;
	vec3 charges[10];
	charges[0] = vec3(0,0,10);
	charges[1] = vec3(0.1,0.1,-10);
	const int N = 2;	
	vec2 position = gl_FragCoord.xy / resolution.xy - resolution.xy/2.0;
	position.x = (gl_FragCoord.x - resolution.x/2.0)/resolution.x;
	position.y = (gl_FragCoord.y - resolution.y/2.0)/resolution.x;
	float r = distance(position.xy,vec2(mouse.x - 0.5, (mouse.y - 0.5)*resolution.y/resolution.x));
	float s = mouse_charge/(r*r);
	for(int i=0; i < N; i++){
		r = distance(position.xy,charges[i].xy);
		s += charges[i].z / (r*r);
	}
	gl_FragColor = vec4(fract(-log(s)*10.),fract(-log(s)*1.),fract(-log(s)/10.),1.);
}"""

surface_tris = eglfloats( (  - 1.0, - 1.0, 1.0, 
                             - 1.0, 1.0, 1.0, 
                               1.0, 1.0, 1.0, 
                             - 1.0, - 1.0, 1.0, 
                               1.0, 1.0, 1.0, 
                             1.0, - 1.0, 1.0 ) ) # 2 tris

egl = EGL(alpha_flags=1<<16) # fullscreen, RGBA, alpha-PREMULT flag on
#e=EGL(pref_width = 640, pref_height=480)


def draw(programObject,time_ms, mouse, resolution, Vbo):
    opengles.glClear ( GL_COLOR_BUFFER_BIT )

    location = opengles.glGetUniformLocation(programObject, "time")
    opengles.glUniform1f(location, eglfloat(time_ms))
    try:
        egl._check_glerror()
    except GLError, error:
        print "Error setting time uniform var"
        print error

    location = opengles.glGetUniformLocation(programObject, "mouse")
    opengles.glUniform2f(location, eglfloat(float(mouse.x) / resolution[0].value), eglfloat(float(mouse.y) / resolution[1].value))
    try:
        egl._check_glerror()
    except GLError, error:
        print "Error setting mouse uniform var"
        print error

    location = opengles.glGetUniformLocation(programObject, "resolution")
    opengles.glUniform2f(location, resolution[0], resolution[1])
    try:
        egl._check_glerror()
    except GLError, error:
        print "Error setting resolution uniform var"
        print error

    opengles.glBindBuffer(GL_ARRAY_BUFFER, Vbo)

    opengles.glEnableVertexAttribArray(0);
    
    opengles.glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3*4, 0)
    
    # Draws a non-indexed triangle array
    opengles.glDrawArrays ( GL_TRIANGLE_STRIP, 0, 6 )    # 2 tris
    opengles.glBindBuffer(GL_ARRAY_BUFFER, 0)
    egl._check_glerror()

    openegl.eglSwapBuffers(egl.display, egl.surface)
    time.sleep(0.02)
    

def run_shader(frag_shader):
    try:
        class FakeM():
            def __init__(self, x,y):
                self.x = x
                self.y = y
        mouse = FakeM(400,300)

        _v_src = """attribute vec3 position;
                     void main() {
                            gl_Position = vec4( position, 1.0 );
                     }"""

        vertexShader = egl.load_shader(_v_src, GL_VERTEX_SHADER )
        fragmentShader = egl.load_shader(frag_shader, GL_FRAGMENT_SHADER)
        # Create the program object
        programObject = opengles.glCreateProgram ( )

        opengles.glAttachShader ( programObject, vertexShader )
        opengles.glAttachShader ( programObject, fragmentShader )
        egl._check_glerror()

        opengles.glBindAttribLocation ( programObject, 0, "position" )
        egl._check_glerror()

        # Link the program
        opengles.glLinkProgram ( programObject )
        egl._check_glerror()

        # Check the link status
        if not (egl._check_Linked_status(programObject)):
            print "Couldn't link the shaders to the program object. Check the bindings and shader sourcefiles."
            raise Exception

        opengles.glClearColor ( eglfloat(0.3), eglfloat(0.3), eglfloat(0.5), eglfloat(1.0) )
        egl._check_glerror()

        opengles.glUseProgram( programObject )
        egl._check_glerror()

        # Make a VBO buffer obj
        Vbo = eglint()

        opengles.glGenBuffers(1, ctypes.byref(Vbo))
        egl._check_glerror()

        opengles.glBindBuffer(GL_ARRAY_BUFFER, Vbo)
        egl._check_glerror()

        # Set the buffer's data
        opengles.glBufferData(GL_ARRAY_BUFFER, 4 * 6 * 3, surface_tris, GL_STATIC_DRAW)
        egl._check_glerror()

        # Unbind the VBO
        opengles.glBindBuffer(GL_ARRAY_BUFFER, 0)
        egl._check_glerror()

        # render loop
        start = time.time()
        resolution = (eglfloat(egl.width.value), eglfloat(egl.height.value))
        while(1):
            try:
                draw(programObject, (time.time() - start), mouse, resolution, Vbo)
                time.sleep(0.02)
            except KeyboardInterrupt:
                print "Finishing"
                opengles.glClearColor ( eglfloat(0.0), eglfloat(0.0), eglfloat(0.0), eglfloat(0.0) )
                opengles.glClear ( GL_COLOR_BUFFER_BIT )
                opengles.eglSwapBuffers(egl.display, egl.surface)
                break
        del programObject, vertexShader, fragmentShader

    except Exception, error:
        print "Error - finishing"
        opengles.glClearColor ( eglfloat(0.0), eglfloat(0.0), eglfloat(0.0), eglfloat(0.0) )
        opengles.glClear ( GL_COLOR_BUFFER_BIT )
        opengles.eglSwapBuffers(egl.display, egl.surface)
        raise error

if __name__ == "__main__":
    import sys

    frag = example_frag
    if len(sys.argv) == 2:
        glsl_file = open(sys.argv[1], "r")
        frag = glsl_file.read()
        glsl_file.close()

    run_shader(frag)
    del egl
