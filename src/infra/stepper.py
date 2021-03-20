# Created by Patrick Kao

import cv2
import numpy as np
from tinkerforge.bricklet_thermal_imaging import BrickletThermalImaging
from tinkerforge.ip_connection import IPConnection

from src.cv.mask_detection import detect

HOST = "localhost"
PORT = 4223
STEPPER_UID = "6Sbx9V"  # Change XXYYZZ to the UID of your Stepper Brick
IR_UID = "Nb9"
STEP_DEGREES = 1.8
STEPS_PER_ROT = 360 / STEP_DEGREES


def setup_devices():
    ipcon = IPConnection()  # Create IP connection
    stepper = None
    # stepper = SilentStepper(STEPPER_UID, ipcon)  # Create device object

    # ir
    ti = BrickletThermalImaging(IR_UID, ipcon)  # Create device object

    ipcon.connect(HOST, PORT)  # Connect to brickd

    # setup ir
    ti.set_image_transfer_config(ti.IMAGE_TRANSFER_MANUAL_TEMPERATURE_IMAGE)
    ti.set_resolution(BrickletThermalImaging.RESOLUTION_0_TO_655_KELVIN)
    # Don't use device before ipcon is connected

    # stepper.set_motor_current(800)  # 800 mA
    # stepper.set_step_configuration(stepper.STEP_RESOLUTION_1, True)  # 1/8 steps (interpolated)
    # stepper.set_max_velocity(2000)  # Velocity 2000 steps/s
    #
    # # Slow acceleration (500 steps/s^2),
    # # Fast deacceleration (5000 steps/s^2)
    # stepper.set_speed_ramping(500, 5000)
    # stepper.enable()
    return stepper, ti


def dispense_mask(stepper):
    NUM_STEPS = 1 * STEPS_PER_ROT
    stepper.set_steps(NUM_STEPS)


def unmasked_present(image):
    bounds = detect(image)
    unmasked_faces = []
    masked_faces = []
    for box in bounds:
        if box[0]==True:
            unmasked_faces.append(box[1:])
        else:
            masked_faces.append(box[1:])
    return len(unmasked_faces) > 0


def to_f(bin):
    deg_off = bin / 100
    deg_celsius = deg_off - 273.15
    return deg_celsius * 9 / 5 + 32


def control_flow():
    stepper, ti = setup_devices()
    cap = cv2.VideoCapture(0)
    try:
        while True:

            temp = ti.get_temperature_image()
            temp = np.array(temp)
            temp = to_f(temp)
            max_temp = np.max(temp)

            # Capture frame-by-frame
            ret, frame = cap.read()
            # frame dim: height, width, channels

            risk = unmasked_present(frame)

            if risk:
                dispense_mask(stepper)
    finally:
        # stepper.stop()
        # time.sleep(0.4)
        # stepper.disable()
        pass


if __name__ == "__main__":
    control_flow()
