// restart docker containers with
// docker-compose -f docker-compose.yaml up --build

const express = require('express'); // nodejs express web server
const fs = require('fs'); // filestream
const unirest = require('unirest'); // another option for sending post requests
const amqp = require('amqplib/callback_api'); // rabbitmq api

const app = express();
const path = __dirname + '/';

const QUEUE_NAME = process.env.QUEUE_NAME
const HOST_NAME = process.env.QUEUE_IP
const URL = 'http://' + process.env.REST_IP + ':8000'
//const HOST_PORT = 5672
const TMPFILE = 'upload.png';

var rabbitmqChannel = null;
var lastVideoId = 0; // TODO: evaluate from xmlhttp request per name

app.use(express.static(path)); // allows serving static files
app.use(express.json({ limit: '10mb' })); // to support JSON-encoded bodies, limit to prevent error 413: Payload too large
//app.use(express.urlencoded({ extended: true })); // to support URL-encoded bodies

/* not needed if static files are allowed
app.get('/', function(req, res){
    res.sendFile(path + 'index.html');
});*/

app.get('/video', function(req, res) {

    console.log("app get /video...");

    // set video src="path" by <source src="http://localhost:port/video.mp4" type="video/mp4">
    // or embed otherwise (read stream and parse video, stream from source, ...)
    unirest
    .get(URL + '/videos/' + lastVideoId + '/')
    .then(function (response) {

        console.log("get videoId response:");
        console.log(response.body);

        // attempt 1: just return video from resource -> TypeError: path must be absolute or specify root to res.sendFile
        //res.sendFile(response.body.data);

        // attempt 3: write back embedded html
        var html = '<video controls width="640" height="480">' +
                //'<source src="' + response.body.data + '" type="video/mp4">' +
                '<source src="' +
                    ((response.body.data) ? response.body.data.replace('django', 'localhost') : '') +
                '" type="video/mp4">' +
                'Sorry, your browser does not support embedded videos.' +
            '</video>'
        res.writeHead(200, {
            'Content-Type': 'text/html',
            'Content-Length': html.length,
            'Expires': new Date().toUTCString()
        });
        res.end(html);

        // attempt 2: read binary data from resource and propagate back
        /*
        unirest
        .get(response.body.data) // http://django:8000/upload/videos/4_FelgOQ4.mp4
        .then(function (response) {

            // they both are the same
            //console.log("get video response:");
            //console.log(response.body);
            //console.log("raw response:");
            //console.log(response.raw_body);

            // maybe remove null?
            // maybe use data?
            // maybe use binary?
            //fs.writeFileSync('video.mp4', response.raw_body, null, function(err) {
            //fs.writeFileSync('video.mp4', response.body, function(err) {
            //fs.writeFileSync('video.mp4', response.body, 'binary', function(err) {
            fs.writeFileSync('video.mp4', response.raw_body, 'binary', function(err) {
                console.log(err);
            });
            res.sendFile(path + 'video.mp4');

        })
        .catch(error => {
            console.log(error);
            if (error.response.data) console.log(error.response.data);
        });
        */
    })
    .catch(error => {
        console.log(error);
        if (error.response.data) console.log(error.response.data);
    });

    // Error: Can't set headers after they are sent.
    //res.sendFile(path + 'video.html');
});

