#!/usr/bin/env python3

import pika
import sys, os, time
import urllib.request
import shutil
import requests

import ffmpeg, constants

def main():
    # Create needed folders if non-existing
    if not os.path.exists("temp"):
        os.mkdir("temp")

    if not os.path.exists(constants.IMAGE_FOLDER):
        os.mkdir(constants.IMAGE_FOLDER)

    if not os.path.exists(constants.VIDEO_FOLDER):
        os.mkdir(constants.VIDEO_FOLDER)

    if not os.path.exists(constants.OUTPUT_FOLDER):
        os.mkdir(constants.OUTPUT_FOLDER)

    connection = pika.BlockingConnection(pika.ConnectionParameters(host=constants.HOST_NAME))
    channel = connection.channel()
    # Create queue for receiving messages. Needs to be used by the sender.
    channel.queue_declare(queue=constants.QUEUE_NAME)
    print(" [*] Waiting for messages.")

    # Define from which queue we should receive callbacks
    channel.basic_consume(queue=constants.QUEUE_NAME, on_message_callback=callback)
    channel.start_consuming()


def callback(ch, method, properties, body):
    message = str(body.decode()).split('-')
    imageID = message[0]
    videoID = message[1]

    # Download video and image
    downloadImage(imageID)
    downloadVideo(videoID)

    print("Creating video...")
    # Create video from image(s). TODO: Change to appending of image to video
    success = ffmpeg.createVideo(constants.IMAGE_FOLDER, 4, 3, 1920, 1080, f"{constants.OUTPUT_FOLDER}/{videoID}.avi")
    # Empty image folder after video generation
    shutil.rmtree(constants.IMAGE_FOLDER)
    os.mkdir(constants.IMAGE_FOLDER)

    if not success:
        print("Couldn't create video!\n")
        exit(1)

    # Upload video to API
    success = updateVideo(videoID, videoID, "Test")
    # Empty video folder after upload
    shutil.rmtree(constants.VIDEO_FOLDER)
    os.mkdir(constants.VIDEO_FOLDER)

    if not success:
        print("Couldn't upload file!\n")
        exit(1)

    print("Completed!\n")
    print(" [*] Waiting for messages.")
    # Send acknowledgement of completion.
    ch.basic_ack(delivery_tag = method.delivery_tag)
            

def downloadImage(imageID):
    """ Downloads the image with the given ID to the 'temp/images' folder. 
    Arguments:
    imageID -- The ID of the image in the API (>0)     
    """

    imageUrl = constants.DOWNLOAD_IMAGE_ADDRESS + imageID
    urllib.request.urlretrieve(imageUrl, f"{constants.IMAGE_FOLDER}/{imageID}")

def downloadVideo(videoID):
    """ Downloads the video with the given ID to the 'temp/videos' folder. 
    Arguments:
    videoID -- The ID of the video in the API (>0)     
    """

    videoUrl = f"{constants.DOWNLOAD_VIDEO_ADDRESS}/{videoID}" 
    urllib.request.urlretrieve(videoUrl, f"{constants.VIDEO_FOLDER}/{videoID}")

def updateVideo(videoFile, videoID, videoName):
    video = open(f"{constants.OUTPUT_FOLDER}/{videoFile}", 'rb')
    payload = {'name': videoName, 'data': video}
    response = requests.put(f"{constants.VIDEO_ADDRESS}/{videoID}", data=payload)
    return response.status_code == 201


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)