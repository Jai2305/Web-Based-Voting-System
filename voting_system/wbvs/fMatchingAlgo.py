import os
import cv2
import time 
sample = cv2.imread("Altered/Altered-Easy/123__M_Left_index_finger_CR.BMP")

best_score = 0
filename = ""
image = None
kp1, kp2, mp= None, None, None
start = time.time()
for file in [file for file in os.listdir("Real")][:1000] :
    print(file)
    fingerprint_image = cv2.imread("Real/"+file)
    sift = cv2.SIFT_create()

    keypoints_1, desriptors_1 = sift.detectAndCompute(sample,None)
    keypoints_2, desriptors_2 = sift.detectAndCompute(fingerprint_image, None)

    matches = cv2.FlannBasedMatcher({'algorithm':1, 'trees':10},{}).knnMatch(desriptors_1,desriptors_2,k=2)
    match_points = []
    for p,q in matches:
        if p.distance < 0.1*q.distance:
            match_points.append(p)

    keypoints = 0
    if len(keypoints_1) < len(keypoints_2) :
        keypoints = len(keypoints_1)
    else :
        keypoints = len(keypoints_2)

    if len(match_points) / keypoints *100 > best_score :
        best_score = len(match_points)/keypoints*100
        filename = file
        image= fingerprint_image
        kp1, kp2, mp = keypoints_1, keypoints_2, match_points

end = time.time()
print("BEST MATCH:" +filename)
print("SCORE:"+ str(best_score))
print("Time:"+str(end - start))

result = cv2.drawMatches(sample, kp1, image, kp2, mp, None)
result = cv2.resize(result,None, fx=4, fy=4)
cv2.imshow("Result",result)
cv2.waitKey(0)
cv2.destroyAllWindows()
