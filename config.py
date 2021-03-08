import numpy as np


scenarios = ['Basecase',
             'Phasing-Option A',
             'Phasing-Option A2',
             'Phasing-Option A3',
             'Phasing-Option B',
             'Phasing-Option C',
             'Phasing-Option D',
             'Phasing-Option E',
             'Phasing-Option F',
             'Phasing-Option G',
             'Phasing-Option H',
             'Phasing-Option I']

years = range(2020, 2050+1)

fuels = ['elec',
         'gas',
         'steam']

policies = ['tuneup',
            'eui',
            'ghg',
            'electrify']
policy_labels = ['tune-ups',
                 'EUI targets',
                 'GHG targets',
                 'electrification']

bldg_types = ['Distribution Center',
              'High-Rise Multifamily',
              'Hospital',
              'Hotel',
              'K-12 School',
              'Laboratory',
              'Large Office',
              'Low-Rise Multifamily',
              'Medical Office',
              'Mid-Rise Multifamily',
              'Mixed Use Property',
              'Other',
              'Residence Hall',
              'Restaurant',
              'Retail Store',
              'Self-Storage Facility',
              'Senior Care Community',
              'Small- and Mid-Sized Office',
              'Supermarket / Grocery Store',
              'University',
              'Warehouse',
              'Worship Facility']

com_types = filter(lambda typ: 'Multifamily' not in typ, bldg_types)
mult_types = filter(lambda typ: 'Multifamily' in typ, bldg_types)

areas = [('<20k ft$^2$', -np.inf, 20e3),
         ('20k-50k ft$^2$', 20e3, 50e3),
         ('50k-90k ft$^2$', 50e3, 90e3),
         ('90k-220k ft$^2$', 90e3, 220e3),
         ('>220k ft$^2$', 220e3, np.inf)]

# kgCO2e/kBtu
ghg_factors = {'elec': 6.164e-3,
               'gas': 52.98e-3,
               'steam': 52.99e-3}


def get_tuneup_targets(scenario):

    targs = []
    for typ in com_types:
        targs.append({'years': (2021, 2021),
                      'reduct prop': 0.1,
                      'types': [typ],
                      'areas': (50e3, np.inf)})

    scen_targs = {'Basecase': targs,
                  'Phasing-Option A': targs,
                  'Phasing-Option A2': targs,
                  'Phasing-Option A3': targs,
                  'Phasing-Option B': targs,
                  'Phasing-Option C': targs,
                  'Phasing-Option D': targs,
                  'Phasing-Option E': targs,
                  'Phasing-Option F': targs,
                  'Phasing-Option G': targs,
                  'Phasing-Option H': targs,
                  'Phasing-Option I': targs}

    return scen_targs[scenario]


def get_eui_targets(scenario):

    targs = []
    for typ in com_types:

        targs.append({'years': (2025, 2026),
                      'avg year': 2020,
                      'areas': (220e3, np.inf),
                      'types': [typ]})
        targs.append({'years': (2026, 2027),
                      'avg year': 2020,
                      'areas': (90e3, 220e3),
                      'types': [typ]})
        targs.append({'years': (2027, 2028),
                      'avg year': 2020,
                      'areas': (50e3, 90e3),
                      'types': [typ]})

        targs.append({'years': (2030, 2031),
                      'avg year': 2029,
                      'areas': (220e3, np.inf),
                      'types': [typ]})
        targs.append({'years': (2031, 2032),
                      'avg year': 2029,
                      'areas': (90e3, 220e3),
                      'types': [typ]})
        targs.append({'years': (2032, 2033),
                      'avg year': 2029,
                      'areas': (50e3, 90e3),
                      'types': [typ]})

        targs.append({'years': (2035, 2036),
                      'avg year': 2034,
                      'areas': (220e3, np.inf),
                      'types': [typ]})
        targs.append({'years': (2036, 2037),
                      'avg year': 2034,
                      'areas': (90e3, 220e3),
                      'types': [typ]})
        targs.append({'years': (2037, 2038),
                      'avg year': 2034,
                      'areas': (50e3, 90e3),
                      'types': [typ]})

        targs.append({'years': (2040, 2041),
                      'avg year': 2039,
                      'areas': (220e3, np.inf),
                      'types': [typ]})
        targs.append({'years': (2041, 2042),
                      'avg year': 2039,
                      'areas': (90e3, 220e3),
                      'types': [typ]})
        targs.append({'years': (2042, 2043),
                      'avg year': 2039,
                      'areas': (50e3, 90e3),
                      'types': [typ]})

        targs.append({'years': (2045, 2046),
                      'avg year': 2044,
                      'areas': (220e3, np.inf),
                      'types': [typ]})
        targs.append({'years': (2046, 2047),
                      'avg year': 2044,
                      'areas': (90e3, 220e3),
                      'types': [typ]})
        targs.append({'years': (2047, 2048),
                      'avg year': 2044,
                      'areas': (50e3, 90e3),
                      'types': [typ]})

    scen_targs = {'Basecase': targs,
                  'Phasing-Option A': targs,
                  'Phasing-Option A2': targs,
                  'Phasing-Option A3': targs,
                  'Phasing-Option B': targs,
                  'Phasing-Option C': targs,
                  'Phasing-Option D': targs,
                  'Phasing-Option E': targs,
                  'Phasing-Option F': targs,
                  'Phasing-Option G': targs,
                  'Phasing-Option H': targs,
                  'Phasing-Option I': targs}

    return scen_targs[scenario]


