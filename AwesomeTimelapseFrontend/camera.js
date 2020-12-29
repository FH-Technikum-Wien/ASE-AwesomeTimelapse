// fires after all assets are loaded; replaced document.onload
window.onload = function () {
    
    console.log("accessing camera device...");

    // check if camera devices are available
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {

        var video = document.getElementById('video');
        
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
            setDeviceDivDisplay(false);
        });
        
        // elements for taking the image
        var canvas = document.getElementById('canvas');
        var context = canvas.getContext('2d');
        document.getElementById("btnSnap").addEventListener("click", function() {
            takePhoto(context, video);
        });
        
        // button to upload image on server
        document.getElementById("btnUpload").addEventListener("click", function() {
            convertCanvasToImage(canvas);
        });
    }
    else
    {
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
    
    // TODO: actually sending so server, rabbitMQ, ...
    
    // create image from data
    //var img = new Image();
    //img.src = canvas.toDataURL("image/png");
   
    // create image as blob and download per link
    canvas.toBlob(function(blob) {
        
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
    });
}