from sys import byteorder
from array import array
from struct import pack

import audioop
import pyaudio
import wave

THRESHOLD = 500
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
RATE = 44100


def is_silent(snd_data):
    "Returns 'True' if below the 'silent' threshold"
    return max(snd_data) < THRESHOLD

def normalize(snd_data):
    "Average the volume out"
    MAXIMUM = 16384
    times = float(MAXIMUM)/max(abs(i) for i in snd_data)

    r = array('h')
    for i in snd_data:
        r.append(int(i*times))
    return r

def trim(snd_data):
    "Trim the blank spots at the start and end"
    def _trim(snd_data):
        snd_started = False
        r = array('h')

        for i in snd_data:
            if not snd_started and abs(i)>THRESHOLD:
                snd_started = True
                r.append(i)

            elif snd_started:
                r.append(i)
        return r

    # Trim to the left
    snd_data = _trim(snd_data)

    # Trim to the right
    snd_data.reverse()
    snd_data = _trim(snd_data)
    snd_data.reverse()
    return snd_data

def add_silence(snd_data, seconds):
    "Add silence to the start and end of 'snd_data' of length 'seconds' (float)"
    r = array('h', [0 for i in xrange(int(seconds*RATE))])
    r.extend(snd_data)
    r.extend([0 for i in xrange(int(seconds*RATE))])
    return r

def record():
    """
    Record a word or words from the microphone and
    return the data as an array of signed shorts.

    Normalizes the audio, trims silence from the
    start and end, and pads with 0.5 seconds o
    blank sound to make sure VLC et al can play
    it without getting chopped off.
    """

    # open the file for reading.
    wf = wave.open("/home/loudpump/Downloads/WavFile/org.wav", 'rb')


    p = pyaudio.PyAudio()


    """
    stream = p.open(format=FORMAT, channels=1, rate=RATE,
        input=True, output=True,
        frames_per_buffer=CHUNK_SIZE)



    num_silent = 0
    snd_started = False

    r = array('h')

    while 1:
        # little endian, signed short
        snd_data = array('h', stream.read(CHUNK_SIZE))
        if byteorder == 'big':
            snd_data.byteswap()
        r.extend(snd_data)

        silent = is_silent(snd_data)

        if silent and snd_started:
            num_silent += 1
        elif not silent and not snd_started:
            snd_started = True

        if snd_started and num_silent > 30:
            break

    sample_width = p.get_sample_size(FORMAT)
    stream.stop_stream()
    stream.close()
    p.terminate()

    r = normalize(r)
    r = trim(r)
    r = add_silence(r, 0.5)
    return sample_width, r
    """

    # open stream based on the wave object which has been input.
    stream = p.open(format=
                    p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    rate1 = wf.getframerate()
    lenofsound = CHUNK_SIZE


    CHUNK_SIZE2 = rate1

    # read data (based on the chunk size)
    data = wf.readframes(CHUNK_SIZE)
    print(wf.getnframes())  #44200
    print(wf.getnchannels())
    print(wf.getnframes()/wf.getframerate()) # 총 4초
    print(CHUNK_SIZE/wf.getframerate()/wf.getnchannels())  #사이즈당 플레이 시간


    print("rate is {0:.3f}".format(rate1))

    i = 0
    # play stream (looping from beginning of file to the end)
    while data != '':
        # writing to the stream is what *actually* plays the sound.
        stream.write(data)
        data = wf.readframes(CHUNK_SIZE)
        #print("time is " + rate1)
        i = i + 1
        print('time is {0}'.format(i))
        #print(data)
        rms = audioop.rms(data, 2) #width=2 for format=paInt16
        print(rms)
        if rms > THRESHOLD:
            print("detect sound")
        if i > 40 :
            break
    # cleanup stuff.
    stream.close()
    p.terminate()

def record_to_file(path):
    "Records from the microphone and outputs the resulting data to 'path'"
    sample_width, data = record()
    data = pack('<' + ('h'*len(data)), *data)

    wf = wave.open(path, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(sample_width)
    wf.setframerate(RATE)
    wf.writeframes(data)
    wf.close()

if __name__ == '__main__':
    print("please speak a word into the microphone")

    record()
    #record_to_file('demo.wav')
    print("done - result written to demo.wav")
