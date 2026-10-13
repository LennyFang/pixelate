import os

import ffmpeg


def concat_all_temp_videos(video_amount: int, output_dir: str, keep_temp: bool):
    ffmpeg.concat(
        *[ffmpeg.input(os.path.join(output_dir, f"temp_video_{i}.mp4")) for i in range(video_amount)]
    ).output(os.path.join(output_dir, "combined_video.mp4")).run()

    if not keep_temp:
        for i in range(video_amount):
            os.remove(os.path.join(output_dir, f"temp_video_{i}.mp4"))
        


def add_audio_to_export(
        temp_video_path: str, original_video_path: str, output_path: str, output_dir: str, keep_temp: bool
):
    video_input = ffmpeg.input(os.path.join(output_dir, temp_video_path))
    audio_input = ffmpeg.input(original_video_path).audio

    ffmpeg.output(video_input, audio_input, os.path.join(output_dir, output_path)).run()

    if not keep_temp:
        print(" --- Cleaning temp video file --- ")
        os.remove(os.path.join(output_dir, temp_video_path))
        print(" --- Removed temp video file --- ")
