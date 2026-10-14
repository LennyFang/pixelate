import os

import cv2 as cv
import numpy as np


class Context:
    def __init__(
        self, palette_path: str, output_dir: str, pixel_size: int, process_count: int
    ):
        self.palette = read_palette(palette_path)
        self.palette_path = palette_path
        self.output_dir = output_dir
        self.pixel_size = pixel_size
        self.process_count = process_count

    @classmethod
    def create(
        cls, palette_path: str, output_dir: str, pixel_size: int, process_count: int
    ):
        # Check for valid palette_path
        if not os.path.exists(palette_path):
            return None, False
        if palette_path[palette_path.find(".") + 1 :] not in ["png", "jpg", "jpeg"]:
            return None, False

        # Check if the output_dir is valid
        if not os.path.exists(output_dir):
            return None, False

        # Check if the pixel_size is valid
        if pixel_size < 1:
            return None, False

        if process_count < 1:
            return None, False

        return cls(palette_path, output_dir, pixel_size, process_count), True

    def set_palette(self) -> bool:
        if not os.path.exists(self.palette_path):
            return False
        if self.palette_path[self.palette_path.find(".") + 1 :] not in [
            "png",
            "jpg",
            "jpeg",
        ]:
            return False

        self.palette = read_palette(self.palette_path)
        return True


def read_palette(path: str) -> np.ndarray:
    return np.unique(
        cv.imread(path, cv.IMREAD_COLOR).reshape(-1, 3).astype(np.uint8), axis=0
    )
