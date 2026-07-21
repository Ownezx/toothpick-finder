// Import Typst libraries


#set page(
  margin: 0.5cm,
  paper: "a4",
)

#let source_folder = "../apriltag-imgs/tagStandard41h12/"
#let im_index = range(0, 40)
#let images = im_index.map(it => if it >= 10 {
  source_folder + "/tag41_12_000" + str(it) + ".png"
} else {
  source_folder + "/tag41_12_0000" + str(it) + ".png"
})

#grid(
  columns: 4,
  gutter: 8pt,
  ..images.map(it => image(it, width: 100%))
)
