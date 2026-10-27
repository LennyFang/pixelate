import argparse
import os

from pixelate.ffmpeg_util import ffmpeg_util
from pixelate.image_processing import image_processing
from pixelate.util import colours, filters, util
from pixelate.video_processing import video_processing

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
        default=[
            4
        ],  # I have to make this a list because the user input an arg the type is an list
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
    video_parser.add_argument(
        "-f",
        "--filters",
        nargs="*",
        type=str,
        choices=filters.FILTER_LIST,
        help="the filters to apply to video",
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
    image_parser.add_argument(
        "-f",
        "--filters",
        nargs="*",
        type=str,
        choices=filters.FILTER_LIST,
        help="the filters to apply to image",
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
        default=[6],
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
    preview_parser.add_argument(
        "-f",
        "--filters",
        nargs="*",
        type=str,
        choices=filters.FILTER_LIST,
        help="the filters to apply to the preview images",
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

        output_dir, output_file = os.path.split(args.output)

        if args.output != DEFAULT_VIDEO_OUTPUT:
            if args.output[-1] == "/":
                print("Error: ", end="")
                c_ctx.push(colours.ColourFormat(colours.DEFAULT, colours.NORMAL))
                print(f"{args.output} is not a valid file path")
                c_ctx.pop()
                return

            # TODO: Files can have . in their name and it can not be the file extension as well
            # might want to fix this later on
            if args.output.find(".") == -1:
                print("Error: ", end="")
                c_ctx.push(colours.ColourFormat(colours.DEFAULT, colours.NORMAL))
                print(f"{args.output} is has no file extension")
                c_ctx.pop()
                return

            if not os.path.isdir(output_dir) and output_dir != "":
                print("Error: ", end="")
                c_ctx.push(colours.ColourFormat(colours.DEFAULT, colours.NORMAL))
                print(f"{output_dir} is not a valid directory")
                c_ctx.pop()
                return

        output_dir = os.getcwd() if output_dir == "" else output_dir

        c_ctx.pop()

        video_metadata = video_processing.VideoMetadata(args.video_file[0])
        pixel_sizes = video_metadata.get_valid_pixel_sizes()
        selected_pixel_size = -1

        c_ctx.push(colours.ColourFormat(colours.CYAN, colours.NORMAL))
        while selected_pixel_size not in pixel_sizes:
            print("Please choose a pixel size from this list", end="")
            c_ctx.push(colours.ColourFormat(colours.CYAN, colours.BOLD))
            print(f" {pixel_sizes}")
            c_ctx.pop()

            c_ctx.push(colours.ColourFormat(colours.GREEN, colours.BOLD))
            selected_pixel_size = int(input("Pixel Size: "))
            c_ctx.pop()

        c_ctx.clear()

        ctx = util.Context(
            args.palette_file[0],
            output_dir,
            output_file,
            args.output,
            selected_pixel_size,
            args.processes[0],
            args.no_audio,
            args.no_resize,
        )

        # Parse the filters from strings into the their functions
        filters.parse_filter_str_list(
            ctx, video_metadata.get_dimensions(), args.filters
        )

        # TODO: Add in some progress stuff
        video_metadata.process_video_with_multiprocessing(ctx)

        print("Finshed processing chunks")

        print("Concating all the chunks")
        ffmpeg_util.concat_all_temp_videos(ctx, args.keep_temp)
        print("Done concat")

        if not args.no_audio:
            print("Adding audio")
            ffmpeg_util.add_audio_to_export(ctx, video_metadata, args.keep_temp)
        else:
            # We have to rename the temp combined file
            os.rename(
                os.path.join(
                    ctx.output_dir,
                    f"{ctx.temp_video_prefix}_{ctx.combined_video_name}.mp4",
                ),
                ctx.output_path,
            )

        c_ctx.push(colours.ColourFormat(colours.GREEN, colours.BOLD))
        print("\nVideo has finished processing!")

        c_ctx.push(colours.ColourFormat(colours.CYAN, colours.NORMAL))
        print("File Path: ", end="")
        c_ctx.push(colours.ColourFormat(colours.DEFAULT, colours.NORMAL))
        print(f"{ctx.output_path}")

        c_ctx.pop()
        print("Pixel Size: ", end="")
        c_ctx.push(colours.ColourFormat(colours.DEFAULT, colours.NORMAL))
        print(f"{ctx.pixel_size}")

        c_ctx.pop()
        print("Output Resolution: ", end="")
        c_ctx.push(colours.ColourFormat(colours.DEFAULT, colours.NORMAL))
        print(f"{video_metadata.width}x{video_metadata.height}")

        c_ctx.pop()
        print("Pixel Resolution: ", end="")
        c_ctx.push(colours.ColourFormat(colours.DEFAULT, colours.NORMAL))
        print(
            f"{video_metadata.width // ctx.pixel_size}x{video_metadata.height // ctx.pixel_size}"
        )

        c_ctx.clear()

    elif args.subcommand == "image":
        c_ctx.push(colours.ColourFormat(colours.RED, colours.BOLD))
        if not os.path.isfile(args.image_file[0]):
            print("Error: ", end="")
            c_ctx.push(colours.ColourFormat(colours.DEFAULT, colours.NORMAL))
            print(f"{args.image_file[0]} does not exist file")
            c_ctx.pop()
            return

        if not os.path.isfile(args.palette_file[0]):
            print("Error: ", end="")
            c_ctx.push(colours.ColourFormat(colours.DEFAULT, colours.NORMAL))
            print(f"{args.palette_file[0]} does not exist file")
            c_ctx.pop()
            return

        output_dir, output_file = os.path.split(args.output)

        if args.output != DEFAULT_IMAGE_OUTPUT:
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

            if not os.path.isdir(output_dir) and output_dir != "":
                print("Error: ", end="")
                c_ctx.push(colours.ColourFormat(colours.DEFAULT, colours.NORMAL))
                print(f"{output_dir} is not a valid directory")
                c_ctx.pop()
                return

        output_dir = os.getcwd() if output_dir == "" else output_dir

        c_ctx.pop()

        image_metadata = image_processing.ImageMetadata(args.image_file[0])
        pixel_sizes = image_metadata.get_valid_pixel_sizes()
        selected_pixel_size = -1

        c_ctx.push(colours.ColourFormat(colours.CYAN, colours.NORMAL))
        while selected_pixel_size not in pixel_sizes:
            print("Please choose a pixel size from this list", end="")
            c_ctx.push(colours.ColourFormat(colours.CYAN, colours.BOLD))
            print(f" {pixel_sizes}")
            c_ctx.pop()

            c_ctx.push(colours.ColourFormat(colours.GREEN, colours.BOLD))
            selected_pixel_size = int(input("Pixel Size: "))
            c_ctx.pop()

        c_ctx.clear()

        ctx = util.Context(
            args.palette_file[0],
            output_dir,
            output_file,
            args.output,
            selected_pixel_size,
            1,
            False,
            args.no_resize,
        )

        # Parse the filters from strings into the their functions
        filters.parse_filter_str_list(
            ctx, image_metadata.get_dimensions(), args.filters
        )

        image_metadata.process_image(ctx)

        c_ctx.push(colours.ColourFormat(colours.GREEN, colours.BOLD))
        print("\nImage has finished processing!")

        c_ctx.push(colours.ColourFormat(colours.CYAN, colours.NORMAL))
        print("File Path: ", end="")
        c_ctx.push(colours.ColourFormat(colours.DEFAULT, colours.NORMAL))
        print(f"{ctx.output_path}")

        c_ctx.pop()
        print("Pixel Size: ", end="")
        c_ctx.push(colours.ColourFormat(colours.DEFAULT, colours.NORMAL))
        print(f"{ctx.pixel_size}")

        c_ctx.pop()
        print("Output Resolution: ", end="")
        c_ctx.push(colours.ColourFormat(colours.DEFAULT, colours.NORMAL))
        print(f"{image_metadata.width}x{image_metadata.height}")

        c_ctx.pop()
        print("Pixel Resolution: ", end="")
        c_ctx.push(colours.ColourFormat(colours.DEFAULT, colours.NORMAL))
        print(
            f"{image_metadata.width // ctx.pixel_size}x{image_metadata.height // ctx.pixel_size}"
        )

        c_ctx.clear()

    elif args.subcommand == "preview":
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

        if not os.path.isdir(args.output_dir):
            print("Error: ", end="")
            c_ctx.push(colours.ColourFormat(colours.DEFAULT, colours.NORMAL))
            print(f"directory {args.output_dir} does not exist")
            c_ctx.pop()
            return

        video_metadata = video_processing.VideoMetadata(args.video_file[0])
        pixel_sizes = video_metadata.get_valid_pixel_sizes()
        selected_pixel_size = -1

        c_ctx.push(colours.ColourFormat(colours.CYAN, colours.NORMAL))
        while selected_pixel_size not in pixel_sizes:
            print("Please choose a pixel size from this list", end="")
            c_ctx.push(colours.ColourFormat(colours.CYAN, colours.BOLD))
            print(f" {pixel_sizes}")
            c_ctx.pop()

            c_ctx.push(colours.ColourFormat(colours.GREEN, colours.BOLD))
            selected_pixel_size = int(input("Pixel Size: "))
            c_ctx.pop()

        c_ctx.clear()

        ctx = util.Context(
            args.palette_file[0],
            args.output_dir,
            None,
            args.output,
            selected_pixel_size,
            1,
            False,
            args.no_resize,
        )

        # Parse the filters from strings into the their functions
        filters.parse_filter_str_list(
            ctx, video_metadata.get_dimensions(), args.filters
        )

        # TODO: Maybe have a progress bar
        video_metadata.generate_video_preview_images(ctx, args.number[0])

        c_ctx.push(colours.ColourFormat(colours.GREEN, colours.BOLD))
        print("\nPreview images have finished processing!")

        c_ctx.push(colours.ColourFormat(colours.CYAN, colours.NORMAL))
        print("Output Directory: ", end="")
        c_ctx.push(colours.ColourFormat(colours.DEFAULT, colours.NORMAL))
        print(f"{ctx.output_dir}")

        c_ctx.pop()
        print("Pixel Size: ", end="")
        c_ctx.push(colours.ColourFormat(colours.DEFAULT, colours.NORMAL))
        print(f"{ctx.pixel_size}")

        c_ctx.pop()
        print("Output Resolution: ", end="")
        c_ctx.push(colours.ColourFormat(colours.DEFAULT, colours.NORMAL))
        print(f"{video_metadata.width}x{video_metadata.height}")

        c_ctx.pop()
        print("Pixel Resolution: ", end="")
        c_ctx.push(colours.ColourFormat(colours.DEFAULT, colours.NORMAL))
        print(
            f"{video_metadata.width // ctx.pixel_size}x{video_metadata.height // ctx.pixel_size}"
        )

        # args.video_file[0]
        # args.palette_file[0]
        # args.number
        # args.no_resize


if __name__ == "__main__":
    main()
