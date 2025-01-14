
################################################################################
# KMC Image Compression                                                        #
#   Compresses BMP images by downsampling them to 16 colors with the KMeans    #
#   algorithm. KMeans identifies the `k` most representative colors, which are #
#   the centroid values (an RBG value) and replaces every 24-bit pixel with a  #
#   4-bit centroid index. To load an image, the algorithm works in reverse and #
#   replaces each 4-bit index with the 24-bit RGB value of its centroid.       #
#                                                                              #
#   file:   kmcimage.py                                                        #
#   author: prof-tallman                                                       #
#                                                                              #
# Acknowledgements:                                                            #
#   Imad Dabbura - https://medium.com/towards-data-science/                    #
#                  k-means-clustering-algorithm-applications-evaluation-       #
#                  methods-and-drawbacks-aa03e644b48a                          #
################################################################################



################################################################################
#                                   IMPORTS                                    #
################################################################################

import os.path
import argparse
import numpy as np
from typing import Tuple
from sklearn.cluster import KMeans
from matplotlib.image import imread
import matplotlib.pyplot as plt



################################################################################
#                                   MODULE                                     #
################################################################################

def convert_to_kmc16(image:np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """ 
    Compresses picture images using KMeans by reducing the total number of
    colors to 16 colors. 
    Parameters:
        image: 2D np.ndarray, of RGB pixels arranged width x height
    Returns:
        Tuple[np.ndarray, np.ndarray]: a palette of RGB colors and a 2D lookup array using the original image dimensions and referencing the RGB palette.

    Note: This is a lossy compression algorithm.
    """

    if not isinstance(image, np.ndarray):
        raise ValueError(f"Parameter image must be a numpy array")

    height, width, depth = image.shape
    X = image.reshape(width * height, depth)

    km = KMeans(n_clusters=16, n_init='auto')
    km.fit(X)
    pixels = km.labels_.astype(np.uint8)
    palette = np.round(km.cluster_centers_, 0).astype(np.uint8)
    return (palette, pixels)

def convert_from_kmc16(colors:np.ndarray, pixels:np.ndarray) -> np.ndarray:
    """ 
    Converts a KMeans Compressed image back to an RGB image that can be
    processed like any other BMP image file. 
    Parameters:
        Colors (palette): np.ndarray, of 16 RGB colors
        Pixels: np.ndarray, of indices into the palette array
    Returns:
        2D np.ndarray: of RGB values similar to matplotlib.image.imread()
    """

    if not isinstance(colors, np.ndarray):
        raise ValueError(f"Parameter colors must be a numpy array")
    if not isinstance(pixels, np.ndarray):
        raise ValueError(f"Parameter pixels must be a numpy array")

    compressed_image = colors[pixels]
    compressed_image = compressed_image.reshape(pixels.shape[0], pixels.shape[1], 3)

    return compressed_image


def save_kmc_image(colors:np.ndarray, pixels:np.ndarray, filename:str) -> None:
    """
    Saves a compressed image to disk using the KMC file format:
     * 4 byte header 'KMC:'
     * 2 byte unsigned integer width
     * 2 byte unsigned integer height
     * 16x 3 byte RGB color palette
     * Pixel byte pairs; high nibble is first pixel, low nibble is second
    """
    if not isinstance(pixels, np.ndarray):
        raise ValueError(f"Parameter pixels must be a numpy array")
    if not isinstance(colors, np.ndarray):
        raise ValueError(f"Parameter colors must be a numpy array")

    with open(f'{filename}.bmp.kmc', 'w') as file:
        file.write('KMC:') # file type header
        # file.write(len(colors)) # number of colors in palette
        file.write(pixels.shape[0]) # width
        file.write(pixels.shape[1]) # height
        file.write(colors) # palette
        file.write(pixels) # pixels


def load_kmc_image(filename:str) -> Tuple[np.ndarray, np.ndarray]:
    """ 
    Reads a compressed image from disk according to the KMC file format:
     * 4 byte header 'KMC:'
     * 2 byte unsigned integer width
     * 2 byte unsigned integer height
     * 16x 3 byte RGB color palette
     * Pixel byte pairs; high nibble is first pixel, low nibble is second
    
    Returns:
        Tuple[np.ndarray, np.ndarray]: a palette of RGB colors and a 2D lookup array using the original image dimensions and referencing the RGB palette.
    """

    with open(filename, 'rb') as file:
        header = file.read(4)
        print(header)
        if header != b'KMC:':
            raise ValueError(f"Invalid file header: {header}")

        width = file.read(2)
        height = file.read(2)

        print(width, height)
        print(int(width))

        # colors = np.zeros((16, 3), dtype=np.uint8)
        pixels = np.zeros((int(width, 2), int(height, 2)), dtype=np.uint8)

        print(pixels)

        color_bits = file.read(16*3) # color palette bits
        for i in range(color_bits):
            colors[i] = color_bits[i]
        colors = np.array(file.read(16*3)) # color palette bits
        pixels = np.array(file.read()) # pixel bits
        print(colors, pixels)
    return (colors, pixels)


################################################################################
#                               MAIN PROGRAM                                   #
################################################################################

if __name__ == '__main__':
    
    load_kmc_image('hershey.bmp.kmc')

    parser = argparse.ArgumentParser(description='Compress images with the KMeans Clustering format')
    parser.add_argument("action", choices=["load", "save"], help="Action to perform: 'load' or 'save'.")
    parser.add_argument("filename", help="The name of the file to load or save.")
    args = parser.parse_args()

    if not os.path.exists(args.filename) or not os.path.isfile(args.filename):
        print("Error: '{args.filename}' is not a valid file")
        exit()

    try:
        if args.action == 'save':
            src_filename = args.filename
            dst_filename = f'{src_filename}.kmc'
            color_count = 16
            palette_shape = (4, 4)
            raw_image = imread(src_filename)
            colors, pixels = convert_to_kmc16(raw_image)
            save_kmc_image(colors, pixels, dst_filename)
            kmc_image = convert_from_kmc16(colors, pixels)

            # Demo Purposes: two images to display, the before & after images
            fig, ax = plt.subplots(1, 2)
            ax[0].set_title('Original Image')
            ax[0].imshow(raw_image)
            ax[0].axis('off')
            ax[1].set_title('KMC Compressed Image')
            ax[1].imshow(kmc_image)
            ax[1].axis('off')
            plt.tight_layout()

        elif args.action == 'load':
            colors, pixels = load_kmc_image(args.filename)
            raw_image = convert_from_kmc16(colors, pixels)
            palette_shape = (4, 4)
            color_count = len(colors)
            src_filename = args.filename
            dst_filename = src_filename[:-4]

            # Demo Purposes: only one image to display, the KMC image
            plt.figure()
            plt.title('KMC Compressed Image')
            plt.imshow(raw_image)
            plt.axis('off')
            plt.tight_layout()

        else:
            print(f"Error: action {args.action} must be 'load' or 'save'")
            exit()

        # Demo Purposes: show the color palette
        color_blocks = [np.full([100, 100, 3], color) for color in colors]
        rows, cols = palette_shape
        fig, ax = plt.subplots(rows, cols, figsize=(cols, rows))
        for i in range(rows):
            for j in range(cols):
                ax[i][j].axis('off')
                color_index = i*cols + j
                ax[i][j].imshow(color_blocks[color_index])

        # Output the compression results
        original_size = os.path.getsize(src_filename)
        compressed_size = os.path.getsize(dst_filename)
        print(f"  Original Size: {original_size:>11,} bytes")
        print(f"Compressed Size: {compressed_size:>11,} bytes")

        plt.show()

    except Exception as e:
        print(f"Error: {e}")


################################################################################
#                               END OF PROGRAM                                 #
################################################################################
