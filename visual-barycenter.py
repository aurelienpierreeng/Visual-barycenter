#!/usr/bin/env python
# coding: utf-8
#
# Copyright (c) Aurélien Pierre - 2021
# https://aurelienpierre.com
#
# This program is provided without warranty and its use is under the sole responsibility of the user.
#

import sys
import argparse
import os
import numpy as np
from PIL import Image
from matplotlib import pyplot as plt
from scipy.ndimage import gaussian_filter, median_filter, laplace
plt.style.use({'figure.figsize': (20, 20), 'font.size': 22})
np.set_printoptions(precision=2, linewidth=120)

def find_barycenter(density):
    mass = density.sum()
    idx = np.indices(density.shape)
    integral_x = np.sum(idx[0] * density)
    integral_y = np.sum(idx[1] * density)
    return (integral_x / mass, integral_y / mass)


def find_first_moment(density, center):
    # we normalize it at the end to get something plottable
    sum_density = density.sum()
    idx = np.indices(density.shape)
    integral= np.sum(((idx[0] - center[0])**2 + (idx[1] - center[1])**2) * density)
    return integral / sum_density / density.size


def find_details_density(im, denoise=0.5):
    # differences of gaussians to evaluate a laplacian pyramid
    # then collapse the laplacian L1 norm of magnitude and sum over 7 scales
    # then sum over RGB to collapse into a single mask
    # laplacian is normalized by patch-wise average to make it exposure-independent
    grey = 0.055
    diag = (im.shape[0]**2 + im.shape[1]**2)**0.5

    # prefilter step to remove noise and artifacts
    denoised = gaussian_filter(im, denoise)
    result = np.zeros_like(im)

    # laplacian decomposition
    sigma_min = 1. # (2 * np.pi / np.pi**0.5)**0.5 / 2.
    sigma = max(0.001 * diag, sigma_min)

    for i in range(10):
        blur = gaussian_filter(denoised, sigma, mode="nearest", truncate=4)
        result += ((blur - denoised) * 2. * np.pi / (np.pi**0.5 * sigma**2) )**2# / (blur + grey)
        #result += ((blur - denoised))**2
        #result += laplace(blur)**2
        denoised = blur
        sigma *= 2**0.5

    return result**0.5


def find_luminance_density(im):
    # remove gamma assuming sRGB encoding and compute luminance Y in CIE XYZ 1931 2° standard observer
    linear = (im <= 0.04045) * im / 12.92 + (im > 0.04045) * ((im + 0.055) / (1 + 0.055))**2.4
    return 0.2126 * linear[:, :, 0] + 0.7152 * linear[:, :, 1] + 0.0722 * linear[:, :, 2]


# extract program invocation arguments
parser = argparse.ArgumentParser(description='Calcule les barycentres et les premiers moments visuels dans une image RGB')
parser.add_argument('path', metavar='path', type=str,
                    help='un fichier ou un répertoire à traiter')
parser.add_argument('-n',  type=float, default=0.5,
                    help='diamètre du débruitage (en pixels)')
parser.add_argument('-v', action='store_const', const=True,
                    help='sauvegarde les fichiers intermédiaires des masques de densité')
parser.add_argument('-t', action='store_const', const=True,
                    help='affiche la règle des tiers')
parser.add_argument('-g', action='store_const', const=True,
                    help="affiche la règle du nombre d'or")
parser.add_argument('-r', action='store_const', const=True,
                    help="traite les sous-dossiers récursivement")

arg = parser.parse_args()
path = vars(arg)["path"]
denoise = vars(arg)["n"]
verbose = vars(arg)["v"]
thirds = vars(arg)["t"]
golden = vars(arg)["g"]
recursive = vars(arg)["r"]

# assemble files to process
files = []
saving_path = ""

if os.path.isfile(path):
    # use in single-file mode
    files.append(os.path.abspath(path))
    head, tail = os.path.split(path)
    saving_path = os.path.abspath(head)

