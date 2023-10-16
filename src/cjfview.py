#!/usr/bin/env python

import geom_help
import polyscope as ps
import json
import sys
import numpy as np
import math
import click


@click.command()
@click.option('--lod_filter', type=str, default=None, help='Which LoD to filter/keep')
def main(lod_filter):
    ps.init()
    # click.echo("lod_filter={}".format(lod_filter))
    #-- read first line
    lcount = 1
    j1 = json.loads(sys.stdin.readline())
    gvs = np.empty([0, 3], dtype=np.float64)
    gts = np.empty([0, 3], dtype=np.uint32)
    offset = 0
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
            ts = np.array(ts, dtype=np.uint32).reshape((-1, 3))
            ts += offset
            gvs = np.vstack([gvs, vs])
            gts = np.vstack([gts, ts])
            offset += vs.shape[0]
        else:
            break
    visualise(gvs, gts)
    
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

def visualise(vs, fs):
    ps.set_program_name("viewcjl")
    ps.set_up_dir("z_up")
    ps.set_ground_plane_mode("shadow_only")
    ps.set_ground_plane_height_factor(0.01, is_relative=True)
    ps.set_autocenter_structures(True)
    ps.set_autoscale_structures(True) 
    bbox = get_bbox(vs) 
    #-- shift vs to smaller coords
    xs = vs[:, 0] - bbox[0]
    ys = vs[:, 1] - bbox[1] 
    zs = vs[:, 2]
    vs2 = np.column_stack((xs, ys, zs))
    ps_mesh = ps.register_surface_mesh("cityobjects", vs2, fs)
    ps_mesh.set_transparency(0.9)
    ps_mesh.reset_transform()
    ps.show()                

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
