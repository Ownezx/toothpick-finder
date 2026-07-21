// For work notes
#import "@preview/drafting:0.2.2": inline-note, margin-note
#import "@preview/chronos:0.2.1"
#import "@preview/fletcher:0.5.8" as fletcher: diagram, edge, node
#import fletcher.shapes: house

// Font and text size example
#set text(size: 13pt)
// Paragraph setup
#set par(
  justify: true,
)


// Setting the indenting for
#set list(indent: 2em, body-indent: 1em)
#set enum(indent: 2em, body-indent: 1em)

// Page setup and margin
#set page(
  paper: "a4",
)

// make links blue and underlined
#show link: set text(fill: rgb(0, 0, 255))
#show link: underline

// Heading vertical space and numbering
#set heading(numbering: "1.")

// Page numbering
#set page(numbering: "1")

// This is to simplify the creation of narrow no break
#show "_": sym.space.nobreak.narrow

// Setup for the sequence diagram style
#let sequence_webserver_color = rgb("#d4d4d4")

#align(
  center,
  text(2em)[
    *Technical documentation for\ toothpick-finder*
  ],
)


#v(2em)

#outline()

#pagebreak()

= Overview

== Context

When the process behind mapping nodes (i.e., points in which the plant has rooted in the soil) can be very time consuming, repetitive and labor intensive for the following reasons:

+ Indicators of nodes must be placed in the ground
+ These indicators are then mapped on a 2d transparent surface while separating each plant
+ This data then need to be entered accurately in a digital format

Such methodology can lead to errors in the data-gathering process and difficulties evaluating the margin of errors of our measurement.

== Software

This software, although in its infancy, aims to replace steps 2 and 3 to facilitate the process and make it more reliable.

+ Indicators of nodes must be placed in the ground
+ 2D reference images (fiducial markers) should be placed
+ Photos should be gathered in a circular pattern and at two different heights while moving around the targeted plot of land
+ The software would resolve photo location and estimate marker placement.
+ A manual verification step by the operator would be necessary to verify
  - Adequate identification of node markers
  - Adequate identification of fiducial markers
  - Correct plant individal identification
+ A 3D map of the plot would then be automatically generated

= User Manual

This section covers the steps to create a dataset for use in the software.

== Materials

Before going on the field several

- A phone with a decent camera, the software was tested with an Iphone 16e
- Wooden squewer sticks of approximately 20_cm long
- Several different colored paint plus white paint
- White styrophoam balls of about 2.5_cm in diameter
- A printer

Print the calibration sheet and the markers from the ToPrint section of the toothpick repo. These are the tags and calibration checker pattern used with the program.

== Placing markers

== Photo taking method

== Data processing using toothpick-finder

== Data analysis using python

= Fiducial markers

Fiducial markers are reference material on an image to have a reference object with known size and position on an image. In the context of this software, two different kinds of markers will be used, 2D markers for localization and surface topology, and 1D markers for plant node position and identification.

== 2D Fiducial Markers

During review several 2D marker types were found:
- AprilTag @wangAprilTag2Efficient2016
- ARTag @fialaARTagFiducialMarker2005
- ArUco @garrido-juradoAutomaticGenerationDetection2014
- STag @benligiraySTagStableFiducial2019

There are three roles for these fiducial markers:
+ Have a reference objects for camera position
+ Define the plot area for measurements
+ Allow a pre-computing camera position using overlapping tags

Although STag was tested initially, the python wrapper was not reliable and was causing segfaults @benligiraySTagStableFiducial2019.

== 1D Node position markers

These markers are placed in the ground at each nodes

= Technical implementation

== Camera position solving

== 1D marker detection

The 1D marker estimation relies on two steps, the first is to detect lines in each pictures, then, using overlaping picture to estimate the 3D position of the marker.

=== Line detection


#inline-note([Continue literature review here: https://github.com/Vincentqyw/LineSegmentsDetection])
// LSD (Line Segment Detector) , EDLines, Hough Transform, Learned detectors (e.g., L-CNN, SOLD²)

@akinlarEDLinesRealtimeLine2011

=== Line matching

@weiRobustLineSegment2021

LIMAP: @Liu_2023_LIMAP

== Node position estimation


#bibliography("refs.bib")
