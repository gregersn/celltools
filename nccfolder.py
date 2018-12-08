import os
import sys
import json

tokens = {
    '200': 'CONTACT',
    '202': 'NAME',
    '205': 'EMAIL',
    '206': 'ADDRESS',
    '208': 'PHONE',
    '209': 'PHONE',
    '210': 'PHONE',
    '213': 'PHONE',
    '217': 'GROUP',
    '219': 'PHONE',
    '225': 'CONTACT',
    '300': 'PIT_CALLERGROUP',
    '301': 'GROUP_ID',
    '302': 'GROUP_NAME',
    '303': '303',
    '304': '304',
    '307': '307',
    '308': 'PHONE_MODEL',
    '1020': 'PIT_MESSAGE_INBOX',
    '1031': '1031',
    '1032': '1032',
    '1033': 'MESSAGE',
    '1035': '1035',
    '1036': '1036',
    '1038': '1038',
    '1039': '1039', 
    '1040': 'SMS_CENTRAL',
    '1041': 'TIMESTAMP',
    '1048': '1048',
    '1049': '1049',
    '1080': 'SENDER',

}


def parseentry(data):
    parts = data.split("\t", 1)
    t = parts[0]

    parts = parts[1].split("\t")

    outdata = []

    while len(parts) > 0:
        code = parts.pop(0)
        data = parts.pop(0)
        token, info = parsedata(code, data)

        outdata.append(": ".join((token, info)))
    return outdata


def parsecontact(data):
    parts = data.split("\t", 1)
    t = parts[0]
    assert t == 'PIT_CONTACT' or t == 'PIT_CONTACT_SIM', t

    parts = parts[1].split("\t")

    outdata = []

    while len(parts) > 0:
        code = parts.pop(0)
        data = parts.pop(0)
        token, info = parsedata(code, data)

        outdata.append(": ".join((token, info)))
    return outdata


def parsegroup(data):
    parts = data.split("\t", 1)
    t = parts[0]
    assert t == 'PIT_CALLERGROUP', t

    parts = parts[1].split("\t")

    outdata = []

    while len(parts) > 0:
        code = parts.pop(0)
        data = parts.pop(0)
        token, info = parsedata(code, data)

        outdata.append(": ".join((token, info)))
   
    return outdata


def parsemessage(data):
    return parseentry(data)


functions = {
    'CONTACT': parsecontact,
    'PIT_CALLERGROUP': parsegroup,
    'PIT_MESSAGE_INBOX': parsemessage
}


def parsedata(code, data):
    if code not in tokens:
        print("Unknown code: {}".format(code))
        return

    token = tokens[code]
    print(token)
    if token in functions:
        return functions[token](data)

    return tokens[code], data


def parseline(line):
    parts = line.split("\t", 1)
    code = parts[0]
    data = None

    if code not in tokens:
        print("Unknown code: {}".format(code))
        return

    token = tokens[code]

    if token not in functions: 
        print("Unknown token: {}".format(token))

    if token in functions:
        data = functions[token](parts[1])

    return tokens[code], data


def convertfile(folder, fn):
    filename = os.path.join(folder, fn)

    if not os.path.isfile(filename):
        return []
    
    outdata = {}

    with open(filename, 'r', encoding='utf_16') as f:
        lines = f.readlines()
        
        for line in lines:
            linetype, data = parseline(line.rstrip())
            
            if linetype not in outdata:
                outdata[linetype] = []
            outdata[linetype].append(data)

            line = f.readline()
    
    return outdata


def convert(folder, outfile="output.json"):
    data = {}

    phonebook = convertfile(folder, 'PhoneBook.ncc')
    data['phonebook'] = phonebook

    messages = convertfile(folder, 'Messages.ncc')
    data['messages'] = messages

    with open(outfile, 'w', encoding='utf8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def main():
    if len(sys.argv) < 2:
        print("Usage: {} <foldername>".format(__file__))
        return
    
    foldername = sys.argv[1]

    if not os.path.isdir(foldername):
        print("Argument {} is not a folder".format(foldername))
        return
    
    convert(foldername)


if __name__ == "__main__":
    main()