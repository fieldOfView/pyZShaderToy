#!/usr/bin/env python

def import_obj(path):
    name = path.split('\\')[-1].split('/')[-1]
    verts = []
    uvs = []
    faces = []
    normals = []
    uv_dim = 0
    # parse the file
    file = open(path, 'r')
    line = file.next().strip()
    while(line):
        words = line.split()
        if len(words) == 0 or words[0].startswith('#'):
            pass
        elif words[0] == 'v':
            # "v 0.123 0.23 0.69 [0.2]" 
            x, y, z = float(words[1]), float(words[2]), float(words[3])
            verts.append((x, y, z))
        elif words[0] == 'vn':
            # "vn 0.707 0.000 0.707" --> Normals in (x,y,z) form; normals might not be unit.
            x, y, z = float(words[1]), float(words[2]), float(words[3])
            normals.append((x, y, z))
        elif words[0] == 'vt':
            if not uv_dim:
                uv_dim = len(words[1:])
            uvs.append(tuple(map(float, words[1:])))
        elif words[0] == 'f':
            if words[1].count("/") == 0:
                # faces - verts only
                faces = _face_vertex_only(line, file, faces, verts)
            elif words[1].count("/") == 1:
                # faces - verts/texturecoords
                faces = _face_vertex_uvs(line, file, faces, verts, uvs)
            elif words[1].count("/") == 2:
                faces = _face_vertex_uvs_normals(line, file, faces, verts, uvs, normals)
        try:
            line = file.next().strip()
        except StopIteration:
            line = None
    return faces


def _face_vertex_only(line, file, faces, verts):
    while(line):
        words = line.split()
        f = {}
        f['v'] = (verts[int(word[1])-1], verts[int(word[2])-1],verts[int(word[3])-1])
        faces.append(f)
        try:
            line = file.next().strip()
        except StopIteration:
            line = None
    return faces

def _face_vertex_uvs(line, file, faces, verts, uvs):
    while(line):
        words = line.split()
        f = {}
        v,u = [],[]
        for wridx in words[1:]:
            vertidx, uvidx = wridx.split("/")
            v.append(verts[int(vertidx)-1])
            u.append(uvs[int(uvidx)-1])
        f['v'] = v
        f['uv'] = u
        faces.append(f)
        try:
            line = file.next().strip()
        except StopIteration:
            line = None
    return faces

def _face_vertex_uvs_normals(line, file, faces, verts, uvs, normals):
    while(line):
        words = line.split()
        f = {}
        v,u,n = [],[],[]
        for wridx in words[1:]:
            vertidx, uvidx, normidx = wridx.split("/")
            v.append(verts[int(vertidx)-1])
            n.append(normals[int(normidx)-1])
            if uvidx != '':
                u.append(uvs[int(uvidx)-1])
        f['v'] = v
        if u:
            f['uv'] = u
        f['n'] = n
        faces.append(f)
        try:
            line = file.next().strip()
        except StopIteration:
            line = None
    return faces

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 2:
        f = import_obj(sys.argv[1])
        print f[0]
        print f[1]
        print f[2]

