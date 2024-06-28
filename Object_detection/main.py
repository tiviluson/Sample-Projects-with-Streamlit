from cProfile import label
import streamlit as st
from os import path
import cv2
import numpy as np
from PIL import Image

st.set_page_config(page_title='Object detection for Images', page_icon=':writing_hand:', menu_items={
                   'About': "Made by [:rainbow[*tiviluson*] :sunglasses: :raccoon:](https://github.com/tiviluson) "})
st.title('Object Detection for Images using cv2')
st.logo(path.join('assets', 'logo.png'))
st.caption(
    'by [:rainbow[*tiviluson*] :sunglasses: :raccoon:](https://github.com/tiviluson) ')

MODEL = "Object_detection/model/MobileNetSSD_deploy.caffemodel"
PROTOTXT = "Object_detection/model/MobileNetSSD_deploy.prototxt.txt"


def process_image(image):
    image = cv2.resize(image, (300, 300))
    blob = cv2.dnn.blobFromImage(
        image, 1/127.5, (300, 300), (127.5, 127.5, 127.5))
    net = cv2.dnn.readNetFromCaffe(PROTOTXT, MODEL)
    net.setInput(blob)
    detections = net.forward()
    return detections


def annotate_image(image, detections, labels, confidence_threshold=0.5):
    # loop over the detections
    (h, w) = image.shape[:2]
    for i in np.arange(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]

        if confidence > confidence_threshold:
            # extract the index of the class label from the `detections`,
            # then compute the (x, y)-coordinates of the bounding box for
            # the object

            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            start_x, start_y, end_x, end_y = box.astype("int")
            idx = int(detections[0, 0, i, 1])
            label = labels[idx]
            cv2.rectangle(image, (start_x, start_y),
                          (end_x, end_y), (0, 255, 0), 5)
            cv2.putText(image, label, (start_x, start_y - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 255, 0), 5)
    return image


@st.cache_data
def load_labels(label_file):
    with open(label_file) as f:
        labels = f.read().strip().split("\n")
    return labels


def main():
    st.title('Object Detection for Images')
    file = st.file_uploader('Upload Image', type=['jpg', 'png', 'jpeg'])
    labels = load_labels(label_file='Object_detection/model/labels.txt')
    if file is not None:
        col1, col2 = st.columns(2)
        with col1:
            st.image(file, caption="Uploaded Image")

        image = Image.open(file)
        image = np.array(image)
        detections = process_image(image)
        processed_image = annotate_image(image, detections, labels)
        with col2:
            st.image(processed_image, caption="Processed Image")


if __name__ == "__main__":
    main()
