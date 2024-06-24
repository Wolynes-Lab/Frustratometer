from numba import jit
from numba import prange
import numpy as np


ij, ii = range(2)
ijk, iik, iji, ijj, iii = range(5)
ijkl, iikl, ijil, ijjl, ijki, ijkj, ijkk, iiil, iiki, iikk, ijii, ijij, ijji, ijjj, iiii = range(15)

@jit(nopython=True)
def compute_region_means_2_by_2(indicator_0, indicator_1):
    n = indicator_0.shape[0]
    region_sum = np.zeros(15, dtype=np.float64) 
    region_count = np.zeros(15, dtype=np.int64) 
    (ijkl, iikl, ijil, ijjl, ijki, ijkj, ijkk, iiil, iiki, iikk, ijii, ijij, ijji, ijjj, iiii) = range(15)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            for k in range(n):
                if i == k or j==k:
                    continue
                region_sum[iikl] += indicator_0[i, i] * indicator_1[j, k]
                region_sum[ijil] += indicator_0[i, j] * indicator_1[i, k]
                region_sum[ijjl] += indicator_0[i, j] * indicator_1[j, k]
                region_sum[ijki] += indicator_0[i, j] * indicator_1[k, i]
                region_sum[ijkj] += indicator_0[i, j] * indicator_1[k, j]
                region_sum[ijkk] += indicator_0[i, j] * indicator_1[k, k]
            region_sum[iiil] += indicator_0[i, i] * indicator_1[i, j]
            region_sum[iiki] += indicator_0[i, i] * indicator_1[j, i]
            region_sum[iikk] += indicator_0[i, i] * indicator_1[j, j]
            region_sum[ijii] += indicator_0[i, j] * indicator_1[i, i]
            region_sum[ijij] += indicator_0[i, j] * indicator_1[i, j]
            region_sum[ijji] += indicator_0[i, j] * indicator_1[j, i]
            region_sum[ijjj] += indicator_0[i, j] * indicator_1[j, j]
        region_sum[iiii] += indicator_0[i, i] * indicator_1[i, i]
    region_count[ijkl] = n*(n-1)*(n-2)*(n-3)
    region_count[iikl] = n*(n-1)*(n-2)
    region_count[ijil] = n*(n-1)*(n-2)
    region_count[ijjl] = n*(n-1)*(n-2)
    region_count[ijki] = n*(n-1)*(n-2)
    region_count[ijkj] = n*(n-1)*(n-2)
    region_count[ijkk] = n*(n-1)*(n-2)
    region_count[iiil] = n*(n-1)
    region_count[iiki] = n*(n-1)
    region_count[iikk] = n*(n-1)
    region_count[ijii] = n*(n-1)
    region_count[ijij] = n*(n-1)
    region_count[ijji] = n*(n-1)
    region_count[ijjj] = n*(n-1)
    region_count[iiii] = n

    region_mean = [r/c if c>0 else 0 for r,c in zip(region_sum,region_count)]
    if n>3:
        region_mean[ijkl]=indicator_0.mean()*indicator_1.mean()*(n/(n-3))*(n/(n - 2))*(n/(n - 1))-region_sum.sum()/(n*(n-1)*(n-2)*(n-3))
    
    return region_mean

@jit(nopython=True, parallel=True)
def compute_region_means_2_by_2_parallel(indicator_0, indicator_1):
    n = indicator_0.shape[0]
    region_sum = np.zeros(15, dtype=np.float64) 
    region_count = np.zeros(15, dtype=np.int64) 

    # Temporary arrays for private accumulation
    temp_region_sum = np.zeros((n, 15), dtype=np.float64)
    
    (ijkl, iikl, ijil, ijjl, ijki, ijkj, ijkk, iiil, iiki, iikk, ijii, ijij, ijji, ijjj, iiii) = range(15)
    for i in prange(n):
        for j in range(n):
            if i == j:
                continue
            for k in range(n):
                if i == k or j==k:
                    continue
                temp_region_sum[i, iikl] += indicator_0[i, i] * indicator_1[j, k]
                temp_region_sum[i, ijil] += indicator_0[i, j] * indicator_1[i, k]
                temp_region_sum[i, ijjl] += indicator_0[i, j] * indicator_1[j, k]
                temp_region_sum[i, ijki] += indicator_0[i, j] * indicator_1[k, i]
                temp_region_sum[i, ijkj] += indicator_0[i, j] * indicator_1[k, j]
                temp_region_sum[i, ijkk] += indicator_0[i, j] * indicator_1[k, k]
            temp_region_sum[i, iiil] += indicator_0[i, i] * indicator_1[i, j]
            temp_region_sum[i, iiki] += indicator_0[i, i] * indicator_1[j, i]
            temp_region_sum[i, iikk] += indicator_0[i, i] * indicator_1[j, j]
            temp_region_sum[i, ijii] += indicator_0[i, j] * indicator_1[i, i]
            temp_region_sum[i, ijij] += indicator_0[i, j] * indicator_1[i, j]
            temp_region_sum[i, ijji] += indicator_0[i, j] * indicator_1[j, i]
            temp_region_sum[i, ijjj] += indicator_0[i, j] * indicator_1[j, j]
        temp_region_sum[i, iiii] += indicator_0[i, i] * indicator_1[i, i]

    # Reduction step
    for i in range(n):
        region_sum += temp_region_sum[i]
    
    region_count[ijkl] = n*(n-1)*(n-2)*(n-3)
    region_count[iikl] = n*(n-1)*(n-2)
    region_count[ijil] = n*(n-1)*(n-2)
    region_count[ijjl] = n*(n-1)*(n-2)
    region_count[ijki] = n*(n-1)*(n-2)
    region_count[ijkj] = n*(n-1)*(n-2)
    region_count[ijkk] = n*(n-1)*(n-2)
    region_count[iiil] = n*(n-1)
    region_count[iiki] = n*(n-1)
    region_count[iikk] = n*(n-1)
    region_count[ijii] = n*(n-1)
    region_count[ijij] = n*(n-1)
    region_count[ijji] = n*(n-1)
    region_count[ijjj] = n*(n-1)
    region_count[iiii] = n

    region_mean = [r/c if c>0 else 0 for r,c in zip(region_sum,region_count)]
    if n>3:
        region_mean[ijkl]=indicator_0.mean()*indicator_1.mean()*(n/(n-3))*(n/(n - 2))*(n/(n - 1))-region_sum.sum()/(n*(n-1)*(n-2)*(n-3))
    
    return region_mean

