"""
XYZ Grid Nodes for ComfyUI
Implements A1111-style XYZ plot functionality for parameter exploration
"""

import torch
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import itertools
import os
import folder_paths

# Global storage for image collection across workflow runs
_image_collections = {}


class XYZGridInput:
    """
    Generates all combinations of X, Y, Z parameters.
    Outputs values that can be connected to other nodes for parameter sweeps.
    """

    def __init__(self):
        self.current_index = 0
        self.combinations = []

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "x_values": ("STRING", {
                    "multiline": True,
                    "default": "red, blue, green",
                    "tooltip": "Comma-separated values for X axis"
                }),
                "y_values": ("STRING", {
                    "multiline": True,
                    "default": "1, 2, 3",
                    "tooltip": "Comma-separated values for Y axis"
                }),
                "z_values": ("STRING", {
                    "multiline": True,
                    "default": "cat, dog, tree",
                    "tooltip": "Comma-separated values for Z axis (leave empty to disable)"
                }),
                "index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 10000,
                    "step": 1,
                    "tooltip": "Current combination index (use 0 to start, increment for each run)"
                }),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "INT", "INT", "INT", "INT", "STRING")
    RETURN_NAMES = ("x_value", "y_value", "z_value", "x_index", "y_index", "z_index", "total_combinations", "grid_info")
    FUNCTION = "generate_combination"
    CATEGORY = "XYZ Grid"

    def generate_combination(self, x_values, y_values, z_values, index):
        # Parse input values
        x_list = [v.strip() for v in x_values.split(",") if v.strip()]
        y_list = [v.strip() for v in y_values.split(",") if v.strip()]
        z_list = [v.strip() for v in z_values.split(",") if v.strip()] if z_values.strip() else [""]

        # Generate all combinations
        combinations = list(itertools.product(x_list, y_list, z_list))
        total = len(combinations)

        # Get current combination (wrap around if index is too large)
        current_index = index % total if total > 0 else 0

        if total == 0:
            return ("", "", "", 0, 0, 0, 0, "No combinations")

        x_val, y_val, z_val = combinations[current_index]

        # Calculate indices for grid layout
        x_idx = current_index % len(x_list)
        y_idx = (current_index // len(x_list)) % len(y_list)
        z_idx = current_index // (len(x_list) * len(y_list))

        # Generate grid info string
        grid_info = f"Combination {current_index + 1}/{total}: X={x_val}, Y={y_val}, Z={z_val}"

        print(f"[XYZ Grid] {grid_info}")

        return (x_val, y_val, z_val, x_idx, y_idx, z_idx, total, grid_info)


class XYZGridStitch:
    """
    Stitches multiple images into a grid layout.
    Creates a comparison grid from all XYZ combinations.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "x_labels": ("STRING", {
                    "multiline": True,
                    "default": "red, blue, green",
                    "tooltip": "Comma-separated labels for X axis (columns)"
                }),
                "y_labels": ("STRING", {
                    "multiline": True,
                    "default": "1, 2, 3",
                    "tooltip": "Comma-separated labels for Y axis (rows)"
                }),
                "z_labels": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "tooltip": "Comma-separated labels for Z axis (separate grids)"
                }),
                "label_height": ("INT", {
                    "default": 120,
                    "min": 0,
                    "max": 300,
                    "step": 1,
                    "tooltip": "Height in pixels for label area (top) - increased for larger fonts"
                }),
                "label_width": ("INT", {
                    "default": 150,
                    "min": 0,
                    "max": 300,
                    "step": 1,
                    "tooltip": "Width in pixels for Y label area (left) - increased for larger fonts"
                }),
                "gap_size": ("INT", {
                    "default": 4,
                    "min": 0,
                    "max": 50,
                    "step": 1,
                    "tooltip": "Gap size between images in pixels"
                }),
                "layout_style": (["A1111 Style (X blocks)", "Z Horizontal"], {
                    "default": "A1111 Style (X blocks)",
                    "tooltip": "A1111: Each X value gets a block with Y×Z grid inside | Z Horizontal: Z values create grids side-by-side"
                }),
            },
            "optional": {
                "is_complete": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Only stitch when True (connect from Auto Collector)"
                }),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("grid_image",)
    FUNCTION = "stitch_grid"
    CATEGORY = "XYZ Grid"
    OUTPUT_NODE = True

    def stitch_grid(self, images, x_labels, y_labels, z_labels, label_height, label_width, gap_size, layout_style, is_complete=True):
        # Skip stitching if not complete (for use with Auto Collector)
        if not is_complete:
            print("[XYZ Grid Stitch] Skipping - waiting for all images to be collected")
            # Return a small black placeholder so Save Image nodes don't save anything useful
            skip_placeholder = torch.zeros((1, 8, 8, 3))
            return (skip_placeholder,)

        # Parse labels
        x_list = [v.strip() for v in x_labels.split(",") if v.strip()]
        y_list = [v.strip() for v in y_labels.split(",") if v.strip()]
        z_list = [v.strip() for v in z_labels.split(",") if v.strip()] if z_labels.strip() else [""]

        num_x = len(x_list)
        num_y = len(y_list)
        num_z = len(z_list)

        # Convert tensor images to PIL
        pil_images = []
        for img_tensor in images:
            # Convert from torch tensor (B, H, W, C) to PIL
            img_np = (img_tensor.cpu().numpy() * 255).astype(np.uint8)
            pil_images.append(Image.fromarray(img_np))

        if not pil_images:
            # Return empty image if no images
            empty = torch.zeros((1, 512, 512, 3))
            return (empty,)

        # Get image dimensions (assume all same size)
        img_width, img_height = pil_images[0].size

        # Calculate grid dimensions
        if num_z <= 1:
            # Single 2D grid
            grid_width = label_width + num_x * img_width + (num_x + 1) * gap_size
            grid_height = num_y * img_height + (num_y + 1) * gap_size + label_height
            grid_img = self._create_single_grid(
                pil_images, num_x, num_y, img_width, img_height,
                x_list, y_list, label_height, label_width, gap_size, grid_width, grid_height
            )
        elif layout_style == "A1111 Style (X blocks)":
            # A1111 Style: Each X value gets its own block with a Y×Z grid inside
            grid_img = self._create_a1111_grid(
                pil_images, num_x, num_y, num_z, img_width, img_height,
                x_list, y_list, z_list, label_height, label_width, gap_size
            )
        else:
            # Z Horizontal: Multiple 2D grids (one per Z value) arranged horizontally
            single_grid_width = label_width + num_x * img_width + (num_x + 1) * gap_size
            single_grid_height = num_y * img_height + (num_y + 1) * gap_size + label_height

            # Arrange Z grids horizontally
            grid_width = num_z * single_grid_width + (num_z + 1) * gap_size
            grid_height = single_grid_height + label_height

            grid_img = Image.new('RGB', (grid_width, grid_height), color=(40, 40, 40))
            draw = ImageDraw.Draw(grid_img)

            # Try to load a font (3x larger for visibility)
            try:
                font = ImageFont.truetype("arial.ttf", size=max(48, min(label_height - 4, 96)))
            except:
                try:
                    font = ImageFont.truetype("arial.ttf", size=60)
                except:
                    font = ImageFont.load_default()

            images_per_grid = num_x * num_y

            for z_idx in range(num_z):
                # Get images for this Z slice
                start_idx = z_idx * images_per_grid
                end_idx = min(start_idx + images_per_grid, len(pil_images))
                z_images = pil_images[start_idx:end_idx]

                # Create single grid for this Z
                z_grid = self._create_single_grid(
                    z_images, num_x, num_y, img_width, img_height,
                    x_list, y_list, label_height, label_width, gap_size,
                    single_grid_width, single_grid_height
                )

                # Paste into main grid
                x_offset = z_idx * single_grid_width + (z_idx + 1) * gap_size
                y_offset = label_height
                grid_img.paste(z_grid, (x_offset, y_offset))

                # Add Z label at top
                z_label = z_list[z_idx] if z_idx < len(z_list) else f"Z{z_idx}"
                bbox = draw.textbbox((0, 0), z_label, font=font)
                text_width = bbox[2] - bbox[0]
                text_x = x_offset + (single_grid_width - text_width) // 2
                text_y = (label_height - (bbox[3] - bbox[1])) // 2
                draw.text((text_x, text_y), z_label, fill=(255, 255, 255), font=font)

        # Convert back to tensor
        grid_np = np.array(grid_img).astype(np.float32) / 255.0
        grid_tensor = torch.from_numpy(grid_np).unsqueeze(0)

        print(f"[XYZ Grid] Created grid with {len(pil_images)} images ({num_x}x{num_y}x{num_z})")

        return (grid_tensor,)

    def _create_single_grid(self, pil_images, num_x, num_y, img_width, img_height,
                           x_labels, y_labels, label_height, label_width, gap_size, grid_width, grid_height):
        """Create a single 2D grid with labels"""
        grid_img = Image.new('RGB', (grid_width, grid_height), color=(40, 40, 40))
        draw = ImageDraw.Draw(grid_img)

        # Try to load a font (3x larger for visibility)
        try:
            font = ImageFont.truetype("arial.ttf", size=max(48, min(label_height - 4, 96)))
        except:
            try:
                # Try to use a larger default font
                font = ImageFont.truetype("arial.ttf", size=60)
            except:
                font = ImageFont.load_default()

        # Draw X labels (columns) - shifted right by label_width
        for x_idx in range(num_x):
            if x_idx < len(x_labels):
                label = x_labels[x_idx]
                x_pos = label_width + gap_size + x_idx * (img_width + gap_size)
                bbox = draw.textbbox((0, 0), label, font=font)
                text_width = bbox[2] - bbox[0]
                text_x = x_pos + (img_width - text_width) // 2
                text_y = (label_height - (bbox[3] - bbox[1])) // 2
                draw.text((text_x, text_y), label, fill=(255, 255, 255), font=font)

        # Place images and Y labels
        for idx, img in enumerate(pil_images):
            x_idx = idx % num_x
            y_idx = idx // num_x

            if y_idx >= num_y:
                break

            # Images shifted right by label_width
            x_pos = label_width + gap_size + x_idx * (img_width + gap_size)
            y_pos = label_height + gap_size + y_idx * (img_height + gap_size)

            grid_img.paste(img, (x_pos, y_pos))

            # Draw Y label (rows) - only for first column, in the label_width area
            if x_idx == 0 and y_idx < len(y_labels):
                label = y_labels[y_idx]
                # Try to use a larger font for Y labels for better visibility (3x)
                try:
                    y_font = ImageFont.truetype("arial.ttf", size=min(label_width // 2, 72))
                except:
                    y_font = font
                # Draw label in the left margin area
                bbox = draw.textbbox((0, 0), label, font=y_font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                # Center the text in the label_width area
                text_x = max(2, (label_width - text_width) // 2)
                text_y = y_pos + (img_height - text_height) // 2
                # Draw with white color for better visibility
                draw.text((text_x, text_y), label, fill=(255, 255, 255), font=y_font)

        return grid_img

    def _create_a1111_grid(self, pil_images, num_x, num_y, num_z, img_width, img_height,
                          x_labels, y_labels, z_labels, label_height, label_width, gap_size):
        """Create A1111-style grid: Each X value gets a block with Y×Z grid inside"""

        # Load font (3x larger for visibility)
        try:
            font = ImageFont.truetype("arial.ttf", size=max(48, min(label_height - 4, 96)))
            x_label_font = ImageFont.truetype("arial.ttf", size=max(60, min(label_height, 120)))
        except:
            try:
                font = ImageFont.truetype("arial.ttf", size=60)
                x_label_font = font
            except:
                font = ImageFont.load_default()
                x_label_font = font

        # For A1111 style:
        # - Each X value creates a block
        # - Inside each block is a Y×Z grid (Y rows, Z columns)
        # - Blocks are stacked vertically

        # Calculate dimensions for a single block (Y×Z grid)
        block_width = label_width + num_z * img_width + (num_z + 1) * gap_size
        block_height = num_y * img_height + (num_y + 1) * gap_size + label_height

        # Calculate total grid dimensions
        x_label_area = label_height  # Space for the X label on the left of each block
        grid_width = x_label_area + block_width
        grid_height = num_x * block_height + (num_x + 1) * gap_size

        # Create the main canvas
        grid_img = Image.new('RGB', (grid_width, grid_height), color=(40, 40, 40))
        draw = ImageDraw.Draw(grid_img)

        # Create each X block
        images_per_block = num_y * num_z

        for x_idx in range(num_x):
            # Calculate block position
            y_offset = gap_size + x_idx * (block_height + gap_size)
            x_offset = x_label_area

            # Draw X label on the left side of this block
            x_label = x_labels[x_idx] if x_idx < len(x_labels) else f"X{x_idx}"
            bbox = draw.textbbox((0, 0), x_label, font=x_label_font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            # Rotate text 90 degrees for vertical display
            txt_img = Image.new('RGBA', (text_width, text_height), (0, 0, 0, 0))
            txt_draw = ImageDraw.Draw(txt_img)
            txt_draw.text((0, 0), x_label, fill=(255, 255, 255), font=x_label_font)
            txt_img = txt_img.rotate(90, expand=True)
            # Center the label vertically in the block
            label_y = y_offset + (block_height - txt_img.height) // 2
            label_x = (x_label_area - txt_img.width) // 2
            grid_img.paste(txt_img, (label_x, label_y), txt_img)

            # Get images for this X block (all Y×Z combinations)
            start_idx = x_idx * images_per_block
            end_idx = min(start_idx + images_per_block, len(pil_images))
            block_images = pil_images[start_idx:end_idx]

            # Draw Z labels (columns) at the top of this block
            for z_idx in range(num_z):
                if z_idx < len(z_labels):
                    z_label = z_labels[z_idx]
                    img_x_pos = x_offset + label_width + gap_size + z_idx * (img_width + gap_size)
                    bbox = draw.textbbox((0, 0), z_label, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_x = img_x_pos + (img_width - text_width) // 2
                    text_y = y_offset + (label_height - (bbox[3] - bbox[1])) // 2
                    draw.text((text_x, text_y), z_label, fill=(255, 255, 255), font=font)

            # Place images in Y×Z grid
            for img_idx, img in enumerate(block_images):
                z_idx = img_idx % num_z
                y_idx = img_idx // num_z

                if y_idx >= num_y:
                    break

                # Calculate image position
                img_x_pos = x_offset + label_width + gap_size + z_idx * (img_width + gap_size)
                img_y_pos = y_offset + label_height + gap_size + y_idx * (img_height + gap_size)

                grid_img.paste(img, (img_x_pos, img_y_pos))

                # Draw Y label (rows) - only for first column
                if z_idx == 0 and y_idx < len(y_labels):
                    y_label = y_labels[y_idx]
                    try:
                        y_font = ImageFont.truetype("arial.ttf", size=min(label_width // 2, 72))
                    except:
                        y_font = font
                    bbox = draw.textbbox((0, 0), y_label, font=y_font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    text_x = x_offset + max(2, (label_width - text_width) // 2)
                    text_y = img_y_pos + (img_height - text_height) // 2
                    draw.text((text_x, text_y), y_label, fill=(255, 255, 255), font=y_font)

        return grid_img


class XYZGridInputBatch:
    """
    Generates all combinations at once as batch outputs.
    Use this for workflows that support batch processing.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "x_values": ("STRING", {
                    "multiline": True,
                    "default": "red, blue, green",
                    "tooltip": "Comma-separated values for X axis"
                }),
                "y_values": ("STRING", {
                    "multiline": True,
                    "default": "1, 2, 3",
                    "tooltip": "Comma-separated values for Y axis"
                }),
                "z_values": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "tooltip": "Comma-separated values for Z axis (leave empty to disable)"
                }),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "INT")
    RETURN_NAMES = ("x_values_batch", "y_values_batch", "z_values_batch", "total_combinations")
    FUNCTION = "generate_batch"
    CATEGORY = "XYZ Grid"
    OUTPUT_IS_LIST = (True, True, True, False)

    def generate_batch(self, x_values, y_values, z_values):
        # Parse input values
        x_list = [v.strip() for v in x_values.split(",") if v.strip()]
        y_list = [v.strip() for v in y_values.split(",") if v.strip()]
        z_list = [v.strip() for v in z_values.split(",") if v.strip()] if z_values.strip() else [""]

        # Generate all combinations
        combinations = list(itertools.product(x_list, y_list, z_list))
        total = len(combinations)

        if total == 0:
            return ([""], [""], [""], 0)

        # Unzip combinations into separate lists
        x_batch = [combo[0] for combo in combinations]
        y_batch = [combo[1] for combo in combinations]
        z_batch = [combo[2] for combo in combinations]

        print(f"[XYZ Grid Batch] Generated {total} combinations")

        return (x_batch, y_batch, z_batch, total)


