const video = document.getElementById('video');
const captureButton = document.getElementById('captureButton');
const captureWithNameButton = document.getElementById('captureWithNameButton');
const nameInput = document.getElementById('nameInput');
const nameElement = document.getElementById('name');
const resultImage = document.getElementById('resultImage');

navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
    })
    .catch(error => {
        console.error('Error accessing webcam: ', error);
    });

captureButton.addEventListener('click', () => {
    captureImage();
});

captureWithNameButton.addEventListener('click', () => {
    captureImageWithName();
});

function captureImage() {
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(blob => {
        const formData = new FormData();
        formData.append('image', blob);

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                nameElement.textContent = data.error;
                // Show capture button if face is not detected
                captureButton.style.display = 'block';
                captureWithNameButton.style.display = 'none';
                nameInput.style.display = 'none';
            } else if (data.name === 'Unknown') {
                // Show capture with name button and name input if face is unknown
                captureButton.style.display = 'none';
                captureWithNameButton.style.display = 'block';
                nameInput.style.display = 'block';
                nameElement.textContent = '';
            } else {
                nameElement.textContent = `${data.name} - ${data.position}`;
                resultImage.src = canvas.toDataURL();
                displayOverlayText(data);
                // Hide capture buttons if face is recognized
                captureButton.style.display = 'none';
                captureWithNameButton.style.display = 'none';
                nameInput.style.display = 'none';
            }
        })
        .catch(error => {
            console.error('Error uploading image:', error);
        });
    });
}

function captureImageWithName() {
    const name = nameInput.value.trim();
    if (name === '') {
        alert('Please enter a name.');
        return;
    }
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(blob => {
        const formData = new FormData();
        formData.append('image', blob);
        formData.append('name', name);

        fetch('/register', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            nameInput.value = '';
        })
        .catch(error => {
            console.error('Error registering user:', error);
        });
    });
}

function displayOverlayText(data) {
    const overlayCanvas = document.createElement('canvas');
    overlayCanvas.width = video.videoWidth;
    overlayCanvas.height = video.videoHeight;
    const overlayContext = overlayCanvas.getContext('2d');

    // Draw the image
    const image = new Image();
    image.src = resultImage.src;
    image.onload = () => {
        overlayContext.drawImage(image, 0, 0, overlayCanvas.width, overlayCanvas.height);

        // Set text properties
        overlayContext.font = '18px Arial';
        overlayContext.fillStyle = 'red';
        overlayContext.fillText(`Name: ${data.name}`, 10, overlayCanvas.height - 100);
        overlayContext.fillText(`Employee ID: ${data.employee_id}`, 10, overlayCanvas.height - 80);
        overlayContext.fillText(`Department: ${data.department}`, 10, overlayCanvas.height - 60);
        overlayContext.fillText(`Check-in: ${data.check_in}`, 10, overlayCanvas.height - 40);
        overlayContext.fillText(`Fatigue Status: ${data.fatigue_status}`, 10, overlayCanvas.height - 20);

        // Display the canvas with overlay text
        resultImage.src = overlayCanvas.toDataURL();
    };
}

// Initially show capture button and hide capture with name button and name input
captureButton.style.display = 'block';
captureWithNameButton.style.display = 'none';
nameInput.style.display = 'none';

// Function to toggle between capture button and capture with name button
function toggleCaptureButtons() {
    captureButton.style.display = captureButton.style.display === 'block' ? 'none' : 'block';
    captureWithNameButton.style.display = captureWithNameButton.style.display === 'block' ? 'none' : 'block';
    nameInput.style.display = nameInput.style.display === 'block' ? 'none' : 'block';
}
