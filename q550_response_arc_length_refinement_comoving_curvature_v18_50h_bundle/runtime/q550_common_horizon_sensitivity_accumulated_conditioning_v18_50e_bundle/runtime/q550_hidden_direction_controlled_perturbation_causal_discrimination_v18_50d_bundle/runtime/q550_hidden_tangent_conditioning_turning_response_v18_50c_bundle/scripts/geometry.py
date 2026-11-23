"""Numerical direction geometry in an explicitly fixed diagonal metric.

These quantities are chart-based diagnostics, not mechanical covariant derivatives.
"""
import numpy as np


def unit_tangent(v, scale):
    a = np.asarray(v, dtype=float) / np.asarray(scale, dtype=float)
    lengths = np.linalg.norm(a, axis=-1)
    if not np.isfinite(a).all() or np.any(lengths <= 1e-14):
        raise ValueError('Null/invalid hidden tangent')
    return a / lengths[..., None]


def directional_derivative(xi, unit):
    xi = np.asarray(xi, dtype=float)
    if np.any(np.diff(xi) <= 0) or len(xi) < 5:
        raise ValueError('Require increasing grid of length >= 5')
    deriv = np.gradient(unit, xi, axis=0, edge_order=2)
    # Remove tiny numerical radial component from the derivative of a unit vector.
    return deriv - np.einsum('ij,ij->i', deriv, unit)[:, None] * unit


def wedge_components(u, du):
    u, du = np.asarray(u), np.asarray(du)
    assert u.shape == du.shape and u.shape[-1] == 4
    return np.column_stack([u[..., i] * du[..., j] - u[..., j] * du[..., i]
                            for i in range(4) for j in range(i+1, 4)])


def direction_geometry(xi, h, scale):
    u = unit_tangent(h, scale)
    deriv = directional_derivative(xi, u)
    turn_rate = np.linalg.norm(deriv, axis=1)
    omega = wedge_components(u, deriv)
    # In Euclidean 4D |u wedge du| == |du| for unit u, u dot du == 0.
    if np.max(np.abs(np.linalg.norm(omega, axis=1) - turn_rate)) > 1e-6:
        raise RuntimeError('Wedge norm/turn rate identity violated')
    return u, deriv, turn_rate, omega


def secant_angle(a, b):
    co = np.clip(float(np.dot(a, b)), -1., 1.)
    return float(np.degrees(np.arccos(co)))


def interp_row(grid, values, t):
    return np.array([np.interp(t, grid, values[:, j]) for j in range(values.shape[1])])