elif os.path.isdir(path):
    if(recursive):
        for root, subdirs, files in os.walk(path):
            saving_path = root

            for file in files:
                if (file.endswith(".jpg") or file.endswith(".png") or file.endswith(".jpeg") or file.endswith(".webp")
                    or file.endswith(".JPG") or file.endswith(".JPEG") or file.endswith(".PNG")):
                        if ("analyse" not in file) and ("densite" not in file) and ("masque" not in file) and ("crop" not in file):
                            files.append(os.path.join(root, file))
        print("Traitement de %i fichers dans le répertoire %s\n" % (len(files), path))

    else:
        # use in non-recursive directory mode
        path = os.path.abspath(path)
        saving_path = path
        for file in os.listdir(path):
            if (file.endswith(".jpg") or file.endswith(".png") or file.endswith(".jpeg") or file.endswith(".webp")
                or file.endswith(".JPG") or file.endswith(".JPEG") or file.endswith(".PNG")):
                if ("analyse" not in file) and ("densite" not in file) and ("masque" not in file) and ("crop" not in file):
                    files.append(os.path.join(path, file))
        print("Traitement de %i fichers dans le répertoire %s\n" % (len(files), path))

else:
    print("L'argument %s n'est ni un fichier ni un répertoire.\n" % path)
    sys.exit(1)

# run the magic

black_bary_distance = []
details_bary_distance = []
white_bary_distance = []
black_first_moment = []
white_first_moment = []
details_first_moment = []
rotation_moment = []
distance_to_axis = []
barycentric_score = []
rule_of_thirds_score = []
punctum_score = []
chiaroschuro_score = []

