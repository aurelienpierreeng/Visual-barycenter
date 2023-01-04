# A wavelet transform for partial derivative equations solving

Many applications use partial derivative equations to simulate diffusion of heat, flows, molecules or pathogens. Multigrid methods have been proposed to improve accuracy and increase convergence rate[^1]. However, these schemes use interpolation extensively to upscale and downscale the discrete grids.

In signal and image processing, diffusion processes can be used for various reconstruction purposes : inpainting of missing regions, denoising, deblurring, etc. The discrete grids are obtained from experimental measurements and are usually polluted with artifacts such as noise and patterns, and using multigrid methods on them may worsen noise by sequentially upsampling and downsampling it. Moreover, most interpolation methods will affect noise variance non-linearly, except for some carefully chosen that may have other artifacts, so this can be a problem to denoise with a variance prior.

We propose to design a special wavelet transform that will break the image into a sequence of laplacian operators at increasing scale. 	

[^1]: https://en.wikipedia.org/wiki/Multigrid_method