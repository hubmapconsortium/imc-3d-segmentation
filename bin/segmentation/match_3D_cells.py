import bz2
import pickle
from collections import Counter
from os import fspath
from os.path import join
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from aicsimageio.writers import OmeTiffWriter
from scipy.sparse import csr_matrix
from skimage.io import imsave
from skimage.segmentation import find_boundaries


def get_compartments_diff(arr1, arr2):
    a = set((tuple(i) for i in arr1))
    b = set((tuple(i) for i in arr2))
    diff = np.array(list(a - b))
    return diff


def get_matched_cells(cell_arr, cell_membrane_arr, nuclear_arr, mismatch_repair):
    a = set((tuple(i) for i in cell_arr))
    b = set((tuple(i) for i in cell_membrane_arr))
    c = set((tuple(i) for i in nuclear_arr))
    d = a - b
    mismatch_pixel_num = len(list(c - d))
    # print(mismatch_pixel_num)
    mismatch_fraction = len(list(c - d)) / len(list(c))
    if not mismatch_repair:
        if mismatch_pixel_num == 0:
            return np.array(list(a)), np.array(list(c)), 0
        else:
            return False, False, False
    else:
        if mismatch_pixel_num < len(c):
            return np.array(list(a)), np.array(list(d & c)), mismatch_fraction
        else:
            return False, False, False


def append_coord(rlabel_mask, indices, maxvalue):
    masked_imgs_coord = [[[], []] for i in range(maxvalue)]
    for i in range(0, len(rlabel_mask)):
        masked_imgs_coord[rlabel_mask[i]][0].append(indices[0][i])
        masked_imgs_coord[rlabel_mask[i]][1].append(indices[1][i])
    return masked_imgs_coord


def unravel_indices(labeled_mask, maxvalue):
    rlabel_mask = labeled_mask.reshape(-1)
    indices = np.arange(len(rlabel_mask))
    indices = np.unravel_index(indices, (labeled_mask.shape[0], labeled_mask.shape[1]))
    masked_imgs_coord = append_coord(rlabel_mask, indices, maxvalue)
    masked_imgs_coord = list(map(np.asarray, masked_imgs_coord))
    return masked_imgs_coord


def get_coordinates(mask):
    print("Getting cell coordinates...")
    cell_num = np.unique(mask)
    maxvalue = len(cell_num)
    channel_coords = unravel_indices(mask, maxvalue)
    return channel_coords


def compute_M(data):
    cols = np.arange(data.size)
    return csr_matrix((cols, (data.ravel(), cols)), shape=(data.max() + 1, data.size))


def get_indices_sparse(data):
    M = compute_M(data)
    return [np.unravel_index(row.data, data.shape) for row in M]


def show_plt(mask):
    plt.imshow(mask)
    plt.show()
    plt.clf()


def list_remove(c_list, indexes):
    for index in sorted(indexes, reverse=True):
        del c_list[index]
    return c_list


def filter_cells(coords, mask):
    # completely mismatches
    no_cells = []
    for i in range(len(coords)):
        if np.sum(mask[coords[i]]) == 0:
            no_cells.append(i)
    new_coords = list_remove(coords.copy(), no_cells)
    return new_coords


def get_indexed_mask(mask, boundary):
    boundary = boundary * 1
    boundary_loc = np.where(boundary == 1)
    boundary[boundary_loc] = mask[boundary_loc]
    return boundary


def get_boundary(mask):
    mask_boundary = find_boundaries(mask, mode="inner")
    mask_boundary_indexed = get_indexed_mask(mask, mask_boundary)
    return mask_boundary_indexed


def get_mask(cell_list, mask_shape):
    mask = np.zeros((mask_shape))
    for cell_num in range(len(cell_list)):
        mask[tuple(cell_list[cell_num].T)] = cell_num
    return mask


def get_new_slice_mask(current_matched_index, new_matched, new_unmatched, max_cell_num):
    mask = np.zeros((img_current_slice.shape))
    for cell_num in range(len(new_matched)):
        mask[tuple(new_matched[cell_num].T)] = current_matched_index[cell_num] + 1
    for cell_num in range(len(new_unmatched)):
        mask[tuple(new_unmatched[cell_num].T)] = max_cell_num + cell_num + 1
    return mask.astype(int)


def get_unmatched_list(matched_list, total_num):
    unmatched_list_index = []
    for i in range(total_num):
        if i not in matched_list:
            unmatched_list_index.append(i)
    unmatched_list = []
    for i in range(len(unmatched_list_index)):
        unmatched_list.append(new_slice_cell_coords[unmatched_list_index[i]])
    return unmatched_list, unmatched_list_index


def get_indices_pandas(data):
    d = data.ravel()
    f = lambda x: np.unravel_index(x.index, data.shape)
    return pd.Series(d).groupby(d).apply(f)


