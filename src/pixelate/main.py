from pixelate.ffmpeg_util import ffmpeg_util
from pixelate.util import util, colours
from pixelate.video_processing import video_processing

import argparse
import os

DEFAULT_PROCESSES = 4
DEFAULT_VIDEO_OUTPUT = "pixelate.mp4"
DEFAULT_IMAGE_OUTPUT = "pixelate.png"
DEFAULT_PREVIEW_OUTPUT_DIR = os.getcwd()


def main():
    c_ctx = colours.ColourFormatContext()

    parser = argparse.ArgumentParser(
        prog="pixelate", description="pixelate video/images with different palettes"
    )

    sub_parsers = parser.add_subparsers(dest="subcommand")

    video_parser = sub_parsers.add_parser(
        "video",
        description="pixelate a video with a specified palette and pixel size",
        usage=f"\r{colours.ESC}{colours.BOLD};{colours.GREEN}mUsage: {colours.ESC}{colours.NORMAL};{colours.CYAN}mpixelate video [OPTIONS] video_file palette_file{colours.ESC}{colours.NORMAL}m",
    )
    video_parser.add_argument(
        "video_file",
        nargs=1,
        type=str,
        help="the file path of the video to be pixelated",
    )
    video_parser.add_argument(
        "palette_file",
        nargs=1,
        type=str,
        help="the file path of the palette image to use for the video",
    )
    video_parser.add_argument(
        "-p",
        "--processes",
        nargs=1,
        type=int,
        default=4,
        help="the amount of processes used to pixelate the video (default: %(default)s)",
    )
    video_parser.add_argument(
        "-k",
        "--keep_temp",
        action="store_true",
        help="keeps the temporay files after the processing",
    )
    video_parser.add_argument(
        "-a",
        "--no_audio",
        action="store_true",
        help="removes the original audio from the pixelated version of video",
    )
    video_parser.add_argument(
        "-r",
        "--no_resize",
        action="store_true",
        help="keeps the pixelated video at reduced size and doesn't resize the video the original dimensions",
    )
    video_parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=DEFAULT_VIDEO_OUTPUT,
        help="the output file (default: %(default)s)",
    )

    image_parser = sub_parsers.add_parser(
        "image",
        description="pixelate a image with a specified palette and pixel size",
        usage=f"\r{colours.ESC}{colours.BOLD};{colours.GREEN}mUsage: {colours.ESC}{colours.NORMAL};{colours.CYAN}mpixelate image [OPTIONS] image_file palette_file{colours.ESC}{colours.NORMAL}m",
    )
    image_parser.add_argument(
        "image_file",
        nargs=1,
        type=str,
        help="the file path of the image to be pixelated",
    )
    image_parser.add_argument(
        "palette_file",
        nargs=1,
        type=str,
        help="the file path of the palette image to use for the image",
    )
    image_parser.add_argument(
        "-r",
        "--no_resize",
        action="store_true",
        help="keeps the pixelated image at reduced size and doesn't resize the image the original dimensions",
    )
    image_parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=DEFAULT_IMAGE_OUTPUT,
        help="the output file (default: %(default)s)",
    )

    preview_parser = sub_parsers.add_parser(
        "preview",
        description="pixelate (n) number of frames from a video with a specified palette and pixel size",
        usage=f"\r{colours.ESC}{colours.BOLD};{colours.GREEN}mUsage: {colours.ESC}{colours.NORMAL};{colours.CYAN}mpixelate preview [OPTIONS] video_file palette_file{colours.ESC}{colours.NORMAL}m",
    )
    preview_parser.add_argument(
        "video_file",
        nargs=1,
        type=str,
        help="the file path of the image to be pixelated",
    )
    preview_parser.add_argument(
        "palette_file",
        nargs=1,
        type=str,
        help="the file path of the palette image to use for the image",
    )
    preview_parser.add_argument(
        "-n",
        "--number",
        nargs=1,
        type=int,
        default=6,
        help="the number of preview images to generate (default: %(default)s)",
    )
    preview_parser.add_argument(
        "-r",
        "--no_resize",
        action="store_true",
        help="keeps the pixelated image at reduced size and doesn't resize the image the original dimensions",
    )
    preview_parser.add_argument(
        "-o",
        "--output_dir",
        type=str,
        default=DEFAULT_PREVIEW_OUTPUT_DIR,
        help="the output directory of the preview images (default: %(default)s)",
    )

    args = parser.parse_args()

    if args.subcommand is None:
        # Give usage and show off the sub commands like in uv
        print("A CLI application to pixelate video/images with different palettes")
        print()
        c_ctx.push(colours.ColourFormat(colours.GREEN, colours.BOLD))

        print("Usage: ", end="")

        c_ctx.push(colours.ColourFormat(colours.CYAN, colours.NORMAL))
        print("pixelate <COMMAND> [OPTIONS]\n")
        c_ctx.pop()

        print("Commands:")
        c_ctx.push(colours.ColourFormat(colours.CYAN, colours.BOLD))

        print(f"\t{'video':10}", end="")
        c_ctx.push(colours.ColourFormat(colours.DEFAULT, colours.NORMAL))
        print("pixelate a video with a specified palette and pixel size")
        c_ctx.pop()

        print(f"\t{'image':10}", end="")
        c_ctx.push(colours.ColourFormat(colours.DEFAULT, colours.NORMAL))
        print("pixelate a image with a specified palette and pixel size")
        c_ctx.pop()

        print(f"\t{'preview':10}", end="")
        c_ctx.push(colours.ColourFormat(colours.DEFAULT, colours.NORMAL))
        print(
            "pixelate (n) number of frames from a video with a specified palette and pixel size"
        )
        c_ctx.pop()
        c_ctx.clear()
    elif args.subcommand == "video":
        args.video_file[0]
        args.palette_file[0]
        args.output
        args.processes
        args.keep_temp
        args.no_audio
        args.no_resize

        c_ctx.push(colours.ColourFormat(colours.RED, colours.BOLD))
        if not os.path.isfile(args.video_file[0]):
            print("Error: ", end="")
            c_ctx.push(colours.ColourFormat(colours.DEFAULT, colours.NORMAL))
            print(f"{args.video_file[0]} does not exist file")
            c_ctx.pop()
            return

        if not os.path.isfile(args.palette_file[0]):
            print("Error: ", end="")
            c_ctx.push(colours.ColourFormat(colours.DEFAULT, colours.NORMAL))
            print(f"{args.palette_file[0]} does not exist file")
            c_ctx.pop()
            return

        if args.output != DEFAULT_VIDEO_OUTPUT:
            if args.output[-1] == "/":
                print("Error: ", end="")
                c_ctx.push(colours.ColourFormat(colours.DEFAULT, colours.NORMAL))
                print(f"{args.output} is not a valid file path")
                c_ctx.pop()
                return

            if args.output.find(".") == -1:
                print("Error: ", end="")
                c_ctx.push(colours.ColourFormat(colours.DEFAULT, colours.NORMAL))
                print(f"{args.output} is has no file extension")
                c_ctx.pop()
                return

            directory, file = os.path.split(args.output)
            if not os.path.isdir(directory):
                print("Error: ", end="")
                c_ctx.push(colours.ColourFormat(colours.DEFAULT, colours.NORMAL))
                print(f"{directory} is not a valid directory")
                c_ctx.pop()
                return

        c_ctx.pop()

        video_metadata = video_processing.VideoMetadata(args.video_file[0])
        pixel_sizes = video_metadata.get_valid_pixel_sizes()
        selected_pixel_size = -1
        while selected_pixel_size not in pixel_sizes:
            selected_pixel_size = int(
                input(
                    f"Please choose a pixel size from this list {pixel_sizes}\n Pixel Size: "
                )
            )

        # TODO: Take user input for the pixel size choice
        ctx, ok = util.Context.create(
            args.palette_file[0], args.output, selected_pixel_size, args.processes
        )
        if not ok:
            print("Something is wrong with the inputed context")
            return
        video_metadata.process_video_with_multiprocessing(ctx)
        ffmpeg_util.conact_all_temp_videos(ctx, args.keep_temp)
        if not args.no_audio:
            # TODO: Make sure to change the output name to the -o flag
            ffmpeg_util.add_audio_to_export(
                ctx, video_metadata, "something.mp4", args.keep_temp
            )
        # TODO: Some nice formated output message
    elif args.subcommand == "image":
        args.image_file[0]
        args.palette_file[0]
        args.no_resize
    elif args.subcommand == "preview":
        args.video_file[0]
        args.palette_file[0]
        args.number
        args.no_resize

    print(args)

    # ctx, ok = util.Context.create("test.png", "output", 20, 12)
    # if not ok:
    #     print("Not okay")
    #
    # video = video_processing.VideoMetadata("test.webm")
    # video.get_valid_pixel_sizes()

    # video.generate_video_preview_images(ctx, 3)
    # video.process_video_with_multiprocessing(ctx)
    # ffmpeg_util.concat_all_temp_videos(ctx, False)
    # ffmpeg_util.add_audio_to_export(ctx, video, "complete", False)


if __name__ == "__main__":
    main()