def compute_region_means_2_by_2_numpy(indicator_0, indicator_1):
    n=indicator_0.shape[0]
    
    # Outer product of indicators
    indicator_products = np.outer(indicator_0, indicator_1).reshape(n, n, n, n)
    
    # Create arrays of indices
    indices = np.arange(n)
    i, j, k, l = np.meshgrid(indices, indices, indices, indices, indexing='ij', sparse=True)


    masks = {
    # 'ijkl': No index is the same as any other; all four indices are distinct.
    'ijkl': (i != j) & (i != k) & (i != l) & (j != k) & (j != l) & (k != l),
    # 'iikl': The first two indices are equal, and the last two are different from the first two and different from each other.
    'iikl': (i == j) & (i != k) & (i != l) & (k != l),
    # 'ijil, ijjl, ijki, ijkj': Two indices are equal and form a pair, while the other two indices are different from the pair and from each other.
    'ijil': (i != j) & (k != l) & (i == k) & (j != l),
    'ijjl': (i != j) & (k != l) & (j == k) & (i != l),
    'ijki': (i != j) & (k != l) & (i == l) & (j != k),
    'ijkj': (i != j) & (k != l) & (j == l) & (i != k),
    # 'ijkk': The last two indices are equal, and the first two are different from the last two and different from each other.
    'ijkk': (k == l) & (k != i) & (k != j) & (i != j),
    # 'iiil, iiki': The first two indices are equal to one of the last two, the other one of the last two is different.
    'iiil': (i == j) & (i == k) & (i != l),
    'iiki': (i == j) & (i == l) & (i != k),
    # 'iikk': The first two indices form a pair that is equal, and the last two indices form a different pair that is equal, but the two pairs are different from each other.
    'iikk': (i == j) & (k == l) & (i != k),
    # 'ikkk': The last two indices are equal to one of the first two, the other one of the first two is different.
    'ijii': (k == l) & (i == k) & (j != i),
    # 'ijij,ijji': The first and third indices are equal, and the second and fourth indices are equal, but the pairs are different from each other.
    'ijij': (i == k) & (j == l) & (i != j),
    'ijji': (i == l) & (j == k) & (i != j),
    # 'ijjj': The last two indices are equal to one of the first two, the other one of the first two is different.
    'ijjj': (k == l) & (j == k) & (i != j),
    # 'iiii': All indices are equal.
    'iiii': (i == j) & (i == k) & (i == l),
    }
    
    # # Apply masks to the array and store regions in a dictionary
    # region_count = {key: mask.sum() for key, mask in masks.items()}
    # region_mean = {key: (indicator_products[mask].mean() if region_count[key] > 0 else 0) for key, mask in masks.items()}

    # Define the order of regions
    region_order = ['ijkl', 'iikl', 'ijil', 'ijjl', 'ijki', 'ijkj', 'ijkk', 'iiil', 'iiki', 'iikk', 'ijii', 'ijij', 'ijji', 'ijjj', 'iiii']
    
    # Initialize the NumPy array with the correct length
    region_means = np.zeros(len(region_order))
    
    # Calculate region means and store them in the specified order
    for idx, key in enumerate(region_order):
        mask = masks[key]
        region_means[idx] = indicator_products[mask].mean() if mask.any() else 0

    return region_means

@jit(nopython=True)
def compute_region_means_1_by_2(indicator_0, indicator_1):
    n = indicator_1.shape[0]
    region_sum = np.zeros(5, dtype=np.float64) 
    region_count = np.zeros(5, dtype=np.int64) 
    (ijk, iik, iji, ijj, iii) = range(5)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            region_sum[iik] += indicator_0[i] * indicator_1[i, j]
            region_sum[iji] += indicator_0[i] * indicator_1[j, i]
            region_sum[ijj] += indicator_0[i] * indicator_1[j, j]
        region_sum[iii] += indicator_0[i] * indicator_1[i, i]
    
    region_count[iik] = n*(n-1)
    region_count[iji] = n*(n-1)
    region_count[ijj] = n*(n-1)
    region_count[iii] = n
    
    region_mean = [r/c if c>0 else 0 for r,c in zip(region_sum,region_count)]
    if n>2:
        region_mean[ijk]=indicator_0.mean()*indicator_1.mean()*(n/(n - 2))*(n/(n - 1))-region_sum.sum()/(n*(n-1)*(n-2))
    
    return region_mean

def compute_region_means_1_by_2_numpy(indicator_0, indicator_1):
    n = indicator_1.shape[0]
    
    # Outer product of indicators
    indicator_products = np.outer(indicator_0, indicator_1.ravel()).reshape(n, n, n)
    
    # Create arrays of indices
    indices = np.arange(n)
    i, j, k = np.meshgrid(indices, indices, indices, indexing='ij', sparse=True)

    # Define masks for different conditions
    masks = {
        # 'ijk': No index is the same as any other; all three indices are distinct.
        'ijk': (i != j) & (i != k) & (j != k),
        # 'iik': The first two indices are equal, and the last one is different from the first two.
        'iik': (i == j) & (i != k),
        # 'iji': The first and last indices are equal, and the middle one is different from them.
        'iji': (i == k) & (i != j),
        # 'ijj': The last two indices are equal, and the first one is different from them.
        'ijj': (j == k) & (i != j),
        # 'iii': All indices are equal.
        'iii': (i == j) & (i == k)
    }

    # Define the order of regions
    region_order = ['ijk', 'iik', 'iji', 'ijj', 'iii']
    
    # Initialize the NumPy array with the correct length
    region_means = np.zeros(len(region_order))
    
    # Calculate region means and store them in the specified order
    for idx, key in enumerate(region_order):
        mask = masks[key]
        region_means[idx] = indicator_products[mask].mean() if mask.any() else 0

    return region_means

@jit(nopython=True)
def compute_region_means_1_by_1(indicator_0, indicator_1):
    n = indicator_0.shape[0]
    region_sum = np.zeros(2, dtype=np.float64) 
    region_count = np.zeros(2, dtype=np.int64) 
    (ij, ii) = range(2)
    for i in range(n):
        region_sum[ii] += indicator_0[i] * indicator_1[i]
    region_count[ii]=n
    region_mean = [r/c if c>0 else 0 for r,c in zip(region_sum,region_count)]
    if n>1:
        region_mean[ij]=indicator_0.mean()*indicator_1.mean()*(n/(n - 1))-region_sum.sum()/(n*(n-1))
    return region_mean