def concatenate_indices(object1, object2):
    object1 = list(object1)
    for i in range(3):
        object1[i] = np.hstack((object1[i], object2[i]))
    return tuple(object1)


def match_3D_slice(mask_3D, cell_mask_3D):
    for z in range(mask_3D.shape[0]):
        for y in range(mask_3D.shape[1]):
            for x in range(mask_3D.shape[2]):
                if mask_3D[z, y, x] != 0:
                    mask_3D[z, y, x] = cell_mask_3D[z, y, x]
    return mask_3D


def match_repair_cell_nucleus(nuclear_slice, cell_slice):

    cell_membrane_mask = get_boundary(cell_slice)
    cell_coords = get_indices_pandas(cell_slice)[1:]
    nucleus_coords = get_indices_pandas(nuclear_slice)[1:]
    cell_membrane_coords = get_indices_pandas(cell_membrane_mask)[1:]
    cell_coords = list(map(lambda x: np.array(x).T, cell_coords))
    cell_membrane_coords = list(map(lambda x: np.array(x).T, cell_membrane_coords))
    nucleus_coords = list(map(lambda x: np.array(x).T, nucleus_coords))
    cell_matched_index_list = []
    nucleus_matched_index_list = []
    cell_matched_list = []
    nucleus_matched_list = []
    repaired_num = 0
    mismatch_repair = True
    for i in range(len(cell_coords)):
        if len(cell_coords[i]) != 0:
            current_cell_coords = cell_coords[i]
            nuclear_search_num = np.unique(
                list(map(lambda x: nuclear_slice[tuple(x)], current_cell_coords))
            )
            best_mismatch_fraction = 1
            whole_cell_best = []
            for j in nuclear_search_num:
                # print(j)
                if j != 0:
                    if (j - 1 not in nucleus_matched_index_list) and (
                        i not in cell_matched_index_list
                    ):
                        whole_cell, nucleus, mismatch_fraction = get_matched_cells(
                            cell_coords[i],
                            cell_membrane_coords[i],
                            nucleus_coords[j - 1],
                            mismatch_repair=mismatch_repair,
                        )
                        if type(whole_cell) != bool:
                            if mismatch_fraction < best_mismatch_fraction:
                                best_mismatch_fraction = mismatch_fraction
                                whole_cell_best = whole_cell
                                nucleus_best = nucleus
                                i_ind = i
                                j_ind = j - 1
            if best_mismatch_fraction < 1 and best_mismatch_fraction > 0:
                repaired_num += 1

            if len(whole_cell_best) > 0:
                cell_matched_list.append(whole_cell_best)
                nucleus_matched_list.append(nucleus_best)
                cell_matched_index_list.append(i_ind)
                nucleus_matched_index_list.append(j_ind)

    cell_matched_mask = get_mask(cell_matched_list, cell_slice.shape)
    nuclear_matched_mask = get_mask(nucleus_matched_list, nuclear_slice.shape)

    return cell_matched_mask, nuclear_matched_mask


