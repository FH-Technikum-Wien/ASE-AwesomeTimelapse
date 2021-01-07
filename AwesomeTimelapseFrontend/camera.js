// fires after all assets are loaded; replaced document.onload
window.onload = function () {

    console.log("accessing camera device...");

    // check if camera devices are available
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {

        var video = document.getElementById('video');
        var debugMode = true;

        // check if access to the camera device is allowed
        console.log("getting camera access...");
        navigator.mediaDevices.getUserMedia({ video: true }).then(
        function (stream) {
            video.srcObject = stream;
            video.play();
            setDeviceDivDisplay(true);
        },
        function (error) {
            console.log("error initializing camera devices!", error);
            setDeviceDivDisplay(debugMode);
        });
        
        // elements for taking the image
        var canvas = document.getElementById('canvas');
        var context = canvas.getContext('2d');
        document.getElementById("btnSnap").addEventListener("click", function() {
            takePhoto(context, video);
        });

        // input for video name
        var textVideo = document.getElementById("txtVideo");
        textVideo.addEventListener("input", function() {
            btnUpload.disabled = (textVideo.value.length < 1);
        });

        // button to upload image on server
        var btnUpload = document.getElementById("btnUpload");
        btnUpload.disabled = (textVideo.value.length < 1);
        btnUpload.addEventListener("click", function() {
            convertCanvasToImage(canvas);
        });

        // -- TEST just send local image to Django --
        var btnTest = document.getElementById("test");
        if (btnTest) {
            btnTest.addEventListener("click", function() {
                postLocalImage();
            });
        }
    }
    else {
        console.log("no mediaDevices present!");
    }
}

function setDeviceDivDisplay (value) {

    document.getElementById('warnNoDevice').style.display = value ? "none" : "block";
    document.getElementById('divDevice').style.display = value ? "block" : "none";
}

// take a snapshot of the current video stream
// uses input params vor canvas context and video element
function takePhoto (context, video) {

    console.log("taking photo with context and video...");
    context.drawImage(video, 0, 0, 640, 480);

    // enable further processing...
    document.getElementById('divImg').style.display = "block";
}

// converts the currently displayed snapshot to an image
// an uploads it to the webserver
function convertCanvasToImage (canvas) {

    console.log("uploading image to server...");

    // create image from data
    //var img = new Image();
    //img.src = canvas.toDataURL("image/png");

    var data = canvas.toDataURL("image/png");
    sendPost(data);

    // create image as blob and download per link
    /*canvas.toBlob(function(blob) {

        // create a downloadable anchor
        var a = document.createElement("a"), url = URL.createObjectURL(blob);
        console.log("url: " + url);
        document.body.appendChild(a);
        a.style = "display: none";
        a.href = url;
        a.download = "snapshot.png";
        a.click();
        a.remove();
        URL.revokeObjectURL(url);
    });*/
}

// send a post request with the new image (as json)
// to the nodejs server which then calls the rest api
function sendPost (data) {

    console.log("send post...");

    var textVideo = document.getElementById("txtVideo");

    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {

            console.log("received response: " + this.responseText);

            // show link to view video
            document.getElementById('divVideo').style.display = "block";
        }
        /*else {
            console.log("error: readyState = " + this.readyState + " status = " + this.status);
        }*/
    };
    xhttp.open("POST", "/images", true);
    xhttp.setRequestHeader('Content-Type', 'application/json'); // or image/png?
    var payload = JSON.stringify({
        name: textVideo.value,
        data: data
    });
    console.log("sending payload: " + payload);
    xhttp.send(payload);
}

// test for posting local image to django server
function postLocalImage () {

    console.log("post local image...");

    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            console.log("received response: " + this.responseText);
        }
    };
    xhttp.open("POST", "/images", true);
    xhttp.setRequestHeader('Content-Type', 'application/json'); // or image/png?
    xhttp.send();
}