



class RandomnessAnalysis:
    '''Applies randomness tests to Spatialcount'''

    def __init__(self):




def random_points(self ,n):
    # consider integral of cos(lat): sin(lat) - range varies from -1 to 1 for -180 to 180
    y0 = np.sin(np.radians(self.yr[0])) # move to init?
    y1 = np.sin(np.radians(self.yr[1]))
    y = np.degrees(np.asin(np.random.uniform(y0, y1, n)))
    x = np.random.uniform(self.xr[0], self.xr[1], n)
    return zip(x ,y)

def sprinkle_discs(self ,n ,diam):
    """
    generate z random points in enclosing area
    find those in actual area
    find non-overlapping (could optimise with 2d spatial bin search)
    take first n good points
    """
    expected_hit_rate = self.are a /self.enclosing_area
    shortfall = n
    p = []
    overlapped = []

    while True:
        z = int(1.2 * shortfall / expected_hit_rate)  # guess at required number of points
        p0 = self.random_points(z)
        for e in p0:
            pt = sph.create_point(longitude=e[0], latitude=e[1])
            if sph.within(pt, self.polygon):
                if all(sph.distance(pt, e, radius=self.planetary_radius ) >dia m /2 for e in p):
                    p += [pt]
                else:
                    overlapped += [pt]
        shortfall = n - len(p)
        if shortfall < =0:
            break

    return p[:n]

def plain_plot(self ,p):
    import matplotlib.pyplot as plt
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    # plot the unit sphere for reference (optional)
    # u = np.linspace(0, 2 * np.pi, 100)
    # v = np.linspace(0, np.pi, 100)
    # x = np.outer(np.cos(u), np.sin(v))
    # y = np.outer(np.sin(u), np.sin(v))
    # z = np.outer(np.ones(np.size(u)), np.cos(v))
    # ax.plot_surface(x, y, z, color='y', alpha=0.1)


    lam = np.radians(sph.get_x(p))
    phi = np.radians(sph.get_y(p))
    x = np.cos(phi) * np.cos(lam)
    y = np.cos(phi) * np.sin(lam)
    z = np.sin(phi)

    ax.scatter(x ,y ,z, c='b')

    plt.show()

    print()
