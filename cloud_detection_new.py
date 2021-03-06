from bands import *

def cirrus_test():
    cirrus = get_cirrus()
    return cirrus>0.01

def calc_basic_test_with_temp():
    band_7_test = utils.get_truth(get_swir2(), 0.03, '>')
    btc_test = utils.get_truth(utils.convert_to_celsius(get_temp()), 27.0, '<')
    ndsi_test = utils.get_truth(calc_ndsi(), 0.8, '<')
    ndvi_test = utils.get_truth(calc_ndvi(), 0.8, '<')
    basic_test = np.logical_and.reduce((band_7_test,
                                        btc_test,
                                        ndsi_test,
                                        ndvi_test))
    return basic_test

def calc_basic_test():
    band_7_test = utils.get_truth(get_swir2(), 0.03, '>')
    ndsi_test = utils.get_truth(calc_ndsi(), 0.8, '<')
    ndvi_test = utils.get_truth(calc_ndvi(), 0.8, '<')
    basic_test = np.logical_and.reduce((band_7_test,
                                        ndsi_test,
                                        ndvi_test))
    return basic_test

def calc_whiteness():
    """
    Whiteness test seems to include a lot of pixels. Might be safe to exclude.
    """
    blue = get_blue()
    green = get_green()
    red = get_red()
    mean_vis = (blue + green + red) / 3
    whiteness = (np.abs((blue - mean_vis)/mean_vis) + 
                 np.abs((green - mean_vis)/mean_vis) +
                 np.abs((red - mean_vis)/mean_vis))
    whiteness[np.where(whiteness>1)] = 1
    return whiteness
    
def calc_whiteness_test():
    whiteness_test = utils.get_truth(calc_whiteness(), 0.7, '<') # 0.7 in paper
    return whiteness_test

def calc_basic_and_whiteness():
    basic_and_white = np.logical_and(calc_basic_test(), calc_whiteness_test())
    return basic_and_white

def calculate_hot_test():
    """
    Hot test results in omission of cloud pixels. Trying with RTOA.
    Also sometimes produces funky results.
    """
    band = 'rtoa_'
    blue = get_var(band+'483')
    red = get_var(band+'561')
    hot_test = (blue - 0.5*red - 0.08) > 0
    return hot_test
    
def swirnir_test():
    """
    swir/nir test seems to include a lot of pixels. Might be safe to exclude.
    Includes more pixels if 2201 is used in comparison to 1609.
    """
    nir = get_nir()
    swir = get_swir2()
    return (nir/swir) > 0.75 # added by nick

def calc_cirrus_prob():
    cirrus = get_cirrus()
    return cirrus / 0.04

def calc_pcp():
    return np.logical_and.reduce((calc_basic_test(),
                                  calc_whiteness_test(),
                                  calculate_hot_test(),
                                  swirnir_test()))

def calc_pcp_short():
    basic_and_white = calc_basic_and_whiteness()
    return np.logical_and(basic_and_white,
                                  calc_whiteness_test(), swirnir_test())

def calc_pcp_basic():
    return calc_basic_test()

def water_test():
    ndvi = calc_ndvi()
    nir = get_nir()
    water_condition_one = np.logical_and((ndvi < 0.01), (nir > 0.11))
    water_condition_two = np.logical_and((ndvi < 0.1), (nir < 0.05))
    water_test = np.logical_or(water_condition_one, water_condition_two)
    return water_test
    
def clear_sky_water():
    swir = get_swir2()
    clear_sky_water = np.logical_and(water_test(), (swir < 0.03))
    return clear_sky_water

def clear_sky_water_brightness_temp():
    # where(condition, [x, y])
    brightness_temp = utils.convert_to_celsius(get_temp())
    csw_bt = ma.masked_where(np.invert(clear_sky_water()), brightness_temp)
    return csw_bt

def temp_prob_water():
    t_water = utils.calculate_percentile(clear_sky_water_brightness_temp(), 82.5)
    w_temperature_prob = (t_water-utils.convert_to_celsius(get_temp()))/4
    return w_temperature_prob

def brightness_probability_water():
    swir = get_swir2()
    _swir = np.zeros(swir.shape + (2,))
    _swir[:,:,0] = swir
    _swir[:,:,1] = np.ones(swir.shape)*0.11 # paper says 0.11
    swir = None
    brightness_prob = np.amin(_swir, axis=2)/0.11
    return  brightness_prob
    
def cloud_prob_water_old():
    w_cloud_prob = temp_prob_water()*brightness_probability_water()
    return w_cloud_prob

def cloud_prob_water_new():
    w_cloud_prob = brightness_probability_water() + calc_cirrus_prob()
    return w_cloud_prob

