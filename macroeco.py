"""Module for conducting standard macroecological plots and analyses"""

from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
import colorsys
import convhull
from numpy import log10

def get_rad_from_cdf(cdf, S):
    """Return a predicted rank-abundance distribution from a theoretical CDF
    
    Keyword arguments:
    cdf -- a function characterizing the theoretical cdf (likely from pylab)
    S -- the number of species for which the RAD should be predicted. Should
    match the number of species in the community if comparing to empirical data.
    
    Finds the predicted rank-abundance distribution that results from a
    theoretical cumulative distribution function, by rounding the value of the
    cdf evaluated at 1 / S * (Rank - 0.5) to the nearest integer
    
    """

def plot_rad(Ns):
    """Plot a rank-abundance distribution based on a vector of abundances"""
    Ns.sort(reverse=True)
    rank = range(1, len(Ns) + 1)
    plt.plot(rank, Ns, 'bo-')
    plt.xlabel('Rank')
    plt.ylabel('Abundance')

def get_rad_data(Ns):
    """Provide ranks and relative abundances for a vector of abundances"""
    Ns = np.array(Ns)
    Ns_sorted = -1 * np.sort(-1 * Ns)
    relab_sorted = Ns_sorted / sum(Ns_sorted)
    rank = range(1, len(Ns) + 1)
    return (rank, relab_sorted)
    
def plot_multiple_rads(list_of_abund_vectors):
    """Plots multiple rank-abundance distributions on a single plot"""
    #TO DO:
    #  Allow this function to handle a single abundance vector
    #     Currently would treat each value as a full abundance vector
    #     Could then change this to plot_rads and get rid of plot_rad
    plt.figure()
    line_styles = ['bo-', 'ro-', 'ko-', 'go-', 'bx--', 'rx--', 'kx--', 'gx--']
    num_styles = len(line_styles)
    plt.hold(True)
    for (style, Ns) in enumerate(list_of_abund_vectors):
        (rank, relab) = get_rad_data(Ns)
        #Plot line rotating through line_styles and starting at the beginning
        #of line_styles again when all values have been used
        plt.semilogy(rank, relab, line_styles[style % num_styles])
    plt.hold(False)
    plt.xlabel('Rank')
    plt.ylabel('Abundance')
    
def plot_SARs(list_of_A_and_S):
    """Plot multiple SARs on a single plot. 
    
    Input: a list of lists, each sublist contains one vector for S and one vector for A.
    Output: a graph with SARs plotted on log-log scale, with colors spanning the spectrum.
    
    """
    N = len(list_of_A_and_S)
    HSV_tuples = [(x * 1.0 / N, 0.5, 0.5) for x in range(N)]
    RGB_tuples = map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples)
    for i in range(len(list_of_A_and_S)):
        sublist = list_of_A_and_S[i]
        plt.loglog(sublist[0], sublist[1], color = RGB_tuples[i])
    plt.hold(False)
    plt.xlabel('Area')
    plt.ylabel('Richness')
    
def count_pts_within_radius(x, y, radius, logscale=0):
    #TODO: see if we can improve performance using KDTree.query_ball_point
    #http://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.KDTree.query_ball_point.html
    #instead of doing the subset based on the circle
    raw_data = np.array([x, y])
    raw_data = raw_data.transpose()
    
    # Get unique data points by adding each pair of points to a set
    unique_points = set()
    for xval, yval in raw_data:
        unique_points.add((xval, yval))
    
    count_data = []
    for a, b in unique_points:
        if logscale == 1:
            num_neighbors = len(x[((log10(x) - log10(a)) ** 2 +
                                   (log10(y) - log10(b)) ** 2) <= log10(radius) ** 2])
        else:        
            num_neighbors = len(x[((x - a) ** 2 + (y - b) ** 2) <= radius ** 2])
        count_data.append((a, b, num_neighbors))
    return count_data

def plot_color_by_pt_dens(x, y, radius, loglog=0, plot_obj=plt.axes()):
    """Plot bivariate relationships with large n using color for point density
    
    Inputs:
    x & y -- variables to be plotted
    radius -- the linear distance within which to count points as neighbors
    loglog -- a flag to indicate the use of a loglog plot (loglog = 1)
    
    The color of each point in the plot is determined by the logarithm (base 10)
    of the number of points that occur with a given radius of the focal point,
    with hotter colors indicating more points. The number of neighboring points
    is determined in linear space regardless of whether a loglog plot is
    presented.

    """
    plot_data = count_pts_within_radius(x, y, radius, loglog)
    sorted_plot_data = np.array(sorted(plot_data, key=lambda point: point[2]))
    
    if loglog == 1:
        plot_obj.set_xscale('log')
        plot_obj.set_yscale('log')
        plot_obj.scatter(sorted_plot_data[:, 0], sorted_plot_data[:, 1],
                         c = log10(sorted_plot_data[:, 2]), faceted=False)
        plot_obj.set_xlim(min(x) * 0.5, max(x) * 2)
        plot_obj.set_ylim(min(y) * 0.5, max(y) * 2)
    else:
        plot_obj.scatter(sorted_plot_data[:, 0], sorted_plot_data[:, 1],
                    c = log10(sorted_plot_data[:, 2]), faceted=False)
    return plot_obj

def confidence_hull(x, y, radius, confidence_int = 0.95, logscale=0, color='b',
                    alpha=0.5):
    count_data = count_pts_within_radius(x, y, radius, logscale)
    sorted_count_data = np.array(sorted(count_data, key=lambda point: point[2], reverse=True))
    total_count = sum(sorted_count_data[:, 2])
    cum_proportion_of_counts = (np.cumsum(sorted_count_data[:, 2], axis=0) /
                                    total_count)
    sorted_points = sorted_count_data[:, 0:2]
    confidence_points = sorted_points[cum_proportion_of_counts <= confidence_int]
    hull_points = convhull.convex_hull(confidence_points.transpose(), graphic = False)
    plot_points = np.vstack([hull_points, hull_points[0, :]])
    plot_obj = plt.axes()
    if logscale == 1:        
        plot_obj.set_xscale('log')
        plot_obj.set_yscale('log')
        plot_obj.fill(plot_points[:,0], plot_points[:,1], color, alpha=alpha)
    else:
        plot_obj.fill(plot_points[:,0], plot_points[:,1], color, alpha=alpha)
    return hull_points

def e_var(abundance_data):
    """Calculate Smith and Wilson's (1996; Oikos 76:70-82) evenness index (Evar)
    
    Input:
    abundance_data = list of abundance fo all species in a community
    
    """
    S = len(abundance_data)
    ln_nj_over_S=[]
    for i in range(0, S):
        v1 = (np.log(abundance_data[i]))/S
        ln_nj_over_S.append(v1)     
    
    ln_ni_minus_above=[]
    for i in range(0, S):
        v2 = ((np.log(abundance_data[i])) - sum(ln_nj_over_S)) ** 2
        ln_ni_minus_above.append(v2)
        
    return(1 - ((2 / np.pi) * np.arctan(sum(ln_ni_minus_above) / S)))

def obs_pred_rsquare(obs, pred):
    """Determines the prop of variability in a data set accounted for by a model"""
    return 1 - sum((obs - pred) ** 2) / sum((obs - np.mean(obs)) ** 2)