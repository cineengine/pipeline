import sys
import xml.etree.ElementTree as ET
sys.path.append('f:/dev/py')
from timecode import Timecode


TC_BASE = '30'
DEBUG = False
TEST_TREE = 'C:/users/wtron/desktop/Sequence 02.xml'
TEST_CSV = 'C:/users/wtron/desktop/test.csv'


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


# XML TO LOG PROCEDURE
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

