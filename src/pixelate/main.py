import cv2 as cv
import numpy as np

from pixelate.ffmpeg_util import ffmpeg_util
from pixelate.video_processing import video_processing


class Context:
    def __init__(
        self, video_path: str, palette_path: str, output_dir: str, pixel_size: int
    ):
        # TODO: Add some error checking to make sure the file exitst on the system
        self.video_metadata = video_processing.VideoMetadata(video_path)
        self.palette = read_palette(palette_path)
        self.palete_path = palette_path
        self.output_dir = output_dir
        self.pixel_size = pixel_size

    def set_video_metadata(self, video_path: str):
        pass

    def set_palette(self, palette_path: str):
        pass


def main():
    ctx = Context("test.webm", "test.png", "output", 10)
    ctx.video_metadata.process_video_with_multiprocessing(ctx.palette, ctx.pixel_size, 12)
    ffmpeg_util.concat_all_temp_videos(12)
    ffmpeg_util.add_audio_to_export(
        "combined_video.mp4", "test.webm", "complete_output.mp4", True
    )
    # ffmpeg.concat(ffmpeg.input("complete_output.mp4"), ffmpeg.input("complete_output_p5.mp4")).output("combined_video.mp4").run()


def read_palette(path: str) -> np.ndarray:
    return cv.imread(path, cv.IMREAD_COLOR).reshape(-1, 3).astype(np.float32)


if __name__ == "__main__":
    main()
