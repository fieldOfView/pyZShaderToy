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
from utils import import_obj, PerspProjMat, reporterror, \
                  LoadShader, check_Linked_status, get_rotation_m, \
                  wavefront_obj_to_vbo

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
  if not (check_Linked_status(programObject)):
    raise Exception
  
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
