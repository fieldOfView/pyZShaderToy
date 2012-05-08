#!/usr/bin/env python

# Array Indexes
VERTEX_ARRAY = 0
TEXCOORD_ARRAY = 1

TEX_SIZE = 128

from pyopengles import *
from wavefront_obj import import_obj

vertexStride = 5 * 4        # 5 * sizeof(GLfloat) -> vert x,y,z uv u,v

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

  if (compiled.value == 0):
    print "Failed to compile shader '%s'" % shader_src 
    loglength = eglint()
    charswritten = eglint()
    opengles.glGetShaderiv(shader, GL_INFO_LOG_LENGTH, ctypes.byref(loglength))
    logmsg = ctypes.c_char_p(" "*loglength.value)
    opengles.glGetShaderInfoLog(shader, loglength, ctypes.byref(charswritten), logmsg)
    print logmsg.value
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
  linked = eglint()
  opengles.glGetProgramiv ( programObject, GL_LINK_STATUS, ctypes.byref(linked))
  reporterror()

  if (linked.value == 0):
    print "Linking failed!"
    loglength = eglint()
    charswritten = eglint()
    opengles.glGetProgramiv(programObject, GL_INFO_LOG_LENGTH, ctypes.byref(loglength))
    logmsg = ctypes.c_char_p(" "*loglength.value)
    opengles.glGetProgramInfoLog(programObject, loglength, ctypes.byref(charswritten), logmsg)
    print logmsg.value
    
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


def create_triangle():
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

  return Vbo, 3

def get_wavefront_obj(path):
  f = import_obj(path)
  # make a suitable vbo object -> (vert) x,y,z (uv) u,v
  vbo_data = []
  for face in f:
    v1,v2,v3 = face['v']
    uv1, uv2, uv3 = face['uv']
    vbo_data.extend(v1+uv1+v2+uv2+v3+uv3)

  intVertices = eglfloats( vbo_data )

  Vbo = eglint()

  opengles.glGenBuffers(1, ctypes.byref(Vbo))
  reporterror()

  opengles.glBindBuffer(GL_ARRAY_BUFFER, Vbo)

  reporterror()

  # Set the buffer's data
  opengles.glBufferData(GL_ARRAY_BUFFER, len(f) * vertexStride, intVertices, GL_STATIC_DRAW)

  # Unbind the VBO
  opengles.glBindBuffer(GL_ARRAY_BUFFER, 0)
  reporterror()

  return Vbo, len(f) * 3

"""
///
// Draw a triangle using the shader pair created in Init()
//
"""
def Draw(programObject, Vbo, idxs):

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
  
  opengles.glDisable(GL_CULL_FACE)
  reporterror()

  # Draws a non-indexed triangle array
  opengles.glDrawArrays(GL_TRIANGLES, 0, idxs);

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
  CreateTexture(programObj)
  #Vbo, idxs = create_triangle()
  Vbo, idxs = get_wavefront_obj("monkey.obj")
  nooffaces = 0
  while 1:
    nooffaces += 3
    Draw(programObj, Vbo, nooffaces)
    openegl.eglSwapBuffers(egl.display, egl.surface)
    time.sleep(0.02)
    nooffaces %= idxs
