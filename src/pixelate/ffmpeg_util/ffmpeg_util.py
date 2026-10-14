import os

import ffmpeg

from pixelate.util import util
from pixelate.video_processing import video_processing


def concat_all_temp_videos(ctx: util.Context, keep_temp: bool):
    ffmpeg.concat(
        *[
            ffmpeg.input(
                os.path.join(ctx.output_dir, f"{ctx.temp_video_prefix}_{i}.mp4")
            )
            for i in range(ctx.process_count)
        ]
    ).output(
        os.path.join(
            ctx.output_dir, f"{ctx.temp_video_prefix}_{ctx.combined_video_name}.mp4"
        )
    ).run()

    if not keep_temp:
        for i in range(ctx.process_count):
            os.remove(os.path.join(ctx.output_dir, f"{ctx.temp_video_prefix}_{i}.mp4"))


def add_audio_to_export(
    ctx: util.Context,
    video_metadata: video_processing.VideoMetadata,
    output_name: str,
    keep_temp: bool,
):
    video_input = ffmpeg.input(
        os.path.join(
            ctx.output_dir, f"{ctx.temp_video_prefix}_{ctx.combined_video_name}.mp4"
        )
    )
    audio_input = ffmpeg.input(video_metadata.file_path).audio

    ffmpeg.output(
        video_input, audio_input, os.path.join(ctx.output_dir, f"{output_name}.mp4")
    ).run()

    if not keep_temp:
        print(" --- Cleaning temp video file --- ")
        os.remove(
            os.path.join(
                ctx.output_dir, f"{ctx.temp_video_prefix}_{ctx.combined_video_name}.mp4"
            )
        )
        print(" --- Removed temp video file --- ")
