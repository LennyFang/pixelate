import cv2 as cv
import numpy as np
import ffmpeg
import os
import multiprocessing as mp

PALETTE = "test.png"
PIXEL_SIZE = 10

TEMP_VIDEO_PATH = "temp_video.mp4"


def main():
    pal = read_palette(PALETTE)
    # process_video("test.webm", pal)
    # process_video_chunk("test.webm", pal, 0, 0, 60)
    process_video_with_multiprocessing("test.webm", pal, 4)
    # add_audio_to_export(TEMP_VIDEO_PATH, "test.webm", "complete_output.mp4", True)
    # ffmpeg.concat(ffmpeg.input("complete_output.mp4"), ffmpeg.input("complete_output_p5.mp4")).output("combined_video.mp4").run()


def add_audio_to_export(
    temp_video_path: str, original_video_path: str, output_path: str, keep_temp: bool
):
    video_input = ffmpeg.input(temp_video_path)
    audio_input = ffmpeg.input(original_video_path).audio

    ffmpeg.output(video_input, audio_input, output_path).run()

    if not keep_temp:
        print(" --- Cleaning temp video file --- ")
        os.remove(video_path)
        print(" --- Removed temp video file --- ")


def read_palette(path: str) -> np.ndarray:
    return cv.imread(path, cv.IMREAD_COLOR).reshape(-1, 3).astype(np.float32)


def process_video_with_multiprocessing(
    original_video_path: str, palette_array: np.ndarray, process_count: int
):
    # Get general meta data on video
    video = cv.VideoCapture(original_video_path)

    video_width = int(video.get(cv.CAP_PROP_FRAME_WIDTH))
    video_height = int(video.get(cv.CAP_PROP_FRAME_HEIGHT))
    video_fps = video.get(cv.CAP_PROP_FPS)
    video_frame_count = int(video.get(cv.CAP_PROP_FRAME_COUNT))
    video.release()

    frame_per_process = video_frame_count // process_count

    processes = []

    # We discount the last process as we want it to handle all the remaining frames that count not be split properly
    for i in range(process_count - 1):
        processes.append(
            mp.Process(
                target=process_video_chunk,
                args=(
                    original_video_path,
                    palette_array,
                    i,
                    i * frame_per_process,
                    (i + 1) * frame_per_process,
                    video_fps,
                    video_width,
                    video_height,
                ),
            )
        )
        processes[-1].start()
    # Scaler tail
    processes.append(
        mp.Process(
            target=process_video_chunk,
            args=(
                original_video_path,
                palette_array,
                process_count - 1,
                (process_count - 1) * frame_per_process,
                video_frame_count,
                video_fps,
                video_width,
                video_height,
            ),
        )
    )
    processes[-1].start()

    video.release()

    for process in processes:
        process.join()


def process_video_chunk(
    original_video_path: str,
    palette_array: np.ndarray,
    index: int,
    start_frame: int,
    end_frame: int,
    video_fps: float,
    video_width: int,
    video_height: int,
):
    video = cv.VideoCapture(original_video_path)

    video.set(cv.CAP_PROP_POS_FRAMES, start_frame - 1)

    processed_count = 0

    output_video = cv.VideoWriter(
        f"temp_video_{index}.mp4",
        cv.VideoWriter_fourcc(*"mp4v"),
        video_fps,
        (video_width, video_height),
    )

    while start_frame + processed_count < end_frame:
        ok, image = video.read()
        if not ok:
            print("Video is done processing")
            break

        # Reshape the image to group up the pixels by the PIXEL_SIZE and get the mean of the RGB values
        # we cast as a float32 here so we don't run into overflow issues when we do the squared distance computations
        group_pixel_mean = (
            image.reshape(
                video_height // PIXEL_SIZE,
                PIXEL_SIZE,
                video_width // PIXEL_SIZE,
                PIXEL_SIZE,
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
            .reshape(video_height // PIXEL_SIZE, video_width // PIXEL_SIZE, 3)
            .astype(np.uint8)
        )

        # Write the frame to the video but also resize it with nearest neighbour to maintain the pixels
        output_video.write(
            cv.resize(
                pixelated,
                dsize=(video_width, video_height),
                interpolation=cv.INTER_NEAREST,
            ),
        )
        processed_count += 1

    video.release()


def process_video(original_video_path: str, palette_array: np.ndarray):
    video = cv.VideoCapture(original_video_path)

    video_width = int(video.get(cv.CAP_PROP_FRAME_WIDTH))
    video_height = int(video.get(cv.CAP_PROP_FRAME_HEIGHT))
    video_fps = video.get(cv.CAP_PROP_FPS)
    video_frame_count = int(video.get(cv.CAP_PROP_FRAME_COUNT))

    print(
        f" --- Video Metadata --- \nDimensions: {video_width}x{video_height}\nFPS: {video_fps}\nFrame Count: {video_frame_count}"
    )

    output_video = cv.VideoWriter(
        TEMP_VIDEO_PATH,
        cv.VideoWriter_fourcc(*"mp4v"),
        video_fps,
        (video_width, video_height),
    )

    while video.isOpened():
        # Read consumes the current frame and moves the pointer to the next
        ok, image = video.read()
        if not ok:
            print("Video is done processing")
            break

        # Reshape the image to group up the pixels by the PIXEL_SIZE and get the mean of the RGB values
        # we cast as a float32 here so we don't run into overflow issues when we do the squared distance computations
        group_pixel_mean = (
            image.reshape(
                video_height // PIXEL_SIZE,
                PIXEL_SIZE,
                video_width // PIXEL_SIZE,
                PIXEL_SIZE,
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
            .reshape(video_height // PIXEL_SIZE, video_width // PIXEL_SIZE, 3)
            .astype(np.uint8)
        )

        # Write the frame to the video but also resize it with nearest neighbour to maintain the pixels
        output_video.write(
            cv.resize(
                pixelated,
                dsize=(video_width, video_height),
                interpolation=cv.INTER_NEAREST,
            ),
        )

    output_video.release()
    video.release()


if __name__ == "__main__":
    main()
