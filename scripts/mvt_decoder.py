# -*- coding: utf-8 -*-

import argparse
import gzip
import mapbox_vector_tile

# Command-line arguments.
parser = argparse.ArgumentParser(
    description='Decodes binary-encoded MVT messages in a gzipped file.')
parser.add_argument("--mvt_file", type=file, required=True,
                    help="Path to input file with MVT message(s)")
parser.add_argument("--output_file", type=argparse.FileType('w'),
                    help="Path to output file with decoded MVT message(s).",
                    default="decoded_mvt.txt")
args = parser.parse_args()

# Decodes binary-encoded messages.
with gzip.open(args.mvt_file.name, 'rb') as f:
    data = f.read()
decoded_data = mapbox_vector_tile.decode(data)

args.output_file.write(repr(decoded_data))
print 'Decoded messages written to %s.' % (args.output_file.name)