def get_ghg_targets(scenario):

    # kgCO2e/sqft
    type_vals = {'Distribution Center': 0.5,
                 'High-Rise Multifamily': 0.3,
                 'Hospital': 5.7,
                 'Hotel': 1.7,
                 'K-12 School': 1.0,
                 'Laboratory': 5.7,
                 'Large Office': 0.2,
                 'Low-Rise Multifamily': 0.1,
                 'Medical Office': 0.6,
                 'Mid-Rise Multifamily': 0.1,
                 'Mixed Use Property': 1.0,
                 'Other': 1.0,
                 'Residence Hall': 0.3,
                 'Restaurant': 4.0,
                 'Retail Store': 0.8,
                 'Self-Storage Facility': 0.5,
                 'Senior Care Community': 1.7,
                 'Small- and Mid-Sized Office': 0.2,
                 'Supermarket / Grocery Store': 4.2,
                 'University': 1.0,
                 'Warehouse': 0.5,
                 'Worship Facility': 1.1}

    com_20per_2026_targs = []
    for typ in com_types:
        com_20per_2026_targs.append({'years': (2025, 2026),
                                     'reduct prop': 0.2,
                                     'bldg prop': 1.0,
                                     'areas': (220e3, np.inf),
                                     'types': [typ]})
        com_20per_2026_targs.append({'years': (2026, 2027),
                                     'reduct prop': 0.2,
                                     'bldg prop': 1.0,
                                     'areas': (90e3, 220e3),
                                     'types': [typ]})
        com_20per_2026_targs.append({'years': (2027, 2028),
                                     'reduct prop': 0.2,
                                     'bldg prop': 1.0,
                                     'areas': (50e3, 90e3),
                                     'types': [typ]})

    com_30per_2026_targs = []
    for typ in com_types:
        com_30per_2026_targs.append({'years': (2025, 2026),
                                     'reduct prop': 0.3,
                                     'bldg prop': 1.0,
                                     'areas': (220e3, np.inf),
                                     'types': [typ]})
        com_30per_2026_targs.append({'years': (2026, 2027),
                                     'reduct prop': 0.3,
                                     'bldg prop': 1.0,
                                     'areas': (90e3, 220e3),
                                     'types': [typ]})
        com_30per_2026_targs.append({'years': (2027, 2028),
                                     'reduct prop': 0.3,
                                     'bldg prop': 1.0,
                                     'areas': (50e3, 90e3),
                                     'types': [typ]})

    com_swa_2026_targs = []
    for typ in com_types:
        com_swa_2026_targs.append({'years': (2025, 2026),
                                   'targ val': type_vals[typ],
                                   'bldg prop': 1.0,
                                   'areas': (220e3, np.inf),
                                   'types': [typ]})
        com_swa_2026_targs.append({'years': (2026, 2027),
                                   'targ val': type_vals[typ],
                                   'bldg prop': 1.0,
                                   'areas': (90e3, 220e3),
                                   'types': [typ]})
        com_swa_2026_targs.append({'years': (2027, 2028),
                                   'targ val': type_vals[typ],
                                   'bldg prop': 1.0,
                                   'areas': (50e3, 90e3),
                                   'types': [typ]})

    com_20per_2031_targs = []
    for typ in com_types:
        com_20per_2031_targs.append({'years': (2030, 2031),
                                     'reduct prop': 0.2,
                                     'bldg prop': 1.0,
                                     'areas': (220e3, np.inf),
                                     'types': [typ]})
        com_20per_2031_targs.append({'years': (2031, 2032),
                                     'reduct prop': 0.2,
                                     'bldg prop': 1.0,
                                     'areas': (90e3, 220e3),
                                     'types': [typ]})
        com_20per_2031_targs.append({'years': (2032, 2033),
                                     'reduct prop': 0.2,
                                     'bldg prop': 1.0,
                                     'areas': (50e3, 90e3),
                                     'types': [typ]})

    com_20per_2026_20k_targs = com_20per_2026_targs[:]
    for typ in com_types:
        com_20per_2026_20k_targs.append({'years': (2028, 2029),
                                         'reduct prop': 0.2,
                                         'bldg prop': 1.0,
                                         'areas': (20e3, 50e3),
                                         'types': [typ]})

    com_20per_2026_all_targs = com_20per_2026_20k_targs[:]
    for typ in com_types:
        com_20per_2026_all_targs.append({'years': (2029, 2030),
                                         'reduct prop': 0.2,
                                         'bldg prop': 1.0,
                                         'areas': (-np.inf, 20e3),
                                         'types': [typ]})

    com_20per_2026_hospital_targs = []
    for typ in com_types:
        if typ != 'Hospital':
            com_20per_2026_hospital_targs.append({'years': (2025, 2026),
                                                'reduct prop': 0.2,
                                                'bldg prop': 1.0,
                                                'areas': (220e3, np.inf),
                                                'types': [typ]})
            com_20per_2026_hospital_targs.append({'years': (2026, 2027),
                                                'reduct prop': 0.2,
                                                'bldg prop': 1.0,
                                                'areas': (90e3, 220e3),
                                                'types': [typ]})
            com_20per_2026_hospital_targs.append({'years': (2027, 2028),
                                                'reduct prop': 0.2,
                                                'bldg prop': 1.0,
                                                'areas': (50e3, 90e3),
                                                'types': [typ]})

    com_20per_2026_hotel_targs = []
    for typ in com_types:
        if typ != 'Hotel':
            com_20per_2026_hotel_targs.append({'years': (2025, 2026),
                                                'reduct prop': 0.2,
                                                'bldg prop': 1.0,
                                                'areas': (220e3, np.inf),
                                                'types': [typ]})
            com_20per_2026_hotel_targs.append({'years': (2026, 2027),
                                                'reduct prop': 0.2,
                                                'bldg prop': 1.0,
                                                'areas': (90e3, 220e3),
                                                'types': [typ]})
            com_20per_2026_hotel_targs.append({'years': (2027, 2028),
                                                'reduct prop': 0.2,
                                                'bldg prop': 1.0,
                                                'areas': (50e3, 90e3),
                                                'types': [typ]})

    com_20per_2026_restaurant_targs = []
    for typ in com_types:
        if typ != 'Restaurant':
            com_20per_2026_restaurant_targs.append({'years': (2025, 2026),
                                                'reduct prop': 0.2,
                                                'bldg prop': 1.0,
                                                'areas': (220e3, np.inf),
                                                'types': [typ]})
            com_20per_2026_restaurant_targs.append({'years': (2026, 2027),
                                                'reduct prop': 0.2,
                                                'bldg prop': 1.0,
                                                'areas': (90e3, 220e3),
                                                'types': [typ]})
            com_20per_2026_restaurant_targs.append({'years': (2027, 2028),
                                                'reduct prop': 0.2,
                                                'bldg prop': 1.0,
                                                'areas': (50e3, 90e3),
                                                'types': [typ]})

    com_20per_2026_exempt_targs = []
    for typ in com_types:
        if typ not in ['Hospital','Hotel','Restaurant']:
            com_20per_2026_exempt_targs.append({'years': (2025, 2026),
                                                'reduct prop': 0.2,
                                                'bldg prop': 1.0,
                                                'areas': (220e3, np.inf),
                                                'types': [typ]})
            com_20per_2026_exempt_targs.append({'years': (2026, 2027),
                                                'reduct prop': 0.2,
                                                'bldg prop': 1.0,
                                                'areas': (90e3, 220e3),
                                                'types': [typ]})
            com_20per_2026_exempt_targs.append({'years': (2027, 2028),
                                                'reduct prop': 0.2,
                                                'bldg prop': 1.0,
                                                'areas': (50e3, 90e3),
                                                'types': [typ]})

    mult_20per_2031_targs = []
    for typ in mult_types:
        mult_20per_2031_targs.append({'years': (2030, 2031),
                                      'reduct prop': 0.2,
                                      'bldg prop': 1.0,
                                      'areas': (220e3, np.inf),
                                      'types': [typ]})
        mult_20per_2031_targs.append({'years': (2031, 2032),
                                      'reduct prop': 0.2,
                                      'bldg prop': 1.0,
                                      'areas': (90e3, 220e3),
                                      'types': [typ]})
        mult_20per_2031_targs.append({'years': (2032, 2033),
                                      'reduct prop': 0.2,
                                      'bldg prop': 1.0,
                                      'areas': (50e3, 90e3),
                                      'types': [typ]})

    mult_30per_2031_targs = []
    for typ in mult_types:
        mult_30per_2031_targs.append({'years': (2030, 2031),
                                      'reduct prop': 0.3,
                                      'bldg prop': 1.0,
                                      'areas': (220e3, np.inf),
                                      'types': [typ]})
        mult_30per_2031_targs.append({'years': (2031, 2032),
                                      'reduct prop': 0.3,
                                      'bldg prop': 1.0,
                                      'areas': (90e3, 220e3),
                                      'types': [typ]})
        mult_30per_2031_targs.append({'years': (2032, 2033),
                                      'reduct prop': 0.3,
                                      'bldg prop': 1.0,
                                      'areas': (50e3, 90e3),
                                      'types': [typ]})

    mult_swa_2031_targs = []
    for typ in mult_types:
        mult_swa_2031_targs.append({'years': (2030, 2031),
                                    'targ val': type_vals[typ],
                                    'bldg prop': 1.0,
                                    'areas': (220e3, np.inf),
                                    'types': [typ]})
        mult_swa_2031_targs.append({'years': (2031, 2032),
                                    'targ val': type_vals[typ],
                                    'bldg prop': 1.0,
                                    'areas': (90e3, 220e3),
                                    'types': [typ]})
        mult_swa_2031_targs.append({'years': (2032, 2033),
                                    'targ val': type_vals[typ],
                                    'bldg prop': 1.0,
                                    'areas': (50e3, 90e3),
                                    'types': [typ]})

    mult_20per_2036_targs = []
    for typ in mult_types:
        mult_20per_2036_targs.append({'years': (2035, 2036),
                                      'reduct prop': 0.2,
                                      'bldg prop': 1.0,
                                      'areas': (220e3, np.inf),
                                      'types': [typ]})
        mult_20per_2036_targs.append({'years': (2036, 2037),
                                      'reduct prop': 0.2,
                                      'bldg prop': 1.0,
                                      'areas': (90e3, 220e3),
                                      'types': [typ]})
        mult_20per_2036_targs.append({'years': (2037, 2038),
                                      'reduct prop': 0.2,
                                      'bldg prop': 1.0,
                                      'areas': (50e3, 90e3),
                                      'types': [typ]})

    mult_20per_2031_20k_targs = mult_20per_2031_targs[:]
    for typ in mult_types:
        mult_20per_2031_20k_targs.append({'years': (2033, 2034),
                                          'reduct prop': 0.2,
                                          'bldg prop': 1.0,
                                          'areas': (20e3, 50e3),
                                          'types': [typ]})

    mult_20per_2031_all_targs = mult_20per_2031_20k_targs[:]
    for typ in mult_types:
        mult_20per_2031_all_targs.append({'years': (2034, 2035),
                                          'reduct prop': 0.2,
                                          'bldg prop': 1.0,
                                          'areas': (-np.inf, 20e3),
                                          'types': [typ]})

    scen_targs = {'Basecase': [],
                  'Phasing-Option A': com_20per_2026_targs + mult_20per_2031_targs,
                  'Phasing-Option A2': com_30per_2026_targs + mult_30per_2031_targs,
                  'Phasing-Option A3': com_swa_2026_targs + mult_swa_2031_targs,
                  'Phasing-Option B': com_20per_2031_targs + mult_20per_2036_targs,
                  'Phasing-Option C': com_20per_2026_20k_targs + mult_20per_2031_20k_targs,
                  'Phasing-Option D': com_20per_2026_all_targs + mult_20per_2031_all_targs,
                  'Phasing-Option E': com_20per_2026_targs + mult_20per_2031_targs,
                  'Phasing-Option F': com_20per_2026_hospital_targs + mult_20per_2031_targs,
                  'Phasing-Option G': com_20per_2026_hotel_targs + mult_20per_2031_targs,
                  'Phasing-Option H': com_20per_2026_restaurant_targs + mult_20per_2031_targs,
                  'Phasing-Option I': com_20per_2026_exempt_targs + mult_20per_2031_targs}

    return scen_targs[scenario]