def compute_region_means_1_by_1_numpy(indicator_0, indicator_1):
    n = indicator_0.shape[0]
    
    # Element-wise product of indicators
    indicator_products = np.outer(indicator_0,indicator_1)
    
    # Sum over diagonal elements for 'ii' region
    sum_diagonal = np.sum(np.diag(indicator_products))
    count_diagonal = n
    
     # Create a mask for non-diagonal elements
    mask_non_diagonal = np.ones_like(indicator_products, dtype=bool)
    np.fill_diagonal(mask_non_diagonal, 0)
    
    # Sum over non-diagonal elements for 'ij' region
    sum_non_diagonal = np.sum(indicator_products[mask_non_diagonal])
    count_non_diagonal = n * n - n  # Total elements minus diagonal elements
    
    # Define the order of regions
    #region_order = ['ij', 'ii']
    
    # Initialize the NumPy array with the correct length
    region_means = np.zeros(2)
    
    # Calculate region means and store them in the specified order
    region_means[0] = sum_non_diagonal / count_non_diagonal if count_non_diagonal > 0 else 0
    region_means[1] = sum_diagonal / count_diagonal if count_diagonal > 0 else 0

    return region_means


def compute_region_means(indicator_0,indicator_1,parallel=True, use_numba=True):
    indicator_0=np.array(indicator_0)
    indicator_1=np.array(indicator_1)
    s0=indicator_0.shape[0]
    for d in indicator_0.shape:
        assert d==s0, "All dimensions for the indicators should be the same size"
    for d in indicator_1.shape:
        assert d==s0, "Both indicators should be the same size"
    d0 = len(indicator_0.shape)
    d1 = len(indicator_1.shape)

    if use_numba:
        if d0==d1==1:
            result=compute_region_means_1_by_1(indicator_0, indicator_1)
        elif d0==1 and d1==2:
            result=compute_region_means_1_by_2(indicator_0, indicator_1)
        elif d1==1 and d0==2:
            result=compute_region_means_1_by_2(indicator_1, indicator_0)
        elif d0==d1==2:
            if parallel and d0>100:
                result=compute_region_means_2_by_2(indicator_0, indicator_1)
            else:    
                result=compute_region_means_2_by_2(indicator_0, indicator_1)
        else:
            raise NotImplementedError('This method has not be implemented for dimensions {d0} and {d1}')
        return result
    else:
        if d0==d1==1:
            result=compute_region_means_1_by_1_numpy(indicator_0, indicator_1)
        elif d0==1 and d1==2:
            result=compute_region_means_1_by_2_numpy(indicator_0, indicator_1)
        elif d1==1 and d0==2:
            result=compute_region_means_1_by_2_numpy(indicator_1, indicator_0)
        elif d0==d1==2:
            result=compute_region_means_2_by_2_numpy(indicator_0, indicator_1)
        else:
            raise NotImplementedError('This method has not be implemented for dimensions {d0} and {d1}')
        return result
    
def compute_single_region_means(indicators):
    region_means={}
    for i,i0 in enumerate(indicators):
        for j,i1 in enumerate(indicators):
            result=compute_region_means(i0,i1)
            for key in result:
                region_means[(f'{key}_{i}_{j}')]=result[key]
    return region_means

@jit(nopython=True)
def create_region_masks_2_by_2(n_elements):
    ijkl, iikl, ijil, ijjl, ijki, ijkj, ijkk, iiil, iiki, iikk, ijii, ijij, ijji, ijjj, iiii = range(15)
    masks = np.zeros((15, n_elements, n_elements, n_elements, n_elements), dtype=np.bool_)

    for i in range(n_elements):
        for j in range(n_elements):
            for k in range(n_elements):
                for l in range(n_elements):
                    masks[ijkl][i, j, k, l] = (i != j) and (i != k) and (i != l) and (j != k) and (j != l) and (k != l)
                    masks[iikl][i, j, k, l] = (i == j) and (i != k) and (i != l) and (k != l)
                    masks[ijil][i, j, k, l] = (i != j) and (k != l) and (i == k) and (j != l)
                    masks[ijjl][i, j, k, l] = (i != j) and (k != l) and (j == k) and (i != l)
                    masks[ijki][i, j, k, l] = (i != j) and (k != l) and (i == l) and (j != k)
                    masks[ijkj][i, j, k, l] = (i != j) and (k != l) and (j == l) and (i != k)
                    masks[ijkk][i, j, k, l] = (k == l) and (k != i) and (k != j) and (i != j)
                    masks[iiil][i, j, k, l] = (i == j) and (i == k) and (i != l)
                    masks[iiki][i, j, k, l] = (i == j) and (i == l) and (i != k)
                    masks[iikk][i, j, k, l] = (i == j) and (k == l) and (i != k)
                    masks[ijii][i, j, k, l] = (k == l) and (i == k) and (j != i)
                    masks[ijij][i, j, k, l] = (i == k) and (j == l) and (i != j)
                    masks[ijji][i, j, k, l] = (i == l) and (j == k) and (i != j)
                    masks[ijjj][i, j, k, l] = (k == l) and (j == k) and (i != j)
                    masks[iiii][i, j, k, l] = (i == j) and (i == k) and (i == l)
    return masks

