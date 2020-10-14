# https://web.microsoftstream.com/ website subtitle convertor
# find the json file by search transcript in chrome inspect

import json
import sys
import os
import re
import codecs

import getopt
import sys

# convert srt to ass

def fileopen(input_file):
    encodings = ["utf-32", "utf-16", "utf-8", "cp1252", "gb2312", "gbk", "big5"]
    tmp = ''
    for enc in encodings:
        try:
            with codecs.open(input_file, mode="r", encoding=enc) as fd:
                tmp = fd.read()
                break
        except:
            # print enc + ' failed'
            continue
    return [tmp, enc]


def srt2ass(input_file):
    if '.ass' in input_file:
        return input_file

    if not os.path.isfile(input_file):
        print(input_file + ' not exist')
        return

    src = fileopen(input_file)
    tmp = src[0]
    encoding = src[1]
    src = ''
    utf8bom = ''

    if u'\ufeff' in tmp:
        tmp = tmp.replace(u'\ufeff', '')
        utf8bom = u'\ufeff'
    
    tmp = tmp.replace("\r", "")
    lines = [x.strip() for x in tmp.split("\n") if x.strip()]
    subLines = ''
    tmpLines = ''
    lineCount = 0
    output_file = '.'.join(input_file.split('.')[:-1])
    output_file += '.ass'

    for ln in range(len(lines)):
        line = lines[ln]
        if line.isdigit() and re.match('-?\d\d:\d\d:\d\d', lines[(ln+1)]):
            if tmpLines:
                subLines += tmpLines + "\n"
            tmpLines = ''
            lineCount = 0
            continue
        else:
            if re.match('-?\d\d:\d\d:\d\d', line):
                line = line.replace('-0', '0')
                tmpLines += 'Dialogue: 0,' + line + ',*Default,NTP,0000,0000,0000,,'
            else:
                if lineCount < 2:
                    tmpLines+=line
                    
            lineCount += 1
        ln += 1


    subLines += tmpLines + "\n"

    subLines = re.sub(r'\d(\d:\d{2}:\d{2}),(\d{2})\d', '\\1.\\2', subLines)
    subLines = re.sub(r'\s+-->\s+', ',', subLines)
    # replace style
    subLines = re.sub(r'<([ubi])>', "{\\\\\g<1>1}", subLines)
    subLines = re.sub(r'</([ubi])>', "{\\\\\g<1>0}", subLines)
    subLines = re.sub(r'<font\s+color="?#(\w{2})(\w{2})(\w{2})"?>', "{\\\\c&H\\3\\2\\1&}", subLines)
    subLines = re.sub(r'</font>', "", subLines)

    head_str = '''[Script Info]
Title:
Original Script:
Synch Point:0
PlayResY: 0
WrapStyle: 0
ScriptType:v4.00+
Collisions:Normal
WrapStyle:2
Timer:100.0000

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour,  BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,微软雅黑,16,&H00FFFFFF,&HFF000000,&H00000000,-1,0,0,0,100,100,0,0,1,2,0,2,5,5,2,134


[Events]
Format: Layer, Start, End, Style, Actor, MarginL, MarginR, MarginV, Effect, Text'''

    output_str = utf8bom + head_str + '\n' + subLines
    output_str = output_str.encode(encoding)

    with open(output_file, 'wb') as output:
        output.write(output_str)

    output_file = output_file.replace('\\', '\\\\')
    output_file = output_file.replace('/', '//')
    return output_file

# convert cc subtitle to srt.
def time_process(time_string):
    ms = '000'
    mins = '00'
    sec = '00'
    if '.' in time_string:
        rep = re.search("PT.+\.(\d+)S",time_string)
        ms = rep.group(1)

    if 'M' in time_string:
        rep = re.search("PT(\d+)M",time_string)
        mins = rep.group(1)

    rep = re.search("PT\d*?M?(\d+)\.?\d*?S",time_string)
    sec = rep.group(1)
    return mins,sec,ms



if __name__ == "__main__":
    opts,args = getopt.getopt(sys.argv[1:],'-h-i:-v',['help','input=','version'])
    for opt_name,opt_value in opts:
        if opt_name in ('-h','--help'):
            print("[*] Help info")
            exit()
        if opt_name in ('-v','--version'):
            print("[*] Version is v.0.1 ")
            exit()

        if opt_name in ('-i','--input'):
            inputJsonName = opt_value
            
            
    
#     inputJsonName = 'originsub.json'
    with open(inputJsonName) as j:
        sub_dict = json.load(j)
        sub_list = sub_dict['value']

    with open(inputJsonName[:-4]+'srt','w') as f:
        for count,i in enumerate(sub_list):

            time_stamp = "00:{:0>2}:{:0>2},{:0>3} --> 00:{:0>2}:{:0>2},{:0>3}".format(*time_process(i['start']),*time_process(i['end']))
            content = i['eventData']['text'].replace('\r\n',' ')
            this_para = '{}\n{}\n{}\n\n'.format(count+1,time_stamp,content)
            f.write(this_para)

    srt2ass(inputJsonName[:-4]+'srt')