def get_electrify_targets(scenario):

    com_2036_targs = []
    for typ in com_types:
        com_2036_targs.append({'years': (2035, 2036),
                               'areas': (220e3, np.inf),
                               'types': [typ],
                               'bldg prop': 1.0,
                               'fuel prop': 1.0,
                               'coef of perf': 2.0})
        com_2036_targs.append({'years': (2036, 2037),
                               'areas': (90e3, 220e3),
                               'types': [typ],
                               'bldg prop': 1.0,
                               'fuel prop': 1.0,
                               'coef of perf': 2.0})
        com_2036_targs.append({'years': (2037, 2038),
                               'areas': (50e3, 90e3),
                               'types': [typ],
                               'bldg prop': 1.0,
                               'fuel prop': 1.0,
                               'coef of perf': 2.0})

    com_2041_targs = []
    for typ in com_types:
        com_2041_targs.append({'years': (2040, 2041),
                               'areas': (220e3, np.inf),
                               'types': [typ],
                               'bldg prop': 1.0,
                               'fuel prop': 1.0,
                               'coef of perf': 2.0})
        com_2041_targs.append({'years': (2041, 2042),
                               'areas': (90e3, 220e3),
                               'types': [typ],
                               'bldg prop': 1.0,
                               'fuel prop': 1.0,
                               'coef of perf': 2.0})
        com_2041_targs.append({'years': (2042, 2043),
                               'areas': (50e3, 90e3),
                               'types': [typ],
                               'bldg prop': 1.0,
                               'fuel prop': 1.0,
                               'coef of perf': 2.0})

    com_2036_20k_targs = com_2036_targs[:]
    for typ in com_types:
        com_2036_20k_targs.append({'years': (2038, 2039),
                                   'areas': (20e3, 50e3),
                                   'types': [typ],
                                   'bldg prop': 1.0,
                                   'fuel prop': 1.0,
                                   'coef of perf': 2.0})

    com_2036_all_targs = com_2036_20k_targs[:]
    for typ in com_types:
        com_2036_all_targs.append({'years': (2039, 2040),
                                   'areas': (-np.inf, 20e3),
                                   'types': [typ],
                                   'bldg prop': 1.0,
                                   'fuel prop': 1.0,
                                   'coef of perf': 2.0})

    com_2036_5yr_targs = []
    for typ in com_types:
        com_2036_5yr_targs.append({'years': (2032, 2036),
                                   'areas': (220e3, np.inf),
                                   'types': [typ],
                                   'bldg prop': 1.0,
                                   'fuel prop': 1.0,
                                   'coef of perf': 2.0})
        com_2036_5yr_targs.append({'years': (2033, 2037),
                                   'areas': (90e3, 220e3),
                                   'types': [typ],
                                   'bldg prop': 1.0,
                                   'fuel prop': 1.0,
                                   'coef of perf': 2.0})
        com_2036_5yr_targs.append({'years': (2034, 2038),
                                   'areas': (50e3, 90e3),
                                   'types': [typ],
                                   'bldg prop': 1.0,
                                   'fuel prop': 1.0,
                                   'coef of perf': 2.0})

    com_2036_hospital_targs = []
    for typ in com_types:
        if typ != 'Hospital':
            com_2036_hospital_targs.append({'years': (2035, 2036),
                                          'areas': (220e3, np.inf),
                                          'types': [typ],
                                          'bldg prop': 1.0,
                                          'fuel prop': 1.0,
                                          'coef of perf': 2.0})
            com_2036_hospital_targs.append({'years': (2036, 2037),
                                          'areas': (90e3, 220e3),
                                          'types': [typ],
                                          'bldg prop': 1.0,
                                          'fuel prop': 1.0,
                                          'coef of perf': 2.0})
            com_2036_hospital_targs.append({'years': (2037, 2038),
                                          'areas': (50e3, 90e3),
                                          'types': [typ],
                                          'bldg prop': 1.0,
                                          'fuel prop': 1.0,
                                          'coef of perf': 2.0})

    com_2036_hotel_targs = []
    for typ in com_types:
        if typ != 'Hotel':
            com_2036_hotel_targs.append({'years': (2035, 2036),
                                          'areas': (220e3, np.inf),
                                          'types': [typ],
                                          'bldg prop': 1.0,
                                          'fuel prop': 1.0,
                                          'coef of perf': 2.0})
            com_2036_hotel_targs.append({'years': (2036, 2037),
                                          'areas': (90e3, 220e3),
                                          'types': [typ],
                                          'bldg prop': 1.0,
                                          'fuel prop': 1.0,
                                          'coef of perf': 2.0})
            com_2036_hotel_targs.append({'years': (2037, 2038),
                                          'areas': (50e3, 90e3),
                                          'types': [typ],
                                          'bldg prop': 1.0,
                                          'fuel prop': 1.0,
                                          'coef of perf': 2.0})

    com_2036_restaurant_targs = []
    for typ in com_types:
        if typ != 'Restaurant':
            com_2036_restaurant_targs.append({'years': (2035, 2036),
                                          'areas': (220e3, np.inf),
                                          'types': [typ],
                                          'bldg prop': 1.0,
                                          'fuel prop': 1.0,
                                          'coef of perf': 2.0})
            com_2036_restaurant_targs.append({'years': (2036, 2037),
                                          'areas': (90e3, 220e3),
                                          'types': [typ],
                                          'bldg prop': 1.0,
                                          'fuel prop': 1.0,
                                          'coef of perf': 2.0})
            com_2036_restaurant_targs.append({'years': (2037, 2038),
                                          'areas': (50e3, 90e3),
                                          'types': [typ],
                                          'bldg prop': 1.0,
                                          'fuel prop': 1.0,
                                          'coef of perf': 2.0})

    com_2036_exempt_targs = []
    for typ in com_types:
        if typ not in ['Hospital','Hotel','Restaurant']:
            com_2036_exempt_targs.append({'years': (2035, 2036),
                                          'areas': (220e3, np.inf),
                                          'types': [typ],
                                          'bldg prop': 1.0,
                                          'fuel prop': 1.0,
                                          'coef of perf': 2.0})
            com_2036_exempt_targs.append({'years': (2036, 2037),
                                          'areas': (90e3, 220e3),
                                          'types': [typ],
                                          'bldg prop': 1.0,
                                          'fuel prop': 1.0,
                                          'coef of perf': 2.0})
            com_2036_exempt_targs.append({'years': (2037, 2038),
                                          'areas': (50e3, 90e3),
                                          'types': [typ],
                                          'bldg prop': 1.0,
                                          'fuel prop': 1.0,
                                          'coef of perf': 2.0})

    mult_2041_targs = []
    for typ in mult_types:
        mult_2041_targs.append({'years': (2040, 2041),
                                'areas': (220e3, np.inf),
                                'types': [typ],
                                'bldg prop': 1.0,
                                'fuel prop': 1.0,
                                'coef of perf': 2.0})
        mult_2041_targs.append({'years': (2041, 2042),
                                'areas': (90e3, 220e3),
                                'types': [typ],
                                'bldg prop': 1.0,
                                'fuel prop': 1.0,
                                'coef of perf': 2.0})
        mult_2041_targs.append({'years': (2042, 2043),
                                'areas': (50e3, 90e3),
                                'types': [typ],
                                'bldg prop': 1.0,
                                'fuel prop': 1.0,
                                'coef of perf': 2.0})

    mult_2046_targs = []
    for typ in mult_types:
        mult_2046_targs.append({'years': (2045, 2046),
                                'areas': (220e3, np.inf),
                                'types': [typ],
                                'bldg prop': 1.0,
                                'fuel prop': 1.0,
                                'coef of perf': 2.0})
        mult_2046_targs.append({'years': (2046, 2047),
                                'areas': (90e3, 220e3),
                                'types': [typ],
                                'bldg prop': 1.0,
                                'fuel prop': 1.0,
                                'coef of perf': 2.0})
        mult_2046_targs.append({'years': (2047, 2048),
                                'areas': (50e3, 90e3),
                                'types': [typ],
                                'bldg prop': 1.0,
                                'fuel prop': 1.0,
                                'coef of perf': 2.0})

    mult_2041_20k_targs = mult_2041_targs[:]
    for typ in mult_types:
        mult_2041_20k_targs.append({'years': (2043, 2044),
                                    'areas': (20e3, 50e3),
                                   'types': [typ],
                                   'bldg prop': 1.0,
                                   'fuel prop': 1.0,
                                   'coef of perf': 2.0})

    mult_2041_all_targs = mult_2041_20k_targs[:]
    for typ in mult_types:
        mult_2041_all_targs.append({'years': (2044, 2045),
                                    'areas': (-np.inf, 20e3),
                                   'types': [typ],
                                   'bldg prop': 1.0,
                                   'fuel prop': 1.0,
                                   'coef of perf': 2.0})

    mult_2041_5yr_targs = []
    for typ in mult_types:
        mult_2041_5yr_targs.append({'years': (2037, 2041),
                                    'areas': (220e3, np.inf),
                                    'types': [typ],
                                    'bldg prop': 1.0,
                                    'fuel prop': 1.0,
                                    'coef of perf': 2.0})
        mult_2041_5yr_targs.append({'years': (2038, 2042),
                                    'areas': (90e3, 220e3),
                                    'types': [typ],
                                    'bldg prop': 1.0,
                                    'fuel prop': 1.0,
                                    'coef of perf': 2.0})
        mult_2041_5yr_targs.append({'years': (2039, 2043),
                                    'areas': (50e3, 90e3),
                                    'types': [typ],
                                    'bldg prop': 1.0,
                                    'fuel prop': 1.0,
                                    'coef of perf': 2.0})

    scen_targs = {'Basecase': [],
                  'Phasing-Option A': com_2036_targs + mult_2041_targs,
                  'Phasing-Option A2': com_2036_targs + mult_2041_targs,
                  'Phasing-Option A3': com_2036_targs + mult_2041_targs,
                  'Phasing-Option B': com_2041_targs + mult_2046_targs,
                  'Phasing-Option C': com_2036_20k_targs + mult_2041_20k_targs,
                  'Phasing-Option D': com_2036_all_targs + mult_2041_all_targs,
                  'Phasing-Option E': com_2036_5yr_targs + mult_2041_5yr_targs,
                  'Phasing-Option F': com_2036_hospital_targs + mult_2041_targs,
                  'Phasing-Option G': com_2036_hotel_targs + mult_2041_targs,
                  'Phasing-Option H': com_2036_restaurant_targs + mult_2041_targs,
                  'Phasing-Option I': com_2036_exempt_targs + mult_2041_targs}

    return scen_targs[scenario]
