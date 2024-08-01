import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

def E(q, r0, x, y):
    """Return the electric field vector E=(Ex,Ey) due to charge q at r0."""
    den = np.hypot(x-r0[0], y-r0[1])**3
    return q * (x - r0[0]) / den, q * (y - r0[1]) / den

# Grid of x, y points
def generate_vector_field(source_point, nx, ny):
    x = np.linspace(0, nx, nx)
    y = np.linspace(0, ny, ny)
    X, Y = np.meshgrid(x, y)

    charges = []
    source_x, source_y = source_point
    sink_point = (nx-source_x, ny-source_y)
    charges.append((1, source_point))
    charges.append((-1, sink_point))

    # Electric field vector, E=(Ex, Ey), as separate components
    Ex, Ey = np.zeros((ny, nx)), np.zeros((ny, nx))
    for charge in charges:
        ex, ey = E(*charge, x=X, y=Y)
        Ex += ex
        Ey += ey

    # Combine Ex and Ey as pair of coordinates
    Ec = np.stack((Ex, Ey), axis=-1)

    # Normalize the length of each arrow
    for i in range(len(Ec)):
        for j in range(len(Ec[i])):
            dx, dy = Ec[i][j]
            norm = np.sqrt(dx**2 + dy**2)
            Ec[i][j] = [dx/norm, dy/norm]

    Ec = np.array(Ec)
    return x, y, charges, Ex, Ey, Ec
    # return Ec

x, y, charges, Ex, Ey, Ec =  generate_vector_field((30, 70), 100, 100)

# print(Ex)
# # print(Ex.shape)
# print(Ey)
# # print(charges)
# print(Ec)
# print(Ec.shape)

fig = plt.figure()
ax = fig.add_subplot(111)

# Plot the streamlines with an appropriate colormap and arrow style
color = 2 * np.log(np.hypot(Ex, Ey))
ax.streamplot(x, y, Ex, Ey, color=color, linewidth=1, cmap=plt.cm.inferno,
              density=2, arrowstyle='->', arrowsize=1.5)

# Add filled circles for the charges themselves
charge_colors = {True: '#aa0000', False: '#0000aa'}
for q, pos in charges:
    ax.add_artist(Circle(pos, 1, color=charge_colors[q>0]))

# ax.set_xlabel('$x$')
# ax.set_ylabel('$y$')
# ax.set_xlim(0, 100)
# ax.set_ylim(0, 100)
ax.set_axis_off()
ax.set_aspect('equal')
plt.show()