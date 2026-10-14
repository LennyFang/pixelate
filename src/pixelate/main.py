from pixelate.ffmpeg_util import ffmpeg_util
from pixelate.util import util
from pixelate.video_processing import video_processing


def main():
    ctx, ok = util.Context.create("test.png", "output", 20, 12)
    if not ok:
        print("Not okay")

    video = video_processing.VideoMetadata("test.webm")

    # video.generate_video_preview_images(ctx, 3)
    video.process_video_with_multiprocessing(ctx)
    ffmpeg_util.concat_all_temp_videos(ctx, False)
    ffmpeg_util.add_audio_to_export(ctx, video, "complete", False)


if __name__ == "__main__":
    main()
