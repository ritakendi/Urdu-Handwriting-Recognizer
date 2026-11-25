"""Prepare class-folder images for the Urdu character model using OpenCV."""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}


def preprocess_image(image: np.ndarray, size: int = 28, padding: int = 2) -> np.ndarray:
    """Return a centered black-ink-on-white grayscale image of shape (size, size)."""
    if image is None or image.size == 0:
        raise ValueError("Input image is empty")

    if image.ndim == 3 and image.shape[2] == 4:
        gray = cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)
    elif image.ndim == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.astype(np.uint8, copy=False)

    # Binarize consistently, then normalize polarity using the image border.
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    border = np.concatenate((binary[0], binary[-1], binary[:, 0], binary[:, -1]))
    if float(np.mean(border)) < 127:
        binary = cv2.bitwise_not(binary)

    ink = cv2.bitwise_not(binary)
    points = cv2.findNonZero(ink)
    canvas = np.full((size, size), 255, dtype=np.uint8)
    if points is None:
        return canvas

    x, y, width, height = cv2.boundingRect(points)
    crop = ink[y : y + height, x : x + width]
    inner_size = size - 2 * padding
    if inner_size <= 0:
        raise ValueError("Padding must be less than half of the output size")

    scale = min(inner_size / width, inner_size / height)
    resized_width = max(1, round(width * scale))
    resized_height = max(1, round(height * scale))
    resized = cv2.resize(crop, (resized_width, resized_height), interpolation=cv2.INTER_AREA)
    left = (size - resized_width) // 2
    top = (size - resized_height) // 2
    canvas[top : top + resized_height, left : left + resized_width] = 255 - resized
    return canvas


def process_class_folders(input_dir: Path, output_dir: Path, size: int = 28) -> int:
    """Convert supported images in each immediate class subfolder. Return count."""
    if not input_dir.is_dir():
        raise FileNotFoundError(f"Input directory does not exist: {input_dir}")

    processed = 0
    for class_dir in sorted(path for path in input_dir.iterdir() if path.is_dir()):
        destination = output_dir / class_dir.name
        destination.mkdir(parents=True, exist_ok=True)
        for source in sorted(path for path in class_dir.rglob("*") if path.suffix.lower() in IMAGE_SUFFIXES):
            image = cv2.imread(str(source), cv2.IMREAD_UNCHANGED)
            result = preprocess_image(image, size=size)
            relative = source.relative_to(class_dir).with_suffix(".png")
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            if not cv2.imwrite(str(target), result):
                raise OSError(f"Could not write processed image: {target}")
            processed += 1

    if processed == 0:
        raise ValueError(f"No supported images found under {input_dir}")
    return processed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Folder containing one subfolder per class")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--size", type=int, default=28)
    args = parser.parse_args()
    count = process_class_folders(args.input, args.output, size=args.size)
    print(f"Processed {count} images into {args.output}")


if __name__ == "__main__":
    main()
