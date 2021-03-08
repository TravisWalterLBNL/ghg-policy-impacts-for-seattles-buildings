#!/usr/bin/env python

import numpy as np
import os
import pandas as pd
import matplotlib.pyplot as plt
plt.rcParams.update({'mathtext.default': 'regular'})
from config import *
np.random.seed(0)


if not os.path.isdir('plots'):
    os.mkdir('plots')

png_res = 300 # dpi


def main():

    bench = get_benchmarking_data()
    arch = get_architecture_2030_data()

    # fill in arch energy data by sampling from bench energy data
    # - assume arch buildings use only elec and gas (not steam)
    # - sample site eui and elec/site ratio
    # - use sampled values to compute elec and gas
    # - use different distribution for each building type
    # - get probabilities of sampling from each bin from histogram
    # - interpolate to fill in histogram bins with zero counts
    # - sample uniformly within each bin
    num_bins = 25
    bench['site'] = bench['elec'] + bench['gas'] + bench['steam']
    bench['site eui'] = bench['site'] / bench['area']
    bench['elec/site'] = bench['elec'] / bench['site']
    for typ in set(arch['type']):
        aidx = arch['type'] == typ
        bidx = bench['type'] == typ
        for val in ['site eui','elec/site']:
            if val == 'site eui':
                bins = num_bins
            elif val == 'elec/site':
                bins = np.linspace(0, 1, num_bins)
            cnts, bins = np.histogram(bench.loc[bidx,val], bins=num_bins)
            plot_hist(cnts, bins, val, typ)
            probs = np.interp(bins[:-1], bins[:-1][cnts != 0], cnts[cnts != 0])
            probs /= np.sum(probs)
            bin_idxs = np.random.choice(range(len(bins)-1), aidx.sum(), p=probs)
            samples = map(lambda b: np.random.uniform(low=bins[b], high=bins[b+1]), bin_idxs)
            arch.loc[aidx,val] = samples
    arch['site'] = arch['site eui'] * arch['area']
    arch['elec'] = arch['site'] * arch['elec/site']
    arch['gas'] = arch['site'] - arch['elec']
    arch['steam'] = 0.0
    bench.drop(['site','site eui','elec/site'], axis='columns', inplace=True)
    arch.drop(['site','site eui','elec/site'], axis='columns', inplace=True)

    data = pd.concat([bench,arch], sort=False, ignore_index=True)

    data = data[['type','area','elec','gas','steam']]

    for fuel in ['elec','gas','steam']:
        data.rename(columns={fuel: '2020 %s' % fuel}, inplace=True)

    data.to_csv('buildings.csv', index=False)


def get_benchmarking_data():

    file_name = os.path.join('data','2018_Building_Energy_Benchmarking.csv')

    str_cols = {'OSEBuildingID': 'id'}

    num_cols = {'PropertyGFABuilding(s)': 'area',
                'Electricity(kBtu)': 'elec',
                'NaturalGas(kBtu)': 'gas',
                'SteamUse(kBtu)': 'steam'}

    data = pd.read_csv(file_name, dtype=str).fillna('')
    cols = num_cols.copy()
    cols.update(str_cols)
    data = data[cols.keys()]
    data.rename(columns=cols, inplace=True)

    # look up property types
    prop_file = os.path.join('data','OSE Building ID vs Primary Property Type.csv')
    prop_data = pd.read_csv(prop_file, dtype=str).fillna('')
    prop_data.drop_duplicates(inplace=True)
    prop_map = dict(zip(prop_data['SeattleBuildingID'], prop_data['PrimaryPropertyType']))
    data['id'] = data['id'].apply(lambda i: i.replace(',',''))
    data['type'] = data['id'].apply(lambda i: prop_map[i])
    data = data.loc[data['type'] != '']
    data.drop('id', axis='columns', inplace=True)

    # combine some types
    data.loc[data['type']=='College/University', 'type'] = 'University'
    data.loc[data['type']=='Refrigerated Warehouse', 'type'] = 'Warehouse'
    data.loc[data['type']=='Non-Refrigerated Warehouse', 'type'] = 'Warehouse'

    def fix_num(x):
        x = x.replace(',','')
        if x == '':
            x = 'nan'
        x = float(x)
        return x
    for col in num_cols.values():
        data[col] = data[col].apply(fix_num)
        data = data.loc[data[col].notnull()]

    # only keep buildings with area above cutoff
    data = data.loc[data['area'] >= 20e3]

    # drop buildings with high or low site eui
    data['site'] = data['elec'] + data['gas'] + data['steam']
    data['site eui'] = data['site'] / data['area']
    data = data.loc[(data['site eui'] >= 1.0) & (data['site eui'] <= 1000.0)]
    data.drop(['site','site eui'], axis='columns', inplace=True)

    return data


