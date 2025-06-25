// Import Typst libraries


#set page(
  margin: 0.5cm,
  paper: "us-letter",
)

#let source_folder = "HD19"
#let im_index = range(0, 37)
#let images = im_index.map(it => if it >= 10 {
  source_folder + "/000" + str(it) + ".png"
} else {
  source_folder + "/0000" + str(it) + ".png"
})

#grid(
  columns: 4,
  gutter: 1pt,
  ..images.map(it => image(it))
)
