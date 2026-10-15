import os

import cv2 as cv
import numpy as np

PRIME_NUMBERS = [
    2,
    3,
    5,
    7,
    11,
    13,
    17,
    19,
    23,
    29,
    31,
    37,
    41,
    43,
    47,
    53,
    59,
    61,
    67,
    71,
    73,
    79,
    83,
    89,
    97,
    101,
]

TEMP_VIDEO_PREFIX = "temp_video"
COMBINED_VIDEO_NAME = "combined"
PREVIEW_IMAGE_PREFIX = "preview"


class Context:
    def __init__(
        self,
        palette_path: str,
        output_dir: str,
        pixel_size: int,
        process_count: int,
        temp_video_prefix=TEMP_VIDEO_PREFIX,
        combined_video_name=COMBINED_VIDEO_NAME,
        preview_image_prefix=PREVIEW_IMAGE_PREFIX,
    ):
        self.palette = read_palette(palette_path)
        self.palette_path = palette_path

        self.output_dir = output_dir
        self.temp_video_prefix = temp_video_prefix
        self.combined_video_name = combined_video_name
        self.preview_image_prefix = preview_image_prefix

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


def gcd(a: int, b: int):
    assert a > 0
    assert b > 0
    while b != 0:
        (a, b) = (b, a % b)
    return a


def prime_factorization(n: int) -> dict[int, int]:
    counts = {}
    i = 0
    while i < len(PRIME_NUMBERS):
        prime = PRIME_NUMBERS[-(i + 1)]

        if n % prime != 0:
            i += 1
            continue

        n = n // prime

        if counts.get(prime) is None:
            counts[prime] = 1
        else:
            counts[prime] += 1

    return counts


def factors_from_primes(counts: dict[int, int]) -> list[int]:
    factors = [1]
    for prime in PRIME_NUMBERS:
        if counts.get(prime) is None:
            continue

        i = 0
        n = len(factors)
        while i < n:
            factor = factors[i]
            for count in range(counts[prime]):
                factors.append(factor * (prime ** (count + 1)))
            i += 1

    return sorted(factors)
