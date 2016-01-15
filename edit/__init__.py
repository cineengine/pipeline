# built-in
import sys
import xml.etree.ElementTree as ET

# external
sys.path.append('Y:/Workspace/SCRIPTS/python')
from PyQt4 import QtGui, QtCore, uic
from timecode import Timecode

TC_BASE = '59.94'
DEBUG = False

QT_UI = "V:/dev/pipeline/edit/editLog.ui"

TEST_TREE = 'V:/dev/pipeline/edit/test_data/Sequence 02.xml'
TEST_CSV = 'V:/dev/pipeline/edit/test_data/Sequence 02.csv'
TEST_EDL = 'V:/dev/pipeline/edit/test_data/CFP ELEMENT REEL SALES.edl'
EDL_CSV = 'V:/dev/pipeline/edit/test_data/CFP ELEMENT REEL SALES.csv'


class LogWidget(QtGui.QWidget):

    def __init__(self):
        super(self.__class__, self).__init__()
        
        uic.loadUi(QT_UI, self)
        self.setWindowTitle('Edit Log Generator')
        self.initUI()

    def initUI(self):
        self.input_edl = ''
        self.input_xml = ''

        self.edl_btn.clicked.connect(self.importEDL)
        #self.xml_btn.clicked.connect(self.importXML)

        self.export_btn.setEnabled(False)

        self.show()

    def importEDL(self, state):
        self.input_edl = QtGui.QFileDialog.getOpenFileName()

        if not self.input_edl == '':
            self.export_btn.setEnabled(True)
            self.xml_btn.setEnabled(False)

        print self.input_edl

    def importXML(self, state):
        self.input_xml = QtGui.QFileDialog.getOpenFileName()
        
        if not self.input_xml == '':
            self.export_btn.setEnabled(True)
            self.xml_btn.setEnabled(False)

        print self.input_edl

    def export(self, state):
        
        print self.edl_btn.getEnabled()

def run():
    app = QtGui.QApplication(sys.argv)
    wid = LogWidget()
    sys.exit(app.exec_())


def frameToTC(frame, base=TC_BASE):

    tc = Timecode(base, '00:00:00:00')
    tc.frames = frame

    return tc


def sequence(in_, out_, base=TC_BASE, debug=DEBUG):

    if isinstance(in_, int):
        in_ = frameToTC(in_)

    if isinstance(out_, int):
        out_ = frameToTC(out_)

    elif isinstance(in_, Timecode):
        pass

    elif isinstance(out_, Timecode):
        pass

    return (in_, out_)


def xmlToLog(XML=TEST_TREE):

    # LOAD XML TREE
    tree = ET.parse(XML)
    root = tree.getroot()
    
    # CREATE OUTPUT STRING
    out_string = ''
    
    # SET OUT POINT TO 0
    xout = 0

    # Find the Video element
    video = root.find('sequence/media/video')

    # Iterate over all tracks in the video element
    for track in video.iter('track'):

        # Iterate over all clips in the track
        for clipitem in track.findall('clipitem'):

            # Get clip name, timeline in & out points
            name = clipitem.find('name').text
            in_  = clipitem.find('start').text
            out_ = clipitem.find('end').text

            # Add an extra linebreak if the clips do not butt together
            # (Detecting this is why we store the out frame on each iteration)
            if in_ != xout:
                out_string += ',,\n'

            # Write the line (note inline conversion from str to int to timecode)
            out_string += '{},{},{}\n'.format(name, frameToTC(int(in_)), frameToTC(int(out_)))

            # Store the out frame for next iteration
            xout = out_

    # Write the CSV
    with open(TEST_CSV, 'w') as out_stream:
        out_stream.write(out_string)


def edlToLog(EDL=TEST_EDL):

    out_stream = ''

    with open(TEST_EDL, 'r') as edl:
    
        for line in edl:

            line = line.split()
            
            clip_name  = line[1]
            try:
                clip_start = line[6]
                clip_end   = line[7]
            except:
                continue

            '''
            if ('SLATE' in clip_name) or \
               ('BLK' in clip_name) or \
               ('BLACK' in clip_name):
                continue

            else:
            '''
            out_stream += "{},{},{}\n".format(clip_name, clip_start, clip_end)

    with open(EDL_CSV, 'w') as csv:
        csv.write(out_stream)

    return True