@jit(nopython=True)
def mean_inner_product_2_by_2(repetitions,indicator_0,indicator_1):
    ijkl, iikl, ijil, ijjl, ijki, ijkj, ijkk, iiil, iiki, iikk, ijii, ijij, ijji, ijjj, iiii = range(15)
    region_mean= compute_region_means_2_by_2_parallel(indicator_0,indicator_1)
    n_elements= len(repetitions)

    # Create the mean_inner_product array
    mean_inner_product = np.zeros((n_elements, n_elements, n_elements, n_elements)).flatten()
    
    # Create arrays of indices for elements
    #n_i, n_j, n_k, n_l = np.meshgrid(*[repetitions]*4, indexing='ij', sparse=False)
    n_i = np.repeat(repetitions, n_elements**3).reshape(n_elements, n_elements, n_elements, n_elements)
    n_j = n_i.copy().transpose(3, 0, 1, 2).flatten()
    n_k = n_i.copy().transpose(2, 3, 0, 1).flatten()
    n_l = n_i.copy().transpose(1, 2, 3, 0).flatten()
    n_i=n_i.flatten()

    masks = create_region_masks_2_by_2(n_elements)
   
    
    m = masks[iiii].flatten()
    mean_inner_product[m] = (
        n_i[m] * region_mean[iiii] +
        n_i[m] * (n_i[m]-1) * (region_mean[iikk] + region_mean[ijij] + region_mean[ijji] + region_mean[iiil] + region_mean[iiki] + region_mean[ijjj] + region_mean[ijii]) +
        n_i[m] * (n_i[m]-1) * (n_i[m]-2) * (region_mean[ijil] + region_mean[ijjl] + region_mean[ijki] + region_mean[ijkj] + region_mean[iikl] + region_mean[ijkk]) +
        n_i[m] * (n_i[m]-1) * (n_i[m]-2) * (n_i[m]-3) * region_mean[ijkl]
    )
    
    m = masks[iikk].flatten()
    mean_inner_product[m] = (
        n_i[m] * n_k[m] * region_mean[iikk] +
        n_i[m] * n_k[m] * (n_i[m]-1) * region_mean[ijkk] +
        n_i[m] * n_k[m] * (n_k[m]-1) * region_mean[iikl] +
        n_i[m] * n_k[m] * (n_i[m]-1) * (n_k[m]-1) * region_mean[ijkl]
    )
    
    m = masks[ijij].flatten()
    mean_inner_product[m] = (
        n_i[m] * n_j[m] * region_mean[ijij] +
        n_i[m] * n_j[m] * (n_i[m]-1) * region_mean[ijkj] +
        n_i[m] * n_j[m] * (n_j[m]-1) * region_mean[ijil] +
        n_i[m] * n_j[m] * (n_i[m]-1) * (n_j[m]-1) * region_mean[ijkl]
    )

    m = masks[ijji].flatten()
    mean_inner_product[m] = (
        n_i[m] * n_j[m] * region_mean[ijji] +
        n_i[m] * n_j[m] * (n_i[m]-1) * region_mean[ijki] +
        n_i[m] * n_j[m] * (n_j[m]-1) * region_mean[ijjl] +
        n_i[m] * n_j[m] * (n_i[m]-1) * (n_j[m]-1) * region_mean[ijkl]
    )
    
    m = masks[iiil].flatten()
    mean_inner_product[m] = (
        n_i[m] * n_l[m] * region_mean[iiil] +
        n_i[m] * n_l[m] * (n_i[m]-1) * (region_mean[ijjl] + region_mean[ijil] + region_mean[iikl]) +
        n_i[m] * n_l[m] * (n_i[m]-1) * (n_i[m]-2) * region_mean[ijkl]
    )
    
    m = masks[iiki].flatten()
    mean_inner_product[m] = (
        n_i[m] * n_k[m] * region_mean[iiki] +
        n_i[m] * n_k[m] * (n_i[m]-1) * (region_mean[ijki] + region_mean[ijkj] + region_mean[iikl]) +
        n_i[m] * n_k[m] * (n_i[m]-1) * (n_i[m]-2) * region_mean[ijkl]
    )

    m = masks[ijjj].flatten()
    mean_inner_product[m] = (
        n_i[m] * n_j[m] * region_mean[ijjj] +
        n_i[m] * n_j[m] * (n_j[m]-1) * (region_mean[ijjl] + region_mean[ijkj] + region_mean[ijkk]) +
        n_i[m] * n_j[m] * (n_j[m]-1) * (n_j[m]-2) * region_mean[ijkl]
    )

    m = masks[ijii].flatten()
    mean_inner_product[m] = (
        n_i[m] * n_j[m] * region_mean[ijii] +
        n_i[m] * n_j[m] * (n_i[m]-1) * (region_mean[ijki] + region_mean[ijil] + region_mean[ijkk]) +
        n_i[m] * n_j[m] * (n_i[m]-1) * (n_i[m]-2) * region_mean[ijkl]
    )
    
    m = masks[ijil].flatten()
    mean_inner_product[m] = (
        n_i[m] * n_j[m] * n_l[m] * region_mean[ijil] +
        n_i[m] * n_j[m] * n_l[m] * (n_i[m]-1) * region_mean[ijkl]
    )

    m = masks[ijjl].flatten()
    mean_inner_product[m] = (
        n_i[m] * n_j[m] * n_l[m] * region_mean[ijjl] +
        n_i[m] * n_j[m] * n_l[m] * (n_j[m]-1) * region_mean[ijkl]
    )

    m = masks[ijki].flatten()
    mean_inner_product[m] = (
        n_i[m] * n_j[m] * n_k[m] * region_mean[ijki] +
        n_i[m] * n_j[m] * n_k[m] * (n_i[m]-1) * region_mean[ijkl]
    )

    m = masks[ijkj].flatten()
    mean_inner_product[m] = (
        n_i[m] * n_j[m] * n_k[m] * region_mean[ijkj] +
        n_i[m] * n_j[m] * n_k[m] * (n_j[m]-1) * region_mean[ijkl]
    )

    m = masks[ijkk].flatten()
    mean_inner_product[m] = (
        n_i[m] * n_j[m] * n_k[m] * region_mean[ijkk] +
        n_i[m] * n_j[m] * n_k[m] * (n_k[m]-1) * region_mean[ijkl]
    )
    
    m = masks[iikl].flatten()
    mean_inner_product[m] = (
        n_i[m] * n_k[m] * n_l[m] * region_mean[iikl] +
        n_i[m] * n_k[m] * n_l[m] * (n_i[m]-1) * region_mean[ijkl]
    )
    
    m = masks[ijkl].flatten()
    mean_inner_product[m] = (
        n_i[m] * n_j[m] * n_k[m] * n_l[m] * region_mean[ijkl]
    )
    
    # Flatten the mean_inner array and expand each equation
    return mean_inner_product.reshape(n_elements**2, n_elements**2)

@jit(nopython=True)
def create_region_masks_1_by_2(n_elements):
    ijk, iik, iji, ijj, iii = range(5)
    masks = np.zeros((5, n_elements, n_elements, n_elements), dtype=np.bool_)

    for i in range(n_elements):
        for j in range(n_elements):
            for k in range(n_elements):
                masks[ijk][i, j, k] = (i != j) and (i != k) and (j != k)
                masks[iik][i, j, k] = (i == j) and (i != k)
                masks[iji][i, j, k] = (i == k) and (i != j)
                masks[ijj][i, j, k] = (j == k) and (i != j)
                masks[iii][i, j, k] = (i == j) and (i == k)

    return masks

@jit(nopython=True)
def mean_inner_product_1_by_2(repetitions,indicator_0,indicator_1):
    ijk, iik, iji, ijj, iii = range(5)
    region_mean= compute_region_means_1_by_2(indicator_0,indicator_1)
    n_elements= len(repetitions)

    # Create the mean_inner_product array
    mean_inner_product = np.zeros((n_elements, n_elements, n_elements)).flatten()
    
    # Create arrays of indices for elements
    n_i = np.repeat(repetitions, n_elements**2).reshape(n_elements, n_elements, n_elements)
    n_j = n_i.copy().transpose(2, 0, 1).flatten()
    n_k = n_i.copy().transpose(1, 2, 0).flatten()
    n_i=n_i.flatten()

    # Define masks for elements
    masks = create_region_masks_1_by_2(n_elements)

    m = masks[iii].flatten()
    mean_inner_product[m] = (
        n_i[m] * region_mean[iii] +
        n_i[m] * (n_i[m]-1) * (region_mean[iik] + region_mean[iji] + region_mean[ijj]) +
        n_i[m] * (n_i[m]-1) * (n_i[m]-2) * (region_mean[ijk]) 
    )
    
    m = masks[ijj].flatten()
    mean_inner_product[m] = (
        n_i[m] * n_j[m] * region_mean[ijj] +
        n_i[m] * n_j[m] * (n_j[m]-1) * region_mean[ijk]
    )
    
    m = masks[iji].flatten()
    mean_inner_product[m] = (
        n_i[m] * n_j[m] * region_mean[iji] +
        n_i[m] * n_j[m] * (n_i[m]-1) * region_mean[ijk]
    )

    m = masks[iik].flatten()
    mean_inner_product[m] = (
        n_i[m] * n_k[m] * region_mean[iik] +
        n_i[m] * n_k[m] * (n_i[m]-1) * region_mean[ijk]
    )
    
    m = masks[ijk].flatten()
    mean_inner_product[m] = (
        n_i[m] * n_j[m] * n_k[m] * region_mean[ijk]
    )
    # Flatten the mean_inner array and expand each equation
    return mean_inner_product.reshape(n_elements, n_elements**2)

