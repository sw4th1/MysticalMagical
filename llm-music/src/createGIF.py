from PIL import Image
import glob

def create_gif(image_folder, output_gif_path, duration=100, loop=0):
    """
    Creates an animated GIF from images in a specified folder.

    Args:
        image_folder (str): The path to the folder containing the images.
        output_gif_path (str): The desired path and filename for the output GIF.
        duration (int): The duration (in milliseconds) each frame is displayed.
                        Default is 100ms.
        loop (int): The number of times the GIF should loop. 0 means infinite loop.
                    Default is 0.
    """
    image_paths = sorted(glob.glob(f"{image_folder}/*")) # Get all image files in order
    if not image_paths:
        print(f"No images found in {image_folder}")
        return

    images = [Image.open(path) for path in image_paths]

    # Save as GIF
    images[0].save(
        output_gif_path,
        save_all=True,
        append_images=images[1:],
        duration=duration,
        loop=loop
    )
    print(f"GIF successfully created at: {output_gif_path}")

if __name__ == "__main__":
    # Example usage:
    # Replace 'path/to/your/images' with the actual path to your image folder
    image_folder_path = "Images/slider"
    output_filename = "animated_slider.gif"

    create_gif(image_folder_path, output_filename, duration=150, loop=0)