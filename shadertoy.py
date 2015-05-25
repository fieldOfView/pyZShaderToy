#!/usr/bin/python

from pyopengles import *

class ShaderToy():
    vert_shader = """attribute vec3 position;

    void main() {
        gl_Position = vec4(position, 1.);
    }"""


    empty_frag = """precision mediump float;
    uniform float time_ms;
    uniform vec2 mouse;
    uniform vec2 resolution;

    void main(void) {
        gl_FragColor = vec4(0.2,0.2,0.2,1.);
    }"""

    surface_tris = eglfloats( (  - 1.0, - 1.0, 1.0,
                                 - 1.0, 1.0, 1.0,
                                   1.0, 1.0, 1.0,
                                 - 1.0, - 1.0, 1.0,
                                   1.0, 1.0, 1.0,
                                   1.0, - 1.0, 1.0 ) ) # 2 tris

    def __init__(self):
        self.egl = EGL(alpha_flags=1<<16) # fullscreen, RGBA, alpha-PREMULT flag on

        class FakeM():
            def __init__(self, x,y):
                self.x = x
                self.y = y
        self.mouse = FakeM(400,300)

        self.Vbo = None
        self.programObject = None

        self.setupEGL()
        self.loadShader(self.empty_frag)
        self.timeoffset = time.time()


    def run(self):
        # render loop
        while(1):
            try:
                self.draw()
                time.sleep(0.02)
            except (KeyboardInterrupt, SystemExit):
                print ("Finishing")
                self.stop()
                break


    def stop(self):
        opengles.glClearColor ( eglfloat(0.0), eglfloat(0.0), eglfloat(0.0), eglfloat(0.0) )
        opengles.glClear ( GL_COLOR_BUFFER_BIT )
        opengles.eglSwapBuffers(self.egl.display, self.egl.surface)
        
        del self.Vbo, self.programObject, self.egl


    def setupEGL(self):
        try:
            opengles.glClearColor ( eglfloat(0.3), eglfloat(0.3), eglfloat(0.5), eglfloat(1.0) )
            self.egl._check_glerror()

            # Make a VBO buffer obj
            self.Vbo = eglint()

            opengles.glGenBuffers(1, ctypes.byref(self.Vbo))
            self.egl._check_glerror()

            opengles.glBindBuffer(GL_ARRAY_BUFFER, self.Vbo)
            self.egl._check_glerror()

            # Set the buffer's data
            opengles.glBufferData(GL_ARRAY_BUFFER, 4 * 6 * 3, self.surface_tris, GL_STATIC_DRAW)
            self.egl._check_glerror()

            # Unbind the VBO
            opengles.glBindBuffer(GL_ARRAY_BUFFER, 0)
            self.egl._check_glerror()

            self.resolution = (eglfloat(self.egl.width.value), eglfloat(self.egl.height.value))

        except Exception as error:
            print ("Error setting up")
            self.stop()
            raise error


    def loadShader(self, frag_shader):
        try:
            vertexShader = self.egl.load_shader(self.vert_shader, GL_VERTEX_SHADER )
            fragmentShader = self.egl.load_shader(frag_shader, GL_FRAGMENT_SHADER)

            # Create the program object
            programObject = opengles.glCreateProgram ( )

            opengles.glAttachShader ( programObject, vertexShader )
            opengles.glAttachShader ( programObject, fragmentShader )
            self.egl._check_glerror()

            opengles.glBindAttribLocation ( programObject, 0, "position" )
            self.egl._check_glerror()

            # Link the program
            opengles.glLinkProgram ( programObject )
            self.egl._check_glerror()

            # Check the link status
            if not (self.egl._check_Linked_status(programObject)):
                print ("Couldn't link the shaders to the program object. Check the bindings and shader sourcefiles.")
                raise (Exception)

            del self.programObject
            self.programObject = programObject

            opengles.glUseProgram( self.programObject )
            self.egl._check_glerror()

            del vertexShader, fragmentShader

        except Exception as error:
            # only stop if there is no previously created shader
            if not self.programObject:
                print ("Error loading shader.")
                self.stop()
                raise error
            else:
                print ("Error loading new shader. Using previous shader")


    def draw(self):
        time_ms = time.time() - self.timeoffset

        opengles.glClear ( GL_COLOR_BUFFER_BIT )

        location = opengles.glGetUniformLocation(self.programObject, "time")
        opengles.glUniform1f(location, eglfloat(time_ms))
        try:
            self.egl._check_glerror()
        except GLError as error:
            print ("Error setting time uniform var")
            print (error)

        location = opengles.glGetUniformLocation(self.programObject, "mouse")
        opengles.glUniform2f(location, eglfloat(float(self.mouse.x) / self.resolution[0].value), eglfloat(float(self.mouse.y) / self.resolution[1].value))
        try:
            self.egl._check_glerror()
        except GLError as error:
            print ("Error setting mouse uniform var")
            print (error)

        location = opengles.glGetUniformLocation(self.programObject, "resolution")
        opengles.glUniform2f(location, self.resolution[0], self.resolution[1])
        try:
            self.egl._check_glerror()
        except GLError as error:
            print ("Error setting resolution uniform var")
            print (error)

        opengles.glBindBuffer(GL_ARRAY_BUFFER, self.Vbo)

        opengles.glEnableVertexAttribArray(0);

        opengles.glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3*4, 0)

        # Draws a non-indexed triangle array
        opengles.glDrawArrays ( GL_TRIANGLE_STRIP, 0, 6 )    # 2 tris
        opengles.glBindBuffer(GL_ARRAY_BUFFER, 0)
        self.egl._check_glerror()

        opengles.eglSwapBuffers(self.egl.display, self.egl.surface)


if __name__ == "__main__":
    import sys

    shaderToy = ShaderToy()

    if len(sys.argv) == 2:
        glsl_file = open(sys.argv[1], "r")
        frag = glsl_file.read()
        glsl_file.close()
        shaderToy.loadShader(frag)

    shaderToy.run()
