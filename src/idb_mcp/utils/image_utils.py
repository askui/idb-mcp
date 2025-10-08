from dataclasses import dataclass

from PIL import Image


def _calc_center_offset(
    image_size: tuple[int, int],
    container_size: tuple[int, int],
) -> tuple[int, int]:
    """Calculate the offset to center the image in the container.

    If the image is larger than the container, the offset will be negative.

    Args:
        image_size (tuple[int, int]): The size of the image to center (width, height).
        container_size (tuple[int, int]): The size of the container to center the image in (width, height).

    Returns:
        tuple[int, int]: The offset to center the image in the container.
    """
    return (
        (container_size[0] - image_size[0]) // 2,
        (container_size[1] - image_size[1]) // 2,
    )


@dataclass
class ScalingResults:
    """Results of scaling calculations.

    Args:
        factor (float): The scaling factor applied.
        size (tuple[int, int]): The resulting size (width, height).
    """

    factor: float
    size: tuple[int, int]


def _calculate_scaling_for_fit(
    original_size: tuple[int, int],
    target_size: tuple[int, int],
) -> ScalingResults:
    """Calculate the scaling factor and size of an image to fit within target size while maintaining aspect ratio.

    If the image is larger than the target size, the scaling factor will be less than 1.

    Args:
        original_size (tuple[int, int]): The size of the original image (width, height).
        target_size (tuple[int, int]): The target size to fit the image into (width, height).

    Returns:
        ScalingResults: The scaling factor and resulting size.

    Raises:
        ValueError: If the original size or target size is not positive.
    """
    if original_size[0] <= 0 or original_size[1] <= 0:
        error_msg = f"Size must have positive width and height: {original_size}"
        raise ValueError(error_msg)

    if target_size[0] <= 0 or target_size[1] <= 0:
        error_msg = f"Target size must have positive width and height: {target_size}"
        raise ValueError(error_msg)

    aspect_ratio = original_size[0] / original_size[1]
    target_aspect_ratio = target_size[0] / target_size[1]
    if target_aspect_ratio > aspect_ratio:
        factor = target_size[1] / original_size[1]
        width = max(1, int(original_size[0] * factor))  # Ensure minimum width of 1
        height = target_size[1]
    else:
        factor = target_size[0] / original_size[0]
        width = target_size[0]
        height = max(1, int(original_size[1] * factor))  # Ensure minimum height of 1
    return ScalingResults(factor=factor, size=(width, height))


def _center_image_in_background(
    image: Image.Image,
    background_size: tuple[int, int],
    background_color: tuple[int, int, int] = (0, 0, 0),
) -> Image.Image:
    """Center an image in a background image.

    Args:
        image (Image.Image): The image to center.
        background_size (tuple[int, int]): The size of the background (width, height).
        background_color (tuple[int, int, int], optional): The background color. Defaults to `(0, 0, 0)`.

    Returns:
        Image.Image: A new image with the input image centered on the background.
    """
    background = Image.new("RGB", background_size, background_color)
    offset = _calc_center_offset(image.size, background_size)
    background.paste(image, offset)
    return background


def scale_image_to_fit(
    image: Image.Image,
    target_size: tuple[int, int],
) -> Image.Image:
    """Scale an image to fit within specified size while maintaining aspect ratio.

    Use black padding to fill the remaining space.

    Args:
        image (Image.Image): The PIL Image to scale.
        target_size (tuple[int, int]): The target size to fit the image into (width, height).

    Returns:
        Image.Image: A new PIL Image that fits within the specified size.
    """
    scaling_results = _calculate_scaling_for_fit(image.size, target_size)
    scaled_image = image.resize(scaling_results.size, Image.Resampling.LANCZOS)
    return _center_image_in_background(scaled_image, target_size)


def _scale_coordinates(
    coordinates: tuple[int, int],
    offset: tuple[int, int],
    factor: float,
    inverse: bool,
) -> tuple[int, int]:
    """Scale coordinates based on scaling factor and offset.

    Args:
        coordinates (tuple[int, int]): The coordinates to scale.
        offset (tuple[int, int]): The offset to apply.
        factor (float): The scaling factor.
        inverse (bool): Whether to apply inverse scaling.

    Returns:
        tuple[int, int]: The scaled coordinates.
    """
    if inverse:
        result = (
            (coordinates[0] - offset[0]) / factor,
            (coordinates[1] - offset[1]) / factor,
        )
    else:
        result = (
            (coordinates[0]) * factor + offset[0],
            (coordinates[1]) * factor + offset[1],
        )
    return (int(result[0]), int(result[1]))


def _check_coordinates_in_bounds(
    coordinates: tuple[float, float],
    bounds: tuple[int, int],
) -> None:
    """Check if coordinates are within bounds.

    Args:
        coordinates (tuple[float, float]): The coordinates to check.
        bounds (tuple[int, int]): The bounds (width, height).

    Raises:
        ValueError: If coordinates are out of bounds.
    """
    if (
        coordinates[0] < 0
        or coordinates[1] < 0
        or coordinates[0] > bounds[0]
        or coordinates[1] > bounds[1]
    ):
        print(bounds)
        error_msg = f"Coordinates {coordinates[0]}, {coordinates[1]} are out of bounds"
        raise ValueError(error_msg)


def scale_coordinates(
    coordinates: tuple[int, int],
    original_size: tuple[int, int],
    target_size: tuple[int, int],
    inverse: bool = False,
) -> tuple[int, int]:
    """Scale coordinates between original and scaled image sizes.

    Args:
        coordinates (tuple[int, int]): The coordinates to scale.
        original_size (tuple[int, int]): The original image size (width, height).
        target_size (tuple[int, int]): The target size (width, height).
        inverse (bool, optional): Whether to scale from target to original. Defaults to `False`.

    Returns:
        tuple[int, int]: The scaled coordinates.

    Raises:
        ValueError: If the scaled coordinates are out of bounds.
    """
    scaling_results = _calculate_scaling_for_fit(original_size, target_size)
    offset = _calc_center_offset(scaling_results.size, target_size)
    result = _scale_coordinates(coordinates, offset, scaling_results.factor, inverse)
    _check_coordinates_in_bounds(
        result, original_size if inverse else scaling_results.size
    )
    return result


__all__ = [
    "scale_image_to_fit",
    "scale_coordinates",
    "ScalingResults",
]
