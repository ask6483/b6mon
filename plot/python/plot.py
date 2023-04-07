#!/usr/bin/env python

import argparse
import os.path
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('file', type=str, nargs='+', help='Data log file to plot')
    parser.add_argument('-t', '--title', type=str, help='Title for the plot')

    return parser.parse_args()

def parse(files):
    plot = {}
    for file_path in files:
        if not os.path.isfile(file_path):
            print("%s in not a file" % file_path)
            continue

        data = {}
        with open(file_path, 'r') as file:
            header = next(file).split()
            header.remove('#')

            for key in header:
                data[key] = []

            for line in file:
                for i, column in enumerate(line.split()):
                    data[header[i]].append(float(column))

        plot[file.name.rsplit(".", 1)[0]] = data

    return plot

def plot(title, data):
    fig, ax = plt.subplots()
    ax.set_title(title)
    ax.set_xlabel('Time [m]')
    ax.set_ylabel('Voltage [mV]')
    ax.yaxis.set_major_locator(ticker.MultipleLocator(200))
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(50))
    ax.xaxis.set_major_locator(ticker.MultipleLocator(60))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(10))
    ax.grid(color='black', linestyle='--', linewidth=0.2)

    for plot in data:
        x = data[plot]['Time']
        x = [t / 60 for t in x]

        y = data[plot]['V']
        y = [v * 1000 for v in y]

        ax.plot(x, y, label=plot)

    ax.legend()
    plt.show()

if __name__ == "__main__":
    args = parse_args()
    data = parse(args.file)
    if data:
        plot(args.title, data)
    else:
        print('No data to plot!')