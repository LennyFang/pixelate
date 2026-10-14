import multiprocessing as mp
import os.path

import cv2 as cv
import numpy as np

TEMP_VIDEO_PREFIX = "temp_video"
PREVIEW_IMAGE_PREFIX = "preview"


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

    def generate_video_preview_images(
            self, palette_array: np.ndarray, pixel_size: int, n: int, output_dir: str
    ):
        # We will generate n preview images which the first one being the first frame of the video
        # and then other n-1 being evenly spaces throughout the video

        video = cv.VideoCapture(self.file_path)

        interval = self.duration / n
        for i in range(n):
            self.process_video_preview_image(
                video,
                palette_array,
                pixel_size,
                interval * i,
                os.path.join(output_dir, f"{PREVIEW_IMAGE_PREFIX}_{i}.png"),
            )

        video.release()

    def process_video_preview_image(
        self,
        video: cv.VideoCapture,
        palette_array: np.ndarray,
        pixel_size: int,
        timestamp: float,
        output_path: str,
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
                self.height // pixel_size,
                pixel_size,
                self.width // pixel_size,
                pixel_size,
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
                - palette_array.astype(np.float32)[None, :, :]
            )
            ** 2,
            axis=2,
        )

        # Take the index of the palette colour with the least sqaured distance
        colour_indexes = np.argmin(squared_distances, axis=1)

        # Map the indexes to the actual colours on the palette
        pixelated = (
            palette_array[colour_indexes]
            .reshape(self.height // pixel_size, self.width // pixel_size, 3)
            .astype(np.uint8)
        )

        # Write the frame to the image, no resize here because we can do it on the frontend so we can save space here
        cv.imwrite(output_path, pixelated)

    def process_video_with_multiprocessing(
        self,
        palette_array: np.ndarray,
        pixel_size: int,
        process_count: int,
        output_dir: str,
    ):
        # Get general meta data on video

        frame_per_process = self.frame_count // process_count

        processes = []

        # We discount the last process as we want it to handle all the remaining frames that count not be split properly
        for i in range(process_count - 1):
            processes.append(
                mp.Process(
                    target=self.process_video_chunk,
                    args=(
                        palette_array,
                        pixel_size,
                        i,
                        i * frame_per_process,
                        (i + 1) * frame_per_process,
                        output_dir,
                    ),
                )
            )
            processes[-1].start()
        # Scaler tail
        processes.append(
            mp.Process(
                target=self.process_video_chunk,
                args=(
                    palette_array,
                    pixel_size,
                    process_count - 1,
                    (process_count - 1) * frame_per_process,
                    self.frame_count,
                    output_dir,
                ),
            )
        )
        processes[-1].start()

        for process in processes:
            process.join()

    def process_video_chunk(
        self,
        palette_array: np.ndarray,
        pixel_size: int,
        index: int,
        start_frame: int,
        end_frame: int,
        output_dir: str,
    ):
        print(f"Begining Process {index}")
        video = cv.VideoCapture(self.file_path)

        video.set(cv.CAP_PROP_POS_FRAMES, start_frame - 1)

        processed_count = 0

        output_video = cv.VideoWriter(
            os.path.join(output_dir, f"{TEMP_VIDEO_PREFIX}_{index}.mp4"),
            cv.VideoWriter_fourcc(*"mp4v"),
            self.fps,
            (self.width, self.height),
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
                    self.height // pixel_size,
                    pixel_size,
                    self.width // pixel_size,
                    pixel_size,
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
                    - palette_array.astype(np.float32)[None, :, :]
                )
                ** 2,
                axis=2,
            )

            # Take the index of the palette colour with the least sqaured distance
            colour_indexes = np.argmin(squared_distances, axis=1)

            # Map the indexes to the actual colours on the palette
            pixelated = (
                palette_array[colour_indexes]
                .reshape(self.height // pixel_size, self.width // pixel_size, 3)
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
