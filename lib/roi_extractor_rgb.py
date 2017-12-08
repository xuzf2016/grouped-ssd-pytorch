# used to extract roi from image file
# input: 512x512x3 bmp image with box-roi (yellow or red)
# output: text file containing [x_start, x_delta, y_start, y_delta]

# strategy: sum over channels to 512x512 -> yellow or red has specific value
# make them 1, and 0 for other areas -> extract roi from binary image

import numpy as np
import glob
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import cPickle

roi_image_path = '/media/hdd/tkdrlf9202/Datasets/liver_lesion/roi_image'
roi_coordinate_path = '/media/hdd/tkdrlf9202/Datasets/liver_lesion/roi_coordinate'

# specify rgb value of roi lines
# yellow have 2-pixel thick line, red have 1-pixel line
rgb_value_yellow = (255, 255, 0)
rgb_value_red = (255, 0, 0)

# traverse over subjects
for subject in glob.glob(os.path.join(roi_image_path, '*')):
    # debug: A86 have red roi
    #if os.path.basename(os.path.normpath(subject)) != 'A86':
    #    continue
    basename_subject = os.path.basename(os.path.normpath(subject))
    path_subject = os.path.join(roi_coordinate_path, basename_subject)
    if not os.path.exists(path_subject):
        os.mkdir(path_subject)
    # traverse over phases
    for phase in glob.glob(os.path.join(subject, '*')):
        basename_phase = os.path.basename(os.path.normpath(phase))
        path_phase = os.path.join(path_subject, basename_phase)
        if not os.path.exists(path_phase):
            os.mkdir(path_phase)
        # traverse over slices
        for slice in glob.glob(os.path.join(phase, '*')):
            # get roi image and convert to numpy
            roi_image = Image.open(slice, 'r')
            roi_image_tensor = np.array(roi_image)

            # get indices that match rgb value
            index_yellow = np.where(np.all(roi_image_tensor == rgb_value_yellow, axis=-1))
            index_red = np.where(np.all(roi_image_tensor == rgb_value_red, axis=-1))
            # either one of the index list should be empty
            assert not(len(index_yellow[0]) != 0 and len(index_red[0]) != 0)
            assert not (len(index_yellow[0]) == 0 and len(index_red[0]) == 0)
            # yellow case
            if len(index_yellow[0]) != 0:
                x_start = index_yellow[1][0]
                x_end = index_yellow[1][-1]
                x_delta = x_end - x_start
                y_start = index_yellow[0][0]
                y_end = index_yellow[0][-1]
                y_delta = y_end - y_start
            # red case
            elif len(index_red[0]) != 0:
                x_start = index_red[1][0]
                x_end = index_red[1][-1]
                x_delta = x_end - x_start
                y_start = index_red[0][0]
                y_end = index_red[0][-1]
                y_delta = y_end - y_start
            # delta must be positive
            assert x_delta > 0 and y_delta > 0

            coordinate = [x_start, y_start, x_delta, y_delta]
            # write coordinate to text file
            suffix = slice[-8:-4]

            path_slice = os.path.join(path_phase, str(basename_phase)+'_'+str(suffix)+'.txt')
            output_coordinate = open(path_slice, 'w+')
            cPickle.dump(coordinate, output_coordinate)
            output_coordinate.close()
            """
            # debug: draw extracted bounding box and save to image
            output_image = roi_image.copy()
            fig, ax = plt.subplots(1)
            ax.imshow(output_image)
            rect = patches.Rectangle((x_start, y_start), x_delta, y_delta, linewidth=1, edgecolor='g', facecolor='none')
            ax.add_patch(rect)
            plt.savefig(os.path.join(path_phase, str(basename_phase)+'_'+str(suffix)+'.png'))
            plt.close()
            """
    print('subject ' + str(os.path.basename(os.path.normpath(subject))) +
          ' passed: [x_start, y_start, x_delta, y_delta] of last slice = ' + str(coordinate))
