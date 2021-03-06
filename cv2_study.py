from __future__ import print_function

import quaternion
import roslib
roslib.load_manifest('wom_cafe')
import sys
import rospy
import cv2
import numpy as np
from std_msgs.msg import String
from sensor_msgs.msg import Image
from sensor_msgs.msg import CameraInfo
from cv_bridge import CvBridge, CvBridgeError
import tf2_ros
import threading
import time

INPUT_SIZE_X = 1920
INPUT_SIZE_Y = 1080
OUTPUT_SIZE_X = 1920 * 2
OUTPUT_SIZE_Y = 1080

import matplotlib.pyplot as plt

class image_converter:

  def __init__(self):
    self.bridge = CvBridge()
    self.image_sub0 = rospy.Subscriber("/IMX185_0/image_raw", Image, self.callback0)
    # self.image_sub1 = rospy.Subscriber("/IMX185_1/image_raw", Image, self.callback1)
    # self.image_sub2 = rospy.Subscriber("/IMX185_2/image_raw", Image, self.callback2)

    self.camera_info0 = rospy.Subscriber("/IMX185_0/camera_info", CameraInfo, self.camera_info_callback0)
    self.camera_info1 = rospy.Subscriber("/IMX185_1/camera_info", CameraInfo, self.camera_info_callback1)
    self.camera_info2 = rospy.Subscriber("/IMX185_2/camera_info", CameraInfo, self.camera_info_callback2)

    # self.res_img0 = np.zeros((OUTPUT_SIZE_Y, OUTPUT_SIZE_X, 4), dtype=np.uint8)
    # self.res_img1 = np.zeros((OUTPUT_SIZE_Y, OUTPUT_SIZE_X, 4), dtype=np.uint8)
    # self.res_img2 = np.zeros((OUTPUT_SIZE_Y, OUTPUT_SIZE_X, 4), dtype=np.uint8)

    self.projection_matrix0 = None

    self.mapx0 = None
    self.mapy0 = None
    self.border0 = None

    self.mapx1 = None
    self.mapy1 = None

    self.mapx2 = None
    self.mapy2 = None
    self.border2 = None

    self.projection_matrix1 = None
    self.projection_matrix2 = None
    self.projection_matrix_set = False
    # self.res_img = np.zeros((OUTPUT_SIZE_Y, OUTPUT_SIZE_X, 3), dtype=np.uint8)
    self.ready0 = False
    self.ready1 = False
    self.ready2 = False
    self.sem0 = threading.Semaphore()
    self.sem1 = threading.Semaphore()
    self.sem2 = threading.Semaphore()


  def callback0(self,data):
    try:
      # tic = time.time()
      self.image0 = self.bridge.imgmsg_to_cv2(data, "bgr8")
      if self.projection_matrix_set:
        # self.res_img0 = np.zeros((OUTPUT_SIZE_Y, OUTPUT_SIZE_X, 4), dtype=np.uint8)
        # img = self.image0[self.mapy0, self.mapx0].reshape(1080, 1920, 3)
        # self.image0 = self.image0.reshape((1080*1920, 3))
        # self.image0 = self.image0[self.projection_matrix0]
        # self.image0 = self.image0.reshape((1080, 1920, 3))
        # print(self.image0)
        # print(self.image0.shape)
        # tic = time.time()
        # print(self.mapx0)
        # print(self.map)
        # print(self.intrinsic_mat0)
        # dist_coeffs = np.array([self.dist_coeffs0[0], self.dist_coeffs0[1], self.dist_coeffs0[3], self.dist_coeffs0[4], self.dist_coeffs0[2]])
        # img = cv2.undistort(self.image0, self.intrinsic_mat0, dist_coeffs)
        self.res_img0 = cv2.remap(self.image0, self.mapx0, self.mapy0, cv2.INTER_LINEAR, borderMode=cv2.BORDER_TRANSPARENT)
        # toc = time.time()
        # print("time elapsed: ", toc - tic)
        # self.res_img[0:1080, 1920:3840] = res
        # print("time elapsed: ", time.time() - tic)

        # for i in range(1080):
        #   for j in range(1920):
        #     coord = self.projection_matrix0[j, i]
        #     self.res_img[int(coord[1]), int(coord[0])] = self.image0[i, j]

        cv2.imshow("adf", self.res_img0)
        cv2.waitKey(1)

        # self.ready0 = True
        # print("img0 is ready!")
        # self.sem0.acquire()

    except CvBridgeError as e:
      print(e)

  def callback1(self,data):
    try:
      # tic = time.time()
      self.image1 = self.bridge.imgmsg_to_cv2(data, "bgr8")
      if self.projection_matrix_set:
        # tic = time.time()
        # self.res_img1 = np.zeros((OUTPUT_SIZE_Y, OUTPUT_SIZE_X, 4), dtype=np.uint8)
        self.res_img1 = cv2.remap(self.image1, self.mapx1, self.mapy1, cv2.INTER_LINEAR, borderMode=cv2.BORDER_TRANSPARENT)
        # toc = time.time()
        # print("time elapsed: ", toc - tic)
        # self.res_img[0:1080, 3840:5760] = res
        # print("time elapsed: ", time.time() - tic)
        # for i in range(1080):
        #   for j in range(1920):
        #     coord = self.projection_matrix1[j, i]
        #     self.res_img[int(coord[1]), int(coord[0])] = self.image1[i, j]
        self.ready1 = True
        # print("img1 is ready!")
        self.sem1.acquire()

    except CvBridgeError as e:
      print(e)

  def callback2(self,data):
    try:
      # tic = time.time()
      self.image2 = self.bridge.imgmsg_to_cv2(data, "bgr8")
      if self.projection_matrix_set:
        # tic = time.time()
        # self.res_img2 = np.zeros((OUTPUT_SIZE_Y, OUTPUT_SIZE_X, 4), dtype=np.uint8)
        self.res_img2 = cv2.remap(self.image2, self.mapx2, self.mapy2, cv2.INTER_LINEAR, borderMode=cv2.BORDER_TRANSPARENT)
        # toc = time.time()
        # print("time elapsed: ", toc - tic)
        # self.res_img[0:1080, 0:1920] = res
        # print("time elapsed: ", time.time() - tic)
        # for i in range(1080):
        #   for j in range(1920):
        #     coord = self.projection_matrix2[j, i]
        #     self.res_img[int(coord[1]), int(coord[0])] = self.image2[i, j]
        self.ready2 = True
        # print("img2 is ready!")
        self.sem2.acquire()

    except CvBridgeError as e:
      print(e)
    
  def camera_info_callback0(self, data):
      self.intrinsic_mat0 = np.reshape(np.array(data.K), (3, 3))
      self.dist_coeffs0 = np.array(data.D)

  def camera_info_callback1(self, data):
      self.intrinsic_mat1 = np.reshape(np.array(data.K), (3, 3))
      self.dist_coeffs1 = np.array(data.D)

  def camera_info_callback2(self, data):
      self.intrinsic_mat2 = np.reshape(np.array(data.K), (3, 3))
      self.dist_coeffs2 = np.array(data.D)


  def set_extr_mat(self, cam_tf):

    rotation = cam_tf.transform.rotation

    translation = cam_tf.transform.translation

    quat = np.quaternion(rotation.w, rotation.x, rotation.y, rotation.z)

    self.rot_mat = quaternion.as_rotation_matrix(quat)

    self.tr_mat = np.array((translation.x, translation.y, translation.z)).reshape(3,1)

