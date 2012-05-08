#!/usr/bin/env python

"""
//
// Book:      OpenGL(R) ES 2.0 Programming Guide
// Authors:   Aaftab Munshi, Dan Ginsburg, Dave Shreiner
// ISBN-10:   0321502795
// ISBN-13:   9780321502797
// Publisher: Addison-Wesley Professional
// URLs:      http://safari.informit.com/9780321563835
//            http://www.opengles-book.com
//

// Hello_Triangle.c
//
//    This is a simple example that draws a single triangle with
//    a minimal vertex/fragment shader.  The purpose of this 
//    example is to demonstrate the basic concepts of 
//    OpenGL ES 2.0 rendering.
"""

from pyopengles import *

# Create the context (globally accessible to methods)
def reporterror():
  e=opengles.glGetError()
  if e:
    print hex(e)
    raise ValueError

"""
///
// Create a shader object, load the shader source, and
// compile the shader.
//
"""
def LoadShader ( shader_src, shader_type = GL_VERTEX_SHADER ):
  # Convert the src to the correct ctype, if not already done
  if type(shader_src) == basestring:
    shader_src = ctypes.c_char_p(shader_src)

  # Create a shader of the given type
  shader = opengles.glCreateShader(shader_type)
  opengles.glShaderSource(shader, 1, ctypes.byref(shader_src), 0)
  opengles.glCompileShader(shader)
  
  compiled = eglint()

  # Check compiled status
  opengles.glGetShaderiv ( shader, GL_COMPILE_STATUS, ctypes.byref(compiled) )
  
  if (compiled == 0):
    print "Failed to compile shader '%s'" % shader_src 
    #TODO - get log message via ctypes
  else:
    shdtyp = "{unknown}"
    if shader_type == GL_VERTEX_SHADER:
      shdtyp = "GL_VERTEX_SHADER"
    elif shader_type == GL_FRAGMENT_SHADER:
      shdtyp = "GL_FRAGMENT_SHADER"
    print "Compiled %s shader: %s" % (shdtyp, shader_src)
  
  return shader

"""
///
// Initialize the shader and program object
//
"""
def Init():
  vShaderStr = ctypes.c_char_p(
      "attribute vec4 vPosition;    "
      "void main()                  "
      "{                            "
      "   gl_Position = vPosition;  "
      "}                            ")

  fShaderStr = ctypes.c_char_p(  
      "precision mediump float;                     "
      "void main()                                  "
      "{                                            "
      "  gl_FragColor = vec4 ( 1.0, 0.0, 0.0, 1.0 );"
      "}                                            ")

  # Load the vertex/fragment shaders
  vertexShader = LoadShader ( vShaderStr, GL_VERTEX_SHADER )
  fragmentShader = LoadShader ( fShaderStr, GL_FRAGMENT_SHADER )

  # Create the program object
  programObject = opengles.glCreateProgram ( )
   
  opengles.glAttachShader ( programObject, vertexShader )
  opengles.glAttachShader ( programObject, fragmentShader )
  
  # Bind vPosition to attribute 0   
  opengles.glBindAttribLocation ( programObject, 0, "vPosition" )

  # Link the program
  opengles.glLinkProgram ( programObject )

  # Check the link status
  linked = eglint()
  opengles.glGetProgramiv ( programObject, GL_LINK_STATUS, ctypes.byref(linked))

  opengles.glClearColor ( eglfloat(0.0), eglfloat(1.0), eglfloat(1.0), eglfloat(1.0) )
  return programObject

"""
///
// Draw a triangle using the shader pair created in Init()
//
"""
def Draw(programObject):

  vVertices = eglfloats((  0.0,  1.0, 0.0, 
                           -1.0, -1.0, 0.0,
                            1.0, -1.0, 0.0  ))
   
  # Clear the color buffer
  opengles.glClear ( GL_COLOR_BUFFER_BIT )

  # Use the program object
  opengles.glUseProgram ( programObject )

  # Load the vertex data
  opengles.glVertexAttribPointer ( 0, 3, GL_FLOAT, GL_FALSE, 0, vVertices )
  opengles.glEnableVertexAttribArray ( 0 )

  opengles.glDrawArrays ( GL_TRIANGLES, 0, 3 )
  
if __name__ == "__main__":
  import sys
  w,h = 640,480
  if len(sys.argv) == 3:
    w,h = int(sys.argv[1]), int(sys.argv[2])
  egl = EGL(w,h)
  programObj = Init()
  while 1:
    Draw(programObj)
    openegl.eglSwapBuffers(egl.display, egl.surface)
    time.sleep(0.02)