def get_architecture_2030_data():

    file_name = os.path.join('data', 'Architecture 2030 Report Data - AK_All Properties.csv')

    str_cols = {'City Use Type': 'city type',
                'Ecotope Use Type': 'eco type'}

    num_cols = {'Total Floor Area (ft2)': 'area'}

    data = pd.read_csv(file_name, dtype=str).fillna('')
    cols = num_cols.copy()
    cols.update(str_cols)
    data = data[cols.keys()]
    data.rename(columns=cols, inplace=True)

    # map types to same categories as in benchmarking data, exclude some types
    data['city type'] = data['city type'].apply(lambda x: x.strip())
    data['type'] = data['city type'] + '_' + data['eco type']
    data.drop(['city type','eco type'], axis='columns', inplace=True)
    data['type'] = data['type'].apply(map_arch_type)
    data = data.loc[data['type'] != '']

    def fix_num(x):
        x = x.replace(',','').strip()
        if x in ['','-']:
            x = 'nan'
        x = float(x)
        return x
    for col in num_cols.values():
        data[col] = data[col].apply(fix_num)
        data = data.loc[data[col].notnull()]

    # remove bad data
    data = data.loc[data['area'] >= 500.0]

    # only keep buildings with area below cutoff
    data = data.loc[data['area'] < 20e3]

    return data


