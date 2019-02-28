# -*- coding: utf-8 -*-

def interpretAlert(alert):
    # Esta função deve interpretar os dados do alerta do Snort

    splitted_alert = alert.split(' ')
    time_stamp = splitted_alert[1] + " " + splitted_alert[2] + " " + splitted_alert[3]
    type = ''
    snort_rule = False
    alert_dict = {}

    try:
        for part in splitted_alert:
            if part[0] == '{':
                type = part[1:-1]
                snort_rule = True
            else:
                pass
        if type != '':
            pass
        else:
            type = splitted_alert[5][:-1]
    except Exception as e:
        type = 'Not Found'


    if snort_rule:
        alert_dict = {"Time":time_stamp, "Type":type, "Source":splitted_alert[-3], "Destination":splitted_alert[-1][:-1] }
    else:
        alert_dict = {"Time":time_stamp, "Type":type}

    return alert_dict

def read_log_file(file):
    log_file = open(file, 'r')
    logs = log_file.readlines()
    messages = []

    for log_line in logs:
        #message = log_line.split(' ')
        if "Msg:" not in log_line:
            pass
        else:
            messages.append(log_line)

    return messages


if __name__ == "__main__":
    messages = read_log_file("logSnort2.txt")
    for message in messages:
        parsed_syslog = interpretAlert(message)
        parsed_syslog_keys = list(parsed_syslog.keys())
        if not "Source" in parsed_syslog_keys and not "Destination" in parsed_syslog_keys:
            continue
        else:
            #print(parsed_syslog)
            pass