def main(args):
  ic = image_converter()
  rospy.init_node('image_converter', anonymous=True)

  # ic.projection_matrix0 = np.load('projection_matrix_0.npy')
  # ic.projection_matrix1 = np.load('projection_matrix_1.npy')
  # ic.projection_matrix2 = np.load('projection_matrix_2.npy')

  # ic.projection_matrix1 = calculate_proj_mat(ic, 1)
  # ic.projection_matrix0 = calculate_proj_mat(ic, 0)
  # ic.projection_matrix2 = calculate_proj_mat(ic, 2)

  tic = time.time()
  # ic.mapx1, ic.mapy1, border4, _ = calculate_proj_mat(ic, 1)
  ic.mapx0, ic.mapy0, border3, ic.border0 = calculate_proj_mat(ic, 0)
  # ic.mapx2, ic.mapy2, _, ic.border2 = calculate_proj_mat(ic, 2)
  toc = time.time()
  print("time took: ", toc - tic)

  # plt.plot(ic.projection_matrix2[:, 0], ic.projection_matrix2[:, 1], 'bo')
  # plt.plot(ic.projection_matrix0[:, 0], ic.projection_matrix0[:, 1], 'bo')
  # plt.plot(ic.projection_matrix1[:, 0], ic.projection_matrix1[:, 1], 'bo')
  #
  # plt.show()

  ic.projection_matrix_set = True
  print("projection_matrix is set!")


  # plt.plot(p[:, 0], p[:, 1], 'bo')
  # plt.show()

  # cv2.namedWindow("Image window", cv2.WINDOW_NORMAL)
  while(True):
    if (ic.ready0 and ic.ready1 and ic.ready2):
        ic.ready0 = False
        ic.ready1 = False
        ic.ready2 = False
        # res_img = np.zeros_like(ic.res_img0)
        res_img = np.zeros((OUTPUT_SIZE_Y, OUTPUT_SIZE_X, 3), dtype=np.uint8)
        e1 = (ic.border2 + border3)/2
        e2 = (ic.border0 + border4)/2
        # res_img[:, :border3] = ic.res_img2[:, :border3]
        # res_img[:, border3:ic.border2] = ic.res_img2[:, border3:ic.border2] / 2 + ic.res_img0[:, border3:ic.border2] / 2
        # res_img[:, ic.border2:border4] = ic.res_img0[:, ic.border2:border4]
        # res_img[:, border4:ic.border0] = ic.res_img0[:, border4:ic.border0] / 2 + ic.res_img1[:, border4:ic.border0] / 2
        # res_img[:, ic.border0:] = ic.res_img1[:, ic.border0:]

        res_img[:, :e1] = ic.res_img2[:, :e1]
        res_img[:, e1:e2] = ic.res_img0[:, e1:e2]
        res_img[:, e2:] = ic.res_img1[:, e2:]

        # res_img = (ic.res_img0 + ic.res_img1 + ic.res_img2)
        cv2.imshow("Image window", res_img)
        cv2.waitKey(1)
        ic.sem2.release()
        ic.sem0.release()
        ic.sem1.release()

  try:
    rospy.spin()
  except KeyboardInterrupt:
    print("Shutting down")
  cv2.destroyAllWindows()

