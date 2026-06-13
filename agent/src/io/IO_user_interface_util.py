import json
import logging
import os
import time

import IO_csv_util

logger = logging.getLogger()


def convert_time(time):
    hours = int(time / 3600)
    minutes = int((time - hours * 3600) / 60)
    seconds = int(time - hours * 3600 - minutes * 60)
    message = ""
    if seconds == 1:
        second_label = " second"
    else:
        second_label = " seconds"
    if minutes == 1:
        minute_label = " minute"
    else:
        minute_label = " minutes"
    if hours == 1:
        hour_label = " hour"
    else:
        hour_label = " hours"

    # compose message
    if hours > 0:
        message = str(hours) + hour_label
    if minutes >= 0:
        if hours > 0:
            message = message + ", "
            message = message + str(minutes) + minute_label
        else:
            if minutes > 0:
                message = message + str(minutes) + minute_label
    if seconds >= 0:
        if hours > 0:
            message = message + ", and " + str(seconds) + second_label
        else:
            if minutes > 0:
                message = message + " and " + str(seconds) + second_label
            else:
                message = message + str(seconds) + second_label
    return hours, minutes, seconds, message


# silent will not display the message as a box
def timed_alert(
    timeout,
    message_title,
    message_text,
    time_needed=False,
    extraLine="",
    printInCommandLine=True,
    startTime="",
    silent=False,
):
    if time_needed:
        # time has year [0], month [1], dat [2], hour [3], minute [4], second [5] & more
        time_report = time.localtime()
        message_text = message_text + " " + str(time_report[3]) + ":" + str(time_report[4])
        if startTime != "":
            endTime = time.time()
            totalTime = endTime - startTime  # in number of seconds
            hours, minutes, seconds, time_message = convert_time(totalTime)
            if time_message != "":
                message_text = (
                    message_text + " taking " + time_message
                )  # + str(hours) + ' hours, ' + str(minutes) + ' minutes, and ' + str(seconds) + ' seconds'
        message_text = message_text + "."
    if len(extraLine) > 0:
        message_text = message_text + "\n\n" + extraLine
    if printInCommandLine:
        print_message_text = message_text
        if "Started" in print_message_text:
            print_message_text = print_message_text.replace("Started", "\nStarted")
            print_message_text = print_message_text + "\n"
        if "Finished" in print_message_text:
            print_message_text = print_message_text.replace("Finished", "\nFinished")
        print_message_text = "\n" + print_message_text
        if "Opening" in print_message_text:
            print_message_text = print_message_text.replace("Opening", "\nOpening")
        logger.info(print_message_text)
    if not silent:
        if "Finished" not in message_text and "Opening" not in message_text:
            message_text = message_text + "\n\nYou can follow the algorithm in command line."

        logger.info("%s %s", message_title, message_text)

    return time.time()


# inputFilename has complete path
def process_CoreNLP_error(CoreNLP_output, inputFilename, nDocs, filesError, text, silent=True):
    errorFound = False
    duration = 1000
    head, tail = os.path.split(inputFilename)
    error = None
    if isinstance(CoreNLP_output, str):
        logger.warning("[Warning] Stanford CoreNLP output is not JSON. Trying to convert output to JSON... ")

        if text and not CoreNLP_output:
            error = (
                "Bad Response from Stanford CoreNLP Server. This might be due to various reasons. The server might"
                "be busy, and please try later. If you are running it with a proxy, please try turning it off "
                "before running it again."
            )
            logger.error("[Error] " + error)
            errorFound = True
        else:
            try:
                CoreNLP_output = json.loads(CoreNLP_output)
                logger.warning("[Info] Successfully converted CoreNLP output to JSON. Proceeding as normal.")
            except Exception as e:
                logger.error(
                    "[Error] Could not convert CoreNLP output to JSON! Please, check your input file for any corruption. Error: "
                    + str(e)
                )
                errorFound = True
                error = str(e)
    # OutOfMemoryError Java heap space
    # this error may occur with Java JDK version > 8. Java heap memoryy size is set to 32 bits by default instead of 64, leading to this error.
    # for memory errors and solutions https://stackoverflow.com/questions/40832022/outofmemoryerror-when-running-the-corenlp-tool
    # You can use Java8. They use metaspace for heap. So, no heap space error will occur.
    # see also
    # https://stackoverflow.com/questions/909018/avoiding-initial-memory-heap-size-error

    # need to add -d64 to the Java call (e.g., ['java', '-mx' + str(memory_var) + "g", '-d64', '-cp', os.path.join(CoreNLPdir, '*'),
    #          'edu.stanford.nlp.pipeline.StanfordCoreNLPServer', '-timeout', '999999'])
    # TODO % will break the code
    # The reasons are explained here: https://docs.oracle.com/javase/8/docs/api/java/net/URLDecoder.html
    #   The character "%" is allowed but is interpreted as the start of a special escaped sequence.
    # Needs special handling https://stackoverflow.com/questions/6067673/urldecoder-illegal-hex-characters-in-escape-pattern-for-input-string
    if errorFound:
        if len(filesError) > 2:
            silent = True
        elif len(filesError) == 2:
            duration = 1000
        elif len(filesError) == 1:
            duration = 2000
        elif len(filesError) == 0:
            filesError.append(["Document ID", "Document", "Error"])
            duration = 3000
        msg = (
            "Stanford CoreNLP failed to process your document\n\n"
            + tail
            + "\n\nexiting with the following error:\n\n   "
            + (str(CoreNLP_output) if CoreNLP_output else error)
            + "\n\nPlease, CHECK CAREFULLY THE REASONS FOR FAILURE REPORTED BY STANFORD CORENLP. If necessary, then edit the file leading to errors if necessary."
        )
        msgPrint = "Stanford CoreNLP failed to process your document " + tail
        # + '\nexiting with the following error:\n\n' + CoreNLP_output + '\n\nTHE ERROR MAY HAPPEN WHEN CoreNLP HANGS. REBOOT YOUR MACHINE AND TRY AGAIN.\n\nTHE ERROR IS ALSO LIKELY TO HAPPEN WHEN THE STANFORD CORENLP HAS BEEN STORED TO A CLOUD SERVICE (e.g., OneDrive) OR INSIDE THE /NLP/src DIRECTORY. TRY TO MOVE THE STANFORD CORENLP FOLDER TO A DIFFERENT LOCATION.
        if nDocs > 1:
            msg = msg + " Processing will continue with the next file."
            msgPrint += " Processing will continue with the next file."
        if not silent:
            timed_alert(duration, "Stanford CoreNLP error", msg)
        logger.info("\n\n" + msgPrint)
        filesError.append(
            [
                len(filesError),
                IO_csv_util.dressFilenameForCSVHyperlink(inputFilename),
                str(CoreNLP_output) + " " + str(error),
            ]
        )
    return errorFound, filesError, CoreNLP_output