class XYZGridIterator:
    """
    Helper node to control iteration through XYZ combinations.
    Outputs the next index automatically.
    """

    def __init__(self):
        self.current_index = 0

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "total_combinations": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 10000,
                }),
                "reset": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Reset index to 0"
                }),
            },
        }

    RETURN_TYPES = ("INT", "BOOLEAN")
    RETURN_NAMES = ("current_index", "is_complete")
    FUNCTION = "iterate"
    CATEGORY = "XYZ Grid"

    def iterate(self, total_combinations, reset):
        if reset:
            self.current_index = 0

        current = self.current_index
        is_complete = current >= total_combinations - 1

        if not is_complete:
            self.current_index += 1
        else:
            self.current_index = 0  # Reset for next run

        print(f"[XYZ Grid Iterator] Index: {current}/{total_combinations - 1}, Complete: {is_complete}")

        return (current, is_complete)


class XYZStringToNumber:
    """
    Converts string values to integers or floats.
    Use this to convert XYZ Grid string outputs to numbers for parameters like steps, CFG, etc.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {
                    "default": "10",
                    "forceInput": True,
                    "tooltip": "String value to convert to number"
                }),
                "output_type": (["INT", "FLOAT"], {
                    "default": "INT",
                    "tooltip": "Convert to integer or float"
                }),
            },
        }

    RETURN_TYPES = ("INT", "FLOAT")
    RETURN_NAMES = ("int_value", "float_value")
    FUNCTION = "convert"
    CATEGORY = "XYZ Grid"

    def convert(self, text, output_type):
        try:
            # Try to convert to number
            if output_type == "INT":
                int_val = int(float(text.strip()))
                float_val = float(int_val)
            else:  # FLOAT
                float_val = float(text.strip())
                int_val = int(float_val)

            return (int_val, float_val)
        except ValueError:
            # If conversion fails, return defaults
            print(f"[XYZ String to Number] Warning: Could not convert '{text}' to number, returning 0")
            return (0, 0.0)


class XYZAutoCollector:
    """
    Automatically collects images and outputs them when all combinations are complete.
    No manual mode switching needed!
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "total_combinations": ("INT", {
                    "default": 9,
                    "forceInput": True,
                    "tooltip": "Connect this to XYZ Grid Input's total_combinations output"
                }),
                "collection_id": ("STRING", {
                    "default": "default",
                    "tooltip": "Unique ID for this collection"
                }),
            },
            "optional": {
                "reset": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Set to True to clear the collection and start over"
                }),
            }
        }

    RETURN_TYPES = ("IMAGE", "INT", "BOOLEAN", "STRING")
    RETURN_NAMES = ("images", "collected_count", "is_complete", "status")
    FUNCTION = "auto_collect"
    CATEGORY = "XYZ Grid"
    OUTPUT_NODE = True

    def auto_collect(self, images, total_combinations, collection_id, reset=False):
        global _image_collections

        # Handle reset
        if reset:
            _image_collections[collection_id] = []
            print(f"[XYZ Auto Collector] Reset collection '{collection_id}'")
            empty = torch.zeros((1, 512, 512, 3))
            return (empty, 0, False, f"Collection reset")

        # Initialize collection if it doesn't exist
        if collection_id not in _image_collections:
            _image_collections[collection_id] = []

        collection = _image_collections[collection_id]
        count_before = len(collection)

        # Add current images to collection
        for img in images:
            collection.append(img.clone())

        count_after = len(collection)
        is_complete = count_after >= total_combinations

        # Automatic output when complete
        if is_complete:
            # Output all collected images
            output_images = torch.stack(collection, dim=0)
            status = f"✓ Complete! Outputting all {count_after} images to grid"
            print(f"[XYZ Auto Collector] {status}")

            # Auto-reset for next run
            _image_collections[collection_id] = []

            return (output_images, count_after, True, status)
        else:
            # Still collecting
            status = f"Collecting... {count_after}/{total_combinations}"
            print(f"[XYZ Auto Collector] {status}")

            # Return a small placeholder image (1x1 black pixel) to avoid triggering save nodes
            # This prevents individual images from being saved during collection
            placeholder = torch.zeros((1, 1, 1, 3))
            return (placeholder, count_after, False, status)


