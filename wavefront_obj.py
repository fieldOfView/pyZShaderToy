#!/usr/bin/env python

class Wavefront_Obj(object):
    def __init__(self, name):
        self.name = name
        self.faces = []
        self.verts = []
        self.uvs = []
        self.normals = []
        self.v_dim = 0
        self.uv_dim = 0
        self.n_dim = 0

    def get_triangle_number():
        return len(self.faces)

    def get_stride():
        return (self.v_dim + self.uv_dim + self.n_dim) * 4 # sizeof(GL_FLOAT)
       

def import_obj(path, combine=True):
    filename = path.split('\\')[-1].split('/')[-1]
    objects = []
    # parse the file
    file = open(path, 'r')
    line = file.next().strip()
    while(line):
        # wait for first object mention in file before parsing
        words = line.split()
        if len(words) == 0 or words[0].startswith('#'):
            pass
        elif words[0] == 'o':
            name = "".join(words[1:]).strip()
            print "Found new object - %s. Parsing vertices, uvs and normals." % name
            for object in _parse_object(name, file):
                objects.append(object)
            line = None
        try:
            line = file.next().strip()
        except StopIteration:
            line = None
    if objects:
        print "Parsed %s objects in total: %s" % (len(objects), [o.name for o in objects])
    else:
        print "Failed to find any objects to load"
    return objects

def _parse_object(name, file):
    o = Wavefront_Obj(name)
    total_v = 0
    total_uvs = 0
    total_normals = 0
    idx_offsets = [0,0,0]   #v, uvs, normals idx offsets for multiple meshs in same obj
    line = file.next().strip()
    while(line):
        words = line.split()
        if len(words) == 0 or words[0].startswith('#'):
            pass
        elif words[0] == 'v':
            if not o.v_dim:
                o.v_dim = len(words[1:])
            # "v 0.123 0.23 0.69 [0.2]" 
            x, y, z = float(words[1]), float(words[2]), float(words[3])
            o.verts.append((x, y, z))
            total_v += 1
        elif words[0] == 'vn':
            if not o.n_dim:
                o.n_dim = len(words[1:])
            # "vn 0.707 0.000 0.707" --> Normals in (x,y,z) form; normals might not be unit.
            x, y, z = float(words[1]), float(words[2]), float(words[3])
            o.normals.append((x, y, z))
            total_normals += 1
        elif words[0] == 'vt':
            if not o.uv_dim:
                o.uv_dim = len(words[1:])
            o.uvs.append(tuple(map(float, words[1:])))
            total_uvs += 1
        elif words[0] == 'f':
            print "Beginning to parse faces"
            if words[1].count("/") == 0:
                # faces - verts only
                line = _face_vertex_only(line, file, o, idx_offsets)
            elif words[1].count("/") == 1:
                # faces - verts/texturecoords
                line = _face_vertex_uvs(line, file, o, idx_offsets)
            elif words[1].count("/") == 2:
                line = _face_vertex_uvs_normals(line, file, o, idx_offsets)
            if line:
                words = line.split()
            else:
                words = ['null']
            # new object
            print "Loaded %s vertices, with %s tex coords and %s normals -- %s faces" % (len(o.verts), len(o.uvs), len(o.normals), len(o.faces))
            yield o
            # increase the idx offsets
            idx_offsets = [total_v, total_uvs, total_normals]
        if words[0] == 'o':
            name = "".join(words[1:]).strip()
            print "Found new object - %s. Parsing vertices, uvs and normals." % name
            o = Wavefront_Obj(name)
        try:
            line = file.next().strip()
        except StopIteration:
            line = None


def _face_vertex_only(line, file, obj, offset):
    face_parsing = True
    while(face_parsing):
        words = line.split()
        if words[0] != "f":
            face_parsing = False
        else:
            f = {}
            f['v'] = (int(word[3])-1-offset[0], int(word[2])-1-offset[0],int(word[1])-1-offset[0])
            obj.faces.append(f)
            try:
                line = file.next().strip()
            except StopIteration:
                face_parsing = False
                line = None
    return line

def _face_vertex_uvs(line, file, obj, offset):
    face_parsing = True
    while(face_parsing):
        words = line.split()
        if words[0] != "f":
            face_parsing = False
        else:
            f = {}
            v,u = [],[]
            for wridx in words[:0:-1]:
            #for wridx in words[1:]:
                vertidx, uvidx = wridx.split("/")
                v.append(int(vertidx)-1-offset[0])
                u.append(int(uvidx)-1-offset[1])
            f['v'] = v
            f['uv'] = u
            obj.faces.append(f)
            try:
                line = file.next().strip()
            except StopIteration:
                face_parsing = False
                line = None
    return line

def _face_vertex_uvs_normals(line, file, obj, offset):
    face_parsing = True
    while(face_parsing):
        words = line.split()
        if words[0] != "f":
            face_parsing = False
        else:
            f = {}
            v,u,n = [],[],[]
            for wridx in words[:0:-1]:
            #for wridx in words[1:]:
                vertidx, uvidx, normidx = wridx.split("/")
                v.append(int(vertidx)-1-offset[0])
                n.append(int(normidx)-1-offset[2])
                if uvidx != '':
                    u.append(int(uvidx)-1-offset[1])
            f['v'] = v
            if u:
                f['uv'] = u
            f['n'] = n
            obj.faces.append(f)
            try:
                line = file.next().strip()
            except StopIteration:
                face_parsing = False
                line = None
    return line


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 2:
        f = import_obj(sys.argv[1])
        print f[0]
        print f[1]
        print f[2]