app.post('/images', function(req, res) {

    console.log("app post /images...");

    // save uploaded image data to local file
    //console.log("body: " + JSON.stringify(req.body)); // body: {"name": "videoname", "data":"data:image/png;base64,iVBORw0KGgoAAAA....
    let payload = decodeBase64Image(req.body.data); // removes html tags and +, prepends type

    const filename = TMPFILE;
    const videoname = req.body.name;

    //console.log("payload: ", payload); // payload: { type: 'image/png', data: <Buffer 89 50 ... > }

    fs.writeFileSync(filename, payload.data, function(error) {
        if (error) {
            console.log('error writing file!', error);
        }
        else {
            console.log('File created');
        }
    });

    unirest
    .post(URL + '/images/')
    //.headers({'Content-Type': 'multipart/form-data'}) // not needed
    .attach('data', filename) // reads directly from local file
    //.attach('data',  fs.createReadStream(filename)) // creates a read stream
    .then(function (response) {

        console.log("img upload response: ", response.body);

        let imgId = response.body.id;
        if (imgId === null) {
            throw "could not upload image!";
        }

        // get id for video name
        unirest
        .get(URL + '/videos/')
        .query({ name: videoname })
        .then(function (response) {

            console.log("get video response:");
            console.log(response.body);

            if (response.body.length > 0) {

                sendToRabbitMQ(imgId, response.body[0].id); // response is an array!
            }
            // create new video if does not exist
            else {

                console.log("no video found for name: " + videoname + " -> creating a new one...");

                unirest
                .post(URL + '/videos/')
                .send({
                    name: videoname,
                    data: null
                })
                .then(function (response) {

                    console.log("get video creation response:");
                    console.log(response.body);

                    sendToRabbitMQ(imgId, response.body.id);
                })
                .catch((error) => console.log(error.response.data));
            }
        })
        .catch((error) => console.log(error.response.data));
    })
    .catch((error) => console.log(error.response.data));

    res.send("shit's workin"); // sends data back
});

app.listen(8080, function () {

    console.log('Server is listening on port 8080...')
});

//initRabbitMQ(); // -> tries to connect before queue is started -> delay initialization
delayedInitRabbitMQ();

function delayedInitRabbitMQ () {
    setTimeout(function() {
        initRabbitMQ();
    }, 5000);
}

function initRabbitMQ () {

    console.log('initializing RabbidMQ...')

    try {

        amqp.connect('amqp://' + HOST_NAME, function(error, connection) {
            if (error) {
                console.log("initRabbitMQ error: ", error);
                delayedInitRabbitMQ(); // try to restart the queue connection if failed
                return;
            }

            connection.createChannel(function(error, channel) {
                if (error) {
                    throw error;
                }

                channel.assertQueue(QUEUE_NAME, {
                    durable: false
                });

                rabbitmqChannel = channel;
                console.log('created RabbidMQ channel')
            });
        });
    }
    catch (error) {

        console.log('initRabbitMQ error: ', error);
        delayedInitRabbitMQ(); // try to restart the queue connection if failed
    }
}

function sendToRabbitMQ (imgId, vidId) {

    if (!rabbitmqChannel) {
        console.log('no channel created yet! (or died)...')
        return;
    }

    // backup last requested videoId to show on extra page
    // TODO: replace videoId with name, given from XMLHttpRequest
    lastVideoId = vidId;

    try {
        console.log('Send to RabbitMQ...')
        var msg = imgId + '-' + vidId;
        rabbitmqChannel.sendToQueue(QUEUE_NAME, Buffer.from(msg));
        console.log(" [x] Sent to queue: %s", msg);
    } 
    catch (error) {
        console.log('sendToRabbitMQ error: ', error);
    }
}

function decodeBase64Image (dataString) {

    var matches = dataString.match(/^data:([A-Za-z-+\/]+);base64,(.+)$/), response = {};
    if (matches.length !== 3) {
        return new Error('Invalid input string');
    }

    response.type = matches[1];
    response.data = Buffer.from(matches[2], 'base64');
    return response;
}

function encodeVideo () {
    /*
    let req = response.request;

    var path = response.body.data;
    var stat = fs.statSync(path);
    var total = stat.size;
    if (req.headers['range']) {
        var range = req.headers.range;
        var parts = range.replace(/bytes=/, "").split("-");
        var partialstart = parts[0];
        var partialend = parts[1];

        var start = parseInt(partialstart, 10);
        var end = partialend ? parseInt(partialend, 10) : total-1;
        var chunksize = (end-start)+1;
        console.log('RANGE: ' + start + ' - ' + end + ' = ' + chunksize);

        var file = fs.createReadStream(path, {start: start, end: end});
        res.writeHead(206, { 'Content-Range': 'bytes ' + start + '-' + end + '/' + total, 'Accept-Ranges': 'bytes', 'Content-Length': chunksize, 'Content-Type': 'video/mp4' });
        file.pipe(res);
    } else {
        console.log('ALL: ' + total);
        res.writeHead(200, { 'Content-Length': total, 'Content-Type': 'video/mp4' });
        fs.createReadStream(path).pipe(res);
    }
    */
}
