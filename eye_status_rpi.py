import cv2
import time
import mediapipe as mp
from scipy.spatial import distance as dis

cap = cv2.VideoCapture(0)
p_time = 0
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 640)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)

min_tolerance = 5.0
D_Score = 0 # drowsiness score (increases when driver eyes are closed below a threshold)
B_Score = 0 # behaviour score (increases when driver face moves out of the white frame)

p1 = (106, 60)
p2 = (534, 420)
 
mpDraw = mp.solutions.drawing_utils
mpFaceMesh = mp.solutions.face_mesh
faceMesh = mpFaceMesh.FaceMesh(max_num_faces=1)
drawSpec = mpDraw.DrawingSpec(thickness=1, circle_radius=2)

red = (0,0,255)
blue = (255,0,0)
green = (0,255,0)

left_eye = [ 362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385,384, 398 ]
right_eye = [ 33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161 , 246 ]  

left_eye_top_bottom = [386, 374]
left_eye_left_right = [263, 362]

right_eye_top_bottom = [159, 145]
right_eye_left_right = [133, 33]

upper_lower_lips = [13, 14]
left_right_lips = [78, 308]


face=[ 10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400,
       377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103,67, 109]

#print(len(face))
# 16 + 16 + 4 + 36 = 72 landmakrs detected in total

def draw_landmarks(image, results, land_mark, color):
    height, width =image.shape[:2]
             
    for index in land_mark:
        point = results.multi_face_landmarks[0].landmark[index]
        
        point_scale = ((int)(point.x * width), (int)(point.y*height))
        point_x = point_scale[0]
        point_y = point_scale[1]
        lm = [] 
        # lm.append((face,(int)(point.x * width), (int)(point.y*height)))
        # lm.append((face, point_x, point_y))
        # print(len(lm[0]))
        cv2.circle(image, point_scale, 2, color, 1)

def get_euclidean_distance(image, top, bottom):
    height, width = image.shape[0:2]
            
    point1 = int(top.x * width), int(top.y * height)
    point2 = int(bottom.x * width), int(bottom.y * height)
    
    distance = dis.euclidean(point1, point2)
    return distance

def get_aspect_ratio(image, outputs, top_bottom, left_right):
    landmark = outputs.multi_face_landmarks[0]
            
    top = landmark.landmark[top_bottom[0]]
    bottom = landmark.landmark[top_bottom[1]]
    
    top_bottom_dis = get_euclidean_distance(image, top, bottom)
    
    left = landmark.landmark[left_right[0]]
    right = landmark.landmark[left_right[1]]
    
    left_right_dis = get_euclidean_distance(image, left, right)
    
    aspect_ratio = left_right_dis/ top_bottom_dis
    
    return aspect_ratio


# cascade_face = cv2.CascadeClassifier('/home/siddharth/catkin_ws/src/computer_vision/open_cv/face/haarcascade_frontalface_default.xml')

while True:
    success, frame = cap.read()
    # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    induvidual_scores = []
    results = faceMesh.process(frame)
    if results.multi_face_landmarks:
        # mesh_coords = landmark_detection(frame, results, False)
        draw_landmarks(frame, results, face, green)
        draw_landmarks(frame, results, left_eye_top_bottom, red)
        draw_landmarks(frame, results, left_eye_left_right, red)
        draw_landmarks(frame, results, right_eye_top_bottom, red)
        draw_landmarks(frame, results, right_eye_left_right, red)
        draw_landmarks(frame, results, left_eye, blue)
        draw_landmarks(frame, results, right_eye, blue)
        draw_landmarks(frame, results, upper_lower_lips, red)
        draw_landmarks(frame, results, left_right_lips, red)

        ratio_left =  get_aspect_ratio(frame, results, left_eye_top_bottom, left_eye_left_right)
        ratio_right =  get_aspect_ratio(frame, results, right_eye_top_bottom, right_eye_left_right)
            
        ratio = (ratio_left + ratio_right)/2.0
        
        if ratio > min_tolerance:
            D_Score +=1
            if D_Score > 20:
                D_Score = 20
        else:
            D_Score -=1
            if D_Score < 0:
                D_Score = 0 
        
        cv2.putText(frame, f'D_Score: {int(D_Score)}', (350, 48), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)
        height, width = frame.shape[0:2]

        roi = cv2.rectangle(frame, p1, p2, (255, 255, 255), 1)
        for index in face:
            point = results.multi_face_landmarks[0].landmark[index]
            
        
            x = (int)(point.x * width)
            y = (int)(point.y * height)
            # print(x, y)

            if x > 106 and x < 534:
                if y > 60 and y < 420:
                    induvidual_scores.append(0)
                else:
                    induvidual_scores.append(1)
            else:
                induvidual_scores.append(1)

            B_Score = sum(induvidual_scores)
            
            # print(B_Score)
            

    c_time = time.time()
    fps = 1/(c_time - p_time)
    p_time = c_time

    cv2.putText(frame, f'B_Score: {int(B_Score)}', (350, 90), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)
    # faces = cascade_face.detectMultiScale(frame, scaleFactor = 1.1, minNeighbors = 2)
    # for x, y, w, h in faces:
    #   frame = cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
    cv2.putText(frame, f'FPS: {int(fps)}', (20, 48), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
    if frame is not None:
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break