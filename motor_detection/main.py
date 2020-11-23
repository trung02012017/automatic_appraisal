import cv2


class YOLOV3PlateModelRecognition:
    def __init__(self, model_config, model_path, label_path, debug=False):
        self.debug = debug
        self.conf_threshold = 0.2
        self.nms_threshold = 0.2
        self.inp_width = 320
        self.inp_height = 320
        with open(label_path, 'r') as f:
            self.classes = f.read().rstrip('\n').split('\n')
        self.net = cv2.dnn_DetectionModel(model_config, model_path)
        self.net.setInputSize(self.inp_width, self.inp_height)
        self.net.setInputScale(1.0 / 255)
        # self.net.setInputSwapRB(True)

    def test(self, img, classes, confidences, boxes):
        frame = img
        cv2.imshow("origin", frame)
        for classId, confidence, box in zip(classes.flatten(), confidences.flatten(), boxes):
            label = '%s' % (self.classes[classId])
            labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            left, top, width, height = box
            top = max(top, labelSize[1])
            cv2.rectangle(frame, box, color=(0, 255, 0), thickness=3)
            cv2.rectangle(frame, (left, top - labelSize[1]), (left + labelSize[0], top + baseLine), (255, 255, 255),
                          cv2.FILLED)
            cv2.putText(frame, label, (left, top), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))

        cv2.imshow('out', frame)
        cv2.waitKey(0)

    def map_class(self, class_ids):
        if not isinstance(class_ids, list):
            class_ids = list(class_ids)
        classes = []
        for i in range(len(class_ids)):
            classes.append(self.classes[class_ids[i]])
        return classes

    def predict(self, img):
        class_ids, confidences, boxes = self.net.detect(img, confThreshold=0.5, nmsThreshold=0.2)

        if len(class_ids) == 0:
            return []

        if self.debug:
            self.test(img, class_ids, confidences, boxes)

        classes = self.map_class(class_ids.flatten())
        return classes