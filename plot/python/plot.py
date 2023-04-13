#!/usr/bin/env python

import sys
import argparse
import os.path
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import statistics as stat

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('file', type=str, nargs='+', help='Data log file to plot')
    parser.add_argument('-t', '--title', type=str, default='', help='Title for the plot')
    parser.add_argument('-s', '--show', action='store_true', help='Show plot intead of saving image')
    parser.add_argument('-c', '--clut', type=int, help='Generate C lookup table')

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

        plot[os.path.basename(file.name).rsplit(".", 1)[0]] = data

    return plot

def plot(title, data, show):
    fig, ax = plt.subplots(figsize=(15, 8))

    ax.set_title(title)
    ax.set_xlabel('Time [m]')
    ax.set_ylabel('Voltage [mV]')
    ax.yaxis.set_major_locator(ticker.MultipleLocator(200))
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(50))
    ax.xaxis.set_major_locator(ticker.MultipleLocator(30))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(5))
    ax.grid(color='black', linestyle='--', linewidth=0.2)

    for plot in data:
        x = data[plot]['Time']
        x = [t / 60 for t in x]

        y = data[plot]['V']
        y = [v * 1000 for v in y]

        label = plot + ' ' + str("%.2f" % stat.mean(data[plot]['A'])) + 'A'

        ax.plot(x, y, label=label)

    ax.legend()

    if show:
        plt.show()
    elif title:
        plt.savefig(title + '.svg')
    else:
        plt.savefig('plot.svg')

def clut(data, count):
    print('typedef struct {')
    print('    int16_t soc;')
    print('    int16_t voltage;')
    print('} batt_soc_t;\n')

    for plot in data:
        voltage = data[plot]['V'].copy()
        voltage.sort(reverse=True)
        length = len(voltage)
        step = int(length / count) - 1

        print('const batt_soc_t {0}[{1}] = {{'.format(plot, count + 1))

        v = 0
        soc = 100
        for i in range(length):
            if i % step == 0:
                soc = round(soc)
                v = round(voltage[i] * 1000)
                print('    {{ {0}, {1} }},'.format(str(soc).ljust(4, ' '), v))
                soc -= 100 / count

        print('};\n')

if __name__ == "__main__":
    args = parse_args()
    data = parse(args.file)
    if data:
        if args.clut:
            clut(data, args.clut)
        plot(args.title, data, args.show)
    else:
        print('No data to plot!', file=sys.stderr)
        exit(-1)
    exit(0)