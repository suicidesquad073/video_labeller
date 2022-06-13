import cv2
from ffpyplayer.player import MediaPlayer
import ffmpeg
import sys
import os 
from PyQt5.QtWidgets import  QWidget, QLabel, QApplication, QGridLayout, QPushButton, QButtonGroup, QStyle
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap

beer_types = [
    "Glas",
    "Spies",
    "Plastic beker",
    "Blik",
    "Anders"
]

names = [
    "Bastiaan",
    "David",
    "Freek",
    "Han",
    "JvT",
    "Kaz",
    "Koen",
    "Max",
    "Nick",
    "Rob",
    "Sam",
    "Sjoerd",
    "Teun",
    "Thom",
    "Thomas"
]

quantities = [
    "1",
    "2",
    "3",
    "4",
    "Anders" # Usually people don't chuck more than four beers (... usually)
]

special_video = [
    "Niet speciaal",
    "Leuk",
    "Anders"
]

class VideoPlayerThread(QThread):
    """ Thread that displays the given mp4 video """

    changePixmap = pyqtSignal(QImage)

    def __init__(self, path, parent=None):
        QThread.__init__(self, parent)
        self.path = path

    def stop(self):
        self.video_capture.release()

    def run(self):
        self.video_capture = cv2.VideoCapture(self.path)
        self.player = MediaPlayer(self.path, loglevel='quiet')
        self.length = int(self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT))

        while self.video_capture.isOpened():
            ret, frame = self.video_capture.read()
            audio_frame, val = self.player.get_frame()
            if ret:
                # https://stackoverflow.com/a/55468544/6622587
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                self.changePixmap.emit(p)
                self.msleep(1000//30)
            else:
                break

        self.player.close_player()
        self.video_capture.release()

class App(QWidget):
    def __init__(self, argv, paths):
            super(App,self).__init__()
            self.title = 'Video labeller'
            self.paths = paths
            
            self.current_video_index = 0
            self.left = 100
            self.top = 100
            self.width = 640
            self.height = 480
            self.buttons = []

            self.current_name = "Undefined"
            self.current_type = "Undefined"
            self.current_quantity = "Undefined"
            self.current_duration = "Undefined"
            self.current_fun = "Undefined"

            self.initUI()
            print("video_file;duration;name;type;quantity;fun")

    def initUI(self):
        """ Initializes the GUI """

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.resize(800, 600)
        self.grid_layout = QGridLayout()
        self.setLayout(self.grid_layout)

        self.previous_button = QPushButton("Previous")
        pixmapi = getattr(QStyle, "SP_MediaSkipBackward")
        icon = self.style().standardIcon(pixmapi)
        self.previous_button.setIcon(icon)
        self.previous_button.resize(10, 25)
        self.previous_button.clicked.connect(self.play_previous_video)

        self.next_button = QPushButton("Next")
        pixmapi = getattr(QStyle, "SP_MediaSkipForward")
        icon = self.style().standardIcon(pixmapi)
        self.next_button.setIcon(icon)
        self.next_button.resize(10, 25)
        self.next_button.clicked.connect(self.play_next_video)

        self.grid_layout.addWidget(self.previous_button, 15, 0)
        self.grid_layout.addWidget(self.next_button, 15, 1)

        # Create QLabel for video player
        self.label = QLabel(self)
        self.grid_layout.addWidget(self.label, 0, 0, 14, 2)
        self.label.resize(640, 480)

        # Create label buttons
        self.name_button_group = self.initLabelButtonColumn(names, 2, self.name_clicked)        
        self.quantities_button_group = self.initLabelButtonColumn(beer_types, 3, self.quantities_clicked)        
        self.beer_type_button_group = self.initLabelButtonColumn(quantities, 4, self.beer_type_clicked)        
        self.fun_button_group = self.initLabelButtonColumn(special_video, 5, self.fun_clicked)        

        self.play_video(self.paths[self.current_video_index])

    def play_video(self, path):
        """ Plays the given .mp4 file in the video player """

        self.current_duration = ffmpeg.probe(path)["streams"][0]["duration"]
        
        self.video_player = VideoPlayerThread(path, self)
        self.video_player.changePixmap.connect(lambda p: self.setPixMap(p))
        self.video_player.start()

    def setPixMap(self, p):
        """ Callback function for the video player to display a video frame in the GUI """

        p = QPixmap.fromImage(p)    
        p = p.scaled(640, 480, Qt.KeepAspectRatio)
        self.label.setPixmap(p)

    def initLabelButtonColumn(self, labels, column, callback):
        """ Initializes a column of buttons with the given labels """
        button_group = QButtonGroup()
        button_group.setExclusive(True)

        for i, name in enumerate(labels):
            button = QPushButton(name)
            button.resize(10, 50)
            
            self.grid_layout.addWidget(button, i, column)     
            button_group.addButton(button)

        button_group.buttonClicked.connect(callback)

        return button_group

    def fun_clicked(self, button):

        for grey_button in self.fun_button_group.buttons():
            grey_button.setStyleSheet("")
        button.setStyleSheet("background-color:rgb(0,255,0)")

        self.current_fun = button.text()

    def quantities_clicked(self, button):

        for grey_button in self.quantities_button_group.buttons():
            grey_button.setStyleSheet("")
        button.setStyleSheet("background-color:rgb(0,255,0)")

        self.current_quantity = button.text()

    def name_clicked(self, button):

        for grey_button in self.name_button_group.buttons():
            grey_button.setStyleSheet("")
        button.setStyleSheet("background-color:rgb(0,255,0)")

        self.current_name = button.text()

    def beer_type_clicked(self, button):

        for grey_button in self.beer_type_button_group.buttons():
            grey_button.setStyleSheet("")
        button.setStyleSheet("background-color:rgb(0,255,0)")        

        self.current_type = button.text()
        
    def play_next_video(self, button):
        """ Plays the next video """
        
        self.label_video()
        
        if self.current_video_index >= len(self.paths) - 1:
            return
        else:
            self.current_video_index += 1
        
        self.video_player.stop()
        self.play_video(self.paths[self.current_video_index])

        for grey_button in self.name_button_group.buttons():
            grey_button.setStyleSheet("")
        for grey_button in self.beer_type_button_group.buttons():
            grey_button.setStyleSheet("")            

    def play_previous_video(self, button):
        """ Plays the previous video """

        if self.current_video_index == 0:
            return
        else:
            self.current_video_index -= 1
        
        self.video_player.stop()
        self.play_video(self.paths[self.current_video_index])

        for grey_button in self.name_button_group.buttons():
            grey_button.setStyleSheet("")
        

    def label_video(self):
        
        csv_entry = ""
        csv_entry += self.paths[self.current_video_index] + ';'
        csv_entry += self.current_duration + ';'
        csv_entry += self.current_name + ';'
        csv_entry += self.current_type + ';'
        csv_entry += self.current_quantity + ';'
        csv_entry += self.current_fun
        print(csv_entry)
        self.current_duration = "Undefined"
        self.current_name = "Undefined"
        self.current_type = "Undefined"

if __name__ == '__main__':

    paths = []
    mp4_dir = None 

    # Get the paths to all .mp4 files in the given directory
    if len(sys.argv) >= 2:
        if os.path.isdir(sys.argv[-1]):
            mp4_dir = sys.argv[-1]

            for file in os.listdir(mp4_dir):
                if file.endswith(".mp4"):
                    path = os.path.join(mp4_dir + "/", file)
                    paths.append(path)
                    
            if len(paths) == 0:
                print("ERROR no files found in", mp4_dir)
                sys.exit(-1)
        else:
            print("ERROR invalid or no path to .mp4 files")
            sys.exit(-1)
    else:
        print("ERROR No path to .mp4 files given")
        sys.exit(-1)
    
    # Start the GUI
    app = QApplication(sys.argv)
    ex = App(sys.argv, paths)
    ex.show()
    sys.exit(app.exec_())