#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import numpy as np

from util.logger import log
from lib.rays import rays_from_silh, rays_from_landmark
from models.smpl import model_params_in_camera_coords

sess = None


class FrameData(object):
    pass


def batch_invert(x):
    try:
        import tensorflow as tf
        global sess

        tx = tf.convert_to_tensor(x, dtype=tf.float32)
        txi = tf.transpose(tf.matrix_inverse(tf.transpose(tx)))

        if sess is None:
            sess = tf.Session()

        return sess.run(txi)

    except ImportError:
        log.info('Could not load tensorflow. Falling back to matrix inversion with numpy (slower).')

    return np.asarray([np.linalg.inv(t) for t in x.T]).T


def setup_frame_rays(base_smpl, camera, camera_t, camera_rt, pose, trans, mask):
    f = FrameData()

    f.trans, f.pose = model_params_in_camera_coords(trans, pose, base_smpl.J[0], camera_t, camera_rt)
    f.mask = mask

    base_smpl.pose[:] = f.pose
    camera.t[:] = f.trans

    f.Vi = batch_invert(base_smpl.V.r)
    f.rays = rays_from_silh(f.mask, camera)

    return f





#paper 2

def setup_frame_rays_paper2(base_smpl, camera, camera_t, camera_rt, pose, trans, mask, face_landmark):
    f = FrameData()

    f.trans, f.pose = model_params_in_camera_coords(trans, pose, base_smpl.J[0], camera_t, camera_rt)
    f.mask = mask

    base_smpl.pose[:] = f.pose
    camera.t[:] = f.trans

    f.Vi = batch_invert(base_smpl.V.r)
    f.rays = rays_from_silh(f.mask, camera)
    #print("f.rays  ",f.rays)

    # paper2

    # shape (70,3)->(x,y,scores)
    f.face_landmark = np.array(face_landmark).reshape(-1, 3) * np.array([0.5, 0.5, 1])
    #print("f.face_landmark shape ",f.face_landmark.shape)
    f.face_rays = rays_from_landmark(f.face_landmark, camera)
    #print("f.face_rays  ",f.face_rays)

    return f