def map_arch_type(typ):

    typ_map = {'ARCADE (573)_Other Commercial': 'Other',
               'AUDITORIUM (302)_Other Commercial': 'Other',
               'AUTO DEALERSHIP, COMPLETE (455)_Other Commercial': 'Other',
               'AUTOMOBILE SHOWROOM (303)_Other Commercial': 'Other',
               'AUTOMOTIVE CENTER (410)_Other Commercial': 'Other',
               'Administrative Office (600)_Office': 'Small- and Mid-Sized Office',
               'Art Gallery/Museum/Soc Srvc_Other Commercial': 'Other',
               'BANK (304)_Office': 'Small- and Mid-Sized Office',
               'BAR/TAVERN (442)_Restaurant': 'Restaurant',
               'BARBER SHOP (384)_Other Commercial': 'Other',
               'BARN (305)_Other Commercial': 'Other',
               'BASEMENT, FINISHED (701)_Other Commercial': 'Other',
               'BASEMENT, OFFICE (705)_Office': 'Small- and Mid-Sized Office',
               'BASEMENT, PARKING (706)_Omit': '',
               'BASEMENT, STORAGE (708)_Warehouse': 'Warehouse',
               'BASEMENT, UNFINISHED (703)_Omit': '',
               'BOWLING ALLEY (306)_Other Commercial': 'Other',
               'BROADCAST FACILITIES (498)_Other Commercial': 'Other',
               'Banquet Hall (718)_Other Commercial': 'Other',
               'Bed & Breakfast_Hotel Motel': 'Hotel',
               'CAFETERIA (530)_Restaurant': 'Restaurant',
               'CHURCH WITH SUNDAY SCHOOL (308)_Other Commercial': 'Worship Facility',
               'CLUBHOUSE (311)_Other Commercial': 'Other',
               'COCKTAIL LOUNGE (441)_Restaurant': 'Restaurant',
               'COLD STORAGE FACILITIES (447)_Other Commercial': 'Other',
               'COLLEGE (ENTIRE) (377)_University': 'University',
               'COMMUNITY SHOPPING CENTER (413)_Dry Goods Retail': 'Retail Store',
               'COMPUTER CENTER (497)_Other Commercial': 'Other',
               'CONDO HOTEL, LIMITED SERVICE (853)_Hotel Motel': 'Hotel',
               'CONDO, OFFICE (845)_Office': 'Small- and Mid-Sized Office',
               'CONDO, PARKING STRUCTURE (850)_Omit': '',
               'CONDO, RETAIL (846)_Dry Goods Retail': 'Retail Store',
               'CONVALESCENT HOSPITAL (313)_Hospital': 'Hospital',
               'CONVENIENCE MARKET (419)_Dry Goods Retail': 'Supermarket / Grocery Store',
               'CONVENTION CENTER (482)_Other Commercial': 'Other',
               'COUNTRY CLUB (314)_Other Commercial': 'Other',
               'Campground_Omit': '',
               'Car Wash - Automatic (436)_Other Commercial': 'Other',
               'Car Wash - Drive Thru (435)_Other Commercial': 'Other',
               'Car Wash - Self Serve (434)_Other Commercial': 'Other',
               'Casino (515)_Other Commercial': 'Other',
               'Classroom (356)_School': 'K-12 School',
               'Classroom (College) (368)_University': 'University',
               'Commons (College) (369)_University': 'University',
               'Community Center (514)_Other Commercial': 'Other',
               'DAY CARE CENTER (426)_School': 'K-12 School',
               'DENTAL OFFICE/CLINIC (444)_Office': 'Medical Office',
               'DEPARTMENT STORE (318)_Dry Goods Retail': 'Retail Store',
               'DISCOUNT STORE (319)_Dry Goods Retail': 'Retail Store',
               'DORMITORY (321)_Multifamily': 'Residence Hall',
               'Drug Store (511)_Dry Goods Retail': 'Retail Store',
               'Dry Cleaners-Laundry (499)_Other Commercial': 'Other',
               'ELEMENTARY SCHOOL (ENTIRE) (365)_School': 'K-12 School',
               'EQUIPMENT (SHOP) BUILDING (470)_Warehouse': 'Warehouse',
               'EQUIPMENT SHED (472)_Warehouse': 'Warehouse',
               'Easement_Omit': '',
               'FAST FOOD RESTAURANT (349)_Restaurant': 'Restaurant',
               'FIELD HOUSES (486)_Other Commercial': 'Other',
               'FIRE STATION (STAFFED) (322)_Other Commercial': 'Other',
               'FIRE STATION (VOLUNTEER) (427)_Other Commercial': 'Other',
               'FITNESS CENTER (483)_Other Commercial': 'Other',
               'FLORIST SHOP (532)_Dry Goods Retail': 'Retail Store',
               'Fine Arts & Crafts Building (355)_University': 'University',
               'Forest Land(Class-RCW 84.33)_Omit': '',
               'Fraternity/Sorority House_Multifamily': 'Residence Hall',
               'GARAGE, SERVICE REPAIR (528)_Other Commercial': 'Other',
               'GOVERNMENT COMMUNITY SERVICE BUILDING (491)_Office': 'Small- and Mid-Sized Office',
               'GROUP CARE HOME (424)_Multifamily': 'Senior Care Community',
               'Gas Station_Other Commercial': 'Other',
               'Greenhouse, Hoop, Arch-Rib, Small (135)_Other Commercial': 'Other',
               'Gymnasium (School) (358)_School': 'K-12 School',
               'HANDBALL-RACQUETBALL CLUB (417)_Other Commercial': 'Other',
               'HANGAR, MAINTENANCE & OFFICE (329)_Office': 'Small- and Mid-Sized Office',
               'HEALTH CLUB (418)_Other Commercial': 'Other',
               'HIGH SCHOOL (ENTIRE) (484)_School': 'K-12 School',
               'HOTEL, FULL SERVICE (841)_Hotel Motel': 'Hotel',
               'HOTEL, SUITE (842)_Hotel Motel': 'Hotel',
               'Hospital_Hospital': 'Hospital',
               'Hotel, Full Service (594)_Hotel Motel': 'Hotel',
               'Hotel, Limited Service (595)_Hotel Motel': 'Hotel',
               'INDUSTRIAL ENGINEERING BUILDING (392)_Other Commercial': 'Other',
               'INDUSTRIAL FLEX BUILDINGS (453)_Other Commercial': 'Other',
               'INDUSTRIAL HEAVY MANUFACTURING (495)_Other Commercial': 'Other',
               'INDUSTRIAL LIGHT MANUFACTURING (494)_Other Commercial': 'Other',
               'JAIL - POLICE STATION (489)_Other Commercial': 'Other',
               'JUNIOR HIGH SCHOOL (ENTIRE) (366)_School': 'K-12 School',
               'KENNELS (490)_Other Commercial': 'Other',
               'LABORATORIES (496)_Hospital': 'Laboratory',
               'LIGHT COMMERCIAL UTILITY BUILDING (471)_Other Commercial': 'Other',
               'LINE RETAIL (860)_Dry Goods Retail': 'Retail Store',
               'LOFT (338)_Multifamily': 'Low-Rise Multifamily',
               'Lodge (537)_Hotel Motel': 'Hotel',
               'MATERIAL STORAGE BUILDING (391)_Warehouse': 'Warehouse',
               'MINI WAREHOUSE, HI-RISE (525)_Warehouse': 'Self-Storage Facility',
               'MINI-LUBE GARAGE (423)_Other Commercial': 'Other',
               'MINI-MART CONVENIENCE STORE (531)_Grocery': 'Supermarket / Grocery Store',
               'MINI-WAREHOUSE (386)_Warehouse': 'Self-Storage Facility',
               'MIXED RETAIL W/RES. UNITS (459)_Multifamily': 'Mixed Use Property',
               'MIXED USE OFFICE (840)_Office': 'Small- and Mid-Sized Office',
               'MIXED USE RETAIL (830)_Dry Goods Retail': 'Retail Store',
               'MIXED USE-OFFICE CONDO (847)_Office': 'Small- and Mid-Sized Office',
               'MIXED USE-RETAIL CONDO (848)_Office': 'Small- and Mid-Sized Office',
               'MOTEL, FULL SERVICE (843)_Hotel Motel': 'Hotel',
               'MOTEL, SUITE (844)_Hotel Motel': 'Hotel',
               'MULTIPLE RESIDENCE (LOW RISE) (352)_Multifamily': 'Low-Rise Multifamily',
               'MULTIPLE RESIDENCE (SENIOR CITIZEN) (451)_Multifamily': 'Senior Care Community',
               'MULTIPLE RESIDENCE, RETIREMENT COMMUNITY COMPLEX_Multifamily': 'Senior Care Community',
               'MULTIPLE RESIDENCES ASSISTED LIVING (LOW RISE)_Multifamily': 'Senior Care Community',
               'MUNICIPAL SERVICE GARAGE (527)_Other Commercial': 'Other',
               'MUSEUM (481)_Other Commercial': 'Other',
               'Material Shelter (473)_Warehouse': 'Warehouse',
               'Mixed Retail w/ Office Units (597)_Office': 'Small- and Mid-Sized Office',
               'Multifamily_Multifamily': 'Low-Rise Multifamily',
               'NATATORIUM (485)_Other Commercial': 'Other',
               'NEIGHBORHOOD SHOPPING CENTER (412)_Dry Goods Retail': 'Retail Store',
               'OFFICE BUILDING (344)_Office': 'Small- and Mid-Sized Office',
               'OPEN OFFICE (820)_Office': 'Small- and Mid-Sized Office',
               'Open Space Tmbr Land/Greenbelt_Omit': '',
               'Open Space(Agric-RCW 84.34)_Omit': '',
               'Open Space(Curr Use-RCW 84.34)_Omit': '',
               'PARKING STRUCTURE (345)_Omit': '',
               'POST OFFICE - BRANCH(582)_Other Commercial': 'Other',
               'POST OFFICE - MAIL PROCESSING(583)_Other Commercial': 'Other',
               'POST OFFICE - MAIN(581)_Other Commercial': 'Other',
               'Passenger Terminal (571)_Other Commercial': 'Other',
               'REGIONAL SHOPPING CENTER (414)_Dry Goods Retail': 'Retail Store',
               'RESTAURANT, TABLE SERVICE (350)_Restaurant': 'Restaurant',
               'RESTROOM BUILDING (432)_Other Commercial': 'Other',
               'RETAIL STORE (353)_Dry Goods Retail': 'Retail Store',
               'ROOMING HOUSE (551)_Hotel Motel': 'Hotel',
               'Reforestation(RCW 84.28)_Omit': '',
               'Reserve/Wilderness Area_Omit': '',
               'Residence (348)_Single Family': '',
               'Right of Way/Utility, Road_Omit': '',
               'Rooming House_Hotel Motel': 'Hotel',
               'SHED, MATERIAL STORAGE (468)_Warehouse': 'Warehouse',
               'SKATING RINK (405)_Other Commercial': 'Other',
               'SNACK BAR (529)_Restaurant': 'Restaurant',
               'STABLE (378)_Other Commercial': 'Other',
               'STORAGE WAREHOUSE (406)_Warehouse': 'Warehouse',
               'SUPERMARKET (446)_Grocery': 'Supermarket / Grocery Store',
               'Senior Center (985)_Other Commercial': 'Senior Care Community',
               'Service Garage Shed (526)_Other Commercial': 'Other',
               'Service Station (408)_Other Commercial': 'Other',
               'Service Station_Other Commercial': 'Other',
               'Shell Structure_Warehouse': 'Warehouse',
               'Shell, Apartment (596)_Multifamily': 'Low-Rise Multifamily',
               'Shell, Industrial (454)_Other Commercial': 'Other',
               'Shell, Multiple Residence (587)_Multifamily': 'Low-Rise Multifamily',
               'Shell, Office (492)_Office': 'Small- and Mid-Sized Office',
               'Single Family_Single Family': '',
               'Single-Family Residence (351)_Single Family': '',
               'Ski Area_Omit': '',
               'Sport Facility_Other Commercial': 'Other',
               'TENNIS CLUB, INDOOR (416)_Other Commercial': 'Other',
               'THEATER, CINEMA (380)_Other Commercial': 'Other',
               'THEATER, LIVE STAGE (379)_Other Commercial': 'Other',
               'TRANSIT WAREHOUSE (387)_Warehouse': 'Warehouse',
               'Tideland, 2nd Class_Omit': '',
               'Transferable Dev Rights_Omit': '',
               'UNDERGROUND PARKING STRUCTURE (388)_Omit': '',
               'VETERINARY HOSPITAL (381)_Hospital': 'Hospital',
               'VISITOR CENTER (574)_Other Commercial': 'Other',
               'VOCATIONAL SCHOOLS (487)_School': 'K-12 School',
               'Vacant(Commercial)_Omit': '',
               'Vacant(Multi-family)_Omit': '',
               'Vacant(Single-family)_Omit': '',
               'WAREHOUSE DISCOUNT STORE (458)_Warehouse': 'Warehouse',
               'WAREHOUSE FOOD STORE (533)_Grocery': 'Supermarket / Grocery Store',
               'WAREHOUSE OFFICE (810)_Office': 'Small- and Mid-Sized Office',
               'WAREHOUSE SHOWROOM STORE (534)_Dry Goods Retail': 'Retail Store',
               'WAREHOUSE, DISTRIBUTION (407)_Warehouse': 'Warehouse',
               'Water Body, Fresh_Omit': '',
               '_Omit': ''}

    return typ_map[typ]


