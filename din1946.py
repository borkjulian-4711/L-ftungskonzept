def calc_feuchteschutz(ANE, fWS):
    return fWS * (-0.002 * ANE**2 + 1.15 * ANE + 11)