from time import time

class WithTankFormatter:
    def __init__(self, outFile, startTime):
        self.File = outFile
        self.start = startTime
    def writeHeader( self) :
        self.File.write( 'TimeStamp,UUID,Zone1Threshold,Zone1Reading,Zone2Threshold,Zone2Reading,Zone3Threshold,Zone3Reading,Zone4Threshold,Zone4Reading,Zone5Threshold,Zone5Reading,Zone6Threshold,Zone6Reading,Zone7Threshold,Zone7Reading,Zone8Threshold,Zone8Reading,Votes,AvgThreshold,AvgReading,Verdict,Type\n')
    def writeOut( self, buffer, uuid, touch):
        outline =  ['' for i in range(23)]
        outline[22] = touch
        outline[0] = str( int(round(time() - self.start)))
        outline[1] = uuid
        lines = buffer.splitlines()
        for line in lines :
            pieces = line.split(':')
            if len(pieces) < 4 : continue
            data = pieces[2].strip()
            if data == 'Level':
                levels = pieces[3].split(',')
                for i in range(8):
                    outline[i*2+3] = levels[i].lstrip()
            if data == 'Thrsh':
                levels = pieces[3].split(',')
                for i in range(8):
                    outline[i*2+2] = levels[i].lstrip()
            if data == 'Avg Level':
                outline[20] = pieces[3].lstrip()
            if data == 'Avg Thrsh':
                outline[19] = pieces[3].lstrip()
            if data == 'Votes':
                outline[18] = pieces[3].lstrip()
            if data == 'Verdict':
                outline[21] = pieces[3].strip()
        self.File.write( ','.join( outline))

class TanklessFormatter:
    def __init__(self, outFile, startTime):
        self.File = outFile
        self.start = startTime
    def writeHeader( self) :
        self.File.write( 'TimeStamp,UUID,Data01,Data02,Data03,Data04,Data05,Data06,Data07,Data08,Data09,Data10,Data11,Data12,Data13,Data14,Data15,Data16,N_Detected,Verdict,Touched\n')
    def writeData( self, buffer, uuid, touch):
        outline =  ['' for i in range(21)]
        outline[20] = touch
        outline[0] = str( int(round(time() - self.start)))
        outline[1] = uuid
        lines = buffer.splitlines()
        for line in lines :
            pieces = line.split(':')
            if len(pieces) < 4 : continue
            data = pieces[2].strip()
            if data.startswith('line_data'):
                dataline = int(data[-1]) - 1
                for lineN in range(4):
                    outline[2+(4*dataline)+lineN] = pieces[3].split(',')[lineN].strip()
            if data == 'Verdict':
                outline[19] = pieces[3].strip()
            if data == 'n_detected':
                outline[18] = pieces[3].strip()
        self.File.write( ','.join( outline))

class DataFormatter() :
    def __init__( self, tankless, outFile, startTime) :
        if tankless :
            self.processor = TanklessFormatter(outFile, startTime)
        else :
            self.processor = WithTankFormatter(outFile, startTime)
    def writeHeader( self) :
        self.processor.writeHeader()
    def writeData( self, buffer, temp, touch) :
        self.processor.writeData( buffer, temp, touch)
        