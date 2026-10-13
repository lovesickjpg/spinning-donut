"""
Spinning ASCII donut in the terminal.

The math is from Andy Sloane's donut.c:
https://www.a1k0n.net/2011/07/20/donut-math.html

The difference is that here the whole frame is computed with numpy at once,
including the z-buffer, so there's no python loop over points.
"""

import argparse
import os
import shutil
import sys
import time

import numpy as np

# darkest -> brightest
SHADES = np.array(list(".,-~:;=!*#$@"))

R1 = 1.0  # radius of the tube
R2 = 2.0  # distance from the center of the donut to the center of the tube
K2 = 5.0  # distance from the viewer to the donut

# a terminal cell is roughly twice as tall as it is wide,
# without this the donut looks squished
CHAR_ASPECT = 2.0

HIDE_CURSOR = "\x1b[?25l"
SHOW_CURSOR = "\x1b[?25h"
CLEAR = "\x1b[2J"
HOME = "\x1b[H"


class Torus:
    """Points on the surface of a torus. They don't depend on rotation,
    so they're computed once and reused for every frame."""

    def __init__(self, theta_step=0.07, phi_step=0.02):
        # theta goes around the tube, phi goes around the center of the donut
        theta, phi = np.meshgrid(
            np.arange(0, 2 * np.pi, theta_step),
            np.arange(0, 2 * np.pi, phi_step),
            indexing="ij",
        )
        theta, phi = theta.ravel(), phi.ravel()

        self.cos_t, self.sin_t = np.cos(theta), np.sin(theta)
        self.cos_p, self.sin_p = np.cos(phi), np.sin(phi)

        # the circle that gets swept around the y axis to make the donut
        self.circle_x = R2 + R1 * self.cos_t
        self.circle_y = R1 * self.sin_t


def render_frame(torus, a, b, width, height):
    """Returns the frame as a (height, width) array of characters.
    a is the rotation around the x axis, b around the z axis."""
    cos_a, sin_a = np.cos(a), np.sin(a)
    cos_b, sin_b = np.cos(b), np.sin(b)

    ct, st = torus.cos_t, torus.sin_t
    cp, sp = torus.cos_p, torus.sin_p
    cx, cy = torus.circle_x, torus.circle_y

    # rotate around y (phi), then x (a), then z (b)
    x = cx * (cos_b * cp + sin_a * sin_b * sp) - cy * cos_a * sin_b
    y = cx * (sin_b * cp - sin_a * cos_b * sp) + cy * cos_a * cos_b
    z = K2 + cos_a * cx * sp + cy * sin_a
    ooz = 1 / z  # "one over z", the bigger it is the closer the point

    # surface normal dotted with the light direction (0, 1, -1).
    # goes from -sqrt(2) to sqrt(2)
    lum = (cp * ct * sin_b - cos_a * ct * sp - sin_a * st
           + cos_b * (cos_a * st - ct * sin_a * sp))

    # the original used 3/8 of the screen width here, but with perspective
    # the close side of the donut gets bigger and goes off screen when it tilts.
    # worst case a point projects to (R1 + R2) / (K2 - R1), so scale by that
    # and leave a bit of margin
    max_extent = (R1 + R2) / (K2 - R1)
    k1 = 0.45 * min(width / CHAR_ASPECT, height) / max_extent

    col = np.floor(width / 2 + CHAR_ASPECT * k1 * ooz * x).astype(int)
    row = np.floor(height / 2 - k1 * ooz * y).astype(int)

    visible = (col >= 0) & (col < width) & (row >= 0) & (row < height)
    col, row, ooz, lum = col[visible], row[visible], ooz[visible], lum[visible]

    # z-buffer: for every cell remember the closest 1/z,
    # then draw only the points that are the closest in their cell
    cell = row * width + col
    zbuf = np.zeros(width * height)
    np.maximum.at(zbuf, cell, ooz)
    front = ooz == zbuf[cell]

    shade = np.clip((lum[front] * 8).astype(int), 0, len(SHADES) - 1)

    frame = np.full(width * height, " ")
    frame[cell[front]] = SHADES[shade]
    return frame.reshape(height, width)


def to_text(frame):
    return "\n".join("".join(line) for line in frame)


def parse_args():
    parser = argparse.ArgumentParser(description="spinning ascii donut")
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--speed", type=float, default=1.0,
                        help="rotation speed multiplier")
    return parser.parse_args()


def main():
    args = parse_args()

    if os.name == "nt":
        # turns on ansi escape codes in the old windows console.
        # looks like nonsense but it actually works
        os.system("")

    torus = Torus()
    frame_time = 1 / args.fps
    a = b = 0.0
    last_size = None

    sys.stdout.write(HIDE_CURSOR + CLEAR)
    try:
        while True:
            started = time.perf_counter()

            size = shutil.get_terminal_size()
            if size != last_size:
                # leftovers from the old frame stay on screen after a resize
                sys.stdout.write(CLEAR)
                last_size = size

            # one line less, otherwise the terminal scrolls on the last \n
            frame = render_frame(torus, a, b, size.columns, size.lines - 1)
            sys.stdout.write(HOME + to_text(frame))
            sys.stdout.flush()

            a += 0.04 * args.speed
            b += 0.02 * args.speed

            time.sleep(max(0.0, frame_time - (time.perf_counter() - started)))
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write(SHOW_CURSOR + "\n")


if __name__ == "__main__":
    main()