@jit(nopython=True)
def create_region_masks_1_by_1(n_elements):
    ij, ii = range(2)
    masks = np.zeros((2, n_elements, n_elements), dtype=np.bool_)

    for i in range(n_elements):
        for j in range(n_elements):
            masks[ij][i, j] = (i != j)
            masks[ii][i, j] = (i == j)

    return masks

@jit(nopython=True)
def mean_inner_product_1_by_1(repetitions,indicator_0,indicator_1):
    ij, ii = range(2)
    region_mean= compute_region_means_1_by_1(indicator_0,indicator_1)
    n_elements= len(repetitions)

    # Create the mean_inner_product array
    mean_inner_product = np.zeros((n_elements, n_elements)).flatten()
    
    # Create arrays of indices for elements
    n_i = np.repeat(repetitions, n_elements).reshape(n_elements, n_elements)
    n_j = n_i.copy().transpose(1, 0).flatten()
    n_i=n_i.flatten()

    # Define masks for elements
    masks = create_region_masks_1_by_1(n_elements)
    
    m = masks[ii].flatten()
    mean_inner_product[m] = (
        n_i[m] * region_mean[ii] +
        n_i[m] * (n_i[m]-1) * region_mean[ij]
    )
    
    m = masks[ij].flatten()
    mean_inner_product[m] = (
        n_i[m] * n_j[m] * region_mean[ij]
    )
 
    return mean_inner_product.reshape(n_elements, n_elements)

def create_region_masks(n_elements):
    masks = {}
    masks.update(create_region_masks_1_by_1(n_elements))
    masks.update(create_region_masks_1_by_2(n_elements))
    masks.update(create_region_masks_2_by_2(n_elements))
    return masks



def mean_inner_product(repetitions,indicator_0,indicator_1, parallel=True, use_numba=True):
    s0=indicator_0.shape[0]
    for d in indicator_0.shape:
        assert d==s0, "All dimensions for the indicators should be the same size"
    for d in indicator_1.shape:
        assert d==s0, "Both indicators should be the same size"
    d0 = len(indicator_0.shape)
    d1 = len(indicator_1.shape)
    
    if d0==d1==1:
        result = mean_inner_product_1_by_1(repetitions,indicator_0, indicator_1)
    elif d0==1 and d1==2:
        result = mean_inner_product_1_by_2(repetitions,indicator_0,indicator_1)
    elif d1==1 and d0==2:
        result = mean_inner_product_1_by_2(repetitions,indicator_1,indicator_0).T
    elif d0==d1==2:
        result = mean_inner_product_2_by_2(repetitions,indicator_0,indicator_1)
    else:
        raise NotImplementedError('This method has not be implemented for indicator dimensions {d0} and {d1}')
    return result 

@jit(nopython=True)
def build_mean_inner_product_matrix(repetitions,indicators1d,indicators2d):
    num_matrices1d = len(indicators1d)
    num_matrices2d = len(indicators2d)
    num_matrices = num_matrices1d + num_matrices2d
    n_elements=len(repetitions)
    
    # Compute the size of each block and the total size
    block_sizes = [n_elements for ind in indicators1d] + [n_elements**2 for ind in indicators2d]
    total_size = sum(block_sizes)
    
    # Create the resulting matrix filled with zeros
    R = np.zeros((total_size, total_size))
        
    # Compute the starting indices for each matrix
    #start_indices = np.cumsum([0] + block_sizes[:-1])
    start_indices=np.zeros(len(block_sizes),dtype=np.int64)
    start=0
    for i in range(1,len(block_sizes)):
        start=start+block_sizes[i-1]
        start_indices[i] = start
    
    for i in range(num_matrices):
        for j in range(i, num_matrices):  # Use symmetry, compute only half
            if i<num_matrices1d and j<num_matrices1d:
                result_block = mean_inner_product_1_by_1(repetitions,indicators1d[i], indicators1d[j])
            elif i<num_matrices1d and j>=num_matrices1d:
                result_block = mean_inner_product_1_by_2(repetitions,indicators1d[i],indicators2d[j-num_matrices1d])
            elif j<num_matrices1d and i>=num_matrices1d:
                result_block = mean_inner_product_1_by_2(repetitions,indicators1d[j],indicators2d[i-num_matrices1d]).T
            elif i>=num_matrices1d and j>=num_matrices1d:
                result_block = mean_inner_product_2_by_2(repetitions,indicators2d[i-num_matrices1d],indicators2d[j-num_matrices1d])
           
            si, sj = start_indices[i], start_indices[j]
            ei, ej = si + result_block.shape[0], sj + result_block.shape[1]
            R[si:ei, sj:ej] = result_block
            if i != j:
                R[sj:ej, si:ei] = result_block.T  # Leverage symmetry
            
    return R

