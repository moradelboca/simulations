h = 0.001


def diff_ec(t, c):
    return 0.025 * t - 0.5 * c - 12.85


def next_y(y, k1, k2, k3, k4):
    return y + h / 6 * (k1 + 2*k2 + 2*k3 + k4)


def runge_kutta(x, y):
    while y > 0:
        k1 = diff_ec(x, y)
        k2 = diff_ec(x+h/2, y+k1*h/2)
        k3 = diff_ec(x+h/2, y+k2*h/2)
        k4 = diff_ec(x+h/2, y+k3*h/2)
        x += h
        y = next_y(y, k1, k2, k3, k4)
    return x
