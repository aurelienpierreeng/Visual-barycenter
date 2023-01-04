# Image processing does not kill people… and it's a shame

[toc]

Among the technical fields, quite a few have the potential to harm the public : the first that come to mind are medicine and civil engineering. Both have in common their scientific basis : studies, data, models and history form a corpus of knowledge and tools used by the practitioners to help making choices. However scientific their basis is, the practice remains an art or a craft. Indeed, while the state of the art provides models, data and methods, it is the practitioner's responsibility to identify which model applies to the current circumstances, which tools are the best suited to the current situation, and which are the priorities that will make the best solution stand out of the reasonable ones. 

However scientifically-based the discipline, there is still a considerable room for perception, interpretation, heuristics, political and arbitrary preferences and bad judgment, because no equation, no model, no algorithm can design a bridge by itself or chose the best treatment for a patient. But all models, equations and algorithms need to be used properly within their domain of validity, and properly interconnected to form a big picture tying data together, which will provide support for the practitioner's opinion, and lead to a decision. For these reasons, potentially-harming disciplines have : 

* ethics codes and comities, 
* uniformed methods and protocols, 
* regulations and standards, 
* practice permits, 
* obligations of continuing education for professionals, 
* a notion of *due process* and *due diligence* that requires every professional to do their job to the full extent of their abilities, following the state-of-the-art procedures for which they need to stay updated, 
* a duty toward the public, of impartial counseling and fair advertising.

Ethics and due process, unfortunately, is an estranged notion for the non-harming technical fields such as image processing and many others — despite being just as scientific as the harming kind — which provides an excuse for negligence, lack of rigor and overall laziness. Lower stakes seems to make scientific method a moot point or even an optional constraint, enable amateurism and *laissez-aller*. While such negligence will not kill people, it will however mislead, misinform and lose everyone's time and money in the saddest way : one that could have been avoided.

## Do the right thing, the right way, at the right time

Image processing, while admittedly an acquired taste, is probably one of the most beautiful thing in the world : it is science serving art, in a way that ties rational matters to unleashed creativity, in order to open possibilities and provide powerful tools to artists. But it is also an overwhelmingly complex matter connecting light spectra to hardware electronics, electronics to data, data to color perception, and color perception to display media, through optics, statistics, psychophysics, but also psychological aesthetics, art history, culture and sociology.

The only salvation comes from dividing matters into a sequential pipeline to :

1. undo image artifacts and restore the latent image (lens distortion, sensor noise, CFA patterns, clipping reconstruction),
2. correct the image to a perceptually neutral ground-truth (chromatic adaptation, color profiling, imaginary colors trimming),
3. apply creative effects (color grading, tone grading, creative distortions),
4. prepare the image for the output display medium while trying to :
   1. account for the medium technical limitations (gamut of the color space, dynamic range, quantization),
   2. account for the original artist intent (retain the original relationships between tones and colors).
5. encode the image to meet standards format and/or hardware expectations.

You will notice here that most of the pipeline has nothing to do with neither art or creativity, but has to deal with input and output technical constraints. Photography and cinema are technically-defined arts, and the amount of signal processing and salvaging required in a digital era may look overwhelming.

Unfortunately, a lot of academic papers don't care about pipelines and propose standalone algorithms, supposed to work *ex-nihilo*, and therefore mostly unusable in real applications. Worse, some propose algorithms that do several things at once, like the histogram normalization methods (CLAHE and the likes) or all the infamous local tone-mapping operators. These have 3 quintessential properties that make them unsuitable for artists :

* they look like absolute shit, with unacceptable artifacts,
* they don't deal with color aside from tonalities, but as a joint side-effect,
* they aim at doing internal automatic thresholding with little user input.

Nonetheless, Drago [^1] , Reinhard[^2] and Mertens[^3] have respectively 951, 2088 and 510 citations in Google Scholar, as of feb. 2021, and I have had to fight software developers on the merits of these algorithms only to meet arguments based on their number of citations, while not addressing the elephant in the room : they over-complicate things by working in wrong color spaces (OETF-encoded, display-referred RGB) and, again, look like absolute shit. I mean no offense to their authors, they come from 2002, 2003 and 2007 and were probably meant for processing in 8 bits unsigned integers, but in the 2020's, we can do better and shield-walling behind the number of citations is unacceptable as an argument.

Working in the right space is paramount in image processing. Electrical signal processing has several transforms to send signal to spaces where they exhibit specific properties that make them easier to work with :

* the Fourier transform, using frequential representations,
* the Laplace transform, generalizing the Fourier one,
* the Z transform, discretizing the Laplace one,
* the wavelets transforms, blending the frequential properties of Fourier analysis with spatial properties to allow multi-scale analysis.

