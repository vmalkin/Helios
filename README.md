# Helios
Refactor of the gigantic mess that is the Helios GOES image monitoring software! Mostly, this repo is a bucket of older GOES image processing applications. There's a lot of code thats in include files as functionality was added, so I want to shrink some of this down. 

- Download and process the LASCO Coronagraph images.
  - Remove Speckle from particle hits.
  - Perform a convolution of the LASCO image to enable automated CME detection.
    - Account for satellite rotation that shifts the suns position from it's assumed "centre" of the image.
- Download the process the SUVI GOES images in 3 wavelengths.
  - Create false colour image emphasising coronal holes.
    - To be used for solar wind forecasting.
  - Create false colour difference images to emphasise Earth-facing CME.
- Create solar wind guestimate based on SW data

This repo is a project for Dunedin Aurora, and is subject to the following [licence](http://dunedinaurora.nz/licence.html)
