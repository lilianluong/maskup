# Created by Patrick Kao
import time

from tinkerforge.brick_silent_stepper import SilentStepper
from tinkerforge.ip_connection import IPConnection

HOST = "localhost"
PORT = 4223
UID = "6Sbx9V"  # Change XXYYZZ to the UID of your Stepper Brick
STEP_DEGREES = 1.8
STEPS_PER_ROT = 360 / STEP_DEGREES


def setup_stepper():
    ipcon = IPConnection()  # Create IP connection
    stepper = SilentStepper(UID, ipcon)  # Create device object

    ipcon.connect(HOST, PORT)  # Connect to brickd
    # Don't use device before ipcon is connected

    stepper.set_motor_current(800)  # 800 mA
    stepper.set_step_configuration(stepper.STEP_RESOLUTION_1, True)  # 1/8 steps (interpolated)
    stepper.set_max_velocity(2000)  # Velocity 2000 steps/s

    # Slow acceleration (500 steps/s^2),
    # Fast deacceleration (5000 steps/s^2)
    stepper.set_speed_ramping(500, 5000)
    stepper.enable()
    return stepper


def dispense_mask(stepper):
    NUM_STEPS = 1 * STEPS_PER_ROT
    stepper.set_steps(NUM_STEPS)


def unmasked_present():
    return False


def control_flow():
    stepper = setup_stepper()
    while True:
        risk = unmasked_present()  # could be server code
        if risk:
            dispense_mask(stepper)


if __name__ == "__main__":
    stepper = setup_stepper()
    dispense_mask(stepper)
    stepper.stop()
    time.sleep(0.4)
    stepper.disable()
