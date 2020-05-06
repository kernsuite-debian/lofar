# Copyright (C) 2012-2015  ASTRON (Netherlands Institute for Radio Astronomy)
# P.O. Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This file is part of the LOFAR software suite.
# The LOFAR software suite is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The LOFAR software suite is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with the LOFAR software suite. If not, see <http://www.gnu.org/licenses/>.

from numpy import sqrt, sin, cos, arctan2, array, cross, dot, ones
from numpy.linalg.linalg import norm
from scipy.interpolate import Rbf # Radial basis function interpolation.
from numpy.linalg import lstsq

__all__ = ['geographic_from_xyz', 'pqr_cs002_from_xyz']


def normalized_earth_radius(latitude_rad):
    wgs84_f = 1./298.257223563
    return 1.0/sqrt(cos(latitude_rad)**2 + ((1.0 - wgs84_f)**2)*(sin(latitude_rad)**2))


def geographic_from_xyz(xyz_m):
    '''
    convert xyz coordinates to wgs84 coordinates
    :param xyz_m: 1D array/list/tuple of x,y,z in meters
    :return: tuple of lat_rad, lon_rad, height_m
    '''
    wgs84_a = 6378137.0
    wgs84_f = 1./298.257223563
    wgs84_e2 = wgs84_f*(2.0 - wgs84_f)
    
    x_m, y_m, z_m = xyz_m
    lon_rad = arctan2(y_m, x_m)
    r_m = sqrt(x_m**2 + y_m**2)
    # Iterate to latitude solution
    phi_previous = 1e4
    phi = arctan2(z_m, r_m)
    while abs(phi -phi_previous) > 1.6e-12:
        phi_previous = phi
        phi = arctan2(z_m + wgs84_e2*wgs84_a*normalized_earth_radius(phi)*sin(phi),
                      r_m)
    lat_rad = phi
    height_m = r_m*cos(lat_rad) + z_m*sin(lat_rad) - wgs84_a*sqrt(1.0 - wgs84_e2*sin(lat_rad)**2)
    return lat_rad, lon_rad, height_m


def xyz_from_geographic(lon_rad, lat_rad, height_m):
    c = normalized_earth_radius(lat_rad)
    wgs84_f = 1./298.257223563
    wgs84_a = 6378137.0
    s = c*((1 - wgs84_f)**2)
    return array([
        ((wgs84_a*c) + height_m)*cos(lat_rad)*cos(lon_rad),
        ((wgs84_a*c) + height_m)*cos(lat_rad)*sin(lon_rad),
        ((wgs84_a*s) + height_m)*sin(lat_rad)])



def normal_vector_ellipsoid(lon_rad, lat_rad):
    return array([cos(lat_rad)*cos(lon_rad),
                  cos(lat_rad)*sin(lon_rad),
                  sin(lat_rad)])

def normal_vector_meridian_plane(xyz_m):
    x_m, y_m, _ = xyz_m
    return array([y_m, -x_m, 0.0])/sqrt(x_m**2 + y_m**2)

def projection_matrix(xyz0_m, normal_vector):
    r_unit = normal_vector
    meridian_normal = normal_vector_meridian_plane(xyz0_m)
    q_unit = cross(meridian_normal, r_unit)
    q_unit /= norm(q_unit)
    p_unit = cross(q_unit, r_unit)
    p_unit /= norm(p_unit)
    return array([p_unit, q_unit, r_unit]).T

def transform(xyz_m, xyz0_m, mat):
    offsets = xyz_m  - xyz0_m
    return array([dot(mat, offset) for offset in offsets])

LOFAR_XYZ0_m = array([3826574.0, 461045.0, 5064894.5])
LOFAR_REF_MERIDIAN_NORMAL = normal_vector_meridian_plane(LOFAR_XYZ0_m)
LOFAR_PQR_TO_ETRS_MATRIX = array([[ -1.19595105e-01,  -7.91954452e-01,   5.98753002e-01],
                                  [  9.92822748e-01,  -9.54186800e-02,   7.20990002e-02],
                                  [  3.30969000e-05,   6.03078288e-01,   7.97682002e-01]])



def pqr_from_xyz(xyz_m, xyz0_m=LOFAR_XYZ0_m, matrix=LOFAR_PQR_TO_ETRS_MATRIX):
    return transform(xyz_m, xyz0_m, matrix.T)

def interpolation_function(pqr):
    '''
    Return an interpolation function fn(x, y, z), which returns the value at x, y.
    '''
    rbfi = Rbf(pqr[:,0], pqr[:,1], 0.0*pqr[:,2], pqr[:,2], function='linear')
    def interpolator(x_m, y_m):
        return rbfi(x_m, y_m, y_m*0.0)
    return interpolator


def fit_plane(xyz):
    # data_model z = ax +by +c
    # M colvec(a, b, c) = colvec(z)
    # M row i = (x_i, y_i, 1.0)
    mean_position = xyz.mean(axis=0)

    mat = array([xyz[:,0]- mean_position[0],
                 xyz[:,1]- mean_position[1],
                 ones(len(xyz[:,2]))]).T
    a, b, c = lstsq(mat, xyz[:,2] - mean_position[2])[0]
    normal_vector = array([-a, -b, 1.0])
    normal_vector /= norm(normal_vector)
    return {'mean': mean_position, 'normal': normal_vector}


def pqr_cs002_from_xyz(xyz_m):
    '''
    convert xyz coordinates to lofar pqr coordinates with origin in CS002
    :param xyz_m: 1D array/list/tuple of x,y,z in meters
    :return: tuple of pqr coords in meters
    '''
    pqr = pqr_from_xyz(array([xyz_m]),
                       xyz0_m=array([ 3826577.462,   461022.624,  5064892.526]))
    return pqr[0][0], pqr[0][1], pqr[0][2]