def cloud_prob_water():
    w_cloud_prob = brightness_probability_water() + calc_cirrus_prob()
    return w_cloud_prob

def clear_sky_land():
    clear_sky_land = np.logical_and(np.invert(calc_pcp()), np.invert(water_test()))
    return clear_sky_land
    
def clear_sky_land_brightness_temp():
    # where(condition, [x, y])
    brightness_temp = utils.convert_to_celsius(get_temp())
    csl_bt = ma.masked_where(np.invert(clear_sky_land()), brightness_temp)
    return csl_bt

def temp_prob_land():
    csl_bt = clear_sky_land_brightness_temp()
    t_low, t_high = utils.calculate_percentile(csl_bt, 17.5), utils.calculate_percentile(csl_bt, 82.5)
    btc = utils.convert_to_celsius(get_temp())
    l_temperature_prob = (t_high + 4 - btc)/(t_high + 4 - (t_low-4))     
    return l_temperature_prob

def mask_ndvi():
    ndvi_masked = ma.masked_where((get_nir()-get_red())>0, calc_ndvi())
    return ndvi_masked
    
def mask_ndsi():
    ndsi_masked = ma.masked_where((get_swir()-get_green())>0, calc_ndsi())
    return ndsi_masked
    
def variability_prob_land():
    ndvi_masked = mask_ndvi()
    ndsi_masked = mask_ndsi()
    _var_prob = np.zeros(ndvi_masked.shape + (3,))
    _var_prob[:,:,0] = np.abs(ndvi_masked)
    ndvi_masked = None
    _var_prob[:,:,1] = np.abs(ndsi_masked)
    ndsi_masked = None
    _var_prob[:,:,2] = calc_whiteness()
    variability_prob = 1 - np.amax(_var_prob, axis=2)
    return variability_prob*1.1 # added by nick
    
def cloud_prob_land_old(): 
    l_cloud_prob = (temp_prob_land()*variability_prob_land())*1.1 # added by nick
    return l_cloud_prob

def cloud_prob_land_new(): 
    l_cloud_prob = (calc_cirrus_prob()*variability_prob_land())
    return l_cloud_prob

def cloud_prob_land(): 
    l_cloud_prob = (calc_cirrus_prob()*variability_prob_land())
    return l_cloud_prob

def calc_csl_l_cloud_prob():
    cslcb = ma.masked_where(np.invert(clear_sky_land()), cloud_prob_land())
    return cslcb

def water_threshold():
    csl_w_cloud_prob = ma.masked_where(clear_sky_land(), cloud_prob_water())
    water_threshold = utils.calculate_percentile(csl_w_cloud_prob, 82.5)  + 0.2 # added by nick
    print("The water threshold is {0}.".format(water_threshold))
    return water_threshold

def land_threshold():
    csl_l_cloud_prob = ma.masked_where(np.invert(clear_sky_land()), cloud_prob_land())
    land_threshold = utils.calculate_percentile(csl_l_cloud_prob, 82.5)  + 0.2 # added by nick
    print("The land thrshold is {0}.".format(land_threshold))
    return land_threshold

def pcl_cond_one(pcp):
    condition_one = np.logical_and.reduce((pcp, water_test(), (cloud_prob_water()>water_threshold())))
    return condition_one
    
def pcl_cond_two(pcp):
    condition_two = np.logical_and.reduce((pcp,
                                           np.invert(water_test()),
                                           (cloud_prob_land()>land_threshold())))
    return condition_two

def pcl_cond_three():
    condition_three = np.logical_and((cloud_prob_land()>0.99),
                                     np.invert(water_test()))
    return condition_three

def pcl_cond_five():
    condition_three = np.logical_and((cloud_prob_water()>0.99),
                                     water_test())
    return condition_three

def pcl_cond_four():
    btc = utils.convert_to_celsius(get_temp())
    csl_bt = clear_sky_land_brightness_temp()
    t_low = utils.calculate_percentile(csl_bt, 17.5)
    return (btc < (t_low - 35))
    
def calc_pcl(pcp):
    condition_one = pcl_cond_one(pcp)
    condition_two = pcl_cond_two(pcp)
    condition_three = pcl_cond_three()
    condition_four = pcl_cond_four()
    condition_five = pcl_cond_five()
    one_or_two = np.logical_or(condition_one, condition_two)
    three_or_four = np.logical_or(condition_three, condition_four)
    pcl = np.logical_or(one_or_two, three_or_four)
    return pcl

if __name__ == "__main__":
    water = water_test()
    pcp = calc_pcp()
    cirrus = get_cirrus()
    pcl = calc_pcl(pcp)
    import views
    img = views.create_composite(get_red(), get_green(), get_blue())
