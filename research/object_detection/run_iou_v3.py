from ssdmodel import *
from calculate_iou_final2 import *

LIST_OF_MODELS = ['ssd_mobilenet_v1_coco_2017_11_17', 'ssd_inception_v2_coco_2017_11_17',
                  'faster_rcnn_resnet101_lowproposals_coco_2018_01_28',
                  'faster_rcnn_resnet101_coco_2018_01_28', 'faster_rcnn_nas_lowproposals_coco_2018_01_28',
                  'faster_rcnn_nas_coco_2018_01_28']
BB_XY_INDEX = [['ymin', 'xmin', 'ymax', 'xmax'], ['ymin', 'xmin', 'ymax', 'xmax'],
               ['xc', 'yc', 'w', 'h'], ['xc', 'yc', 'w', 'h'],
               ['xc', 'yc', 'w', 'h'], ['xc', 'yc', 'w', 'h']]

# List directory path to Kitti Data Set Images
# PATH_TO_IMAGES = 'C:/Users\KAA\Documents\Rutgers\Research S18\Object Detection Models\KITTI_CAR_DATASET/2011_09_26/2011_09_26_drive_0001_sync\image_02\ground_truth'
PATH_TO_IMAGES = '/Users/Mac/Downloads/2011_09_26/2011_09_26_drive_0001_sync/image_00/data'

LIST_IMAGE_PATH = imgpaths_from_dir(PATH_TO_IMAGES)


def modify_coordinates(coor, sw, model_xy):
    if sw == 's':
        xmin = coor[model_xy.index('xmin')]
        ymin = coor[model_xy.index('ymin')]
        xmax = coor[model_xy.index('xmax')]
        ymax = coor[model_xy.index('ymax')]
    elif sw == 'f':
        xmin = coor[model_xy.index('xc')] - coor[model_xy.index('w')] / 2
        xmax = coor[model_xy.index('xc')] + coor[model_xy.index('w')] / 2
        ymin = coor[model_xy.index('yc')] - coor[model_xy.index('h')] / 2
        ymax = coor[model_xy.index('yc')] + coor[model_xy.index('h')] / 2

    return xmin, ymin, xmax, ymax


for mdl, MODEL_NAME in enumerate([LIST_OF_MODELS[0]]):
    # OUTPUT_DIR = 'C:/Users\KAA\Documents\Rutgers\Research S18\Object Detection Models\KITTI_CAR_DATASET/2011_09_26/2011_09_26_drive_0001_sync\image_02/' + "metrics_" + MODEL_NAME
    OUTPUT_DIR = '/Users/Mac/Downloads/2011_09_26/2011_09_26_drive_0001_sync/image_00' + "metrics_" + MODEL_NAME
    print(MODEL_NAME)
    SW = MODEL_NAME[0]
    SW = 's'

    list_of_imageDetections, total_run_time, mean_detection_time, std_det_time = ssdmodel(LIST_IMAGE_PATH, MODEL_NAME)
    print("total run time (s): " + str(total_run_time))
    # Rearrange in form to correctly calculate IOU
    all_pred_bbox_entries = []
    for i in range(len(list_of_imageDetections)):
        curr_detection = list_of_imageDetections[i]
        bbox_array = list_of_imageDetections[
            i].pred_bbox_array  # in each img detection, there is an array of bb predictions
        for j in range(len(bbox_array)):
            xmin, ymin, xmax, ymax = modify_coordinates(bbox_array[j], SW, BB_XY_INDEX[mdl])
            #### WHAT ARE THE 0,1,2,3
            #     _____()
            #    |     |
            #    |     |
            #  ()|_____|

            list_of_imageDetections[i].pred_bbox_array[j][0] = xmin
            list_of_imageDetections[i].pred_bbox_array[j][1] = ymin
            list_of_imageDetections[i].pred_bbox_array[j][2] = xmax
            list_of_imageDetections[i].pred_bbox_array[j][3] = ymax

            bbox_entry = [curr_detection.basename,
                          list_of_imageDetections[i].pred_bbox_array[j]]  # one box coordinate prediction
            # assigns default vals

            list_of_imageDetections[i].gt_bbox_map.insert(j, -1)
            list_of_imageDetections[i].isUsed.insert(j, 0)
            list_of_imageDetections[i].iou_map.insert(j, -1)
            all_pred_bbox_entries.append(bbox_entry)

    # write_boxes_to_CSV(all_pred_bbox_entries, 'predicted_boxes.csv')

    # Write path to ground truth CSV file
    FILEPATH_TO_GT = '/Users/Mac/Downloads/GT_2011_09_26_drive_0001.csv '
    list_of_truthDetections = read_boxes_csv(FILEPATH_TO_GT)

    # Rearrange ground truths for the correct IOU equation
    for i in range(len(list_of_truthDetections)):
        curr_detection = list_of_truthDetections[i]
        bbox_array = list_of_truthDetections[
            i].t_bbox_array  # in each img detection, there is an array of bb predictions
        for j in range(len(bbox_array)):
            curr_bbox = bbox_array[j]  # one bounding box prediction
            xmin = float(curr_bbox[0])
            xmax = float(curr_bbox[1])
            ymin = float(curr_bbox[2])
            ymax = float(curr_bbox[3])
            # should be in form: xmin ymin xmax ymax
            list_of_truthDetections[i].t_bbox_array[j][0] = xmin
            list_of_truthDetections[i].t_bbox_array[j][1] = ymin
            list_of_truthDetections[i].t_bbox_array[j][2] = xmax
            list_of_truthDetections[i].t_bbox_array[j][3] = ymax
            # assigns default vals
            list_of_truthDetections[i].num_of_detection.insert(j, 0)
            list_of_truthDetections[i].isUsed.insert(j, 0)
            list_of_truthDetections[i].pred_bbox_map.insert(j, 0)
            list_of_truthDetections[i].iou_map.insert(j, 0)
            list_of_truthDetections[i].pred_time.insert(j, 0)
            list_of_truthDetections[i].scores_array.insert(j, 0)

    list_of_imageDetections, list2 = calculate_all_iou(list_of_imageDetections, list_of_truthDetections)

    all_gt = draw_iou_boxes(list_of_imageDetections, OUTPUT_DIR)
    # write_boxes_to_CSV(all_gt, 'ground_truth_maps.csv')

    write_final_to_CSV(list_of_imageDetections, list2, OUTPUT_DIR, total_run_time, mean_detection_time, std_det_time)

print("End program")