def combinatorial_numpy_inner_product(native_sequence, indicator_0,indicator_1):
    elements = np.unique(native_sequence)
    len_elements = len(elements)
    len_sequence = len(native_sequence)
    
    # Flatten indicators
    ind_0 = indicator_0.flatten()
    ind_1 = indicator_1.flatten()

    mean_inners = []
    for indicator_0, indicator_1 in [(ind_0, ind_0), (ind_1, ind_0), (ind_0, ind_1), (ind_1, ind_1)]:
        
        # Outer product of indicators
        indicator_products = np.outer(indicator_0, indicator_1).reshape(len_sequence, len_sequence, len_sequence, len_sequence)
        
        # Create arrays of indices
        indices = np.arange(len_sequence)
        i, j, k, l = np.meshgrid(indices, indices, indices, indices, indexing='ij', sparse=True)
        
        def create_region_masks(i,j,k,l):
            masks = {
            # 'ijkl': No index is the same as any other; all four indices are distinct.
            'ijkl': (i != j) & (i != k) & (i != l) & (j != k) & (j != l) & (k != l),
            # 'ijjl': Two indices are equal and form a pair, while the other two indices are different from the pair and from each other.
            'ijjl': (i != j) & (k != l) & (((i == k) & (j != l)) | ((i == l) & (j != k)) | ((j == k) & (i != l)) | ((j == l) & (i != k))),
            # 'iikl': The first two indices are equal, and the last two are different from the first two and different from each other.
            'iikl': (i == j) & (i != k) & (i != l) & (k != l),
            # 'ijkk': The last two indices are equal, and the first two are different from the last two and different from each other.
            'ijkk': (k == l) & (k != i) & (k != j) & (i != j),
            # 'iiil': The first two indices are equal to one of the last two, the other one of the last two is different.
            'iiil': ((i == j) & (i == k) & (i != l)) | ((i == j) & (i == l) & (i != k)),
            # 'ikkk': The last two indices are equal to one of the first two, the other one of the first two is different.
            'ikkk': ((k == l) & (i == k) & (j != i)) | ((k == l) & (j == k) & (i != j)),
            # 'ijij': The first and third indices are equal, and the second and fourth indices are equal, but the pairs are different from each other.
            'ijij': (((i == k) & (j == l)) | ((i == l) & (j == k))) & (i != j),
            # 'iikk': The first two indices form a pair that is equal, and the last two indices form a different pair that is equal, but the two pairs are different from each other.
            'iikk': (i == j) & (k == l) & (i != k),
            # 'iiii': All indices are equal.
            'iiii': (i == j) & (i == k) & (i == l),
            }
            return masks
        
        
        # Define masks
        #Define masks
        masks = create_region_masks(i,j,k,l)

        # Apply masks to the array and store regions in a dictionary
        region_count = {key: mask.sum() for key, mask in masks.items()}
        region_mean = {key: (indicator_products[mask].mean() if region_count[key] > 0 else 0) for key, mask in masks.items()}
        
        # Create the mean_inner_product array
        mean_inner_product = np.zeros((len_elements, len_elements, len_elements, len_elements))
        
        aa_repetitions = np.array([(native_sequence == k).sum() for k in elements])
        
        # Create arrays of indices for elements
        i, j, k, l = np.meshgrid(indices[:len_elements], indices[:len_elements], indices[:len_elements], indices[:len_elements], indexing='ij', sparse=True)
        n_i, n_j, n_k, n_l = np.meshgrid(aa_repetitions, aa_repetitions, aa_repetitions, aa_repetitions, indexing='ij', sparse=False)
        
        # Define masks for elements
        masks = create_region_masks(i,j,k,l)
        
        m = masks['iiii']
        mean_inner_product[m] = (
            n_i[m] * region_mean['iiii'] +
            n_i[m] * (n_i[m]-1) * (region_mean['iikk'] + 2*region_mean['ijij'] + 2*region_mean['iiil'] + 2*region_mean['ikkk']) +
            n_i[m] * (n_i[m]-1) * (n_i[m]-2) * (4*region_mean['ijjl'] + region_mean['iikl'] + region_mean['ijkk']) +
            n_i[m] * (n_i[m]-1) * (n_i[m]-2) * (n_i[m]-3) * region_mean['ijkl']
        )
        
        m = masks['iikk']
        mean_inner_product[m] = (
            n_i[m]*n_k[m] * region_mean['iikk'] +
            n_i[m]*n_k[m] * (n_k[m]-1) * region_mean['iikl'] +
            n_i[m]*n_k[m] * (n_i[m]-1) * region_mean['ijkk'] +
            n_i[m]*(n_i[m]-1)*n_k[m]*(n_k[m]-1) * region_mean['ijkl']
        )
        
        m = masks['ijij']
        mean_inner_product[m] = (
            n_i[m]*n_j[m] * region_mean['ijij'] +
            (n_i[m]*n_j[m]*(n_j[m]-1) + n_j[m]*n_i[m]*(n_i[m]-1)) * region_mean['ijjl'] +
            n_i[m]*(n_i[m]-1)*n_j[m]*(n_j[m]-1) * region_mean['ijkl']
        )
        
        m = masks['iiil'] 
        n_x=n_k*(i!=k) + n_l*(i!=l) # Sometimes is k and sometimes is l the one that is different
        mean_inner_product[m] = (
            n_x[m]*n_i[m]* region_mean['iiil'] +
            n_x[m]*n_i[m]*(n_i[m]-1) * (2*region_mean['ijjl'] + region_mean['iikl']) +
            n_x[m]*n_i[m]*(n_i[m]-1)*(n_i[m]-2) * region_mean['ijkl']
        )
        
        m = masks['ikkk'] # Sometimes is i and sometimes is j the one that is different
        n_x=n_i*(i!=k)+n_j*(j!=k)
        mean_inner_product[m] = (
            n_x[m]*n_k[m] * region_mean['ikkk'] +
            n_x[m]*n_k[m]*(n_k[m]-1) * (2*region_mean['ijjl'] + region_mean['ijkk']) +
            n_x[m]*n_k[m]*(n_k[m]-1)*(n_k[m]-2) * region_mean['ijkl']
        )
        
        m = masks['ijjl']
        n_a=n_j*(i==k)+n_j*(i==l)+n_i*(j==k)+n_i*(j==l) #Different pair from first group
        n_b=n_i*(i==k)+n_i*(i==l)+n_j*(j==k)+n_j*(j==l) #Equal pair from first group
        n_c=n_l*(i==k)+n_k*(i==l)+n_l*(j==k)+n_k*(j==l) #Different pair from second group
        mean_inner_product[m] = (
            n_a[m]*n_b[m]*n_c[m] * region_mean['ijjl'] +
            n_a[m]*n_b[m]*(n_b[m]-1)*n_c[m] * region_mean['ijkl']
        )
        
        m = masks['ijkk']
        mean_inner_product[m] = (
            n_i[m]*n_j[m]*n_k[m] * region_mean['ijkk'] +
            n_i[m]*n_j[m]*n_k[m]*(n_k[m]-1) * region_mean['ijkl']
        )
        
        m = masks['iikl']
        mean_inner_product[m] = (
            n_i[m]*n_k[m]*n_l[m] * region_mean['iikl'] +
            n_i[m]*(n_i[m]-1)*n_k[m]*n_l[m] * region_mean['ijkl']
        )
        
        m = masks['ijkl']
        mean_inner_product[m] = (
            n_i[m]*n_j[m]*n_k[m]*n_l[m] * region_mean['ijkl']
        )
        
        # Flatten the mean_inner array and expand each equation
        mean_inners.append(mean_inner_product.reshape(len_elements**2, len_elements**2))

    return np.concatenate([np.concatenate([mean_inners[0], mean_inners[1]]), np.concatenate([mean_inners[2], mean_inners[3]])], axis=1)

