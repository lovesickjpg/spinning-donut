import math
import sys
import time
import numpy as np

screen_width = 80
screen_height = 30
theta_spacing = 0.07
phi_spacing = 0.02
r1 = 1
r2 = 2
k2 = 5
k1 = screen_width * k2 * 3 / (8 * (r1 + r2))

output = np.full((screen_height, screen_width), ' ', dtype='<U1')
zbuffer = np.zeros((screen_height, screen_width), dtype=np.float32)

def render(a, b):
    output.fill(' ')
    zbuffer.fill(0)
    
    theta = np.arange(0, 2 * np.pi, theta_spacing)
    phi = np.arange(0, 2 * np.pi, phi_spacing)
    theta_grid, phi_grid = np.meshgrid(theta, phi, indexing='ij')
    
    costheta, sintheta = np.cos(theta_grid), np.sin(theta_grid)
    cosphi, sinphi = np.cos(phi_grid), np.sin(phi_grid)
    cosa, sina = np.cos(a), np.sin(a)
    cosb, sinb = np.cos(b), np.sin(b)
    
    circlex = r2 + r1 * costheta
    circley = r1 * sintheta
    
    x = circlex * (cosb * cosphi + sina * sinb * sinphi) - circley * cosa * sinb
    y = circlex * (sinb * cosphi - sina * cosb * sinphi) + circley * cosa * cosb
    z = k2 + cosa * circlex * sinphi + circley * sina
    ooz = 1 / z
    
    xp = (screen_width / 2 + k1 * ooz * x).astype(np.int32)
    yp = (screen_height / 2 - k1 * ooz * y).astype(np.int32)
    
    l = (cosphi * costheta * cosb - cosa * sintheta * sinb - 
         cosphi * costheta * sinb - cosa * sintheta * cosb - 
         sina * sintheta)
    
    xpflat = xp.ravel()
    ypflat = yp.ravel()
    oozflat = ooz.ravel()
    lflat = l.ravel()
    
    mask = ((xpflat >= 0) & (xpflat < screen_width) & 
            (ypflat >= 0) & (ypflat < screen_height))
    
    for i in np.where(mask)[0]:
        xi, yi = int(xpflat[i]), int(ypflat[i])
        depth = float(oozflat[i])
        lum = float(lflat[i])
        
        if depth > zbuffer[yi, xi]:
            zbuffer[yi, xi] = depth
            lumindex = int(lum * 8)
            lumindex = max(0, min(lumindex, 11))
            output[yi, xi] = '.,-~:;=!*#$@'[lumindex]

def show():
    sys.stdout.write("\x1b[H")
    sys.stdout.write('\n'.join(''.join(row) for row in output))
    sys.stdout.flush()

sys.stdout.write("\x1b[2J\x1b[?25l")

a = 0
b = 0

try:
    while True:
        render(a, b)
        show()
        a += 0.04
        b += 0.02
        time.sleep(0.03)
except KeyboardInterrupt:
    sys.stdout.write("\x1b[?25h")
    print("\n")
