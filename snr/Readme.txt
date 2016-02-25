
# Functions to extract radius of certain range from snr file
a=15; savetxt('smp_c_snr_%s_%s.txt' %(a, a+10), snr[logical_and(snr[:,3]>=a, snr[:,3]<(a+10))], fmt='%.4f')

# plot_snr_scatter.py
SNR - Radius scattering plot

# plot_snr_scatter_2.py
scattering plot, plus histogram