Algebraic operations like multiplications have different meanings depending on the space they are applied in : in Fourier space, they represent a convolution product, while in spatial/time space, they represent a gain. No electrical engineer in his right mind would carelessly mix spaces for a given operation.

But image processing suffers from working in spaces that may look interchangeable, while they are definitely not :

* radiometric RGB spaces, unbounded and linear (or affine) compared to light emission intensities, representing a light spectrum as a vector of 3 integral products between the spectrum and the filters transmittance,
* display-referred RGB space, encoded with some Electronico-Optical Transfer Function (EOTF) to prepare RGB for 8 bits unsigned integers quantization, 
* radiometrically-linear perceptual spaces, supposed to represent the physiological response of the retina, like CIE XYZ 1931 2° standard observer, or CIE 2006 LMS space, or CIE 1976 UCS,
* perceptually-linear perceptual spaces, supposed to represent the psychological perception derivated from optical nerve response, like old CIE Lab 1976, or more modern IPT, IPT-HDR, JzAzBz,
* made-up, *ad-hoc* spaces decoupling lightness and chromaticity in ways that are neither perceptual nor physical, like HSL, HSV, Yuv, Yhs, etc. These spaces are anonymous vector space transforms that have no ties with real world. Yuv was introduced by TV as a way to encode color RGB TV that was retro-compatible with old monochrome TV (so they would use only the Y channel on monochrome TV sets and decode the whole Yuv pack on color sets). HSV/HSL were just a cheap way to break an RGB vector into a hue/chroma decomposition on old computers, in a meaningless way. The reason they are still in use is beyond me. 

EOTF are what the ICC still calls "gamma". It's very easy to check that $aR^\gamma + bG^\gamma + cB^\gamma ≠ (aR + bG + cB)^{\gamma}$, and yet, would you think image-processing researchers care to precise if they work in radiometric RGB or non-linear display-referred RGB when they publish ? Most of the time, they don't, and when you open the Matlab source code they usually provide along, you discover they don't bother removing the gamma when, for example, doing blind deconvolution (and it **is** a problem).

Everything physical, like removing or adding optical blur or photon noise, belongs to radiometric RGB : it's the closest we can get to pure light. **But** the space is not all, we also need to ensure our radiometric RGB has not been non-linearly tempered with yet. So, not only do we need to care about the space in which we work, but also about signal's history and traceability. 

Display-referred is worth shit to us : it's neither physical nor perceptual. It is only good to prepare images for quantization when using unsigned integer encoding. Display-referred breaks alpha compositing[^4], yet blend modes like overlay and screen rely on it by implying 50 % encodes middle grey[^5]. How nonsensical is that ?

Perceptual spaces, either radiometrically or perceptually encoded, are what we need for all things color : hue/chromaticity decomposition, gamut mapping, GUI controls to pixel operations parameters. RGB is not color, radiometric RGB encodes a light spectrum at some intensity into a tristimulus at some intensity, display-referred RGB encodes shit (in case you missed it). So real color needs to be dealt with in perceptual spaces where chromaticity means something.

Any algorithm using something neither perceptual nor physical defined, like HSV or HSL, is basically using a space that doesn't exist. These are a flawed polar decomposition of an otherwise cartesian space. What most people don't know is HSL/HSV decompositions are actually contextual to the original RGB they are computed from. HSL from Rec 2020 is not the same as HSL from Rec709, so HSL/HSV are methods to transform cartesian coordinates into polar ones, following the diagonal of the RGB cube, but are not defined spaces (let alone standardized). Also HSL will simply not work for scene-referred (unbounded) signals, since $S = \frac{\max(RGB) - \min(RGB)]}{2 - \min(RGB) - \max(RGB)}$ will yield a negative saturation whenever $\min(RGB) + \max(RGB) > 2$, and since the saturation is supposed to represent the distance between a color and the achromatic axis ($R = G = B$, hence the diagonal of the RGB cube), it cannot be negative. So, in addition to representing nothing, it even fails at even doing its job if you don't mind its domain of validity.

Regarding perceptual spaces, there is still a cult of CIE Lab/Lch 1976, probably the legacy of some Dan Margulis guy, specialized in overcooked 2000's pictures that did not age well, where greens look toxic, skies look like neons and contrast is cranked all the way to the top. CIE Lab has many flaws, that have been demonstrated over the years (it's actually not hue linear, not even uniform across the dynamic range, and obviously not suited for HDR), and more importantly, it's old and we have better. Yet every moron image dev sees CIE LCh, the polar variant of CIE Lab, as some sort of better HSL that saves kittens and keep you warm at night. Do you treat your cold with bloodletting ? So why are you still using old crap when we know better ? 

