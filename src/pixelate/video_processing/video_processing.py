import multiprocessing as mp
import os.path

import cv2 as cv
import numpy as np

from pixelate.util import util


class VideoMetadata:
    def __init__(self, file_path: str):
        video = cv.VideoCapture(file_path)

        self.file_path = file_path
        self.width = int(video.get(cv.CAP_PROP_FRAME_WIDTH))
        self.height = int(video.get(cv.CAP_PROP_FRAME_HEIGHT))
        self.fps = video.get(cv.CAP_PROP_FPS)
        self.frame_count = int(video.get(cv.CAP_PROP_FRAME_COUNT))
        self.duration = self.frame_count / self.fps  # in seconds

        video.release()

    def get_valid_pixel_sizes(self) -> list[int]:
        gcd = util.gcd(self.width, self.height)
        primes = util.prime_factorization(gcd)
        return util.factors_from_primes(primes)

    def generate_video_preview_images(self, ctx: util.Context, n: int):
        # We will generate n preview images which the first one being the first frame of the video
        # and then other n-1 being evenly spaces throughout the video

        video = cv.VideoCapture(self.file_path)

        interval = self.duration / n
        for i in range(n):
            self.process_video_preview_image(
                ctx,
                video,
                interval * i,
            )

        video.release()

    def process_video_preview_image(
        self,
        ctx: util.Context,
        video: cv.VideoCapture,
        timestamp: float,
    ):
        assert timestamp >= 0
        assert timestamp < (self.frame_count / self.fps)

        start_frame = int(self.fps * timestamp)

        video.set(cv.CAP_PROP_POS_FRAMES, start_frame - 1)

        ok, image = video.read()
        if not ok:
            print("Unable to read frame of video")

        # Reshape the image to group up the pixels by the PIXEL_SIZE and get the mean of the RGB values
        # we cast as a float32 here so we don't run into overflow issues when we do the squared distance computations
        group_pixel_mean = (
            image.reshape(
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

        # Write the frame to the image, no resize here because we can do it on the frontend so we can save space here
        cv.imwrite(
            os.path.join(
                ctx.output_dir, f"{ctx.preview_image_prefix}_{start_frame}.png"
            ),
            pixelated,
        )

    def process_video_with_multiprocessing(
        self,
        ctx: util.Context,
    ):
        # Get general meta data on video

        frame_per_process = self.frame_count // ctx.process_count

        processes = []

        process_method = (
            self.process_video_chunk_no_resize
            if ctx.no_resize
            else self.process_video_chunk
        )
        # We discount the last process as we want it to handle all the remaining frames that count not be split properly
        for i in range(ctx.process_count - 1):
            processes.append(
                mp.Process(
                    target=process_method,
                    args=(
                        ctx,
                        i,
                        i * frame_per_process,
                        (i + 1) * frame_per_process,
                    ),
                )
            )
            processes[-1].start()
        # Scaler tail
        processes.append(
            mp.Process(
                target=process_method,
                args=(
                    ctx,
                    ctx.process_count - 1,
                    (ctx.process_count - 1) * frame_per_process,
                    self.frame_count,
                ),
            )
        )
        processes[-1].start()

        for process in processes:
            process.join()


    def process_video_chunk(
        self,
        ctx: util.Context,
        index: int,
        start_frame: int,
        end_frame: int,
    ):
        print(f"Begining Process {index}")
        video = cv.VideoCapture(self.file_path)

        video.set(cv.CAP_PROP_POS_FRAMES, start_frame - 1)

        processed_count = 0

        pixelated_width = self.width // ctx.pixel_size
        pixelated_height = self.height // ctx.pixel_size

        output_video = cv.VideoWriter(
            os.path.join(ctx.output_dir, f"{ctx.temp_video_prefix}_{index}.mp4"),
            cv.VideoWriter_fourcc(*"mp4v"),
            self.fps,
            (pixelated_width, pixelated_height),
        )

        while start_frame + processed_count < end_frame:
            ok, image = video.read()
            if not ok:
                print("Video is done processing")
                break

            # Reshape the image to group up the pixels by the pixel_size and get the mean of the RGB values
            # we cast as a float32 here so we don't run into overflow issues when we do the squared distance computations
            group_pixel_mean = (
                image.reshape(
                    pixelated_height,
                    ctx.pixel_size,
                    pixelated_width,
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
                .reshape(pixelated_height, pixelated_width, 3)
                .astype(np.uint8)
            )

            # Write the frame to the video but also resize it with nearest neighbour to maintain the pixels
            output_video.write(
                cv.resize(
                    pixelated,
                    dsize=(self.width, self.height),
                    interpolation=cv.INTER_NEAREST,
                ),
            )
            processed_count += 1

        video.release()
        output_video.release()

    # This variation is here for the sake of trying to prevent branch predict
    # It might be really negligible, but we should try to optimize where we can for simple things like this
    def process_video_chunk_no_resize(
        self,
        ctx: util.Context,
        index: int,
        start_frame: int,
        end_frame: int,
    ):
        print(f"Begining Process {index}")
        video = cv.VideoCapture(self.file_path)

        video.set(cv.CAP_PROP_POS_FRAMES, start_frame - 1)

        processed_count = 0

        pixelated_width = self.width // ctx.pixel_size
        pixelated_height = self.height // ctx.pixel_size

        output_video = cv.VideoWriter(
            os.path.join(ctx.output_dir, f"{ctx.temp_video_prefix}_{index}.mp4"),
            cv.VideoWriter_fourcc(*"mp4v"),
            self.fps,
            (pixelate_width, pixelated_height),
        )

        while start_frame + processed_count < end_frame:
            ok, image = video.read()
            if not ok:
                print("Video is done processing")
                break

            # Reshape the image to group up the pixels by the pixel_size and get the mean of the RGB values
            # we cast as a float32 here so we don't run into overflow issues when we do the squared distance computations
            group_pixel_mean = (
                image.reshape(
                    pixelated_height,
                    ctx.pixel_size,
                    pixelated_width,
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
                .reshape(pixelated_height, pixelated_width, 3)
                .astype(np.uint8)
            )

            # Write the frame to the video
            output_video.write(pixelated)

            processed_count += 1

        video.release()
        output_video.release()
