import cv2



cap = cv2.VideoCapture(0)

while cap.isOpened():

	ret, frame = cap.read()
	cv2.imshow('get_lane', frame)


        if cv2.waitKey(1) & 0xFF == ord('q'):
                break


cv2.destroyAllWindows()
cap.release()
