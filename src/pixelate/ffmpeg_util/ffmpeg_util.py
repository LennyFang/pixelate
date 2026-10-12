import ffmpeg


def concat_all_temp_videos(video_amount: int):
    ffmpeg.concat(
        *[ffmpeg.input(f"temp_video_{i}.mp4") for i in range(video_amount)]
    ).output("combined_video.mp4").run()


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