[figure align="center"]
![](https://eng.aurelienpierre.com/wp-content/uploads/sites/8/2021/02/hue-linearity.jpg "Title")
[figcaption]

The legendary hue linearity and uniformity of CIE Lab/Luv 1976 compared to IPT from Fairchild, IC~T~P~T~ from ITU-R BT.2100, CIECAM 2016 UCS, and JzAzBz[^7] (picture from [^7]). This practically means :

1. pushing chroma radially along the same polar angle (dashed lines) does not actually result in a constant perceptual hue (dotted lines), especially reds and blues have a very large deviation, which is a shame considering skin tones lie in the red range and blue is the color range where human vision is the most sensible to small variations,
2. a 25 % push of chroma results in non-uniform perceptual color steps depending on the hue, especially the cyan radial coverage is much more compacted than blue, green or red.

[/figcaption]
[/figure]

Perceptual spaces are very limited in what they can achieve, and again it only has to do with color remapping. They will be mostly great for GUI controls, which parameters will be converted to RGB and sent to RGB pixel code, because they provide perceptually uniform controls that behave well. But not every developer in the joint is aware of the model-view-controller paradigm[^6], so many of them don't even imagine that the GUI controls could work in CIE Lch while the pixel code runs in large-gamut RGB like Rec 2020 and the final view is converted to sRGB.

Pixel algorithms, at least the good kind, tend to digitally model real-life phenomenons. Like all scientific models, they have a domain of validity, a set of base assumptions and working hypotheses. Using non-radiometric spaces to perform optical operations is as wrong as using subsonic fluid dynamics to design a supersonic aircraft. Except people won't die of bad image processing design, so the image dudes get sloppy and think they can violate basic epistemology. No, **you simply don't use a model outside of its domain of validity and outside of the space in which it is defined**. 

Just the same, doing operations in the wrong order is wrong too. If a non-linear transform or, worse, a non-invertible transform, has been applied earlier in the pipeline, you can go to a "radiometric" space all you want, it's not radiometric anymore. Order of operations matters because traceability of the signal matters. Stacking filters on top of each other, treating them blindly as generic black boxes, will get you full speed in the wall and applying the proper color space conversion to go in the right space won't exonerate yourself from double-checking signal traceability.  

Finally, shield-walling behind standards is not going to do the trick either. Standards cast in stone methods and protocols already in use, they rarely define new methods before they are actually used, and they are only good for intercommunication between black boxes, by defining the expected state of the signal at the junction between the boxes. Standards are contextual to an application, which defines their scope and their necessary trade-offs, but referencing and abiding by standards will not exonerate you from checking if your particular application fits within their scope and in what measure. Fact is many engineers love standards because they think it is only a matter of following them and letting their brain rest in the process. Many color and imaging standards and specifications are stupid, ignorant, and written by normalization freaks who have never pushed pixels, based on 30 years-old research, starting with the ICC, PNG, SVG and W3C CSS ones (incidentally, you will find they share the same idiots on their board). Also, many of these standards try to account for the lowest common denominator and aim at producing numerical methods able to run on low-end and embedded CPU, which is completely out of the scope of modern multi-threaded and GPU-offloaded image processing applications.  

## But it looks good…

The usual excuse to forgive sloppiness on theory and epistemology violation is this : it looks good. To whom ? In which conditions ? Under which settings ? On which samples ? All these are variable-geometry heuristics. And when it doesn't look good anymore, it is because the parameters of the faulty algorithm have been pushed too far. How convenient is that ?

There is incredible hubris in the digital computing world for trying to break free from the real world and inventing anonymous color transforms that have no ground in real life, that is either photons physics or psychophysics. Smart-asses like such are responsible from creating an image processing monster that has no link with legacy analog processing whereas light is still light, color is still color, so basically all the same concepts still apply but are now tied and manipulated with anonymous parameters expressed as unit-less values disconnected from legacy and practice. The consequence is the digital processing world has not built on top of analog legacy, but aside of it, and has confused not only experienced analog photographers switching to digital, but also the new generation of digital kids willing to try analog photography. The consequence is knowledge acquired either in digital or analog is simply not transferable to the other… while cameras still have the same shutter speed, ISO and aperture settings in both cases, and still record the same light.

Meanwhile, the 3D rendering world has gone to great lengths to accurately model photons physics to produce photo-realistic renderings that often look more credible than most digital photographs, using radiometric and even spectral spaces. In a field using brittle and temporarily valid models to represent color perception, physics not only defines the ground truth of organic-looking transforms but also the only little certainty we have about the phenomenons we try to describe, model and emulate digitally.

Pixels are not anonymous data, pixels encode a continuous light emission in a discrete, sampled fashion. Digital sensors record light, LCD and LED panels emit light, it is a light in/light out pipeline. For millennia, painters have played with physics to mix pigments in a way that produces the expected result, while not using any perceptual color framework but only physics and chemistry, albeit not explicitly named and recognized. They have been able to train their eye and hand to predict the result of pigment mixing in the least intuitive way possible to match their expectations. Here again, the model-view-controller architecture is of the essence : the model and controller being physically defined do not prevent the view and result to be purely perceptual. 

Looking good or not is not for the researchers or the developers to decide, because both have artists to serve and only artists will decide. Also because researchers have already deemed "aesthetically pleasing" results that were beyond unusable, so to everyone's his job. But what actually matters to artists is not so much how good it looks "out of the box» than how close from their intent and expected result they can push the output of the algorithm. Also, no empiric test can ever be exhaustive enough to ensure that an *ad-hoc*, empirical method, will "work" all the time, all the more if "working" is defined in terms of subjective aesthetics, mainly because aesthetics preferences depend on *habitus*[^8], in which art[^10] and color[^9][^11] education takes a large place for the matter at hand. Just as a stopped clock is accurate twice a day, good-looking samples may well be carefully curated cases. Actually, the academic world is riddled by this guilty pleasure of finding the corner cases of some notorious state-of-the-art algorithm, design an *ad-hoc* algorithm meant to fix them, but with different corner cases, publish a paper with samples showing on-par and better results that the state-of-the-art, only to have that new algorithm mocked by the next paper that will do just the same. 

Looking good is not the purpose of any image processing algorithm. As image processing is a sequential pipeline of specialized pixel operations, each algorithm is only responsible for a achieving a specific and defined task with minimal side-effects. Looking good is the responsibility of the whole pipeline, under the supervision of the artist, not on its own. As such, each algorithm should accomplish a minimal set of tasks in a fine-grained fashion, and ideally fully separate tonal corrections (brightness and contrast) from color corrections (hue and chroma). Yet the trend is to pack as many features as possible in algorithms that provide a "two-clicks magic" to untrained users yearning for complex software that can dispense them from learning complex skills.

The quality of an algorithm is to be evaluated solely against its goal, which should be defined in terms of either color properties or reconstruction fidelity. Given the whole set of pixel operations, mandatory to prepare a raw sensor reading for display, each requirement is to be broken into basic operations that provide several degrees of freedom for the users to drive the unavoidable compromises and trade-offs needed by an imperfect pipeline. Which brings us to the next point…  

## Hacking is not designing

The open-source tradition is to half-ass hacks to solve ASAP local problems hastily defined, without giving much thought about future-proofing, extensibility, scalability, reliability and usability, in the fastest way that "just works". That leaves the FLOSS ecosystem with an ever-growing constellation of non-functional and non-interoperable pieces of software, each of them non-working in its very own way, which overall creates an illusion of choice : real choice is made between fully workable options, not between non-working ones failing at different times. All this is permitted by open source licenses stating the software is "provided as-is", "for what it is worth", "in case it helps", and "without guaranty". Acceptable for toys, not good enough for tools, regardless of paid development or not. The matter is simply ethical. 

As the artificial intelligence field is growing in staff and applications, end users are tempted to perceive software more and more as a clever object performing advanced operations like taking decisions on its own based on data hidden to the user. But, as Hertzmann states[^12]:

> Today, the most-successful AI and machine learning algorithms are best thought of as glorified data-fitting procedures. That is, these algorithms are basically like fitting a curve to a set of datapoints, except with very sophisticated ways to fit high-dimensional curves to millions of datapoints. 

This applies to AI, and very few pieces of software actually use true AI (regardless of what their marketing says), so what is to say about usual, non-AI, software ? Today, the most-successful image processing algorithms are best thought of as glorified darkroom enlargers. That is, these algorithms are basically like blasting more or less light through a film negative during a paper printing process, except with very sophisticated ways to control the amount of light and its spatial repartition.

An image processing software is a virtual darkroom, where paper and film are entirely simulated. Same as surgery can now be performed remotely, by a surgeon operating a robot arm from a remote interface through internet, the image processing software GUI is merely a control panel for the robot arm manipulating a film remotely. Except the film is not in another country but in another dimension : a virtual one created from data. So there is no magic in software, only remote control of real processes simulated in the matrix. 

As such, the purpose of good software is to provide users ways to remotely access their image and modify their properties from outside the computer. Software is not to be clever or make decisions on its own, like a virtual lab technician, but to create axes of movement and degrees of freedom for a remote lab technician. This implies breaking down the whole picture process into elementary steps and assessing what degrees of freedom are necessary to complete each step in a way that comes close to the artist's intent and visual expectations. 

This is **design** : 

1. starting with the needs of one human being, 
2. translating those human-defined needs into a technical problem, 
3. breaking that technical problem into elementary technical tasks, 
4. identifying the goals, constraints, scope and success/failure criteria for each task (that will point to validation tests), 
5. finding a set of degrees of freedom that can help the human being to control each task to favor one preferred solution among the set of possible solutions,
6. binding these degrees of freedom into an unifying model that will output a result from an input under supervision of the human user,
7. translating this unifying model into a computationally-efficient algorithm that can actually run on a consumer's computer, 
8. providing a meaningful interface to the human being to control each and every degree of freedom of the model. 

Design is not jumping head first into an IDE, prototype code that will never be anything more than a prototype, butcher a GUI that gives access to anonymous parameters, and release the result as "open-source software". It requires :

* careful translations of user desires, 
* complete understanding and careful definition of the problem, 
* careful identification of the success/failure criteria, 
* *due process* on the background searches to come with a theoretically sound model, based either on psychophysics or on simple physics, to abide by previously known behaviors. 

But designers also often overlook a very important aspect of design : the scope of the solution. It is composed of two parameters : 

* the target user,
* the target conditions of use.

Indeed, training and education condition a lot user expectation, perception and obviously ability. For example, it has been shown that subjects trained to color theory have an average *Just Noticeable Difference* of 1.5 (minimum CIE $\Delta$E 1976 color difference between 2 seemingly-different colors) while untrained subjects range at 2.8[^13]. Trying to accommodate both beginner and experienced users is therefore foolish and will probably end up frustrating both. But even for similarly trained professionals, photo-reporters covering the Olympic Games and live-feeding their pictures directly to the news room have very different working conditions and expectations than fine-art photographers, working at a slower pace but seeking higher end results, or even fashion photographers, seeking the same high end results but with a larger team and at a faster pace.

Notice that designing for an "average" user is just as foolish as designing for everyone. When talking to users, you will notice they all claim to be the epitome of the average user, with no backing statistics, and no matter their level of practice, skills and expectations. That is a grown-up way to say they want you to care and design for them because they matter. But even if there was such a statistically-accurate average available, average is a metric supposed to model the center of mass of the user range. Yet the center of mass of a hollow body can well be outside of its material envelope, so nothing guarantees that the statistically-accurate average user actually matches any existing and definite class of users. And we are back to square one : designing for an average might well be designing for no-one real. So at the end, who you design for is solely a matter of choice and politics, and don't even try to hide behind stats to avoid stating your personal ethics on the matter. 

##  What is a good algorithm anyway ?

Theoretically, a good algorithm is one that fulfills user's needs while taking into account their training and expectations, with perfect color science and no side-effects. In practice, of course, it is more nuanced. 

First of all, accurate color science leads to many degrees of freedom. For example, the CIECAM 02 adaptation model defines 6 dimensions of colors : hue, lightness, brightness, chroma, colorfulness and saturation[^14]. This will go against ease of use and, without proper training, might be off-putting for a lot of users, especially since lightness/brightness or chroma/saturation/colorfulness seem totally interchangeable in common language. That is where knowing for whom you design is paramount.

But even so, state-of-the-art color science still barely qualifies for "accurate" and, while fairly usable, is still brittle, imperfect and soon-to-be superseded. All perceptual color models are fitted on top of experimental data, recorded on samples of 12 to 20 persons usually recruited among the under-graduate students of the researcher who publishes the paper. Hell, universities are poor and the time where professors customarily traveled first class at the expense of their employer is long gone. So, let's say we know a lot about how the undergrad student's of the Rochester Institute of Technology perceive color, and we only have to hope that the rest of the World sees the same. In addition, color data are acquired within a certain range of luminance, so SDR models can't be scaled nor extrapolated to HDR, and current HDR models are designed for a peak luminance of 10.000 Cd/m²[^7], without being usable above. 

As stated above, perceptual color spaces are best fitted for color adaptation, at the output of the image pipeline, for example to adapt colors to another medium white point or to compensate for the viewing conditions in the final image (surround lighting, noticeably).

Then, a good algorithm uses transforms that are mathematically sound :

* definite, positive and continuous over the whole working range,
* $C^1$ and if possible $C^2$ over the whole working range (meaning the transform is derivable 1 to 2 times, and the derivatives are continuous),
* monotonic by design or within a certain safe parameters range,
* invertible (meaning continuous and monotonic), which is important to be able to solve or pre-compute suitable algorithm parameters from external data or constraints (so the solution is unique),
* the asymptotic behavior should match a physical behavior : for $f(x) = y$, what happens to $y$ when $x \rightarrow 0$ and $x \rightarrow +\infty$ ? (dampening or steady-state) 
* numerical undeterminations like division by 0, power of negative numbers, etc. should be avoided and gracefully handled when they cannot be avoided.

Zero-valued pixels need a special care as to what they represent. Since RGB values are re-encoded at the beginning of the pixel pipeline to normalize them between 0 and 1, the meaning of a "0" RGB data is "lower bound of the range", which is to be semantically mapped to a non-zero luminance on the scene and on the display. However, 0 is a neutral element for many algebraic operations and will yield a special behavior in these operations, compared to the rest of the range, while this data represents something not special in regard of the light emission it represents. 

After the maths issues, a good algorithm is computationally sound : 

* avoid pixel-wise heuristics and branching to enable proper SIMD vectorization,
* prefer linear operations if possible, rather than transcendent functions,
* limit I/O use and deal with a minimal number of neighboring pixels,
* prefer separable convolution filters if possible,
* treat R, G, and B channels in the most uniform way possible,
* collapse pixels loops as much as possible, to limit I/O.

Internal assumptions of algorithms regarding signal state and workflow should be reduced to the strict minimum, advertised and documented, and there should be some flexible way to change them at runtime. This is not only to plan for future changes, but also to leave a backdoor to fix developer's mistakes (implementation-wise or theory-wise) and provide users with a kill-switch. Ideally, algorithm should have a modular architecture that allows refining or replacing some parts without changing the whole algorithm. But, of course, a modular architecture is going to be more challenging for the compiler to optimize (if possible at all), so there is a trade-off to find. 

The step #4 of the above design sequence is about identifying the goals, constraints, scope and success/failure criteria for each task. For example, for a tonal operator, we could have :

> * **goal** : increasing/decreasing contrast,
> * **constraints** : leaving chromaticity unchanged,
> * **scope** : local, piece-wise
> * **criteria of success** : 
>   * piece-wise $C^2$ continuous transform,
>   * smooth transition between pieces
> * **criteria of failure** :
>   * halos between pieces,
>   * gradient reversals.

The constraint of leaving chromaticity unchanged is important to defer color adjustments to another step and avoid messing with prior color adjustments, because this operator is about tones. This set of specifications points towards a local tone-mapping operator, but immediately discards gaussian filters (producing halos) and bilateral filters (producing gradient reversals). This leaves us with local laplacian, edge-aware wavelets, guided filters, and adaptative manifolds as possible choices.  

If we were to go to step #5, finding a set of degrees of freedom that can help the human being to control each task to favor one preferred solution among the set of possible solutions, we could immediately thing of 3 degrees of freedom :

1. the slope of the transform (actual contrast $\frac{\mathrm{d}T(x)}{\mathrm{d}x}$),
2. the point around which the slope pivots (neutral value where $T(x) = x$),
3. the boundaries value conditions (shape and blending of the transform, rate of convergence toward boundaries),
4. the radius of the pieces to process (for the local filter),
5. the rate of transition between included and excluded patches (edge sensitivity of the local filter),

This gives a minimal set of parameters for an user to define a large set of contrast transforms and will yield a class of suitable functions (polynomials, splines, radial-basis functions, sigmoids, etc.). 

The quality of the algorithm is therefore solely asserted by its respect of the constraints and the criteria. Given that the end user is provided with several parameters to control the intensity, shape, radius and sensibility of the algorithm, as far as we are concerned, output look is none of our business. We only aim at building a model, a framework, that will give remote control to the user over the image local contrast. **The user will do the driving**, we only need to ensure the stirring wheel rotates fast enough and the gear stick is not too stiff. 

The most important point to ensure is to do only one thing at a time, otherwise our separate pipeline steps are not going to be orthogonal to each other, which will yield circular editing and trouble for the user. 

Finally, the property of a good algorithm is to fail gracefully. That is, we know beforehand that parameters cranked up all the way to the top will produce an ugly result, and asserting the visual quality of an algorithm is such circumstances will tell us nothing. However, asserting the conservation of the design constraints along the transform (like the absence of halos or the conservation of chromaticity), even with "unreasonable" parameters indicates its ability to carry on with its task no matter the circumstances. A good algorithm simply meets its design goal reliably, no matter how the image looks. We can work on improving consistent and reliable failure, but we can't do anything about random failure. 

## Asserting the quality of image processing algorithms

Here is a non-exhaustive list of things to check taken from my experience :

* for demosaicing and sharpening methods, ensure that :
  * periodic patterns of period $\approx$ 1 px do not create moiré,
  * sharp diagonal edges do not create aliasing (stair-casing effect),
  * noise does not get coarser or more intense,
  * RGB plates do not get decorrelated (chromatic aberrations at edges),
* for sharpening methods, ensure that : 
  * no artificial patterns (crosses, rings) are created,
* for any color correcting method, ensure that : 
  * colors in-gamut at the input stay in-gamut at the output,
* for chroma/saturation correcting methods, ensure that : 
  * hues are preserved unchanged between input and output,
  * luminance is preserved (only for chroma),
  * any chroma boost applied on achromatic color results in a no-operation,
* for hue correcting methods, ensure that : 
  * luminance and chroma are preserved unchanged between input and output,
* for local/global tone (contrast, brightness, luminance) correcting methods, ensure that :
  * chromaticity (hue and chroma) is preserved unchanged between input and output,
  * contrast is not reversed unless explicitly set this way, 
  * the tonal transitions are smooth and no posterization artifact is created,
* for local tone correcting methods, ensure that :
  * no halos and other edge artifacts are created,
  * global luminance relationships between areas are preserved, that is areas brighter than the surround in real life remain brighter at the output,
* for low-pass, blurring and convolution filters, ensure that :
  * no fringes are created on edges between saturated colors.
* for any layered masking methods (using alpha), ensure that :
  * no fringes happen at the boundaries of the masks, 
  * compositing layers painted with gradients over solid primary colors does not create fringes in the middle of the gradient,
  * compositing 3 layers painted with solid primary colors (R, G, B) blended in addition over of a black opaque matte results in achromatic white,
* for any rotation and distortion method, ensure that :
  * solid sharp colorful geometries over a background of the opponent color doesn't yield fringes at edges

![](https://eng.aurelienpierre.com/wp-content/uploads/sites/8/2021/02/etoile-inkscape.png)
*Bad alpha implementation in display-referred non-linear RGB (Inkscape 1.0.2) : green star over red background, 100 % opacities – notice the brown fringes along edges and the aliasing. Partial occlusion models rely on an optical interpretation of the RGB signal.*

![](https://eng.aurelienpierre.com/wp-content/uploads/sites/8/2021/02/etoile-krita.png)
*Good alpha implementation in scene-referred radiometric RGB (Krita 4.4.2) : green star over red background, 100 % opacities – no fringes*

![](https://eng.aurelienpierre.com/wp-content/uploads/sites/8/2021/02/etoile-krita-tourne-non-lineaire.jpg)*JPEG sRGB file drawn from Krita (from above) in scene-referred RGB, re-opened and rotated in Krita 4.4.2 : bad implementation, sRGB EOTF is not undone before rotation – notice the brown fringes along edges*

![](https://eng.aurelienpierre.com/wp-content/uploads/sites/8/2021/02/etoile-krita-pivote-gimp.jpg)*JPEG sRGB file drawn from Krita (from above) in scene-referred RGB, opened and rotated in Gimp 2.10.22 : good interpolation,  sRGB is undone before rotating and redone after – no fringes*
    
![blur comparison](https://eng.aurelienpierre.com/wp-content/uploads/sites/8/2021/02/blur.jpg)
*Left : gaussian blur applied on scene-referred radiometric RGB ; Right : gaussian blur applied on display-referred sRGB EOTF RGB – Notice the fringes on the right.*

All of the interpolation, rotation and convolution problems illustrated above fall back to the same mistake. Let : 

* $G(x)$ be a general convolution filter such that $\int_{\Omega}G(\Omega) \mathrm{d}\Omega = 1, \Omega \subset \mathbb{R}^n$ for a continuous filter, or $||G(x)||_{p,q} = 1, x \in \mathbb{N}$ for a discrete filter,
* $u(t)$ be the radiometrically-scaled signal,
* $y(x) = x^\gamma, \gamma \in \mathbb{R^*}$ be an ordinary power-like EOTF encoding, 
* $u^\gamma(t)$ be the EOTF-encoded signal. 

$G$ could, for example, be a gaussian filter $G(x) = \frac{1}{\sqrt{2 \pi} \sigma} e^{-\frac{x^2}{2 \sigma^2}}$, or a 2D rotation kernel of angle $\theta$  : $\left[\begin{matrix} \cos\theta & -\sin\theta\\\sin\theta & \cos\theta\end{matrix}\right]$.

The general 1D convolution product of a signal $u(t)$ followed by the EOTF is :
$$
(u * G)^\gamma(t) = \left|\int_{-\infty}^{+\infty} u(t - x) G(x) \, \mathrm{d}x \right|^\gamma \neq \int_{-\infty}^{+\infty} u^\gamma(t - x) G(x) \, \mathrm{d}x
$$
Applied to a discrete space with a finite filter of width $n$, the equations becomes : 
$$
(u * G)^\gamma(t) = \left| \sum_{i = -n/2}^{+n/2} u(t - i)G(i) \right|^\gamma \neq \sum_{i = -n/2}^{+n/2} u^\gamma(t - i)G(i)
$$
The second member shows a physically-accurate convolution filtering the optical signal as-is, that is what would have happened if we physically rotated the paper sheet on the table or placed a lens in front of a video-projector. The third member shows the equation applied by all the faulty fringing implementations, like the CSS3 effects and compositing, Gnome desktop compositor, Inkscape drawing, Krita rotation and interpolation, etc. 

## Conclusion

Image processing is linked to something fun : taking or making pictures. For most people, this is merely a hobby. But you know what else is fun ? ~~Flags~~ Doing things correctly. 

For artists, image processing software is no toy but a working tool. Reliability and fine-grained control are of the essence. Lack of due process and negligence will make everyone's work more tedious but will also hold back imaging applications for years, especially if mistakes happen in the core architecture design (like alpha compositing).

It is often a simple matter of caring about the domain of validity of the models used and about the properties of the vector spaces used to process pixels. Any vector space is a proxy for a real-life aspect. Therefore, it is also a matter of caring about the links between pixels operations and their real-life meaning, and trying to enforce pixels transforms that make sense on a physical level. Our imaging pipeline has photon physics at both ends anyway, and it simply does not make sense that rotating a picture printed on a paper sheet doesn't yield the same visual result as rotating the same picture in software, or timing primary lights under a color enlarger does not yield the same visual result as dialing RGB gains in software, or blurs do not look the same when applied digitally or physically. 

The overhead of doing proper design might sound tedious, but it actually saves everyone's time on the long term. **Badly designed features are more damageable than no features at all**, since users will still try to, not only make them work, but also to make sense of them and to adapt to them. When properly designed features emerge, they might get more confused than helped, and simply resist the change. Bad tools are more than bad tools, they impregnate user's habits and understanding, they do cognitive damage that will need work later to be reversed, making everyone lose time and energy in the process. All that **for something that could have been avoided in the first place**, if due process had been enforced.

I beg you, treat image processing as if it could kill people and take all available measures to commit clean designs, sound on a theoretical level, doing minimal assumptions, and with users bypasses, kill-switches and clutches everywhere something is automatically done by the software. That is all a researcher, designer, engineer or developer can do. It is not our place to decide what looks good or not, but only to provides users ways to remote-access their images, from outside the computer to within the matrix, that can be manipulated by them to get the results they expect. That is to say, users who randomly fiddle with GUI controls with no clear intent on the visual result are not really a target crowd for design. 

[^1]: DRAGO, Frédéric, MYSZKOWSKI, Karol, ANNEN, Thomas, *et al.* Adaptive logarithmic mapping for displaying high contrast scenes. In : *Computer graphics forum*. Oxford, UK : Blackwell Publishing, Inc, 2003. p. 419-426.
[^2]: REINHARD, Erik, STARK, Michael, SHIRLEY, Peter, *et al.* Photographic tone reproduction for digital images. In : *Proceedings of the 29th annual conference on Computer graphics and interactive techniques*. 2002. p. 267-276.
[^3]: MERTENS, Tom, KAUTZ, Jan, et VAN REETH, Frank. Exposure fusion. In : *15th Pacific Conference on Computer Graphics and Applications (PG'07)*. IEEE, 2007. p. 382-390.
[^4]: Even Wikipedia knows it : https://en.wikipedia.org/wiki/Alpha_compositing#Composing_alpha_blending_with_gamma_correction
[^5]: https://en.wikipedia.org/wiki/Blend_modes#Overlay
[^6]: https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller
[^7]: SAFDAR, Muhammad, CUI, Guihua, KIM, Youn Jin, *et al.* Perceptually uniform color space for image signals including high dynamic range and wide gamut. *Optics express*, 2017, vol. 25, no 13, p. 15131-15151. https://www.osapublishing.org/oe/fulltext.cfm?uri=oe-25-13-15131&id=368272
[^8]: https://en.wikipedia.org/wiki/Habitus_(sociology)
[^9]: RISTIC, Ivan, STANKOVIC, Sasa, et PARAVINA, Rade D. Influence of color education and training on shade matching skills. *Journal of Esthetic and Restorative Dentistry*, 2016, vol. 28, no 5, p. 287-294.
[^10]: NODINE, Calvin F., LOCHER, Paul J., et KRUPINSKI, Elizabeth A. The role  of formal art training on perception and aesthetic judgment of art  compositions. *Leonardo*, 1993, vol. 26, no 3, p. 219-227. https://doi.org/10.2307/1575815
[^11]: KERUN, Li, CAIJIN, Zhang, et YAO, Wang. Research on the difference of  architecture color harmony and color preference between observers with  and without professional background. In : *2016 International Conference on Advanced Materials for Science and Engineering (ICAMSE)*. IEEE, 2016. p. 665-668.
[^12]: HERTZMANN, Aaron. Can computers create art?. In : *Arts*. Multidisciplinary Digital Publishing Institute, 2018. p. 18. https://doi.org/10.3390/arts7020018
[^13]: FERNÁNDEZ-VÁZQUEZ, Rocío, STINCO, Carla M., HERNANZ, Dolores, *et al.* Colour training and colour differences thresholds in orange juice. *Food Quality and Preference*, 2013, vol. 30, no 2, p. 320-327.
[^14]: FAIRCHILD, Mark D. Color appearance models. *John Wiley & Sons*, 2005, 2nd edition, p.271-273.