for f in files:
    head, tail = os.path.split(f)
    print("Nous traitons %s, patientez…" % tail)

    # Open image and remove alpha channel if available
    image = Image.open(f).convert('RGB')
    im = np.asarray(image) / 255.
    density_grey = find_luminance_density(im)
    details_density = find_details_density(density_grey, denoise=denoise)

    f, ext = os.path.splitext(f)

    if(verbose):
        Image.fromarray((np.clip(details_density * 8, 0., 1.)**(1./2.4) * 255.).astype(np.uint8)).save(f + "-densite-details.jpg", optimize=True)
        Image.fromarray((255 * np.clip(1. - density_grey, 0., 1.)**(2.4)).astype(np.uint8)).save(f + "-densite-luminosite.jpg", optimize=True)

    x_1, y_1 = find_barycenter(1. - density_grey)
    x_2, y_2 = find_barycenter(details_density)
    x_3, y_3 = find_barycenter(density_grey)

    I_1 = find_first_moment(1. - density_grey, (x_1, y_1))
    I_2 = find_first_moment(details_density, (x_2, y_2))
    I_3 = find_first_moment(density_grey, (x_3, y_3))

    y_center = im.shape[1] / 2.
    x_center = im.shape[0] / 2.

    # Compute stats
    diagonal = (im.shape[0]**2 + im.shape[1]**2)**0.5

    # distance between barycenters and image center in % of image diagonal
    black_bary_distance.append((((x_center - x_1) ** 2 + (y_center - y_1) ** 2) ** 0.5) / diagonal * 100.)
    details_bary_distance.append((((x_center - x_2) ** 2 + (y_center - y_2) ** 2) ** 0.5) / diagonal * 100.)
    white_bary_distance.append((((x_center - x_3) ** 2 + (y_center - y_3) ** 2) ** 0.5) / diagonal * 100.)

    black_first_moment.append(I_1 * 100.)
    details_first_moment.append(I_2 * 100.)
    white_first_moment.append(I_3 * 100.)

    # vector product to find the area of the barycentric triangle
    u = np.array([x_1 - x_2, y_1 - y_2, 0.]) / diagonal * 100.
    v = np.array([x_3 - x_2, y_3 - y_2, 0.]) / diagonal * 100.
    area = np.abs(np.cross(u, v)[2] / 2.)
    rotation_moment.append(area)

    # barycentric distance between black and white
    barycentric_distance = ((x_1 - x_3)**2 + (y_1 - y_3)**2)**0.5

    # distance between details barycenter and white/black barycentric axis
    distance = np.abs((x_3 - x_1) * (y_1 - y_2) - (x_1 - x_2) * (y_3 - y_1)) / barycentric_distance
    barycentric_distance *= 100. / diagonal
    distance *= 100. / diagonal
    distance_to_axis.append(distance)

    # Compute the score of rule of thirds respect
    thirds_score = 0.

    mask = np.zeros((im.shape[0], im.shape[1]))
    third_v_1 = int(im.shape[0] / 3.)
    third_v_2 = int(im.shape[0] * 2. / 3.)
    third_h_1 = int(im.shape[1] / 3.)
    third_h_2 = int(im.shape[1] * 2. / 3.)

    mask[third_v_1, :] = 1.
    mask[third_v_2, :] = 1.
    mask[:, third_h_1] = 1.
    mask[:, third_h_2] = 1.

    # apply unnormalized gaussian filter
    sigma = diagonal / 40.
    mask1 = gaussian_filter(mask, sigma) * (2 * np.pi * sigma**2)**0.5 / 2.

    sigma = diagonal / 30.
    mask2 = gaussian_filter(mask, sigma) * (2 * np.pi * sigma**2)**0.5 / 2.

    collapsed_grey = density_grey.sum(axis=2) if len(density_grey.shape) > 2 else density_grey
    collapsed_details = details_density.sum(axis=2) if len(details_density.shape) > 2 else details_density
    collapsed_grey = np.abs(gaussian_filter(collapsed_grey, sigma) - gaussian_filter(collapsed_grey, 1.)) + collapsed_details

    thirds_mask_ratio = np.sum(mask1) / mask1.size
    thirds_details_ratio = np.sum(collapsed_details * mask1) / np.sum(collapsed_details)
    thirds_details = thirds_details_ratio / thirds_mask_ratio

    covar = np.cov([mask2.flatten(), collapsed_grey.flatten()])
    thirds_features = (covar[0, 1]**2 / (covar[0, 0] * covar[1, 1]))**0.25
    print(covar)

    thirds_score = 100. * (thirds_features * thirds_details)**0.5
    rule_of_thirds_score.append(thirds_score)
    print("%f ; %f ; %f ; %f\n" % (thirds_mask_ratio, thirds_details, thirds_features, thirds_score))

    if(verbose):
        Image.fromarray((255 * np.clip(mask1 * collapsed_details * 8., 0., 1.)**(1./2.4)).astype(np.uint8)).save(f + "-masque.jpg", optimize=True)
        Image.fromarray((255 * np.clip(mask2 * collapsed_grey, 0., 1.)**(1./2.4)).astype(np.uint8)).save(f + "-masque-2.jpg", optimize=True)
        crop_radius = I_2 * np.hypot(im.shape[0], im.shape[1]) * 1.5
        y_min = int(max(y_2 - crop_radius, 0))
        y_max = int(min(y_2 + crop_radius, im.shape[1]))
        x_min = int(max(x_2 - crop_radius, 0))
        x_max = int(min(x_2 + crop_radius, im.shape[0]))
        Image.fromarray((im[x_min:x_max,y_min:y_max,...]*255).astype(np.uint8)).save(f + "-crop.jpg", optimize=True)

    # puctum score
    punctum = (I_1 / I_2) * 100.
    punctum_score.append(punctum)

    # chiaroschuro score
    chiaroschuro = (I_1 / I_3 - 1) * 100.
    chiaroschuro_score.append(chiaroschuro)

    # barycentric score
    barycentric = (1. - area / 100. * distance / barycentric_distance) * 100.
    barycentric_score.append(barycentric)

    # Plot the pretty pictures

    plt.imshow(image, cmap="Greys_r")

    if (thirds):
        plt.axhline(im.shape[0] / 3., color="white")
        plt.axhline(2. * im.shape[0] / 3., color="white")
        plt.axvline(im.shape[1] / 3., color="white")
        plt.axvline(2. * im.shape[1] / 3., color="white")

    if (golden):
        ratio = 2. / (1. + np.sqrt(5.))
        plt.axhline(im.shape[0] * ratio, color="white")
        plt.axhline(im.shape[0] * (1. - ratio), color="white")
        plt.axvline(im.shape[1] * ratio, color="white")
        plt.axvline(im.shape[1] * (1. - ratio), color="white")

    plt.plot([y_3, y_1, y_2, y_3], [x_3, x_1, x_2, x_3], "-", color="white", linewidth=2)
    plt.plot(y_1, x_1, "o", markersize=15, markerfacecolor="red", markeredgecolor="none", label="barycentre des noirs")
    plt.plot(y_3, x_3, "o", markersize=15, markerfacecolor="green", markeredgecolor="none", label="barycentre des blancs")
    plt.plot(y_2, x_2, "o", markersize=15, markerfacecolor="blue", markeredgecolor="none", label="barycentre des détails")

    plt.plot(y_center, x_center, "+", markersize=30, markerfacecolor="c", markeredgecolor="c", markeredgewidth=3, label="centre de l'image")

    plt.scatter(y_1, x_1, c="none", s=I_1 * im.size, edgecolors="red", plotnonfinite=True, linewidths=3)
    plt.scatter(y_3, x_3, c="none", s=I_3 * im.size, edgecolors="green", plotnonfinite=True, linewidths=3)
    plt.scatter(y_2, x_2, c="none", s=I_2 * im.size, edgecolors="blue", plotnonfinite=True, linewidths=3)

    plt.legend(bbox_to_anchor=(1., 1.), loc='upper left')

    lab = "Scores :\n\n"
    lab += "{0:15} : {1:+3.1f} %\n".format("barycentrique", barycentric)
    lab += "{0:15} : {1:+3.1f} %\n".format("punctum", punctum)
    lab += "{0:15} : {1:+3.1f} %\n".format("clair-obscur", chiaroschuro)
    lab += "{0:15} : {1:+3.1f} %".format("règle des tiers", thirds_score)
    plt.text(im.shape[1] * 1.01, im.shape[0] * 0.99, lab, fontdict={"family": "monospace"})

    plt.axis('off')
    plt.savefig(f + "-analyse.jpg", bbox_inches="tight", pil_kwargs={'optimize': True})
    plt.close()
    print("%s terminé avec succès. \n" % tail)

