#!/usr/bin/env python3

import subprocess, os
from itertools import count
import constants

def createVideo(imagePath, outputPath):
    """
    Creates a (new) video file from the given images with the given framerate and resolution.
    The inputPath should point to a directory with multiple images.
    """
    command = ('ffmpeg' +                                                                       # Using ffmpeg
                ' -f image2' +                                                                  # Demuxer type (image2 -> Image file demuxer)
                ' -loop 1'                                                                      # Loops the image to create a video
                f' -t {constants.VIDEO_IMAGE_DURATION}' +                                       # Sets duration of the image
                f' -i ./{imagePath}' +                                                          # Path to the images
                ' -c:v libx264' +                                                               # Better encoder than default
                ' -crf 0' +                                                                     # Constant rate factor (0-51 with 23 being default and 0 being lossless)
                f' -vf "scale={constants.VIDEO_WIDTH}:{constants.VIDEO_HEIGHT}:' +              # Sets the input dimension (needed for padding)
                'force_original_aspect_ratio=1,' +                                              # Forces original aspect ratio of image (requires padding)
                f'pad={constants.VIDEO_WIDTH}:{constants.VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2"' +  # Pads the video to fit 1920x1080 with black borders
                ' -hide_banner' +                                                               # Hide printouts
                ' -loglevel error' +                                                            # Only show errors
                f' {outputPath}'                                                                # Location and name for output file
                )

    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as processError:
        print(processError.stderr)
        return False
    else:
        return True

def appendToVideo(videoPath, imagePath, outputPath):
command = ('ffmpeg' +                                                                               # Using ffmpeg
                f' -i ./{videoPath}' +                                                              # Video to append image to
                ' -f image2' +                                                                      # Demuxer type for image to append
                ' -loop 1' +                                                                        # Loop image to create video
                f' -t {constants.VIDEO_IMAGE_DURATION}' +                                           # Duration of image as video
                f' -i ./{imagePath}' +                                                              # Image to append
                ' -c:v libx264' +                                                                   # Encoder for image to video
                ' -crf 0' +                                                                         # Lossless
                f' -filter_complex "' +                                                             # Filter for appending
                    f'[0]scale={constants.VIDEO_WIDTH}:{constants.VIDEO_HEIGHT}:' +                 # Set scale for video
                    'force_original_aspect_ratio=decrease,' +                                       # Force aspect ratio to decrease
                    f'pad={constants.VIDEO_WIDTH}:{constants.VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2,' +  # Add pad for keeping aspect ratio
                    f'setsar=1[im];' +                                                              
                    f'[1]scale={constants.VIDEO_WIDTH}:{constants.VIDEO_HEIGHT}:' +                 # Set scale for image
                    'force_original_aspect_ratio=decrease,' +                                       # Foce aspect ratio to decrease
                    f'pad={constants.VIDEO_WIDTH}:{constants.VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2,' +  # Add pad for keeping aspect ratio
                    'setsar=1[vid];[im][vid]concat=n=2:v=1:a=0"' +                                  
                ' -hide_banner' +                                                                   # Hide printouts
                ' -loglevel error' +                                                                # Only show errors
                f' {outputPath}'
            )
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as processError:
        print(processError.stderr)
        return False
    else:
        return True