def plot_hist(cnts, bins, val, typ):

    fig, ax = plt.subplots()
    ax.bar(bins[:-1], cnts, width=bins[1]-bins[0])
    plt.ylabel('number of buildings')
    if val == 'site eui':
        plt.xlabel('site EUI (kBtu/ft$^2$)')
        hist_file = 'site-eui-histogram_%s.png' % type_file_name(typ)
    elif val == 'elec/site':
        plt.xlabel('proportion of electric to site energy')
        hist_file = 'elec-site-ratio-histogram_%s.png' % type_file_name(typ)
    plt.tight_layout()
    plt.savefig(os.path.join('plots',hist_file), dpi=png_res)
    plt.close()


def type_file_name(typ):
    typ_name_map = {'Hospital': 'hospital',
                    'Hotel': 'hotel',
                    'K-12 School': 'k-12-school',
                    'Laboratory': 'laboratory',
                    'Low-Rise Multifamily': 'low-rise-multifamily',
                    'Medical Office': 'medical-office',
                    'Mixed Use Property': 'mixed-use-property',
                    'Other': 'other',
                    'Residence Hall': 'residence-hall',
                    'Restaurant': 'restaurant',
                    'Retail Store': 'retail-store',
                    'Self-Storage Facility': 'self-storage-facility',
                    'Senior Care Community': 'senior-care-community',
                    'Small- and Mid-Sized Office': 'small-and-mid-sized-office',
                    'Supermarket / Grocery Store': 'supermarket-grocery-store',
                    'University': 'university',
                    'Warehouse': 'warehouse',
                    'Worship Facility': 'worship-facility'}
    name = typ_name_map[typ]
    return name


if __name__ == '__main__':
    main()
