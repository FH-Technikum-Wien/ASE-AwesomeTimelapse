# "BACKEND" aka. VideoBuilderWorker
- Uses a RabbitMQ to receive requests from the Frontend.
- A request must contain the imageID and the videoID in the following pattern:
    - \<imageID\>-\<videoID\>
- Creates/Extends video with given image
