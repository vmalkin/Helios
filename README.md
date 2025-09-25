# Helios
Refactor of the gigantic mess that is the Helios GOES image monitoring software!

- Download and process the LASCO Coronagraph images.
  - Remove Speckle from particle hits.
  - Perform a convolution of the LASCO image to enable automated CME detection.
    - Account for satellite rotation that shifts the suns position from it's assumed "centre" of the image.
- Download the process the SUVI GOES images in 3 wavelengths.
  - Create false colour image emphasising coronal holes.
    - to be used for SOlar Wind forecasting.
  - Create false colour difference images to emphasise Earth-facing CME.
