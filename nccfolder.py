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
    '1049': 'CONTINUATION',
    '1080': 'SENDER',
    '1420': 'PIT_CLDR2_MEETING',
    '1421': 'STARTTIME',
    '1422': 'ENDTIME',
    '1423': 'DESCRIPTION',
    '1424': '1424',
    '1425': '1425',
    '1426': '1426',
    '1427': '1427',
    '1428': '1428',
    '1430': 'PIT_CLDR2_BIRTHDAY',
    '1431': 'BIRTHDATE',
    '1432': '1432',
    '1433': 'NAME',
    '1434': '1434',
    '1435': 'BIRTHYEAR',
    '1436': '1436',
    '1437': '1437',
    '1440': 'PIT_CLDR2_CALLTO',
    '1441': 'EVENTTIME',
    '1442': 'PHONE',
    '1443': 'NAME',
    '1444': '1444',
    '1445': '1445',
    '1446': '1446',
    '1447': '1447',
    '1448': '1448',
    '1450': 'PIT_CLDR2_MEMO',
    '1451': 'MEMO_DATE',
    '1452': 'MEMO_DATE_2',
    '1453': 'MEMO',
    '1454': '1454',
    '1455': '1455',
    '1456': '1456',
    '1457': '1457',
    '1458': '1458',
    '1460': 'PIT_CLDR2_REMINDER',
    '1461': 'REMINDER_TIME',
    '1462': 'REMINDER',
    '1463': '1463',
        

}


def parseentry(data):
    parts = data.split("\t", 1)
    t = parts[0]

    parts = parts[1].split("\t")

    outdata = []

    while len(parts) > 1:
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


def parseevent(data):
    return parseentry(data)


def parsememo(data):
    return parseentry(data)


functions = {
    'CONTACT': parsecontact,
    'PIT_CALLERGROUP': parsegroup,
    'PIT_MESSAGE_INBOX': parsemessage,
    'PIT_CLDR2_MEETING': parseevent,
    'PIT_CLDR2_CALLTO': parseevent,
    'PIT_CLDR2_BIRTHDAY': parseevent,
    'PIT_CLDR2_MEMO': parsememo,
    'PIT_CLDR2_REMINDER': parseevent
}


def parsedata(code, data):
    if code not in tokens:
        print("Unknown code: {}".format(code))
        return code, data

    token = tokens[code]
    if token in functions:
        return functions[token](data)

    return tokens[code], data


def parseline(line):
    parts = line.split("\t", 1)
    code = parts[0]
    data = None

    if code not in tokens:
        print("Unknown code: {}".format(code))
        return code, parts[1]

    token = tokens[code]

    if token not in functions: 
        print("Unknown token: {}".format(token))
        return tokens[code], parts[1]

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

    calendar = convertfile(folder, 'Calendar.ncc')
    data['calendar'] = calendar

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