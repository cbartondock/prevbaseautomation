# Automated prevbase manufacture for SSBB
## Directory Structure
The usage here is fairly straightforward. There are three directories: `buttons`, `inputs`, and `outputs`. You don't need to worry about `buttons` unless you want to replace the images of the gamecube buttons I have therein, in which case be my guest!

The inputs directory should be filled with directories that are named after the stages you want to make prevbases for, eg:

```
inputs/
  battlefield/
  temple/
  hyrule/
```

Each stage directory should have a subimages directory (for alternates - this directory can have anywhere between 0 and 10 images), and a base stage image (whose name doesn't matter), eg:

```
temple/
  subimages/
  temple_image_name_irrelevant.png
```
 
Finally, the subimages directory should contain all the screenshots of alternate stages named with their button combination (buttons separated by underscore), eg:

```
subimages/
  Z_X.png
  L_Z_R.png
  UP_Z.png
```

## Configuration File
Finally we come to the config file `config.txt`. It has several options, all of which are self explanatory (and explained via comments in the config file itself). They are

  * shear: A decimal between -1 and 1, <0 means the top of the image
  moves right, >0 means the top of the image moves left. Typically
  you will want to stay between -.1 and .1 but I left it open.
  * buttonopacity: A decimal between 0 and 1, pretty self explanatory.
  * buttonsizeboost: A decimal between -1 and 1, >0 increases button size, <0 decreases buttonsize. Again going that far from 0 isn't useful.
  * posterize: An integer between 1 and 8, or any negative number if you want to disable posterize (it is disabled by default). The integer represents the number of bits you are reducing the color to, ie 1 is the most posterized and 8 the least. 
  * solarize: An integer between 1 and 256, or any negative number if you want to disable solarize (it is disabled by default). The integer represents the value above and including which colors will be inverted, ie 1 inverts the image and 256 does nothing.
  * borderwidth: An integer between 1 and 20 or any negative number if you want to disable borders. The integer is the width in pixels of the separating borders.


That's it! Just run build the prevbases via `python prevbase_maker.py` and your files, correctly named after your stages, will be in the `outputs` directory. The program does all the thinking about layouts and where buttons should go for you, and so long as your screenshots are good it will just work.