def calculate_proj_mat(ic, k, delta = 0):
    tfBuffer = tf2_ros.Buffer()
    listener = tf2_ros.TransformListener(tfBuffer)
    j = 0
    while True:
        try:
            cam_tf = tfBuffer.lookup_transform('IMX185_' + str(k) + '_base_link', 'velodyne_base_link', rospy.Time())
            ic.set_extr_mat(cam_tf)
            j += 1
            if (j == 10):
                break
        except (tf2_ros.LookupException, tf2_ros.ConnectivityException, tf2_ros.ExtrapolationException):
            pass

    inv = np.linalg.inv(ic.intrinsic_mat0)
    rot_mat_inv = np.linalg.inv(ic.rot_mat)
    dist_coeffs = ic.dist_coeffs0
    dist_coeffs = np.array([ic.dist_coeffs0[0], ic.dist_coeffs0[1], ic.dist_coeffs0[3], ic.dist_coeffs0[4], ic.dist_coeffs0[2]])
    mapx1, mapy1 = cv2.initUndistortRectifyMap(cameraMatrix=ic.intrinsic_mat0, distCoeffs=dist_coeffs, R=np.eye(3), newCameraMatrix=ic.intrinsic_mat0, size=(INPUT_SIZE_X, INPUT_SIZE_Y), m1type=cv2.CV_32FC1)
    # print(mapx1)
    # print(np.eye(3))
    # asdf

    # print("rot_mat_" + str(k) + ": ", ic.rot_mat)
    # print("tr_mat_" + str(k) + ": ", ic.tr_mat)

    # projection_matrix = np.zeros([1920, 1080, 2])
    # projection_matrix = np.zeros((1080*1920, 2), dtype=np.uint32)
    mapx = np.zeros((OUTPUT_SIZE_Y, OUTPUT_SIZE_X), dtype=np.float32)
    mapy = np.zeros((OUTPUT_SIZE_Y, OUTPUT_SIZE_X), dtype=np.float32)

    shift = 2000
    # if (k == 2):
    #     shift = 2880
    # elif (k == 0):
    #     shift = 960
    # else:
    #     shift = -960

    tic = time.time()
    x = np.arange(0, INPUT_SIZE_X, 0.1)
    x = [x]
    x = np.array(np.repeat(x, INPUT_SIZE_Y * 10, axis=0))
    x = x.reshape(1, x.shape[0] * x.shape[1])
    # print("x: ", x)
    # print("x.shape: ", x.shape)
    y = np.arange(0, INPUT_SIZE_Y, 0.1)
    y = np.repeat(y, INPUT_SIZE_X * 10)
    y = y.reshape(1, y.shape[0])
    # print("y: ", y)
    # print("y.shape: ", y.shape)
    xy = np.zeros((3, INPUT_SIZE_Y * INPUT_SIZE_X * 100))
    xy[0] = x
    xy[1] = y
    xy[2] = np.repeat(1, INPUT_SIZE_Y * INPUT_SIZE_X * 100)
    # print("Input mat xy: ", xy)
    toc = time.time()
    # print("creation time: ", toc - tic)

    tic = time.time()
    uvw = np.matmul(inv, xy)
    uvw_axis_change = np.zeros_like(uvw)
    uvw_axis_change[0] = uvw[2]
    uvw_axis_change[1] = -uvw[0]
    uvw_axis_change[2] = -uvw[1]
    # uvw = np.array([uvw[2], -uvw[0], -uvw[1]])
    uvw_axis_change -= ic.tr_mat
    res = np.matmul(rot_mat_inv, uvw_axis_change)
    toc = time.time()
    # print("calc time 1: ", toc - tic)

    tic = time.time()
    xs = -np.arctan2(res[1], res[0]) * 560 + shift
    ys = -res[2]/np.sqrt((np.square(res[0]) + np.square(res[1]))) * 315 + 528
    # print("xs: ", xs)
    # print("ys: ", ys)
    # print("xs max: ", max(xs))
    # print("xs min: ", min(xs))
    # print("ys max: ", max(ys))
    # print("ys min: ", min(ys))
    xs = np.clip(xs, 0, OUTPUT_SIZE_X - 1)
    ys = np.clip(ys, 0, OUTPUT_SIZE_Y - 1)
    xs = np.around(xs)
    ys = np.around(ys)
    xs = xs.astype(np.int32)
    ys = ys.astype(np.int32)
    # print("xs: ", xs)
    # print("ys: ", ys)
    toc = time.time()
    # print("calc time 2: ", toc - tic)

    tic = time.time()
    valsx = np.arange(INPUT_SIZE_Y * INPUT_SIZE_X * 100, dtype=np.float32)
    valsy = np.arange(INPUT_SIZE_Y * INPUT_SIZE_X * 100, dtype=np.float32)

    valsx = np.mod(valsx, INPUT_SIZE_X * 10) / 10
    valsy = np.floor_divide(valsy, INPUT_SIZE_X * 10) / 10
    mapx[ys, xs] = valsx
    mapy[ys, xs] = valsy
    mapx2 = mapx1[np.clip(np.around(mapx).astype(np.int32), 0, 1079), np.around(mapy).astype(np.int32)]
    mapy2 = mapy1[np.clip(np.around(mapx).astype(np.int32), 0, 1079), np.around(mapy).astype(np.int32)]
    # print(mapx2)
    # print(mapx2.shape)
    # adsf
    toc = time.time()
    # print("calc time 3: ", toc - tic)

    # i = 0
    # # for i in range(0, 1920, 0.1):
    # while(i < 1920):
    #     j = 0
    #     while(j < 1080):
    #     # for j in range(0, 1080, 0.1):
    #     #     print(j,i)
    #         pt = np.dot(inv, np.array([i, j, 1], dtype=np.float32))
    #         pt = np.array([pt[2], -pt[0], -pt[1]]) - ic.tr_mat.T
    #         pt = pt[0]
    #         pt = np.dot(rot_mat_inv, pt)
    #         # projection_matrix[i, j, 0] = (-np.arctan2(pt[1], pt[0]) + delta) * 320 + 960
    #         # projection_matrix[i, j, 1] = -pt[2] / (np.sqrt(pt[0] * pt[0] + pt[1] * pt[1])) * 180 + 180
    #
    #         x = (-np.arctan2(pt[1], pt[0]) + delta) * 640 + shift
    #         y = -pt[2] / (np.sqrt(pt[0] * pt[0] + pt[1] * pt[1])) * 360 + 360
    #         #y = - pt[2] / np.linalg.norm(pt[0:2]) * 540 + 540
    #         # print(y,x)
    #         x = int(np.clip(round(x), 0, 1919))
    #         y = int(np.clip(round(y), 0, 1079))
    #         # print(y,x)
    #         mapx[y, x] = i
    #         mapy[y, x] = j
    #         # projection_matrix[1920 * y + x, 0] = j
    #         # projection_matrix[1920 * y + x, 1] = i
    #         j += 0.5
    #
    #     i += 0.5
    #     print("i: ", i)
        # print(i)
            # projection_matrix[i, j, 0] = pt[0]
            # projection_matrix[i, j, 1] = pt[1]

            # print("camera: " + str(k) + " i: " + str(i) + " j: " + str(j) + " z: " + str(pt[2]))
        # print("camera: " + str(k) + " i: " + str(i) + " j: " + str(j) + " x: " + str(pt[0]) + " y: " + str(pt[1]))
        #     if (i == 0):
        #         print("i: " + str(i) + " j: " + str(j) + " x: " + str(projection_matrix[i, j, 0]) + " y: " + str(projection_matrix[i, j, 1]))

    # adfa
    # p = projection_matrix.reshape(1920 * 1080, 2)
    # plt.plot(p[:, 0], p[:, 1], 'bo')
    # plt.show()
    # asdf

    # print('x: {:.5f} to {:.5f}, y: {:.5f} to {:.5f}'.format(np.amin(p[:, 0]), np.amax(p[:, 0]), np.amin(p[:, 1]),
    #                                                         np.amax(p[:, 1])))
    # projection_matrix = projection_matrix.astype(np.int32)
    # projection_matrix[:, :, 0] = np.clip(projection_matrix[:, :, 0], 0, 1919)
    # projection_matrix[:, :, 1] = np.clip(projection_matrix[:, :, 1], 0, 359)
    # np.save('projection_matrix_2.npy', projection_matrix)

    # ic.projection_matrix0 = np.load('projection_matrix_0.npy')
    # ic.projection_matrix1 = np.load('projection_matrix_1.npy')
    # ic.projection_matrix2 = np.load('projection_matrix_2.npy')

    print("projection_matrix " + str(k) + " is set!")
    # mapy, mapx = projection_matrix.transpose()
    return mapx2, mapy2, xs[0], xs[-1]


