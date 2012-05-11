#!/usr/bin/env python

# Array Indexes
VERTEX_ARRAY = 0
TEXCOORD_ARRAY = 1
NORMAL_ARRAY = 2

TEX_SIZE = 128

from pyopengles import *
from utils import import_obj, PerspProjMat, reporterror, \
                  LoadShader, check_Linked_status, get_rotation_m, \
                  wavefront_obj_to_vbo

PROJ_M = eglfloats(PerspProjMat(45.0, 1.3333,-1.0,1000.0))

vertexStride = 8 * 4        # 5 * sizeof(GLfloat) -> vert x,y,z,w  uv u,v

"""
///
// Initialize the shader and program object
//
"""
def Init():
  fShaderStr = ctypes.c_char_p(
    """
    uniform sampler2D sampler2d;
    varying mediump float	varDot;
    varying mediump vec2	varCoord;
    void main (void)
    {
        gl_FragColor.rgb = texture2D(sampler2d,varCoord).rgb * varDot;
        gl_FragColor.a = 1.0; 
    }
    """)

  vShaderStr = ctypes.c_char_p(
    """
    attribute highp vec4	myVertex;
    attribute mediump vec3	myNormal;
    attribute mediump vec4	myUV;
    uniform mediump mat4	myPMVMatrix;
    uniform mediump mat3	myModelViewIT;
    uniform mediump vec3	myLightDirection;
    varying mediump float	varDot;
    varying mediump vec2	varCoord;

    mat4 view_frustum(
        float angle_of_view,
        float aspect_ratio,
        float z_near,
        float z_far
    ) {
        return mat4(
            vec4(1.0/tan(angle_of_view),           0.0, 0.0, 0.0),
            vec4(0.0, aspect_ratio/tan(angle_of_view),  0.0, 0.0),
            vec4(0.0, 0.0,    (z_far+z_near)/(z_far-z_near), 1.0),
            vec4(0.0, 0.0, -2.0*z_far*z_near/(z_far-z_near), 0.0)
        );
    }

    mat4 translate(float x, float y, float z)
    {
        return mat4(
            vec4(1.0, 0.0, 0.0, 0.0),
            vec4(0.0, 1.0, 0.0, 0.0),
            vec4(0.0, 0.0, 1.0, 0.0),
            vec4(x,   y,   z,   1.0)
        );
    }

    void main(void)
    {
        gl_Position = view_frustum(radians(45.0), 4.0/3.0, 0.0, 50.0) 
                      * translate(0.0, 0.0, 1.0)
                      * myPMVMatrix * myVertex;
        varCoord = myUV.st;
        mediump vec3 transNormal = myModelViewIT * myNormal;
        varDot = max( dot(transNormal, myLightDirection), 0.0 );
    }
    """)

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
  opengles.glBindAttribLocation ( programObject, NORMAL_ARRAY, "myNormal" )
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

  reporterror()

  # Creates the data as a 32bits integer array (8bits per component)
  test_tex=(eglint*(TEX_SIZE*TEX_SIZE))(*[(255<<24) + ((256)<<16) + ((128)<<8) + (120*2)] * (TEX_SIZE * TEX_SIZE))
  test_tex_p = ctypes.pointer(test_tex)

  for i in xrange(TEX_SIZE):
    for j in xrange(TEX_SIZE):
      #col = (255<<24) + ((255-j)<<16) + ((255-i*2)<<8) + (255-i*2)
      #test_tex[j*TEX_SIZE+i] = col
      col = (255<<24) + ((255)<<16) + (255 << 8) + (255)
      test_tex[j*TEX_SIZE+i] = col

  opengles.glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, TEX_SIZE, TEX_SIZE, 0, GL_RGBA, GL_UNSIGNED_BYTE, test_tex_p)

  reporterror()

  opengles.glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, eglfloat(GL_NEAREST) )
  reporterror()
  opengles.glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, eglfloat(GL_LINEAR) )
  reporterror()

  opengles.glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, eglint(GL_REPEAT) )
  reporterror()

  opengles.glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, eglint(GL_REPEAT) )
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
  Vbo, size, struct_width = wavefront_obj_to_vbo(path)
  vertexStride = struct_width * 4
  return Vbo, size
  """
  f, verts, uvs, normals = import_obj(path)
  # make a suitable vbo object -> (vert) x,y,z (uv) u,v (norm) x,y,z
  vbo_data = []
  for face in f:
    v1,v2,v3 = face['v']
    uv1, uv2, uv3 = face['uv']
    n1,n2,n3 = face['n']
    vbo_data.extend(verts[v1]+uvs[uv1]+normals[n1])
    vbo_data.extend(verts[v2]+uvs[uv2]+normals[n2])
    vbo_data.extend(verts[v3]+uvs[uv3]+normals[n3])

  intVertices = eglfloats( vbo_data )

  Vbo = eglint()

  opengles.glGenBuffers(1, ctypes.byref(Vbo))
  reporterror()

  opengles.glBindBuffer(GL_ARRAY_BUFFER, Vbo)

  reporterror()

  # Set the buffer's data
  opengles.glBufferData(GL_ARRAY_BUFFER, len(f) * 3 * 8 * 4, intVertices, GL_STATIC_DRAW)

  # Unbind the VBO
  opengles.glBindBuffer(GL_ARRAY_BUFFER, 0)
  reporterror()

  return Vbo, len(f) * 3
  """
  