def match_3D_cells(mask_XY, mask_XZ, mask_YZ, data_dir, output_file: Path):

    mask_XZ = np.rot90(mask_XZ, k=1, axes=(0, 2))
    mask_YZ = np.rot90(mask_YZ, k=1, axes=(0, 1))

    X_max = np.max(mask_YZ) + 1
    Y_max = np.max(mask_XZ) + 1
    new_mask = np.zeros(mask_XY.shape)

    # give each pixel a unique index from 3 axes
    for z in range(mask_XY.shape[0]):
        for x in range(mask_XY.shape[1]):
            for y in range(mask_XY.shape[2]):
                Z = mask_XY[z, x, y]
                Y = mask_XZ[z, x, y]
                X = mask_YZ[z, x, y]

                if Z == 0:
                    index_1D = 0
                else:
                    index_1D = X + Y * X_max + Z * X_max * Y_max

                new_mask[z, x, y] = index_1D

    new_mask = new_mask.astype(int)
    new_coords = get_indices_pandas(new_mask)

    max_z = new_mask.shape[0]
    max_x = new_mask.shape[1]
    max_y = new_mask.shape[2]
    mask_binary = np.zeros(new_mask.shape, dtype=int)
    for index in new_coords.index[1:]:
        if len(new_coords[index][0]) < 100:

            Z = index // (X_max * Y_max)
            new_coords_index = new_coords[index]
            mask_binary[new_coords_index] = 1

            z_min = max(min(new_coords_index[0]) - 1, 0)
            z_max = min(max(new_coords_index[0]) + 2, max_z)
            x_min = max(min(new_coords_index[1]) - 1, 0)
            x_max = min(max(new_coords_index[1]) + 2, max_x)
            y_min = max(min(new_coords_index[2]) - 1, 0)
            y_max = min(max(new_coords_index[2]) + 2, max_y)
            mask_binary_boundary = find_boundaries(
                mask_binary[z_min:z_max, x_min:x_max, y_min:y_max], mode="outer"
            )
            mask_binary_boundary_indices = list(get_indices_sparse(mask_binary_boundary)[1])
            mask_binary_boundary_indices[0] = mask_binary_boundary_indices[0] + z_min
            mask_binary_boundary_indices[1] = mask_binary_boundary_indices[1] + x_min
            mask_binary_boundary_indices[2] = mask_binary_boundary_indices[2] + y_min
            mask_binary_boundary_indices = tuple(mask_binary_boundary_indices)
            boundary_XY_cell_indices = mask_XY[mask_binary_boundary_indices]
            boundary_3D_cell_indices = new_mask[mask_binary_boundary_indices]

            boundary_3D_cell_indices_matched = boundary_3D_cell_indices[
                np.where(boundary_XY_cell_indices == Z)
            ]
            boundary_3D_cell_indices_matched = boundary_3D_cell_indices_matched[
                boundary_3D_cell_indices_matched != index
            ]
            mask_binary[new_coords[index]] = 0
            # remove small bits
            if len(boundary_3D_cell_indices_matched) > 0:

                value, count = Counter(boundary_3D_cell_indices_matched).most_common()[0]
                if len(new_coords[value][0]) < 100:
                    new_mask[new_coords[index]] = 0
                else:
                    new_mask[new_coords[index]] = value
            else:
                new_mask[new_coords[index]] = 0

    new_coords_no_bits = get_indices_pandas(new_mask)

    XY_coords = get_indices_sparse(mask_XY.astype(int))

    # impute final mask according matched cells from XY axis
    new_mask_imput = new_mask.copy()
    for index in new_coords_no_bits.index[1:]:
        new_coords_no_bits_index = new_coords_no_bits[index]
        Z = int(index // (X_max * Y_max))
        XY_coords_Z = XY_coords[Z]
        z_min = min(new_coords_no_bits_index[0])
        z_max = max(new_coords_no_bits_index[0])
        x_min = min(new_coords_no_bits_index[1])
        x_max = max(new_coords_no_bits_index[1])
        y_min = min(new_coords_no_bits_index[2])
        y_max = max(new_coords_no_bits_index[2])
        impute_range = np.where(
            (XY_coords_Z[0] >= z_min)
            & (XY_coords_Z[0] <= z_max)
            & (XY_coords_Z[1] >= x_min)
            & (XY_coords_Z[1] <= x_max)
            & (XY_coords_Z[2] >= y_min)
            & (XY_coords_Z[2] <= y_max)
        )
        XY_coords_Z = list(XY_coords_Z)
        XY_coords_Z[0] = XY_coords_Z[0][impute_range]
        XY_coords_Z[1] = XY_coords_Z[1][impute_range]
        XY_coords_Z[2] = XY_coords_Z[2][impute_range]
        XY_coords_Z = tuple(XY_coords_Z)
        new_mask_imput[XY_coords_Z] = index
    new_coords_no_bits_imputed = get_indices_pandas(new_mask_imput)

    new_mask_imputed = np.zeros(new_mask.shape)
    for index in new_coords_no_bits_imputed.index[1:]:
        new_mask_imputed[new_coords_no_bits_imputed[index]] = index

    # construct 4-channel masks
    nuclear_slice = np.load(join(data_dir, "nuclear_mask_XY.npy"))
    cell_mask_3D = new_mask_imputed

    repaired_nuclear_slices = []
    matched_cell_slices = []
    for slice_idx in range(nuclear_slice.shape[0]):
        matched_cell_slice, repaired_nuclear_slice = match_repair_cell_nucleus(
            nuclear_slice[slice_idx], cell_mask_3D[slice_idx]
        )
        matched_cell_slices.append(matched_cell_slice)
        repaired_nuclear_slices.append(repaired_nuclear_slice)

    repaired_nuclear_slice = np.stack(repaired_nuclear_slices)
    matched_cell_slice = np.stack(matched_cell_slices)
    matched_cell_3D = match_3D_slice(matched_cell_slice, cell_mask_3D)
    matched_nuclear_3D = match_3D_slice(repaired_nuclear_slice, cell_mask_3D)
    matched_cell_membrane_3D = get_indexed_mask(
        matched_cell_3D, find_boundaries(matched_cell_3D, mode="inner")
    )
    matched_nuclear_membrane_3D = get_indexed_mask(
        matched_nuclear_3D, find_boundaries(matched_nuclear_3D, mode="inner")
    )

    image = np.stack(
        (
            matched_cell_3D,
            matched_nuclear_3D,
            matched_cell_membrane_3D,
            matched_nuclear_membrane_3D,
        )
    )

    channel_names = ["cells", "nuclei", "cell_boundaries", "nucleus_boundaries"]
    OmeTiffWriter.save(image, fspath(output_file), channel_names=channel_names)

    return image