# Print stats
f = open(os.path.join(saving_path, "rapport.txt"), "w")

head, tail = os.path.split(path)
f.write("Rapport pour %s \n" % tail)
f.write("\n")
f.write("Les valeurs suivantes sont données normalisées, sous la forme (moyenne ± écart-type) % :\n")
f.write("  - en % de la longueur de la diagonale de l'image, pour les distances,\n")
f.write("  - en % de l'aire de l'image, pour les premiers moments et les aires.\n")
f.write("\n")
f.write("Des écarts-types proches de zéro indiquent une forte concentration des valeurs indidividuelles autour de la moyenne, donc moyenne significative.\n")
f.write("\n")

M = np.array([ black_bary_distance,
               white_bary_distance,
               details_bary_distance,
               black_first_moment,
               white_first_moment,
               details_first_moment,
               rotation_moment,
               distance_to_axis,
               barycentric_score,
               punctum_score,
               chiaroschuro_score,
               rule_of_thirds_score], dtype=np.float64)

avg = np.mean(M, axis=1)
std = np.std(M, axis=1)

titres = ["distance (barycentre noir -> centre de l'image)..............",
          "distance (barycentre blanc -> centre de l'image).............",
          "distance (barycentre détails -> centre de l'image)...........",
          "premier moment des noirs.....................................",
          "premier moment des blancs....................................",
          "premier moment des détails...................................",
          "aire du triangle barycentrique...............................",
          "distance (barycentre détails -> axe barycentrique noir-blanc)",
          "score barycentrique..........................................",
          "score de punctum.............................................",
          "score de clair-obscur........................................",
          "score de la règle des tiers.................................." ]

f.write("RÉSULTATS :\n")
for i in range(len(titres)):
    f.write("%s (%.2f ± %.2f) %%\n" % (titres[i], avg[i], std[i]))

if(len(black_bary_distance) > 1):
    f.write("\n")
    f.write("MATRICE DE COVARIANCE : \n")
    f.write("%s" % np.cov(M))
    f.write("\n")
    f.write("La matrice est rangée dans le même ordre que les variables ci-dessus.\n")
    f.write("\nDes valeurs élevées (en valeur absolue) indiquent une forte corrélation entre 2 variables.\n")


f.close()

print("Le programme s'est terminé sans erreur.")
sys.exit(0)
