# Created by Patrick Kao
import datetime
import time

import cv2
import numpy as np
from tinkerforge.brick_silent_stepper import SilentStepper
from tinkerforge.bricklet_thermal_imaging import BrickletThermalImaging
from tinkerforge.ip_connection import IPConnection
from twilio.rest import Client

from src.cv.mask_detection import detect

HOST = "localhost"
PORT = 4223
STEPPER_UID = "6Sbx9V"  # Change XXYYZZ to the UID of your Stepper Brick
IR_UID = "Nb9"
STEP_DEGREES = 1.8
STEPS_PER_ROT = 360 / STEP_DEGREES
TEXT_FREQ = datetime.timedelta(0, 60)


def setup_devices():
    ipcon = IPConnection()  # Create IP connection
    stepper = SilentStepper(STEPPER_UID, ipcon)  # Create device object

    # ir
    ti = BrickletThermalImaging(IR_UID, ipcon)  # Create device object

    ipcon.connect(HOST, PORT)  # Connect to brickd

    # setup ir
    ti.set_image_transfer_config(ti.IMAGE_TRANSFER_MANUAL_TEMPERATURE_IMAGE)
    ti.set_resolution(BrickletThermalImaging.RESOLUTION_0_TO_655_KELVIN)
    # Don't use device before ipcon is connected

    stepper.set_motor_current(800)  # 800 mA
    stepper.set_step_configuration(stepper.STEP_RESOLUTION_1, True)  # 1/8 steps (interpolated)
    stepper.set_max_velocity(2000)  # Velocity 2000 steps/s

    # Slow acceleration (500 steps/s^2),
    # Fast deacceleration (5000 steps/s^2)
    stepper.set_speed_ramping(500, 5000)
    stepper.enable()
    return stepper, ti


def dispense_mask(stepper):
    NUM_STEPS = 1 * STEPS_PER_ROT
    stepper.set_steps(NUM_STEPS)


def unmasked_present(image):
    bounds = detect(image)
    unmasked_faces = []
    masked_faces = []
    max_width = -999
    max_height = -999

    for box in bounds:
        if box[0] == False:
            unmasked_faces.append(box[1:])
        else:
            masked_faces.append(box[1:])

    for box in unmasked_faces:
        max_width = max(max_width, box[2] - box[0])
        max_height = max(box[3] - box[1], max_height)

    face_close = False
    if max_width > 140 and max_height > 180:
        face_close = True

    return len(unmasked_faces) > 0, face_close


def to_f(bin):
    deg_off = bin / 100
    deg_celsius = deg_off - 273.15
    return deg_celsius * 9 / 5 + 32


def control_flow():
    stepper, ti = setup_devices()
    cap = cv2.VideoCapture(1)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    client = Client("AC46e4ac967021aac04155bc42bbd2cb8a",
                    "876df1548202229c46da2032a0a8bee1")

    last_text_time = datetime.datetime.fromordinal(1)
    try:
        while True:

            temp = ti.get_temperature_image()
            temp = np.array(temp)
            temp = to_f(temp)
            max_temp = np.max(temp)

            print(max_temp)

            if max_temp > 100 and datetime.datetime.now() - last_text_time > TEXT_FREQ:
                warn_str = f"Your temperature is too high! We measured {int(max_temp)} degrees " \
                           f"fahrenheit"
                client.messages.create(to="+16508344535",
                                       from_="+14153199415",
                                       body=warn_str)
                print(warn_str)
                last_text_time = datetime.datetime.now()

            # Capture frame-by-frame
            ret, frame = cap.read()

            # frame dim: height, width, channels

            risk, close = unmasked_present(frame)

            # print(f"Risk present: {risk}\nRisk close: {close}")

            # if risk and close:
            if risk:
                dispense_mask(stepper)
                time.sleep(10)
                for _ in range(10):
                    ret, frame = cap.read()

    finally:
        stepper.stop()
        time.sleep(0.4)
        stepper.disable()
        pass


def test_video():
    cap = cv2.VideoCapture(1)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    while True:
        ret, frame = cap.read()
        cv2.imshow("pic", frame)
        risk, close = unmasked_present(frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        print(f"Risk present: {risk}\nRisk close: {close}")


if __name__ == "__main__":
    control_flow()
    # test_video()
