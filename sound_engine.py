import os
import random
import pygame
from config import asset_path


class SoundEngine:

    def __init__(self):
        pygame.mixer.init()
        self._files = os.listdir(asset_path.joinpath('sound'))
        to_load = ['tmpchime', 'flipper_on', 'flipper_off', 'launch', 'tear', 'click', 'doubleclick', 'buzz']
        self.sounds = {name: self._load_sounds(name) for name in to_load}

    def _load_sounds(self, sound_name):
        appropriate = [s for s in self._files if s.startswith(sound_name)]
        return [pygame.mixer.Sound(str(asset_path.joinpath('sound').joinpath(file))) for file in appropriate]

    def play(self, sound_name):
        if sound_name in self.sounds:
            sound = random.choice(self.sounds[sound_name])
            sound.play()
        else:
            pass