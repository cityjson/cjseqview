#!/usr/bin/env python

import geom_help
import json
import sys
import numpy as np
import math
import click
import rerun as rr
import trimesh
import random

@click.command()
@click.option('--lod_filter', type=str, default=None, help='Which LoD to filter/keep')
def main(lod_filter):
    rr. init("rerun_tin", spawn=True)
    # click.echo("lod_filter={}".format(lod_filter))
    #-- read first line
    lcount = 1
    j1 = json.loads(sys.stdin.readline())
    while True:
        line = sys.stdin.readline()
        if line != '':
            lcount += 1
            j = json.loads(line)
            if not( "type" in j and j["type"] == 'CityJSONFeature'):
               raise IOError("Line {} is not of type 'CityJSONFeature'.".format(lcount))
            #-- do the work
            v = []
            for each in j["vertices"]:
                x = (each[0] * j1["transform"]["scale"][0]) + j1["transform"]["translate"][0]
                y = (each[1] * j1["transform"]["scale"][1]) + j1["transform"]["translate"][1]
                z = (each[2] * j1["transform"]["scale"][2]) + j1["transform"]["translate"][2]
                v.append([x, y, z])
            vs = np.asarray(v)
            ts = []
            for co in j["CityObjects"]:
                extract_surfaces(co, j, vs, ts, lod_filter)
            vs2 = []
            ts2 = []
            i = 0
            for t in ts:
                ts2.append(i)
                ts2.append(i+1)
                ts2.append(i+2)
                vs2.append(vs[t[0]])
                vs2.append(vs[t[1]])
                vs2.append(vs[t[2]])
                i += 3
            name = "n_{}".format(lcount)
            vs = np.asarray(vs2)
            ts = np.array(ts2, dtype=np.uint32).reshape((-1, 3))
            visualise_rr(vs, ts, name)
        else:
            break
    # visualise(gvs, gts)

def visualise_rr(vs, ts, name):
    #-- random colour
    cr = random.randint(0, 256)
    cg = random.randint(0, 256)   
    cb = random.randint(0, 256)
    vcs = []
    for i in range(len(vs)):
        vcs.append([cr, cg, cb])
    mesh = trimesh.Trimesh(vertices=vs, faces=ts, process=False)
    rr.log(
        name,
        rr.Mesh3D(
            vertex_positions=mesh.vertices,
            vertex_colors=np.array(vcs),
            vertex_normals=mesh.vertex_normals,  
            # vertex_texcoords=vertex_texcoords,
            # albedo_texture=albedo_texture,
            indices=mesh.faces,
            # mesh_material=mesh_material,
        ),
    )

def visualise_rr_2(vs, ts, name):
    #-- random colour
    cr = random.randint(0, 256)
    cg = random.randint(0, 256)   
    cb = random.randint(0, 256)
    vcs = []
    for i in range(len(vs)):
        vcs.append([cr, cg, cb])
    # np.array(vns)    
    # c = np.vstack((cr, cg, cb)).transpose()

    mesh = trimesh.Trimesh(vertices=vs, faces=ts)
    rr.log(
        name,
        rr.Mesh3D(
            vertex_positions=mesh.vertices,
            vertex_colors=np.array(vcs),
            vertex_normals=mesh.vertex_normals,  
            # vertex_texcoords=vertex_texcoords,
            # albedo_texture=albedo_texture,
            indices=mesh.faces,
            # mesh_material=mesh_material,
        ),
    )


def extract_surfaces(co, j, vs, ts, lod_filter):
    if 'geometry' in j['CityObjects'][co]:
        for geom in j['CityObjects'][co]['geometry']:
            if lod_filter is not None:
                if geom["lod"] != lod_filter:
                    continue
            if (geom['type'] == 'MultiSurface') or (geom['type'] == 'CompositeSurface'):
                for i, face in enumerate(geom['boundaries']):
                    if ((len(face) == 1) and (len(face[0]) == 3)):
                        re = np.array(face)
                        ts.append(re[0])
                    else:
                        re, b = geom_help.triangulate_face_mapbox_earcut(face, vs)
                        if b == True:
                            for each in re:
                                ts.append(each)
            elif (geom['type'] == 'Solid'):
                for sidx, shell in enumerate(geom['boundaries']):
                    for i, face in enumerate(shell):
                        if ((len(face) == 1) and (len(face[0]) == 3)):
                            re = np.array(face)
                            ts.append(re[0])
                        else:
                            re, b = geom_help.triangulate_face_mapbox_earcut(face, vs)
                            if b == True:
                                for each in re:
                                    ts.append(each)
            elif ((geom['type'] == 'MultiSolid') or (geom['type'] == 'CompositeSolid')):
                for solididx, solid in enumerate(geom['boundaries']):
                    for sidx, shell in enumerate(solid):
                        for i, face in enumerate(shell):
                            if ((len(face) == 1) and (len(face[0]) == 3)):
                                re = np.array(face)
                                ts.append(re[0])
                            else:
                                re, b = geom_help.triangulate_face_mapbox_earcut(face, vs)
                                if b == True:
                                    for each in re:
                                        ts.append(each)
            elif (geom['type'] == 'GeometryInstance'):
                #-- TODO: implement GeometryInstance for the trees blocking the sun!
                print("GeometryInstance not supported in this viewer (yet)")
                pass

       

def get_bbox(vs):
    return [ np.min(vs[:,0]), np.min(vs[:,1]), np.max(vs[:,0]), np.max(vs[:,1]) ]

def recusionvisit(a, fs):
    if isinstance(a[0], int):
        print(len(a))
    else:
        for each in a:
            recusionvisit(each, fs)

if __name__ == '__main__':
    main()
