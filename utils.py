# Common utilities

from pyopengles import *
from wavefront_obj import import_obj

def PerspProjMat(fov, aspect, znear, zfar):
  xymax = znear * math.tan(fov * (math.pi/360.0))
  ymin = -xymax
  xmin = -xymax

  width = xymax - xmin
  height = xymax - ymin

  depth = zfar - znear
  q = -(zfar + znear) / depth
  qn = -2 * (zfar * znear) / depth

  w = 2 * znear / width
  w = w / aspect
  h = 2 * znear / height

  m = ( w,0,0,0,
        0,h,0,0,
        0,0,q,-1,
        0,0,qn,0)
  return m

# Create the context (globally accessible to methods)
def reporterror():
  e=opengles.glGetError()
  if e:
    print hex(e)
    raise ValueError

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

def check_Linked_status(programObject):
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
    return False
  return True

def get_rotation_m(angle, axis="x"):
  sinr = math.sin(angle)
  cosr = math.cos(angle)

  # left-handed - swap sin signs around for rh
  if axis.lower() == "x" or axis.lower() not in ['x','y','z']:
    return eglfloats(( 1,    0,     0, 0,
                     0, cosr, -sinr, 0,
                     0, sinr,  cosr, 0,
                     0,    0,     0, 1 ))
  elif axis.lower() == "y":
    return eglfloats(( cosr,   0,  sinr, 0,
                          0,   1,     0, 0,
                      -sinr,   0,  cosr, 0,
                          0,   0,     0, 1 ))
  elif axis.lower() == 'z':
    return eglfloats(( cosr,  -sinr,  0, 0,
                        sinr,   cosr,  0, 0,
                           0,      0,  1, 0,
                           0,      0,  0, 1 ))

afIdentity_m = eglfloats(( 1,0,0,0,
                         0,1,0,0,
                         0,0,1,0,
                         0,0,0,1 ))
