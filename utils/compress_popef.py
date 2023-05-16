# Copyright (c) 2023 Graphcore Ltd. All rights reserved.
import os
import numpy as np
import typing
import popef
import argparse
import sys

"""
Poplar Executable Compression Tool:

Usage: compress_popef.py <path_to_popef_1>,<path_to_popef_2>...<path_to_popef_N>

Pass in 1 or more comma separated popef files (no whitespace) as singular argument.
This file will compress executable files, reducing the total container size significantly. 

Compressed executable is created in same directory as existing uncompressed executable,
with `<name>.popef` replaced with `<name>.popef_compressed.popef`
"""

def removeFilesIfExist(filename):
    if os.path.exists(filename):
        os.remove(filename)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('filenames')
    args = parser.parse_args()

    print("Compressing ", args.filenames)

    filenames = args.filenames.split(',')
    
    for filename in filenames:
        print(filename)
        try:
            reader = popef.Reader()
            reader.parseFile(filename)
        except:
            print("Error while reading the file")
    
        try:
            open(filename + "_compressed.popef", mode='w+')
            writer = popef.Writer(filename + "_compressed.popef")

            print("Checking metadata...")
            for metadata in reader.metadata():
                writer.writeMetadata(metadata)

            # assert len(reader.executables()) == 1
            for executable in reader.executables():
                print("Found executable: ", executable.name)
                executableContent = executable.executable()
                exe_name = executable.name
                executableBlob = writer.createExecutable(executable.name, True)
                executableBlob.write(executableContent, len(executableContent))
                print("Done: ", filename + "_compressed.popef")


            print("Checking tensors...")
            for tensor in reader.tensors():
                # print(tensor.info)
                tensorBlob = writer.createTensorData(tensor.info)
                tensorBlob.write(tensor.data().tobytes(), tensor.info.tensorInfo().sizeInBytes())

            print("Checking feeds...")
            for feed in reader.feeds():
                feedBlob = writer.createFeedData(feed.info)
                feedBlob = writer.write(feed.data().tobytes(), feed.info.tensorInfo().sizeInByte())

            print("Checking opaques...")
            for opaque in reader.opaqueBlobs():
                opaqueBlob = writer.createOpaqueBlob(opaque.name, opaque.executable)
                data = opaque.data()
                opaqueBlob.write(data, len(data))

            writer.close()

        except BaseException as e:
            print("Error while writing the file", e)
            removeFilesIfExist(filename + "_compressed.popef")
            continue
