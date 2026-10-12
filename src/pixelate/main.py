import cv2 as cv
import numpy as np
from pixelate.video_processing import video_processing
from pixelate.ffmpeg_util import ffmpeg_util

PALETTE = "test.png"

def main():
    pal = read_palette(PALETTE)
    video_metadata = video_processing.VideoMetadata("test.webm")
    # process_video("test.webm", pal)
    # process_video_chunk("test.webm", pal, 0, 0, 60)
    # process_video_preview_image(video_metadata, pal, 10.5)
    # video_processing.generate_video_preview_images(video_metadata, pal, 6)
    video_processing.process_video_with_multiprocessing("test.webm", pal, 12)
    ffmpeg_util.concat_all_temp_videos(12)
    ffmpeg_util.add_audio_to_export("combined_video.mp4", "test.webm", "complete_output.mp4", True)
    # ffmpeg.concat(ffmpeg.input("complete_output.mp4"), ffmpeg.input("complete_output_p5.mp4")).output("combined_video.mp4").run()


def read_palette(path: str) -> np.ndarray:
    return cv.imread(path, cv.IMREAD_COLOR).reshape(-1, 3).astype(np.float32)


if __name__ == "__main__":
    main()
