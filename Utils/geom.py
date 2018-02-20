#!/usr/bin/env python3

from panda3d.core import LVector3
from panda3d.bullet import BulletTriangleMeshShape, BulletTriangleMesh


def normalized(*args):
    vec = LVector3(*args)
    vec.normalize()

    return vec


def bullet_shape_from(source, dynamic=False):
    mesh = BulletTriangleMesh()

    for geom_node in source.findAllMatches('**/+GeomNode'):
        gn = geom_node.node()
        ts = gn.getTransform()
        for geom in gn.getGeoms():
            mesh.addGeom(geom, True, ts)

    return BulletTriangleMeshShape(mesh, dynamic=dynamic)
