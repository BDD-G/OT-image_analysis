'''
Author: A1yssa8 a1yssa.yu@outlook.com
Date: 2023-07-13 14:16:38
LastEditors: A1yssa8 a1yssa.yu@outlook.com
LastEditTime: 2023-07-16 22:31:40
FilePath: \github-upload\OT_image_analysis\robot-control\detection_functions.py

Copyright (c) 2023 by a1yssa.yu@outlook.com, All Rights Reserved. 
'''


import json
import OT2_functions
import cv2
import os

def take_photo(filename,output_folder):
    #camera setup
    cap = cv2.VideoCapture(0)
    _, frame = cap.read()
    
    # 定义目标文件夹路径和文件名
    output_folder = output_folder
    #output_folder = "/home/pi/Desktop/object_detection/image"

    # 构建完整的输出路径
    output_path = f"{output_folder}/{filename}"

    # 使用 imwrite 将图像写入指定文件夹
    cv2.imwrite(output_path, frame)
    print('finish')
    cap.release()

def find_key_value_by_keyword(dictionary, keyword):
    key_value_dict = {key: value for key, value in dictionary.items() if keyword in key and value}
    key_value_dict = list(key_value_dict.values())
    key_value = list()
    for value in key_value_dict[0]:
        key_value.append(value['bbox'])
    return key_value

def detect(output1):
    bbox_dict1 = output1
    print(bbox_dict1)
    bbox_dict = json.loads(bbox_dict1)
    tips = find_key_value_by_keyword(bbox_dict, 'tip')
    if len(tips) != 8:
        print(len(tips))
        print('error')
        
        liquids = [None]   
    else:
        liquids = find_key_value_by_keyword(bbox_dict, 'liquid')
    return tips, liquids

def save_threshold(boxes1, boxes2):
    matched_boxes = []
    liquid_level_all = []

    for box1 in boxes1:
        min_distance = float('inf')
        matched_box = None
     
        for box2 in boxes2:
            distance = abs(box1[0] - box2[0])
            if distance < min_distance:
                min_distance = distance
                matched_box = box2

        if matched_box is not None:
            liquid_level = abs(box1[1] / matched_box[1])
            matched_boxes.append((box1, matched_box))
            liquid_level_all.append(liquid_level)
    ### not use numpy
    #total = sum(arr)
    #length = len(arr)
    #average = total / length
    liquid_level_mean = np.mean(liquid_level_all)
    print(liquid_level_mean)
    
    return liquid_level_mean

def match_boxes(boxes1, boxes2, threshold):
    matched_boxes = []

    for box1 in boxes1:
        min_distance = float('inf')
        matched_box = None

        for box2 in boxes2:
            distance = abs(box1[0] - box2[0])
            if distance < min_distance:
                min_distance = distance
                matched_box = box2

        if matched_box is not None:
            liquid_level = abs(box1[1] / matched_box[1])
            # 预警
            if 0.8 * threshold < liquid_level < 1.1*threshold:
                print('no warning')
            else:
                print(f'Warning: Liquid level is below the threshold! Current level: {liquid_level}')
                
            matched_boxes.append((box1, matched_box))

    return match_boxes

def colour(bbox_coordinates,source):
    image = cv2.imread(source)
    image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    for i, bbox in enumerate(bbox_coordinates):
        x, y, _, _ = bbox
        image_height, image_width, _ = image.shape

        # 计算边界框的中心点坐标
        center_x = int(x*image_width)
        center_y = int(y*image_height)

        # 提取中心点位置的颜色值（使用HSV颜色空间）
        color_hsv = image_hsv[center_y, center_x]
        h, s, v = color_hsv
        
        if s < 40:
            colour = "Transparent"
        else:
            # 根据H值确定颜色标签
            colour = "Undefined"
            if 0 <= h < 5:
                colour = "Red"
            elif 5 <= h < 22:
                colour = "Orange"
            elif 22 <= h < 33:
                colour = "Yellow"
            elif 33 <= h < 73:
                colour = "Green"
            elif 73 <= h < 131:
                colour = "Blue"
            elif 131 <= h < 167:
                colour = "Violet"
            else:
                colour = "Red"

        
        # 在图像上标记中心点
        cv2.circle(image, (center_x,center_y), 2, (255, 0, 0), -1)  # 以红色填充的圆形标记
        cv2.putText(image, colour, (center_x, center_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 1)

        print("colour of tip {}: {}".format(i+1, colour))
        print(h,s,v)
        
     # 获取更改路径和源文件名称
    output_dir = "D:\github-upload\OT_image_analysis\object-detection\marked_image"
    filename = os.path.basename(source)
    output_path = os.path.join(output_dir, "marked_" + filename)
    print(output_path)

    cv2.imwrite(output_path, image)  # 保存到更改路径和源文件名称的图像