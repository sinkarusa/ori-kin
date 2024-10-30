import numpy as np


def calculate_parameters(r, n):
    theta1 = np.radians(180 / (n * (n + 1)))
    theta_l = (np.pi / n) - theta1
    CD = (theta_l - theta1) / (n - 1)
    
    thetas = [theta1 + i * CD for i in range(n)]
    s = [2 * r * np.sin(theta / 2) for theta in thetas]
    A = [np.pi/2 - theta/2 for theta in thetas]
    beta = [A[i] + A[i+1] for i in range(n-1)]
    a = [2 * r * np.cos((np.pi - (thetas[i] + thetas[i+1])) / 2) for i in range(n-1)]
    
    alpha = []
    for i in range(0, n-1):
        alpha_i1 = np.arcsin(np.sin(beta[i]) * s[i+1] / a[i])
        alpha_i2 = np.arcsin(np.sin(beta[i]) * s[i] / a[i])
        alpha.append((alpha_i1, alpha_i2))
    
    # Calculate heights (h)
    h = [s[0] * np.sin(alpha[0][0])]  # h1 uses alpha11
    h.extend([s[i] * np.sin(alpha[i][0]) for i in range(1, n-1)])

    # calculate last parameters that are special
    alpha_l1 = np.pi - (beta[-1] + alpha[-2][1])
    alpha_l2 = np.pi/2 - alpha_l1

    hl = s[-1]*np.sin(alpha_l1)
    alpha.append((alpha_l1,alpha_l2))
    
    h.append(hl)
    
    # Calculate number of radial segments
    num_radial_segments = int(round(360 / (2 * np.degrees(alpha[0][0]/2))))
    
    return thetas, s, A, beta, a, alpha, h, theta1, theta_l, CD, alpha[0][0], num_radial_segments