from itertools import permutations

def permutation_numpy_inner_product(native_sequence, indicators):
    elements = np.unique(native_sequence)
    decoy_sequences = np.array(list(permutations(native_sequence)))
    
    # Determine the length of phi_decoy
    phi_len = sum(len(elements) if len(ind.shape) == 1 else len(elements)**2 for ind in indicators)
    
    phi_inner_products = []
    for decoy_sequence in decoy_sequences:
        phi_decoy = np.zeros(phi_len)
        offset = 0
        decoy_pairs = (np.array(np.meshgrid(decoy_sequence, decoy_sequence)) * np.array([1, len(elements)])[:, None, None]).sum(axis=0).ravel()
        for indicator in indicators:
            if len(indicator.shape) == 1:  # 1D indicator
                np.add.at(phi_decoy, decoy_sequence + offset, indicator)
                offset += len(elements)
            elif len(indicator.shape) == 2:  # 2D indicator
                np.add.at(phi_decoy, decoy_pairs + offset, indicator.ravel())
                offset += len(elements) ** 2
        
        phi_inner_products.append(np.outer(phi_decoy, phi_decoy))
    
    phi_inner_products = np.array(phi_inner_products)
    mean_phi_inner = phi_inner_products.mean(axis=0)
    
    return mean_phi_inner


def template_test_compute_region_means(compute_func_numpy, compute_func, setup_func, length_range, atol=1e-8):
    """
    Generic test function to compare the outputs of compute_func_numpy and compute_func.
    Ensures that the computed region means by both functions are equal within a tolerance.
    
    Raises an AssertionError if the computed dictionaries do not match for any key in any iteration.
    """
    for length in length_range:
        print(length)
        indicator_0, indicator_1 = setup_func(length)

        # Compute region means using both functions
        s0 = compute_func_numpy(indicator_0, indicator_1)
        s1 = compute_func(indicator_0, indicator_1)

        # Ensure keys match
        if len(s0) != len(s1):
            raise AssertionError(f"Arrays of different length for length {length}. Numpy: {len(s0)}, Original: {len(s1)}")
        
        # Extract keys and values
        s0_values = s0
        s1_values = s1

        # Find indices where values are not close
        not_close = ~np.isclose(s0_values, s1_values, atol=atol)
        if np.any(not_close):
            s0_diff = s0_values[not_close]
            s1_diff = s1_values[not_close]
            diffs = "\n".join([f"{key}: numpy={s0_val}, original={s1_val}" 
                               for key, s0_val, s1_val in zip(not_close, s0_diff, s1_diff)])
            raise AssertionError(f"Mismatch found in results for length {length}:\n{diffs}")

# Setup functions for each test scenario
def setup_1_by_1(length):
    return np.random.rand(length), np.random.rand(length)

def setup_1_by_2(length):
    indicator_0 = np.random.rand(length)
    indicator_1 = np.random.rand(length, length)
    indicator_1 = (indicator_1 + indicator_1.T) / 2
    return indicator_0, indicator_1

def setup_2_by_2(length):
    indicator_0 = np.random.rand(length, length)
    indicator_1 = np.random.rand(length, length)
    indicator_0 = (indicator_0 + indicator_0.T) / 2
    indicator_1 = (indicator_1 + indicator_1.T) / 2
    return indicator_0, indicator_1

# Specific test functions
def test_compute_region_means_1_by_1():
    template_test_compute_region_means(compute_region_means_1_by_1_numpy, compute_region_means_1_by_1, setup_1_by_1, range(1, 200))

def test_compute_region_means_1_by_2():
    template_test_compute_region_means(compute_region_means_1_by_2_numpy, compute_region_means_1_by_2, setup_1_by_2, range(1, 100))

def test_compute_region_means_2_by_2():
    template_test_compute_region_means(compute_region_means_2_by_2_numpy, compute_region_means_2_by_2, setup_2_by_2, range(1, 40))

def test_compute_region_means_2_by_2_parallel():
    template_test_compute_region_means(compute_region_means_2_by_2, compute_region_means_2_by_2_parallel, setup_2_by_2, range(1, 50))


def test_compute_region_means():
    template_test_compute_region_means(compute_region_means, compute_region_means_1_by_1, setup_1_by_1, range(1, 400,5))
    template_test_compute_region_means(compute_region_means, compute_region_means_1_by_2, setup_1_by_2, range(1, 400,5))
    template_test_compute_region_means(compute_region_means, compute_region_means_2_by_2_parallel, setup_2_by_2, range(1, 300,5))

def test_mean_inner_product_2_by_2():
    #indicator_0,indicator_1=setup_2_by_2(200)
    #repetitions=np.array([10]*20)
    #print(mean_inner_product_2_by_2(repetitions,indicator_0,indicator_1)-np.mean(indicator_0)*np.outer(np.outer(repetitions,repetitions).ravel(),np.outer(repetitions,repetitions).ravel())*np.mean(indicator_1))
    # Define test cases
    native_sequences=[
        [0,1],
        [0,1,1],
        [0,1,1,1],
        [0,1,2],
        [0,1,2,2],
        [0,1,1,2,2],
        [0,1,1,2,2,2],
        [0,1,2,3,4],
        [0,1,2,3,4,5],
        [0,1,1,2,3,4],
        [0,0,1,1,2,2],
        [0,1,1,1,1],
        [0,1,1,1,1,1],
        [0,1,1,1,1,1,1],
        [0,0,1,1],
        [0,0,1,1,1],
        [0,0,0,1,1,1],
        [0,1,2,3],
        [0,0,1,2,3],
        [0,0,0,1,2,3],
        [0,0,0,1,1,2,3], 
        [0,0,0,0,1,2,3],
    ]

    # Test each case
    for i, seq in enumerate(native_sequences):
        print(f"Testing case {i+1}/{len(native_sequences)}: {seq}")
        indicator_0=np.random.rand(*[len(seq)]*2)
        indicator_1=np.random.rand(*[len(seq)]*2)
        indicator_0=(indicator_0+indicator_0.T)/2
        indicator_1=(indicator_1+indicator_1.T)/2
        values_numpy_combinatorial=combinatorial_numpy_inner_product(seq,indicator_0,indicator_1)
        values_numpy_permutation=permutation_numpy_inner_product(seq,[indicator_0,indicator_1])

        elements = np.unique(seq)
        aa_repetitions = np.array([(seq == k).sum() for k in elements])
        values_numba=build_mean_inner_product_matrix(aa_repetitions,[],[indicator_0,indicator_1])

        assert values_numba.shape == values_numpy_combinatorial.shape, f"Shapes differ combinatorial_numpy_inner_product shape.shape {values_numpy_combinatorial.shape} build_mean_inner_product_matrix.shape{values_numba.shape}"
        assert values_numba.shape == values_numpy_permutation.shape, f"Shapes differ combinatorial_numpy_inner_product shape.shape {values_numpy_permutation.shape} build_mean_inner_product_matrix.shape{values_numba.shape}"
        
        # Compare the results
        if np.allclose(values_numba, values_numpy_combinatorial):
            print("Results are the same!")
        else:
            print("Results differ!")
            # Optionally, show where they differ
            print("Difference:")
            print(values_numba - values_numpy_combinatorial)
            break
        
        # Compare the results
        if np.allclose(values_numba, values_numpy_permutation):
            print("Results are the same!")
        else:
            print("Results differ!")
            # Optionally, show where they differ
            print("Difference:")
            print(values_numba - values_numpy_permutation)
            break

