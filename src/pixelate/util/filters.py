import functools
from enum import Enum

import numpy as np

from pixelate.util import util

FILTER_LIST = ["hori-crt", "vert-crt"]


DEFAULT_CRT_THRESHOLD = 15


class CrtFilterKind(Enum):
    HORIZONTAL = 0
    VERTICAL = 1


def parse_filter_str_list(ctx: util.Context, dimension: (int, int), filters: [str]):
    for s in filters:
        match s:
            case "hori-crt":
                ctx.add_filter(
                    create_crt_filter(
                        ctx, dimension, DEFAULT_CRT_THRESHOLD, CrtFilterKind.HORIZONTAL
                    )
                )
            case "vert-crt":
                ctx.add_filter(
                    create_crt_filter(
                        ctx, dimension, DEFAULT_CRT_THRESHOLD, CrtFilterKind.VERTICAL
                    )
                )


def create_crt_filter(
    ctx: util.Context, dimension: (int, int), threshold: int, kind: CrtFilterKind
):
    match kind:
        case CrtFilterKind.HORIZONTAL:
            return functools.partial(
                apply_horizontal_crt_filter,
                threshold=threshold,
                crt_rows=[i for i in range(0, dimension[1] // ctx.pixel_size, 2)],
            )
        case CrtFilterKind.VERTICAL:
            return functools.partial(
                apply_vertical_crt_filter,
                threshold=threshold,
                crt_cols=[i for i in range(0, dimension[0] // ctx.pixel_size, 2)],
            )


def apply_horizontal_crt_filter(
    data_array: np.ndarray, threshold: int, crt_rows: [int]
):
    mask = data_array < threshold
    data_array[crt_rows] = np.where(mask[crt_rows], 0, data_array[crt_rows] - threshold)


def apply_vertical_crt_filter(data_array: np.ndarray, threshold: int, crt_cols: [int]):
    mask = data_array < threshold
    data_array[:, crt_cols] = np.where(
        mask[:, crt_cols], 0, data_array[:, crt_cols] - threshold
    )
