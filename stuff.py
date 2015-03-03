import cloud_detection_new as cloud_detection
from matplotlib import pyplot as plt
import views
from skimage import exposure

nir = cloud_detection.get_nir()[0:600,2000:2600]
red = cloud_detection.get_red()[0:600,2000:2600]
green = cloud_detection.get_green()[0:600,2000:2600]
blue = cloud_detection.get_blue()[0:600,2000:2600] # or use coastal
coastal = cloud_detection.get_coastal()[0:600,2000:2600]
marine_shadow_index = (green-blue)/(green+blue)

img = views.create_composite(red, green, blue)
img_rescale = exposure.rescale_intensity(img, in_range=(0, 90))

plt.rcParams['savefig.facecolor'] = "0.8"
vmin, vmax=0.0,0.1
def example_plot(ax, data, fontsize=12):
     ax.imshow(data, vmin=vmin, vmax=vmax)
     ax.locator_params(nbins=3)
     ax.set_xlabel('x-label', fontsize=fontsize)
     ax.set_ylabel('y-label', fontsize=fontsize)
     ax.set_title('Title', fontsize=fontsize)

plt.close('all')
fig = plt.figure


ax1=plt.subplot(243)
ax2=plt.subplot(244)
ax3=plt.subplot(247)
ax4=plt.subplot(248)
ax5=plt.subplot(121)

a_coastal = coastal[500:600, 500:600]
a_blue = blue[500:600, 500:600]
a_green = green[500:600, 500:600]
a_red = red[500:600, 500:600]
a_nir = nir[500:600, 500:600]
a_img = img[500:600, 500:600]
spec1 = [a_coastal[60, 60], a_blue[60, 60], a_green[60, 60], a_red[60, 60], a_nir[60, 60]]

b_coastal = coastal[200:300, 100:200]
b_blue = blue[200:300, 100:200]
b_green = green[200:300, 100:200]
b_red = red[200:300, 100:200]
b_nir = nir[200:300, 100:200]
b_img = img[200:300, 100:200]

example_plot(ax1, coastal)
example_plot(ax2, blue)
example_plot(ax3, green)
example_plot(ax4, red)
ax5.imshow(img)

# plt.tight_layout()
plt.close('all')
spec = [b_coastal[60, 60], b_blue[60, 60], b_green[60, 60], b_red[60, 60], b_nir[60, 60]]
plt.plot(spec, 'k*-')
plt.plot(spec1, 'k.-')

plt.close('all')
cbg = (coastal+blue+green)/3

plt.imshow(cbg/red)