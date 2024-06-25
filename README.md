# face_recognition

This is the repository for the face_recognition application. This application requires the installation of dlib and face_recognition libraries.

You can check out the repository for the face_recognition library [here](https://github.com/ageitgey/face_recognition).
## Installation

To install the dependencies required for this project, simply run:

pip install -r requirements.txt

This command will install all the necessary packages listed in the requirements.txt file.

## Usage

### Running the Website

#### 2 way to add data of your photo to the dataset

1. you can add manually to the folder ID, remember the name of the file is the name of yours, so please double check it. and ensure your name written correctly on the file name.
2. later on, on the website, you can add your photo if your face undefined/unknown.

To run the website and access the interface, navigate to the master branch, pull all file from master branch run sqlite_data.py to create the database file with this command:

python sqlite_data.py


after that you can run the API_output.py file using Python:

python API_output.py

This will start the server, and you can access the website interface through your browser.


### Running the Raw Output from python code (not from website)

If you prefer to run the application without the website interface, you can run the face_data.py on raw branch, pull it out run the sqlite_data.py if you didnt have the database file then go to run the file with:

python face_data.py

## Note

Please note that after saving a new face, you may need to restart the server to ensure the changes take effect. This is a known limitation of the project.


### you can check the challenge on docx file i've already created



### new code:

for visualization you can see from code visualization.py

to run it you can do is:

python visual.py
