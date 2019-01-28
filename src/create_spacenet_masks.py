#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import apls_tools
"""
Created on Tue Dec  5 16:56:31 2017

@author: avanetten
"""

import os
import sys
import argparse
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
code_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.append(os.path.join(code_dir, 'spacenet',
                             'utilities', 'python'))
from spaceNetUtilities import geoTools as gT
from spaceNetUtilities import labelTools as lT

def processRasterChip(rasterImage, rasterDescription, geojson, geojsonDescription, outputDirectory='',
                      imagePixSize=-1, clipOverlap=0.0, randomClip=False,
                      minpartialPerc=0.0,
                      outputPrefix=''):

    # cut Image to Size
    chipSummaryList = []
    if imagePixSize > 0:

        rasterFileList = [[rasterImage, rasterDescription]]
        shapeFileSrcList = [[geojson, geojsonDescription]]
        # cut image to size
        print(rasterFileList)
        chipSummaryList = gT.cutChipFromMosaic(rasterFileList,
                                               shapeFileSrcList,
                                               outputDirectory=outputDirectory,
                                               outputPrefix=outputPrefix,
                                               clipSizeMX=imagePixSize,
                                               clipSizeMY=imagePixSize,
                                               minpartialPerc=minpartialPerc,
                                               createPix=True,
                                               clipOverlap=clipOverlap,
                                               noBlackSpace=True,
                                               randomClip=-1
                                               )

    else:
        chipSummary = {'rasterSource': rasterImage,
                       'chipName': rasterImage,
                       'geoVectorName': geojson,
                       'pixVectorName': ''
                       }

        chipSummaryList.append(chipSummary)

    return chipSummaryList


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--buffer_meters', default=2, type=float,
                        help='Buffer distance (meters) around graph')
    parser.add_argument('--burnValue', default=150, type=int,
                        help='Value of road pixels (for plotting)')
    parser.add_argument('--filepath', type=str,
                        default='/home/ananya/Documents/data/spacenet/SpaceNet_Buildings_Competition_Round2_Sample/AOI_3_Paris_Roads_Train/')
    parser.add_argument('--imgSizePix', type=int, default=416)
    args = parser.parse_args()

    # set paths
    path_apls_src = os.path.dirname(os.path.realpath(__file__))
    path_apls = os.path.dirname(path_apls_src)
    path_data = args.filepath
    path_outputs = os.path.join(args.filepath, 'annotations')
    path_images_raw = os.path.join(path_data, 'RGB-PanSharpen')
    path_images_8bit = os.path.join(path_data, 'RGB-PanSharpen_clip_8bit')
    path_labels = os.path.join(path_data, 'geojson/spacenetroads')
    # output directories
    path_masks = os.path.join(
        path_outputs, 'clip_masks_' + str(args.buffer_meters) + 'm')
    path_masks_plot = os.path.join(
        path_outputs, 'clip_masks_' + str(args.buffer_meters) + 'm_plots')
    # create directories
    for d in [path_outputs, path_images_8bit, path_masks, path_masks_plot]:
        if not os.path.exists(d):
            os.mkdir(d)

    # iterate through images, chip, convert to 8-bit, and create masks
    im_files = os.listdir(path_images_raw)
    for im_file in im_files:
        if not im_file.endswith('.tif'):
            continue
        # chip images
        name_root = im_file.split('_')[-1].split('.')[0]
        label_file = os.path.join(path_labels, 'spacenetroads_AOI_3_Paris_'
                                  + name_root + '.geojson')
        chipSummaryList = processRasterChip(os.path.join(path_images_raw,im_file), path_images_raw,
                                            label_file, os.path.dirname(label_file),
                                            outputDirectory=path_outputs,
                                            imagePixSize=args.imgSizePix, clipOverlap=0.0, randomClip=False,
                                            minpartialPerc=0.0,
                                            outputPrefix='')
        for chipSummary in chipSummaryList:
            # create 8-bit image
            # im_file_raw = os.path.join(path_images_raw, im_file)
            # im_file_out = os.path.join(path_images_8bit, im_file)
            # annotationName = os.path.basename(chipSummary['rasterSource'])
            # annotationName = os.path.join(path_outputs, annotationName)

            im_file_raw = chipSummary['rasterSource']
            im_file_out = os.path.join(
                path_images_8bit, chipSummary['chipName'])
            # convert to 8bit
            apls_tools.convert_to_8Bit(im_file_raw, im_file_out,
                                       outputPixType='Byte',
                                       outputFormat='GTiff',
                                       rescale_type='rescale',
                                       percentiles=[2, 98])

            # determine output files
            # label_file = os.path.join(path_labels, 'spacenetroads_AOI_3_Paris_'
            #                           + name_root + '.geojson')
            # label_file_tot = os.path.join(path_labels, label_file)
            label_file_tot = chipSummary['geoVectorName']
            output_raster = os.path.join(
                path_masks, 'mask_' + name_root + '.tif')
            plot_file = os.path.join(
                path_masks_plot, 'mask_' + name_root + '.png')

            print("\nname_root:", name_root)
            print("  output_raster:", output_raster)
            print("  output_plot_file:", plot_file)

            # create masks
            mask, gdf_buffer = apls_tools.get_road_buffer(label_file_tot, im_file_out,
                                                          output_raster,
                                                          buffer_meters=args.buffer_meters,
                                                          burnValue=args.burnValue,
                                                          bufferRoundness=6,
                                                          plot_file=plot_file,
                                                          # (13,4),
                                                          figsize=(6, 6),
                                                          fontsize=8,
                                                          dpi=200, show_plot=False,
                                                          verbose=False)
    return


###############################################################################
if __name__ == "__main__":
    main()
