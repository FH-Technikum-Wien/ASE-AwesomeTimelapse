#!/usr/bin/env python3

import pika
import sys, os, time
import urllib.request
import shutil
import requests

import ffmpeg, constants

def main():
    # Create needed folders if non-existing
    if not os.path.exists(constants.TEMP_FOLDER):
        os.mkdir(constants.TEMP_FOLDER)
    if not os.path.exists(constants.IMAGE_FOLDER):
        os.mkdir(constants.IMAGE_FOLDER)
    if not os.path.exists(constants.VIDEO_FOLDER):
        os.mkdir(constants.VIDEO_FOLDER)
    if not os.path.exists(constants.OUTPUT_FOLDER):
        os.mkdir(constants.OUTPUT_FOLDER)

    connection = pika.BlockingConnection(pika.ConnectionParameters(host=constants.HOST_NAME, port=constants.HOST_PORT))
    channel = connection.channel()
    # Create queue for receiving messages. Needs to be used by the sender.
    channel.queue_declare(queue=constants.QUEUE_NAME)
    print("[*] Waiting for messages.")

    # Define from which queue we should receive callbacks
    channel.basic_consume(queue=constants.QUEUE_NAME, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()


def callback(ch, method, properties, body):
    message = str(body.decode()).split(constants.REQUEST_SEPARATOR)
    imageID = message[0]
    videoID = message[1]

    # Name of the generated video file with the wanted file extension
    videoFile = videoID + constants.VIDEO_EXTENSION

    # Download video and image
    downloadImage(imageID)
    (videoDownloaded, videoName) = downloadVideo(videoID)

    imagePath = constants.IMAGE_FOLDER + (os.listdir(constants.IMAGE_FOLDER)[0])
    outputPath = constants.OUTPUT_FOLDER + videoFile
    # Either append to video or create a new video
    if videoDownloaded:
        print("[*] Appending to video...")
        videoPath = constants.VIDEO_FOLDER + videoFile
        success = ffmpeg.appendToVideo(videoPath, imagePath, outputPath)
    else:
        print("[*] Creating video...")
        success = ffmpeg.createVideo(imagePath, outputPath)

    if not success:
        print("[X] Couldn't generate video!\n")
        exit(1)

    # Upload video to API
    success = updateVideo(videoFile, videoID, videoName)

    if not success:
        print("[X] Couldn't update file in API!\n")
        exit(1)    

    # Empty temp folders after completion
    shutil.rmtree(constants.TEMP_FOLDER)
    os.mkdir(constants.TEMP_FOLDER)
    os.mkdir(constants.IMAGE_FOLDER)
    os.mkdir(constants.VIDEO_FOLDER)
    os.mkdir(constants.OUTPUT_FOLDER)

    print("[>] Completed!\n")
    print("[*] Waiting for messages.")            

def downloadImage(imageID):
    """ Downloads the image with the given ID to the 'temp/images' folder. 
    Arguments:
    imageID -- The ID of the image in the API (>0)     
    """

    # Get image obj from API
    response = requests.get(constants.IMAGE_ADDRESS + imageID)
    # Extract needed data (link to image)
    data = response.json()[constants.IMAGE_PROPERTY_DATA]
    # Download image to temp
    urllib.request.urlretrieve(data, constants.IMAGE_FOLDER + imageID + constants.IMAGE_EXTENSION)


def downloadVideo(videoID):
    """ Downloads the video with the given ID to the 'temp/videos' folder.\n
    Arguments:\n
    videoID -- The ID of the video in the API (>0)   
    \n
    Returns:\n
    (Bool, videoName) -- Whether a video was downloaded | The videoName of the video instance
    """
    # Get video obj from API
    response = requests.get(constants.VIDEO_ADDRESS + videoID)
    # Extract needed data (link to video)
    data = response.json()[constants.VIDEO_PROPERTY_DATA]
    name = response.json()[constants.VIDEO_PROPERTY_NAME]
    # Skip download if no video link is available
    if data == None:
        return (False, name)
    urllib.request.urlretrieve(data, constants.VIDEO_FOLDER + videoID + constants.VIDEO_EXTENSION)
    
    return (True, name)

def updateVideo(videoFile, videoID, videoName):
    """
    Updates the video instance in the API with the given videoFile and videoName.
    The videoName should be the same as the downloaded video instance from the API.\n
    Arguments:\n
    videoFile -- Name of the video to be uploaded.\n
    videoID -- ID of the video instance to be updated.\n
    videoName -- Name of the video instance (not the video itself).\n
    Returns true, if the status code returned from the API is 200.
    """
    files = {constants.VIDEO_PROPERTY_DATA: open(constants.OUTPUT_FOLDER + videoFile, 'rb')}
    payload = {constants.VIDEO_PROPERTY_NAME: videoName}
    videoUrl = constants.VIDEO_ADDRESS + videoID + "/"
    response = requests.request("PUT", videoUrl, files=files, data=payload)
    return response.status_code == 200


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('[X] Interrupted!')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)