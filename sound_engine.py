import os
import random
import pygame
from config import asset_path


class SoundEngine:

    def __init__(self):
        pygame.mixer.init()
        self._files = os.listdir(asset_path.joinpath('sound'))
        to_load = ['tmpchime', 'flipper_on', 'flipper_off', 'launch', 'tear', 'click', 'doubleclick', 'buzz_high',
                   'buzz_low', 'coins-', 'coins+']
        channels = ['round', 'ui', 'effects']
        pygame.mixer.set_reserved(len(channels))
        self.sounds = {name: self._load_sounds(name) for name in to_load}
        self.channels = {name: pygame.mixer.Channel(i) for i,name in enumerate(channels)}
        self.set_volume(0.5)

    def _load_sounds(self, sound_name):
        appropriate = [s for s in self._files if s.startswith(sound_name)]
        return [pygame.mixer.Sound(str(asset_path.joinpath('sound').joinpath(file))) for file in appropriate]

    def play(self, sound_name, channel=None):
        if sound_name in self.sounds:
            sound = random.choice(self.sounds[sound_name])
            if channel is None:
                sound.play()
            else:
                self.channels[channel].play(sound)
        else:
            pass

    @staticmethod
    def set_volume(volume):
        for c in range(pygame.mixer.get_num_channels()):
            pygame.mixer.Channel(c).set_volume(volume)
