#!/usr/bin/env python3

import subprocess, os
from itertools import count

def createVideo(inputPath, numberOfZeroes, framerate, width, height, outputPath):
    """
    Creates a (new) video file from the given images with the given framerate and resolution.
    The inputPath should point to a directory with multiple images.
    """
    command = ('ffmpeg' +                                       # Using ffmpeg
               ' -f image2' +                                   # Demuxer type (image2 -> Image file demuxer)
               f' -framerate {framerate}' +                     # Sets framerate (how long each image stays)
               f' -i ./{inputPath}/%{numberOfZeroes}d.jpg' +    # Path to the images
               ' -hide_banner' +                                # Hide printouts
               ' -loglevel error' +                             # Only show errors
               ' -vcodec mpeg4'
               ' -crf 0' +                                      # Constant rate factor (0-51 with 23 being default and 0 being lossless)
               f' -vf "scale={width}:{height}:' +               # Sets the input dimension (needed for padding)
               'force_original_aspect_ratio=1,' +               # Forces original aspect ratio of image (requires padding)
               f'pad={width}:{height}:(ow-iw)/2:(oh-ih)/2"' +   # Pads the video to fit 1920x1080 with black borders
               f' {outputPath}'                                 # Location and name for output file
               )

    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as processError:
        print(processError.stderr)
        return False
    else:
        return True

def extendVideo(videoPath, imagePath, duration):
    command = ('ffmpeg' +
                f' -i ./{videoPath}' +
                ' -loop 1' +
                f' -t {duration}' +
                f' -i ./{imagePath}' +
                ' -f lavfi' +
                f' -t {duration}' +
                ' -i annullsrc' +           # Add empty audio (needed for concatenation)
                ' -filter_complex "[0:v] [0:a] [1:v] [2:a] concat=n=2:v=1:a=1 [v] [a]"' +
                ' -c:v libx264' +
                ' -c:a aac' +
                ' -crf 0' +
                ' -strict' +
                ' -2 -map "[v]" -map "[a]"' +
                ' output.mp4'
            )
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as processError:
        print(processError.stderr)
        return False
    else:
        return True
    
def indexFiles(path, numberOfZeroes = 3):
    """
    Indexes all files in the provided directory
    """
    files = os.listdir(path)
    _, file_extension = os.path.splitext(os.path.join(path, files[0]))

    for index, file in enumerate(files):
        os.rename(os.path.join(path, file), os.path.join(path, "%0{}i".format(numberOfZeroes) % (index + 1) + file_extension))