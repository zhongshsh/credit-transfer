import matplotlib.pyplot as plt
import torch
import torch.nn as nn
import torchvision
import torchvision.transforms as transforms
import numpy as np
from .misc import *
import torch.nn.functional as F
import cv2


def reverse_normalize(x, mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]):
    x[:, 0, :, :] = x[:, 0, :, :] * std[0] + mean[0]
    x[:, 1, :, :] = x[:, 1, :, :] * std[1] + mean[1]
    x[:, 2, :, :] = x[:, 2, :, :] * std[2] + mean[2]
    return x


def visualize(img, cam):
    """
    Synthesize an image with CAM to make a result image.
    Args:
        img: (Tensor) shape => (1, 3, H, W)
        cam: (Tensor) shape => (1, 1, H', W')
    Return:
        synthesized image (Tensor): shape =>(1, 3, H, W)
    """

    _, _, H, W = img.shape
    cam = F.interpolate(cam, size=(H, W), mode="bilinear", align_corners=False)
    cam = 255 * cam.squeeze()
    heatmap = cv2.applyColorMap(np.uint8(cam), cv2.COLORMAP_JET)
    heatmap = torch.from_numpy(heatmap.transpose(2, 0, 1))
    heatmap = heatmap.float() / 255
    b, g, r = heatmap.split(1)
    heatmap = torch.cat([r, g, b])

    result = heatmap + img.cpu()
    result = result.div(result.max())

    return result


# functions to show an image
def make_image(img, mean=(0, 0, 0), std=(1, 1, 1)):
    for i in range(0, 3):
        img[i] = img[i] * std[i] + mean[i]  # unnormalize
    npimg = img.numpy()
    return np.transpose(npimg, (1, 2, 0))


def gauss(x, a, b, c):
    return torch.exp(-torch.pow(torch.add(x, -b), 2).div(2 * c * c)).mul(a)


def colorize(x):
    """Converts a one-channel grayscale image to a color heatmap image"""
    if x.dim() == 2:
        torch.unsqueeze(x, 0, out=x)
    if x.dim() == 3:
        cl = torch.zeros([3, x.size(1), x.size(2)])
        cl[0] = gauss(x, 0.5, 0.6, 0.2) + gauss(x, 1, 0.8, 0.3)
        cl[1] = gauss(x, 1, 0.5, 0.3)
        cl[2] = gauss(x, 1, 0.2, 0.3)
        cl[cl.gt(1)] = 1
    elif x.dim() == 4:
        cl = torch.zeros([x.size(0), 3, x.size(2), x.size(3)])
        cl[:, 0, :, :] = gauss(x, 0.5, 0.6, 0.2) + gauss(x, 1, 0.8, 0.3)
        cl[:, 1, :, :] = gauss(x, 1, 0.5, 0.3)
        cl[:, 2, :, :] = gauss(x, 1, 0.2, 0.3)
    return cl


def show_batch(images, Mean=(2, 2, 2), Std=(0.5, 0.5, 0.5)):
    images = make_image(torchvision.utils.make_grid(images), Mean, Std)
    plt.imshow(images)
    plt.show()


def show_mask_single(images, mask, Mean=(2, 2, 2), Std=(0.5, 0.5, 0.5)):
    im_size = images.size(2)

    # save for adding mask
    im_data = images.clone()
    for i in range(0, 3):
        im_data[:, i, :, :] = im_data[:, i, :, :] * Std[i] + Mean[i]  # unnormalize

    images = make_image(torchvision.utils.make_grid(images), Mean, Std)
    plt.subplot(2, 1, 1)
    plt.imshow(images)
    plt.axis("off")

    # for b in range(mask.size(0)):
    #     mask[b] = (mask[b] - mask[b].min())/(mask[b].max() - mask[b].min())
    mask_size = mask.size(2)
    # print('Max %f Min %f' % (mask.max(), mask.min()))
    mask = upsampling(mask, scale_factor=im_size / mask_size)
    # mask = colorize(upsampling(mask, scale_factor=im_size/mask_size))
    # for c in range(3):
    #     mask[:,c,:,:] = (mask[:,c,:,:] - Mean[c])/Std[c]

    # print(mask.size())
    mask = make_image(
        torchvision.utils.make_grid(0.3 * im_data + 0.7 * mask.expand_as(im_data))
    )
    # mask = make_image(torchvision.utils.make_grid(0.3*im_data+0.7*mask), Mean, Std)
    plt.subplot(2, 1, 2)
    plt.imshow(mask)
    plt.axis("off")


def show_mask(images, masklist, Mean=(2, 2, 2), Std=(0.5, 0.5, 0.5)):
    im_size = images.size(2)

    # save for adding mask
    im_data = images.clone()
    for i in range(0, 3):
        im_data[:, i, :, :] = im_data[:, i, :, :] * Std[i] + Mean[i]  # unnormalize

    images = make_image(torchvision.utils.make_grid(images), Mean, Std)
    plt.subplot(1 + len(masklist), 1, 1)
    plt.imshow(images)
    plt.axis("off")

    for i in range(len(masklist)):
        mask = masklist[i].data.cpu()
        # for b in range(mask.size(0)):
        #     mask[b] = (mask[b] - mask[b].min())/(mask[b].max() - mask[b].min())
        mask_size = mask.size(2)
        # print('Max %f Min %f' % (mask.max(), mask.min()))
        mask = upsampling(mask, scale_factor=im_size / mask_size)
        # mask = colorize(upsampling(mask, scale_factor=im_size/mask_size))
        # for c in range(3):
        #     mask[:,c,:,:] = (mask[:,c,:,:] - Mean[c])/Std[c]

        # print(mask.size())
        mask = make_image(
            torchvision.utils.make_grid(0.3 * im_data + 0.7 * mask.expand_as(im_data))
        )
        # mask = make_image(torchvision.utils.make_grid(0.3*im_data+0.7*mask), Mean, Std)
        plt.subplot(1 + len(masklist), 1, i + 2)
        plt.imshow(mask)
        plt.axis("off")