"""
///
// Draw a VBO using the shader pair created in Init()
//
"""
def Draw(programObject, Vbo, idxs, rotation, lighting):

  # Clear the color buffer
  opengles.glClear ( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )

  opengles.glEnable(GL_DEPTH_TEST)
  reporterror()
  

  sinr = math.sin(rotation)
  cosr = math.cos(rotation)
  
  rot_mat = get_rotation_m(rotation, 'y')
  
  modelView = eglfloats(( cosr,   0,  sinr,
                          0,      1,     0,
                          -sinr,  0,  cosr ))

  location = opengles.glGetUniformLocation(programObject, "myPMVMatrix")
  opengles.glUniformMatrix4fv(location, 1, GL_FALSE, rot_mat)
  reporterror()

  location = opengles.glGetUniformLocation(programObject, "myModelViewIT")
  opengles.glUniformMatrix3fv(location, 1, GL_FALSE, modelView)
  reporterror()

  location = opengles.glGetUniformLocation(programObject, "myLightDirection")
  opengles.glUniform3f(location, eglfloat(1), eglfloat(2), eglfloat(2.0 - lighting))
  location = opengles.glGetUniformLocation(programObject, "myLightDirection")
  opengles.glUniform3f(location, eglfloat(1), eglfloat(2 - lighting), eglfloat(2.0 - lighting))
  reporterror()


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
  
  # Pass the normal coordinates data
  opengles.glEnableVertexAttribArray(NORMAL_ARRAY);
  opengles.glVertexAttribPointer(NORMAL_ARRAY, 3, GL_FLOAT, GL_FALSE, vertexStride, 20);
  reporterror()

  # Draws a non-indexed triangle array
  opengles.glDrawArrays(GL_TRIANGLES, 0, idxs);

  reporterror()
  
  opengles.glBindBuffer(GL_ARRAY_BUFFER, 0);
  reporterror()


if __name__ == "__main__":
  import sys
  path = "example_objs/monkey.obj"
  w,h = 640,480
  if len(sys.argv) == 3:
    w,h = int(sys.argv[1]), int(sys.argv[2])
  elif len(sys.argv) == 2:
    path = sys.argv[1]
  elif len(sys.argv) == 4:
    w,h = int(sys.argv[1]), int(sys.argv[2])
    path = sys.argv[3]
  egl = EGL(w,h)
  programObj = Init()

  openegl.glViewport(eglint(0), eglint(0), eglint(w), eglint(h))

  openegl.glDepthRangef(eglfloat(-10.0), eglfloat(20.0))
  reporterror()

  #opengles.glFrontFace(GL_CCW)

  opengles.glCullFace(GL_BACK)

  opengles.glEnable(GL_CULL_FACE)
  opengles.glEnable(GL_DEPTH_TEST)
  reporterror()
  
  opengles.glDepthFunc(GL_LESS)
  
  CreateTexture(programObj)

  #Vbo, idxs = create_triangle()
  Vbo, idxs = get_wavefront_obj(path)

  rotation = 0
  noofverts = 0
  noofverts_step = idxs / 100
  if noofverts_step == 0:
    noofverts_step = 1
  rotatestep = math.pi / 120
  lighting = 0.0
  while 1:
    noofverts += noofverts_step
    rotation += rotatestep
    rotation %= math.pi * 2
    if (noofverts >= idxs):
      Draw(programObj, Vbo, idxs, rotation, lighting)
    else:
      Draw(programObj, Vbo, noofverts, rotation, lighting)
    openegl.eglSwapBuffers(egl.display, egl.surface)

    time.sleep(0.02)
    noofverts %= idxs * 5
    lighting += 0.01
    lighting %= 4.0
