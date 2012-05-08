#!/usr/bin/env python

# Array Indexes
VERTEX_ARRAY = 0
TEXCOORD_ARRAY = 1

TEX_SIZE = 128

from pyopengles import *
from utils import reporterror, LoadShader, check_Linked_status

vertexStride = 5 * 4        # 5 * sizeof(GLfloat)

"""
///
// Initialize the shader and program object
//
"""
def Init():
  fShaderStr = ctypes.c_char_p(
      "uniform sampler2D sampler2d;                        "
      "varying mediump vec2 myTexCoord;                    "
      "void main()                                         "
      "	{                                                  "
      "	   gl_FragColor = texture2D(sampler2d,myTexCoord); "
      "	}                                                  ")

  vShaderStr = ctypes.c_char_p(  
      "attribute highp vec4	myVertex;                  "
      "attribute mediump vec4	myUV;                      "
      "uniform mediump mat4	myPMVMatrix;               "
      "varying mediump vec2	myTexCoord;                "
      "void main()                                         "
      "{                                                   "
      "  gl_Position = myPMVMatrix * myVertex;             "
      "  myTexCoord = myUV.st;                             "
      "}                                                   ")

  # Load the vertex/fragment shaders
  vertexShader = LoadShader ( vShaderStr, GL_VERTEX_SHADER )
  fragmentShader = LoadShader ( fShaderStr, GL_FRAGMENT_SHADER )
  reporterror()

  # Create the program object
  programObject = opengles.glCreateProgram ( )
  reporterror()
   
  opengles.glAttachShader ( programObject, vertexShader )
  opengles.glAttachShader ( programObject, fragmentShader )
  reporterror()
  
  # Bind vPosition to attribute 0   
  opengles.glBindAttribLocation ( programObject, VERTEX_ARRAY, "myVertex" )
  opengles.glBindAttribLocation ( programObject, TEXCOORD_ARRAY, "myUV" )
  reporterror()
  
  # Link the program
  opengles.glLinkProgram ( programObject )
  reporterror()

  # Check the link status
  if not (check_Linked_status(programObject)):
    raise Exception
  
  # Use the program object
  opengles.glUseProgram( programObject )
  reporterror()

  opengles.glUniform1i(opengles.glGetUniformLocation(programObject, "sampler2d"), 0)
  reporterror()
  
  opengles.glClearColor ( eglfloat(0.6), eglfloat(0.8), eglfloat(1.0), eglfloat(1.0) )
  reporterror()

  return programObject

def CreateTexture(programObject):
  
  # Allocate one tex handle
  tex_handle = eglint()
  opengles.glGenTextures(1, ctypes.byref(tex_handle))
  reporterror()

  # Bind it to allow us to load data into it
  opengles.glBindTexture(GL_TEXTURE_2D, tex_handle)
  reporterror()

  # Creates the data as a 32bits integer array (8bits per component)
  test_tex=(eglint*(TEX_SIZE*TEX_SIZE))(*[(255<<24) + ((256)<<16) + ((128)<<8) + (120*2)] * (TEX_SIZE * TEX_SIZE))
  test_tex_p = ctypes.pointer(test_tex)

  for i in xrange(TEX_SIZE):
    for j in xrange(TEX_SIZE):
      col = (255<<24) + ((255-j*2)<<16) + ((255-i)<<8) + (255-i*2)
      test_tex[j*TEX_SIZE+i] = col

  opengles.glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, TEX_SIZE, TEX_SIZE, 0, GL_RGBA, GL_UNSIGNED_BYTE, test_tex_p)

  reporterror()

  opengles.glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, eglfloat(GL_LINEAR) )
  reporterror()
  opengles.glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, eglfloat(GL_LINEAR) )
  reporterror()

  afVertices = eglfloats(( -1.0, -1.0, 0.0,   # Pos
                            0.0, 0.0,         # UV
                            1.0, -1.0, 0.0,
                            1.0, 0.0,
                            0.0, 1.0 , 0.0,
                            0.5, 1.0 ))

  # Make a VBO buffer obj
  Vbo = eglint()
  
  opengles.glGenBuffers(1, ctypes.byref(Vbo))
  reporterror()
  
  opengles.glBindBuffer(GL_ARRAY_BUFFER, Vbo)

  reporterror()

  # Set the buffer's data
  opengles.glBufferData(GL_ARRAY_BUFFER, 3 * vertexStride, afVertices, GL_STATIC_DRAW)
  
  # Unbind the VBO
  opengles.glBindBuffer(GL_ARRAY_BUFFER, 0)
  reporterror()
  

  return Vbo

"""
///
// Draw a triangle using the shader pair created in Init()
//
"""
def Draw(programObject, Vbo):

  # Clear the color buffer
  opengles.glClear ( GL_COLOR_BUFFER_BIT )

  afIdentity = eglfloats(( 1,0,0,0,
                           0,1,0,0,
                           0,0,1,0,
                           0,0,0,1 ))

  location = opengles.glGetUniformLocation(programObject, "myPMVMatrix")
  reporterror()

  opengles.glUniformMatrix4fv(location, 1, GL_FALSE, afIdentity)

  opengles.glBindBuffer(GL_ARRAY_BUFFER, Vbo)

  reporterror()
  opengles.glEnableVertexAttribArray(VERTEX_ARRAY);
  
  reporterror()
  opengles.glVertexAttribPointer(VERTEX_ARRAY, 3, GL_FLOAT, GL_FALSE, vertexStride, 0);
  
  reporterror()
  # Pass the texture coordinates data
  opengles.glEnableVertexAttribArray(TEXCOORD_ARRAY);
  opengles.glVertexAttribPointer(TEXCOORD_ARRAY, 2, GL_FLOAT, GL_FALSE, vertexStride, 12);

  reporterror()
  # Draws a non-indexed triangle array
  opengles.glDrawArrays(GL_TRIANGLES, 0, 3);

  reporterror()
  opengles.glBindBuffer(GL_ARRAY_BUFFER, 0);
  reporterror()


if __name__ == "__main__":
  import sys
  w,h = 640,480
  if len(sys.argv) == 3:
    w,h = int(sys.argv[1]), int(sys.argv[2])
  egl = EGL(w,h)
  programObj = Init()
  Vbo = CreateTexture(programObj)
  while 1:
    Draw(programObj, Vbo)
    openegl.eglSwapBuffers(egl.display, egl.surface)
    time.sleep(0.02)
