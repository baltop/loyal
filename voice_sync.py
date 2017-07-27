#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import audioop
import pyaudio
import wave


THRESHOLD = 500  # 이거보다 크면 삑소리가 난 거임. 기준치
DEFAULT_CHUNK_SIZE = 1110   # 대략 이정도 데이터가 0.1초 플레이 시간
FORMAT = pyaudio.paInt16
RATE = 44100

languageList = ['ko', 'en', 'jp', 'cn']
ping_time_list = []    # 이 리스트 안에 위의 언어 순서대로 빽소리가 난 시간의 리스트가 들어 가게 됨.


# 각 언어별 빅소리 파일을 훑어서 삑소리가 난 시간을 측정하여 리스트에 담아 위의 ping_time_list에 추가한다.
def ping_time(filename):
    write_on = False
    if filename.endswith("jp"):
        write_on = True
    # 함수 인자로 파일명이 넘어온다. 사용자 지정 파일명 + _ko 의 형식이다.
    filename = filename + '_ping.wav'
    if os.path.exists(filename) == False:   #해당 언어가 없으면 건너 뛴다.
        print(filename,"을 찾을 수 없습니다.")
        return

    # 이번 파일의 삑소리의 시간을 저장할 리스트
    list = []
    ping_sus = False

    wf = wave.open(filename, 'rb')

    p = pyaudio.PyAudio()

    stream = p.open(format=
                    p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
    sample_width = p.get_sample_size(FORMAT)

    rate1 = wf.getframerate()
    if wf.getnchannels() == 1:
        CHUNK_SIZE = DEFAULT_CHUNK_SIZE
    else:
        CHUNK_SIZE = DEFAULT_CHUNK_SIZE * 4

    data = wf.readframes(CHUNK_SIZE)
    print(filename)
    print("number of frame : ", wf.getnframes())
    print("number of channels : ", wf.getnchannels())
    print("play time : ", wf.getnframes()/wf.getframerate())
    print("사이즈당 플레이시간",  CHUNK_SIZE/wf.getframerate())

    print("rate is {0:.3f}".format(rate1))

    # silence 삽입하는 거 테스트.
    if write_on:
        wf2 = wave.open("/home/loudpump/Downloads/WavFile/out.wav", 'wb')
        wf2.setnchannels(2)
        wf2.setsampwidth(sample_width)
        wf2.setframerate(wf.getframerate())
        wf2.writeframes(data)

        silence = b'\x00'  # 묵음 처리

        emptyspace = (silence * CHUNK_SIZE * 5 ) * (5)
        #print("[", emptyspace, "]")
        wf2.writeframes(emptyspace)

    i = 0
    while data != b'':
        # 소리를 들어보려면
        # stream.write(data)
        data = wf.readframes(CHUNK_SIZE)

        i = i + 1
        print('time is {0}'.format(i))

        rms = audioop.rms(data, 2) #width=2 for format=paInt16
        print(rms)
        if rms > THRESHOLD:
            print("detect sound" , i)
            if ping_sus == False:
                list.append(i)
                ping_sus = True
        else:
            ping_sus = False
        if write_on:
            wf2.writeframes(data)


    wf.close()
    if write_on:
        wf2.close()
    stream.close()
    p.terminate()
    ping_time_list.append(list)





def file_process(filename):

    for i, elem in enumerate(languageList):
        ping_time(filename + '_' + languageList[i])


    print(ping_time_list)
    print(ping_time_list[0])



if __name__ == '__main__':
    print("void sync program start")
    if len(sys.argv) == 1 :
        print("명령인자가 없습니다.")
        in_file_name = "/home/loudpump/Downloads/WavFile/my"
    elif len(sys.argv) == 2:
        in_file_name = sys.argv[1]

    file_process(in_file_name)

    print("done ----- ")