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

The process behind mapping points on a 2D surface can be very time consuming, repetitive and labor intensive, for example rooted nodes of a crawling plant in soil. This is due to the following reasons:

+ Indicators of nodes must be placed in the ground
+ These indicators are then mapped on a 2d transparent surface while separating each plant
+ This data then need to be entered accurately in a digital format

Such methodology can lead to errors in the data-gathering process and difficulties evaluating the margin of errors of our measurement.

== Software

This software, although in its infancy, aims to replace steps 2 and 3 to facilitate the process and make it more reliable.

+ Sticks with a high contrast to the background must be placed in nodes of interest
+ April tags should be place on the floor to represent the plane of interest
+ Overlapping photos must be taken
+ The software would resolve photo location and estimate marker placement and a 3D map of plane, node and camera position should be rendered.

= User Manual

This section covers the steps to create a dataset for use in the software.

== Materials

Before going on the field several

- A phone with a decent camera, the software was tested with an Iphone 16e
- Wooden skewer sticks of approximately 15~cm long
- Paint that allows to have a high hue contrast in the studied area
- Printed non reflective the april markers in the ToPrint folder on a rigid flat surface
- Printed calibration sheet in the ToPrint folder on a rigid flat surface

== Measurement condition

Before taking any measurements the following must be verified:
- The painted stick have a high hue contrast compared to the surrounding area, example, light blue or purple in a patch of grass with dirt
- Different light intensities may change the color of the stick leading to worse contrast, example a dark blue stick may work well in intense light conditions but may be too dark for indoor conditions
- The testing area must be in diffuse lighting conditions, ideal outdoor conditions would be uniform cloud layers during the day

You should be avoiding
  - Direct sunlight conditions
  - Rapidly changing lighting such as sunset or passing cloud
  - Reflecting surfaces


== Measurement

- Place AprilTags on the floor plane
- Place the sticks in the ground
- Set your camera to manual to avoid
  - On iphone, long press on the camera until the AE/AF lock indication apears at the top
- Take pictures in a circular manner around the target area at several levels with a lot of picture overlap\
  The begining of this video is a good example of how to take the pictures: https://www.youtube.com/watch?v=6VjA9EfkFSc

== Data processing using toothpick-finder

= Technical implementation

== Overview

The software backend uses the following steps
- Camera position solving: COLMAP @schoenberger2016mvs @schoenberger2016sfm
- Ground plane detection: AprilTag @kallwiesDeterminingImprovingLocalization2020
- Hue based stick detection: Implemented in this repository
- Stick matching (todo)
- Stick intersection with ground plane (todo)

#bibliography("refs.bib")