def convert_point(x, y, w, h):
    x1 = float(x - w/2)
    y1 = float(y - h/2)

    f = float(w/2)
    r = float(w)

    omega = float(w/2)
    z0 = f - np.sqrt(r*r - omega*omega)
    
    zc = (2*z0 + np.sqrt(4*z0*z0 - 4*(x1*x1/(f*f) + 1)*(z0*z0 - r*r)))/(2*(x1*x1/(f*f) + 1))
    
    x2 = float(x1*zc/f + w/2)
    y2 = float(y1*zc/f + h/2)
    return (x2, y2)

def convert_image(frame):
    new_frame = np.zeros(frame.shape, np.uint8)
    width = new_frame.shape[1]
    height = new_frame.shape[0]
    for y in range(height):
        for x in range(width):
            cur_pos_x, cur_pos_y = convert_point(float(x), float(y), width, height)
            top_left_x = int(cur_pos_x)
            top_left_y = int(cur_pos_y)

            if (top_left_x < 0 or 
                top_left_x > width - 2 or 
                top_left_y < 0 or
                top_left_y > height - 2):
                continue
                
            dx = float(cur_pos_x - top_left_x)
            dy = float(cur_pos_y - top_left_y)

            weight_tl = (1.0 - dx) * (1.0 - dy)
            weight_tr = dx * (1.0 - dy)
            weight_bl = (1.0 - dx) * dy
            weight_br = dx * dy

            val = weight_tl * frame[top_left_y, top_left_x] + weight_tr * frame[top_left_y, top_left_x + 1] + weight_bl * frame[top_left_y + 1, top_left_x] + weight_br * frame[top_left_y + 1, top_left_x + 1]
            new_frame[y, x] = val.astype(np.uint8)
    
    return new_frame

def concatenate_images(img1, img2):
    help_mat = (img1 == np.array([0,0,0]))


if __name__ == '__main__':
    main(sys.argv)
