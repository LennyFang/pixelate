import cv2 as cv
import numpy as np

from pixelate.util import util


class ImageMetadata:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.pixels = cv.imread(file_path)
        self.width = np.shape(self.pixels)[1]
        self.height = np.shape(self.pixels)[0]

    def get_dimensions(self) -> (int, int):
        return (self.width, self.height)

    def get_valid_pixel_sizes(self) -> list[int]:
        gcd = util.gcd(self.width, self.height)
        primes = util.prime_factorization(gcd)
        return util.factors_from_primes(primes)

    def process_image(self, ctx: util.Context):
        group_pixel_mean = (
            self.pixels.reshape(
                self.height // ctx.pixel_size,
                ctx.pixel_size,
                self.width // ctx.pixel_size,
                ctx.pixel_size,
                3,
            )
            .mean(axis=(1, 3))
            .clip(0, 255)
            .astype(np.float32)
        )

        # Calculates the squared eculidean distance of each pixel to each colour on the palette
        # There is some forbidden numpy broadcasting here that I don't really understand
        squared_distances = np.sum(
            (
                group_pixel_mean.reshape(-1, 3)[:, None, :]
                - ctx.palette.astype(np.float32)[None, :, :]
            )
            ** 2,
            axis=2,
        )

        # Take the index of the palette colour with the least sqaured distance
        colour_indexes = np.argmin(squared_distances, axis=1)

        # Map the indexes to the actual colours on the palette
        pixelated = (
            ctx.palette[colour_indexes]
            .reshape(self.height // ctx.pixel_size, self.width // ctx.pixel_size, 3)
            .astype(np.uint8)
        )

        for func in ctx.filters:
            func(pixelated)

        # NOTE: There are no two seperate functions for the method for with or without resize because
        # the preivew subcommand should only be run once so branching is negligible

        # Write the frame to the image
        if ctx.no_resize:
            cv.imwrite(
                ctx.output_path,
                pixelated,
            )
        else:
            cv.imwrite(
                ctx.output_path,
                cv.resize(
                    pixelated,
                    dsize=(self.width, self.height),
                    interpolation=cv.INTER_NEAREST,
                ),
            )
