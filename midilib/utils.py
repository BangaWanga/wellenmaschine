import pygame
import pygame.midi

def ask_for_midi_device(kind="input",default_value = False):

    if (default_value != False):
        return __return_pygame_IO__(kind,default_value)

    """ Let the user choose the midi device to use """
    # Check, if we are looking for a valid kind:
    assert (kind in ("input", "output")), "Invalid MIDI device kind: {0}".format(kind)

    is_input = (kind == "input")
    # First, print info about the available devices:
    print()
    print("Available MIDI {0} devices:".format(kind))
    device_ids = []  # list to hold all available device IDs
    device_id = 0
    info_tuple = ()
    # print info about all the devices
    while not pygame.midi.get_device_info(device_id) is None:
        info_tuple = pygame.midi.get_device_info(device_id)
        if info_tuple[2] == is_input:  # this holds 1 if device is an input device, 0 if not
            print("ID: {0}\t{1}\t{2}".format(device_id, info_tuple[0], info_tuple[1]))
            device_ids.append(device_id)
        device_id += 1
    assert (device_id > 0), "No {0} devices found!".format(kind)

    user_input_id = -1
    while not user_input_id in device_ids:  # ask for the desired device ID until one of the available ones is given
        user_input = input("Which device would you like to use as {0}? Please provide its ID: ".format(kind))
        try:  # try to cast the user input into an int
            user_input_id = int(user_input)
        except ValueError:  # if it fails because of incompatible input, let them try again
            pass
    info_tuple = pygame.midi.get_device_info(user_input_id)
    print("Chosen {0} device: ID: {1}\t".format(kind, user_input_id) + str(info_tuple[0]) + "\t" + str(info_tuple[1]))
    # Open port from chosen device
    __return_pygame_IO__(kind,user_input_id)

def __return_pygame_IO__(kind,user_input_id):
    if kind == "input":
        return pygame.midi.Input(device_id=user_input_id)
    elif kind == "output":
        return pygame.midi.Output(device_id=user_input_id, latency=0)