def test_mean_inner_product_1_by_2():
    length=20
    indicator_0 = np.random.rand(length)
    indicator_1 = np.random.rand(length, length)
    indicator_1 = (indicator_1 + indicator_1.T) / 2
    seq=[0,0,1,2,3]*4
    elements = np.unique(seq)
    aa_repetitions = np.array([(seq == k).sum() for k in elements])
    mean_inner_product_1_by_2(aa_repetitions,indicator_0,indicator_1)

def test_mean_inner_product():
    native_sequences=[
        [0,1],
        [0,1,1],
        [0,1,1,1],
        [0,1,2],
        [0,1,2,2],
        [0,1,1,2,2],
        [0,1,1,2,2,2],
        [0,1,2,3,4],
        [0,1,2,3,4,5],
        [0,1,1,2,3,4],
        [0,0,1,1,2,2],
        [0,1,1,1,1],
        [0,1,1,1,1,1],
        [0,1,1,1,1,1,1],
        [0,0,1,1],
        [0,0,1,1,1],
        [0,0,0,1,1,1],
        [0,1,2,3],
        [0,0,1,2,3],
        [0,0,0,1,2,3],
        [0,0,0,1,1,2,3], 
        [0,0,0,0,1,2,3],
    ]

    # Test each case
    for i, seq in enumerate(native_sequences):
        print(f"Testing case {i+1}/{len(native_sequences)}: {seq}")
        indicator1D_0 = np.random.rand(len(seq))
        indicator1D_1 = np.random.rand(len(seq))
        indicator2D_0 = np.random.rand(len(seq), len(seq))
        indicator2D_1 = np.random.rand(len(seq), len(seq))
        indicator2D_0=(indicator2D_0+indicator2D_0.T)/2
        indicator2D_1=(indicator2D_1+indicator2D_1.T)/2
        values_numpy_permutation=permutation_numpy_inner_product(seq,[indicator1D_0, indicator1D_1, indicator1D_0, indicator2D_0, indicator2D_1, indicator2D_0])

        elements = np.unique(seq)
        aa_repetitions = np.array([(seq == k).sum() for k in elements])
        values_numba=build_mean_inner_product_matrix(aa_repetitions,np.array([indicator1D_0, indicator1D_1, indicator1D_0]),np.array([indicator2D_0, indicator2D_1,indicator2D_0]))

        print("type aa_repetitions",type(aa_repetitions))
        print("aa_repetitions.shape",aa_repetitions.shape)
        print("type indicator1D",type([indicator1D_0, indicator1D_1]))
        print("types indicator1D",[type(i) for i in [indicator1D_0, indicator1D_1]])
        print("shapes indicator1D",[i.shape for i in [indicator1D_0, indicator1D_1]])
        print("types indicator2D",[type(i) for i in [indicator2D_0, indicator2D_1]])
        print("shapes indicator2D",[i.shape for i in [indicator2D_0, indicator2D_1]])
        print("type values_numba",type(values_numba))

        assert values_numba.shape == values_numpy_permutation.shape, f"Shapes differ combinatorial_numpy_inner_product shape.shape {values_numpy_permutation.shape} build_mean_inner_product_matrix.shape{values_numba.shape}"
        
        # Compare the results
        if np.allclose(values_numba, values_numpy_permutation):
            print("Results are the same!")
        else:
            print("Results differ!")
            # Optionally, show where they differ
            print("Difference:")
            print(values_numba - values_numpy_permutation)
            raise AssertionError("Results differ!")

if __name__=='__main__':# Call the test function
    # print("Testing compute_region_means_1_by_1")
    # test_compute_region_means_1_by_1()
    # print("Testing compute_region_means_1_by_2")
    # test_compute_region_means_1_by_2()
    # print("Testing compute_region_means_2_by_2")
    # test_compute_region_means_2_by_2()
    # print("Testing compute_region_means_2_by_2_parallel")
    # test_compute_region_means_2_by_2_parallel()
    # print("Testing compute_region_means")
    # test_compute_region_means()
    # print("Testing mean_inner_product_1_by_2")
    # test_mean_inner_product_1_by_2()
    # print("Testing mean_inner_product_2_by_2")
    # test_mean_inner_product_2_by_2()
    print("Testing mean_inner_product")
    test_mean_inner_product()

    
    #Profiling

    # Look up the signature of the first thing that's been compiled.
    signature = build_mean_inner_product_matrix.signatures[0]
    # Find the "overload" for it, this is what Numba uses internally to represent
    # the compiled function.
    overload = build_mean_inner_product_matrix.overloads[signature]

    # This is the pipeline we want to look at, @njit = nopython pipeline.
    pipeline = 'nopython'

    # Print the information, it's in the overload.metadata dictionary.
    width = 20
    print("\n\nTimings:\n")
    for name, time in overload.metadata['pipeline_times'][pipeline].items():
        fmt = (f'{name: <{40}}:'
            f'{time.init:<{width}.6f}'
            f'{time.run:<{width}.6f}'
            f'{time.finalize:<{width}.6f}')
        print(fmt)
    
    numba_functions = [
        compute_region_means_2_by_2_parallel,
        compute_region_means_1_by_2,
        compute_region_means_1_by_1,
        create_region_masks_2_by_2,
        mean_inner_product_2_by_2,
        create_region_masks_1_by_2,
        mean_inner_product_1_by_2,
        create_region_masks_1_by_1,
        mean_inner_product_1_by_1,
        build_mean_inner_product_matrix
    ]

    #Typing
    for func in numba_functions:
        # Print the function name
        print(f"\nFunction: {func.__name__}")

        # Print inferred types
        #print("Inferred types:")
        #func.inspect_types()

        # Print compiled signatures
        print("Compiled signatures:", func.signatures)

    # Time the functions
    import time
    import numpy as np

    
    