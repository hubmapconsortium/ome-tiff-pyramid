#!/usr/bin/env python3
import shutil
from argparse import ArgumentParser
from contextlib import contextmanager
from pathlib import Path
from subprocess import check_call
from typing import Optional

import aicsimageio
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import rasterio
import rasterio.features
import shapely
from skimage.measure import regionprops

padding_default = 128


@contextmanager
def new_plot():
    """
    When used in a `with` block, clears matplotlib internal state
    after plotting and saving things. Probably not necessary to be this
    thorough in clearing everything, but extra calls to `plt.clf()` and
    `plf.close()` don't *hurt*

    Intended usage:
        ```
        with new_plot():
            do_matplotlib_things()

            plt.savefig(path)
            # or
            fig.savefig(path)
        ```
    """
    plt.clf()
    try:
        yield
    finally:
        plt.clf()
        plt.close()


def find_geojson(directory: Path) -> Optional[Path]:
    geojson_files = list(directory.glob("**/*.geojson"))

    if len(geojson_files) > 1:
        raise ValueError(f"Found multiple GeoJSON files in {directory}")
    elif len(geojson_files) == 1:
        return geojson_files[0]
    else:
        return None


def crop_geojson(
    image_path: Path,
    geojson_path: Path,
    padding: int,
    exclude_mask_content: bool,
    debug: bool,
):
    debug_out_dir = Path("crop-debug")

    print("Reading image from", image_path)
    image = aicsimageio.AICSImage(image_path)
    image_data = image.data
    print("Shape:", image_data.shape)

    print("Loading GeoJSON from", geojson_path)
    with open(geojson_path) as f:
        crop_geometry = shapely.from_geojson(f.read())
        if not isinstance(crop_geometry, shapely.GeometryCollection):
            crop_geometry = shapely.geometrycollections([crop_geometry])

        closed_geometry = shapely.GeometryCollection(
            [shapely.Polygon(poly.exterior.coords) for poly in crop_geometry.geoms]
        )

    if debug:
        debug_out_dir.mkdir(exist_ok=True, parents=True)
        pixel_channel_sum_log1p = np.log1p(image_data.squeeze().sum(axis=0))

        crop_geom_gs = gpd.GeoSeries(crop_geometry)
        with new_plot():
            axi = plt.imshow(pixel_channel_sum_log1p, cmap="gray")
            crop_geom_gs.plot(ax=axi.axes, color="#FF000080")
            axi.figure.savefig(debug_out_dir / "1-orig.pdf", bbox_inches="tight")

        closed_geom_gs = gpd.GeoSeries(closed_geometry)
        with new_plot():
            axi = plt.imshow(pixel_channel_sum_log1p, cmap="gray")
            closed_geom_gs.plot(ax=axi.axes, color="#FF000080")
            axi.figure.savefig(debug_out_dir / "2-closed-geom.pdf", bbox_inches="tight")

    identity_transform = rasterio.transform.Affine(1, 0, 0, 0, 1, 0)

    print("Computing mask")
    mask = rasterio.features.geometry_mask(
        [closed_geometry],
        (image.dims['Y'][0], image.dims['X'][0]),
        identity_transform,
        # default behavior for this script is to only include the area
        # contained in the mask, which corresponds to invert=True
        # TODO: reconsider logic and semantics of arguments
        invert=not exclude_mask_content,
    )
    print("Proportion of image selected:", mask.mean())

    if debug:
        with new_plot():
            axi = plt.imshow(mask, cmap="gray")
            axi.figure.savefig(debug_out_dir / "3-mask.pdf", bbox_inches="tight")

    print("Calculating bounding box of selected region")
    rps = list(regionprops(mask.astype(np.uint8)))
    assert len(rps) == 1

    min_y, min_x, max_y, max_x = rps[0].bbox
    image_max_y, image_max_x = (image.dims['Y'][0], image.dims['X'][0])
    pixel_slices = (
        slice(max(0, min_y - padding), min(max_y + padding, image_max_y)),
        slice(max(0, min_x - padding), min(max_x + padding, image_max_x)),
    )
    print("Crop region (y, x):", pixel_slices)

    print("Cropping image with", padding, "pixel(s) of padding")
    image_data_cropped = image.data[:, :, :, *pixel_slices]
    print("Cropping mask with", padding, "pixel(s) of padding")
    mask_data_cropped = mask[*pixel_slices]

    if debug:
        image_data_cropped_sum_log1p = np.log1p(
            image_data_cropped.squeeze().sum(axis=0)
        )
        with new_plot():
            axi = plt.imshow(image_data_cropped_sum_log1p, cmap="gray")
            axi.figure.savefig(
                debug_out_dir / "4-image-data-cropped.pdf", bbox_inches="tight"
            )
        with new_plot():
            axi = plt.imshow(mask_data_cropped, cmap="gray")
            axi.figure.savefig(
                debug_out_dir / "5-mask-cropped.pdf", bbox_inches="tight"
            )

    print("Zeroing pixels outside of selection")
    image_data_cropped[:, :, :, ~mask_data_cropped] = 0

    if debug:
        image_data_cropped_sum_log1p = np.log1p(
            image_data_cropped.squeeze().sum(axis=0)
        )
        with new_plot():
            axi = plt.imshow(image_data_cropped_sum_log1p, cmap="gray")
            axi.figure.savefig(debug_out_dir / "6-masked.pdf", bbox_inches="tight")

    print("Instantiating new AICSImage")
    image_cropped = aicsimageio.AICSImage(
        image_data_cropped,
        channel_names=image.channel_names,
        physical_pixel_sizes=image.physical_pixel_sizes,
    )

    output_path = Path(f"{image_path.name}")
    print("Saving to", output_path)
    image_cropped.save(output_path)


def crop_image(
    image_path: Path,
    dataset_directory: Path,
    ometiff_directory: Path,
    invert_geojson_mask: bool,
    debug: bool,
):
    maybe_geojson_file = find_geojson(ometiff_directory / dataset_directory)
    if maybe_geojson_file is None:
        print("Couldn't find GeoJSON file in", dataset_directory)
        output_path = Path(image_path.name)
        shutil.copy(image_path, output_path)
    else:
        print("Found GeoJSON file at", maybe_geojson_file)
        crop_geojson(
            image_path=image_path,
            geojson_path=maybe_geojson_file,
            padding=padding_default,
            exclude_mask_content=invert_geojson_mask,
            debug=debug,
        )


if __name__ == "__main__":
    p = ArgumentParser()
    p.add_argument("image_path", type=Path)
    p.add_argument("dataset_dir", type=Path)
    p.add_argument("ometiff_directory", type=Path)
    p.add_argument("--invert-geojson-mask", action="store_true")
    p.add_argument("--debug", action="store_true")
    args = p.parse_args()

    crop_image(
        image_path=args.image_path,
        dataset_directory=args.dataset_dir,
        ometiff_directory=args.ometiff_directory,
        invert_geojson_mask=args.invert_geojson_mask,
        debug=args.debug,
    )