class XYZImageCollector:
    """
    Manual image collector with mode control.
    For advanced users who need fine control.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "collection_id": ("STRING", {
                    "default": "default",
                    "tooltip": "Unique ID for this collection (use same ID for related images)"
                }),
                "mode": (["collect", "output_and_reset", "output_only", "reset_only"], {
                    "default": "collect",
                    "tooltip": "collect: add to collection | output_and_reset: output all and clear | output_only: output without clearing | reset_only: clear collection"
                }),
                "expected_count": ("INT", {
                    "default": 9,
                    "min": 1,
                    "max": 10000,
                    "tooltip": "Expected number of images (for tracking progress)"
                }),
            },
        }

    RETURN_TYPES = ("IMAGE", "INT", "BOOLEAN", "STRING")
    RETURN_NAMES = ("images", "collected_count", "is_complete", "status")
    FUNCTION = "collect_images"
    CATEGORY = "XYZ Grid"
    OUTPUT_NODE = True

    def collect_images(self, images, collection_id, mode, expected_count):
        global _image_collections

        # Initialize collection if it doesn't exist
        if collection_id not in _image_collections:
            _image_collections[collection_id] = []

        collection = _image_collections[collection_id]

        # Handle different modes
        if mode == "reset_only":
            _image_collections[collection_id] = []
            print(f"[XYZ Image Collector] Reset collection '{collection_id}'")
            empty = torch.zeros((1, 512, 512, 3))
            return (empty, 0, False, f"Collection '{collection_id}' reset")

        elif mode == "collect":
            # Add current images to collection
            for img in images:
                collection.append(img.clone())

            count = len(collection)
            is_complete = count >= expected_count

            status = f"Collected {count}/{expected_count} images"
            if is_complete:
                status += " - READY TO OUTPUT"

            print(f"[XYZ Image Collector] {status}")

            # Return the current batch for preview (not the full collection)
            return (images, count, is_complete, status)

        elif mode in ["output_and_reset", "output_only"]:
            # Output all collected images
            if len(collection) == 0:
                print(f"[XYZ Image Collector] Warning: Collection '{collection_id}' is empty!")
                empty = torch.zeros((1, 512, 512, 3))
                return (empty, 0, False, f"Collection '{collection_id}' is empty")

            # Stack all images into a batch
            output_images = torch.stack(collection, dim=0)
            count = len(collection)

            status = f"Output {count} images"

            if mode == "output_and_reset":
                _image_collections[collection_id] = []
                status += " and reset collection"

            print(f"[XYZ Image Collector] {status}")

            return (output_images, count, True, status)

        # Fallback
        return (images, 0, False, "Unknown mode")


# Node class mappings for ComfyUI
NODE_CLASS_MAPPINGS = {
    "XYZGridInput": XYZGridInput,
    "XYZGridInputBatch": XYZGridInputBatch,
    "XYZGridStitch": XYZGridStitch,
    "XYZGridIterator": XYZGridIterator,
    "XYZStringToNumber": XYZStringToNumber,
    "XYZAutoCollector": XYZAutoCollector,
    "XYZImageCollector": XYZImageCollector,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "XYZGridInput": "XYZ Grid Input",
    "XYZGridInputBatch": "XYZ Grid Input (Batch)",
    "XYZGridStitch": "XYZ Grid Stitch",
    "XYZGridIterator": "XYZ Grid Iterator",
    "XYZStringToNumber": "XYZ String to Number",
    "XYZAutoCollector": "XYZ Auto Collector",
    "XYZImageCollector": "XYZ Image Collector (Manual)",
}
