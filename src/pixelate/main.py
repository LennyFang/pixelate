import cv2 as cv
import numpy as np

PALETTE = "test.png"
PIXEL_SIZE = 10


def main():
    pal = read_palette(PALETTE)
    process_video("test.mp4", pal)


def read_palette(path: str) -> np.ndarray:
    return cv.imread(path, cv.IMREAD_COLOR).reshape(-1, 3).astype(np.float32)


def process_video(path: str, palette_array: np.ndarray):
    video = cv.VideoCapture(path)

    video_width = int(video.get(cv.CAP_PROP_FRAME_WIDTH))
    video_height = int(video.get(cv.CAP_PROP_FRAME_HEIGHT))
    video_fps = video.get(cv.CAP_PROP_FPS)
    video_frame_count = int(video.get(cv.CAP_PROP_FRAME_COUNT))

    print(
        f" --- Video Metadata --- \nDimensions: {video_width}x{video_height}\nFPS: {video_fps}\nFrame Count: {video_frame_count}"
    )

    output_video = cv.VideoWriter(
        "output.mp4",
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
