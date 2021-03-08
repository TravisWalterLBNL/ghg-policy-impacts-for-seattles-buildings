#!/usr/bin/env python

import numpy as np
import os
import pandas as pd
from config import *
np.random.seed(0)


if not os.path.isdir('results'):
    os.mkdir('results')


def main():

    for scenario in scenarios:
        print(scenario)
        data = pd.read_csv('buildings.csv')
        compute(data, scenario)


def compute(data, scenario):

    # starting year for annual rates (for readjusting rates when other policies end)
    for policy in ['tuneup','eui','ghg']:
        data['%s start year' % policy] = 0
        data['next %s start year' % policy] = 0

    # year in which a building electrified
    data['elec year'] = np.nan

    for year in years[1:]:

        # initialize reductions to zero
        for policy in policies:
            for fuel in fuels:
                data['%d %s %s reduct' % (year,policy,fuel)] = 0.0

        # compute tuneup reductions
        # - reduce each fuel by specified proportion
        # - reduce equal amount each year
        for target in get_tuneup_targets(scenario):

            # find buildings that target applies to
            targ_idx = pd.Series(index=data.index, data=True)
            if 'types' in target.keys():
                targ_idx &= data['type'].isin(target['types'])
            if 'not types' in target.keys():
                targ_idx &= ~data['type'].isin(target['not types'])
            if 'areas' in target.keys():
                min_area, max_area = target['areas']
                targ_idx &= data['area'] >= min_area
                targ_idx &= data['area'] < max_area

            targ_start_year, targ_end_year = target['years']
            if (year >= targ_start_year) and (year <= targ_end_year):

                # if beginning of policy, set start year for tuneup policy
                # - keep that start year unless another policy sets it to next year
                if year == targ_start_year:
                    data.loc[targ_idx,'tuneup start year'] = year
                    oth_idx = data['next tuneup start year'] == year + 1
                    data.loc[targ_idx & ~oth_idx,'next tuneup start year'] = year

                # compute target energy, starting energy, energy reduction, and annual reduction for each fuel
                for fuel in fuels:
                    target_ens = data.loc[targ_idx, '%d %s' % (targ_start_year-1,fuel)] * (1.0 - target['reduct prop'])
                    start_ens = pd.Series(index=data.loc[targ_idx].index, data=np.nan)
                    for start_year in set(data.loc[targ_idx,'tuneup start year']).difference([0]):
                        idx = data.loc[targ_idx,'tuneup start year'] == start_year
                        start_ens.loc[idx] = data.loc[targ_idx, '%d %s' % (start_year-1,fuel)].loc[idx]
                    en_reducts = start_ens - target_ens
                    en_reducts.loc[en_reducts < 0.0] = 0.0
                    ann_reducts = pd.Series(index=data.loc[targ_idx].index, data=np.nan)
                    for start_year in set(data.loc[targ_idx,'tuneup start year']).difference([0]):
                        idx = data.loc[targ_idx,'tuneup start year'] == start_year
                        ann_reducts.loc[idx] = en_reducts.loc[idx] / float(targ_end_year - start_year + 1)
                    data.loc[targ_idx, '%d tuneup %s reduct' % (year,fuel)] = ann_reducts

                # if end of policy, set next start year for other non-electrify policies
                if year == targ_end_year:
                    for policy in ['eui','ghg']:
                        data.loc[targ_idx, 'next %s start year' % policy] = year + 1

        # compute eui reductions
        # - reduce eui to average eui in specified year
        # - average eui is over areas and types of buildings that target applies to
        # - reduce equal amount each year
        for target in get_eui_targets(scenario):

            # find buildings that target applies to
            targ_idx = pd.Series(index=data.index, data=True)
            if 'types' in target.keys():
                targ_idx &= data['type'].isin(target['types'])
            if 'not types' in target.keys():
                targ_idx &= ~data['type'].isin(target['not types'])
            if 'areas' in target.keys():
                min_area, max_area = target['areas']
                targ_idx &= data['area'] >= min_area
                targ_idx &= data['area'] < max_area

            targ_start_year, targ_end_year = target['years']
            if (year >= targ_start_year) and (year <= targ_end_year):

                # if beginning of policy, set start year for eui policy
                # - keep that start year unless another policy sets it to next year
                if year == targ_start_year:
                    data.loc[targ_idx,'eui start year'] = year
                    oth_idx = data['next eui start year'] == year + 1
                    data.loc[targ_idx & ~oth_idx,'next eui start year'] = year

                # compute target energy
                target_year = target['avg year']
                target_year_ens = pd.Series(index=data.loc[targ_idx].index, data=0.0)
                for fuel in fuels:
                    target_year_ens += data.loc[targ_idx, '%d %s' % (target_year,fuel)]
                target_eui = (target_year_ens / data.loc[targ_idx,'area']).mean()
                target_ens = target_eui * data.loc[targ_idx,'area']

                # compute starting energy
                start_ens = pd.Series(index=data.loc[targ_idx].index, data=0.0)
                for start_year in set(data.loc[targ_idx,'eui start year']).difference([0]):
                    idx = data.loc[targ_idx,'eui start year'] == start_year
                    for fuel in fuels:
                        start_ens.loc[idx] += data.loc[targ_idx, '%d %s' % (start_year-1,fuel)].loc[idx]

                # compute energy reductions
                en_reducts = start_ens - target_ens
                en_reducts.loc[en_reducts < 0.0] = 0.0

                # compute annual reduction for each fuel
                # - maintain proportion of fuels (based on site energy)
                for fuel in fuels:
                    ann_reducts = pd.Series(index=data.loc[targ_idx].index, data=np.nan)
                    for start_year in set(data.loc[targ_idx,'eui start year']).difference([0]):
                        idx = data.loc[targ_idx,'eui start year'] == start_year
                        fuel_en = data.loc[targ_idx, '%d %s' % (start_year-1,fuel)].loc[idx]
                        fuel_ratio = fuel_en / start_ens.loc[idx]
                        ann_reducts.loc[idx] = fuel_ratio * en_reducts.loc[idx] / float(targ_end_year - start_year + 1)
                    data.loc[targ_idx, '%d eui %s reduct' % (year,fuel)] = ann_reducts

                # subtract reductions due to earlier policies
                for fuel in fuels:
                    data.loc[targ_idx, '%d eui %s reduct' % (year,fuel)] -= data.loc[targ_idx, '%d tuneup %s reduct' % (year,fuel)]
                    is_neg = data['%d eui %s reduct' % (year,fuel)] < 0.0
                    data.loc[targ_idx & is_neg, '%d eui %s reduct' % (year,fuel)] = 0.0

                # if end of policy, set next start year for other non-electrify policies
                if year == targ_end_year:
                    for policy in ['tuneup','ghg']:
                        data.loc[targ_idx, 'next %s start year' % policy] = year + 1

        # compute ghg reductions
        # - reduce ghg intensity to average in specified year
        # - average is over areas and types of buildings that target applies to
        # - only a specified proportion of buildings comply
        # - reduce equal amount each year, except change amount once in electrification year
        for target in get_ghg_targets(scenario):

            # find buildings that target applies to
            targ_idx = pd.Series(index=data.index, data=True)
            if 'types' in target.keys():
                targ_idx &= data['type'].isin(target['types'])
            if 'not types' in target.keys():
                targ_idx &= ~data['type'].isin(target['not types'])
            if 'areas' in target.keys():
                min_area, max_area = target['areas']
                targ_idx &= data['area'] >= min_area
                targ_idx &= data['area'] < max_area

            # find buildings that will comply with target
            num_bldgs = int(round(targ_idx.sum() * target['bldg prop']))
            np.random.seed(0)
            comp_idxs = np.random.choice(data.loc[targ_idx].index, size=num_bldgs, replace=False)
            comp_idx = pd.Series(index=data.index, data=False)
            comp_idx.loc[comp_idxs] = True

            targ_start_year, targ_end_year = target['years']
            if (year >= targ_start_year) and (year <= targ_end_year):

                # if beginning of policy, set start year for ghg policy
                # - keep that start year unless another policy sets it to next year
                if year == targ_start_year:
                    data.loc[comp_idx,'ghg start year'] = year
                    oth_idx = data['next ghg start year'] == year + 1
                    data.loc[comp_idx & ~oth_idx,'next ghg start year'] = year

                # compute target ghgs (if target is average ghg intensity in specified year)
                if 'avg year' in target.keys():
                    target_year = target['avg year']
                    target_year_ghgs = pd.Series(index=data.loc[comp_idx].index, data=0.0)
                    for fuel in fuels:
                        target_year_ghgs += data.loc[comp_idx, '%d %s' % (target_year,fuel)] * ghg_factors[fuel]
                    target_ghg_int = (target_year_ghgs / data.loc[comp_idx,'area']).mean()
                    target_ghgs = target_ghg_int * data.loc[comp_idx,'area']

                # compute target ghgs (if target is specified percentage of ghgs in year before start)
                elif 'reduct prop' in target.keys():
                    target_ghgs = pd.Series(index=data.loc[comp_idx].index, data=0.0)
                    for fuel in fuels:
                        target_ghgs += data.loc[comp_idx, '%d %s' % (targ_start_year-1,fuel)] * (1.0 - target['reduct prop']) * ghg_factors[fuel]

                # compute target ghgs (if target is specified ghg intensity)
                elif 'targ val' in target.keys():
                    target_ghgs = target['targ val'] * data.loc[comp_idx,'area']

                else:
                    target_ghgs = None

                # compute starting ghgs
                start_ghgs = pd.Series(index=data.loc[comp_idx].index, data=0.0)
                for start_year in set(data.loc[comp_idx,'ghg start year']).difference([0]):
                    idx = data.loc[comp_idx,'ghg start year'] == start_year
                    for fuel in fuels:
                        start_ghgs.loc[idx] += data.loc[comp_idx, '%d %s' % (start_year-1,fuel)].loc[idx] * ghg_factors[fuel]

                # compute ghg reductions
                ghg_reducts = start_ghgs - target_ghgs
                ghg_reducts.loc[ghg_reducts < 0.0] = 0.0

                # compute annual reduction for each fuel
                # - maintain proportion of fuels (same whether based on site energy or ghg emissions)
                for fuel in fuels:
                    ann_reducts = pd.Series(index=data.loc[comp_idx].index, data=np.nan)
                    for start_year in set(data.loc[comp_idx,'ghg start year']).difference([0]):
                        idx = data.loc[comp_idx,'ghg start year'] == start_year
                        fuel_ghg = data.loc[comp_idx, '%d %s' % (start_year-1,fuel)].loc[idx] * ghg_factors[fuel]
                        fuel_ratio = fuel_ghg / start_ghgs.loc[idx]
                        ann_reducts.loc[idx] = fuel_ratio * ghg_reducts.loc[idx] / float(targ_end_year - start_year + 1)
                    data.loc[comp_idx, '%d ghg %s reduct' % (year,fuel)] = ann_reducts / ghg_factors[fuel]

                # subtract reductions due to earlier policies
                for fuel in fuels:
                    data.loc[comp_idx, '%d ghg %s reduct' % (year,fuel)] -= data.loc[comp_idx, '%d tuneup %s reduct' % (year,fuel)]
                    data.loc[comp_idx, '%d ghg %s reduct' % (year,fuel)] -= data.loc[comp_idx, '%d eui %s reduct' % (year,fuel)]
                    is_neg = data['%d ghg %s reduct' % (year,fuel)] < 0.0
                    data.loc[comp_idx & is_neg, '%d ghg %s reduct' % (year,fuel)] = 0.0

                # if end of policy, set next start year for other non-electrify policies
                if year == targ_end_year:
                    for policy in ['tuneup','eui']:
                        data.loc[comp_idx, 'next %s start year' % policy] = year + 1

        # compute electrification reductions
        # - replace non-electric load with electric load (according to coefficient of performance)
        # - only replace a specified proportion of non-electric load
        # - only a specified proportion of buildings electrify
        # - each building does all of its electrification in one year
        # - equal proportion of buildings electrify each year
        for target in get_electrify_targets(scenario):

            # find buildings that target applies to
            targ_idx = pd.Series(index=data.index, data=True)
            if 'types' in target.keys():
                targ_idx &= data['type'].isin(target['types'])
            if 'not types' in target.keys():
                targ_idx &= ~data['type'].isin(target['not types'])
            if 'areas' in target.keys():
                min_area, max_area = target['areas']
                targ_idx &= data['area'] >= min_area
                targ_idx &= data['area'] < max_area

            targ_start_year, targ_end_year = target['years']
            if (year >= targ_start_year) and (year <= targ_end_year):

                # find buildings that will electrify this year
                # - each building does all of its electrification in one year
                # - equal proportion of buildings electrify each year
                # - recompute each year to make sure total number matches target (because of rounding)
                tot_num_bldgs = int(round(targ_idx.sum() * target['bldg prop']))
                year_num_bldgs = int(round((tot_num_bldgs - data.loc[targ_idx,'elec year'].notnull().sum()) / float(targ_end_year - year + 1)))
                nonelec_idx = targ_idx & data['elec year'].isnull()
                year_idxs = np.random.choice(nonelec_idx.loc[nonelec_idx].index, size=year_num_bldgs, replace=False)
                year_idx = pd.Series(index=data.index, data=False)
                year_idx.loc[year_idxs] = True
                data.loc[year_idx,'elec year'] = year

                # for bldgs that electrified, set next start year for all non-electrify policies
                for policy in ['tuneup','eui','ghg']:
                    data.loc[year_idx, 'next %s start year' % policy] = year + 1

                # compute reduction for each non-electric fuel
                # - only for buildings that electrify this year
                # - reduction is based on load after applying this year's reductions from earlier policies
                for fuel in filter(lambda f: f != 'elec', fuels):
                    fuel_amt = data.loc[year_idx, '%d %s' % (year-1,fuel)]
                    fuel_amt -= data.loc[year_idx, '%d tuneup %s reduct' % (year,fuel)]
                    fuel_amt -= data.loc[year_idx, '%d eui %s reduct' % (year,fuel)]
                    fuel_amt -= data.loc[year_idx, '%d ghg %s reduct' % (year,fuel)]
                    data.loc[year_idx, '%d electrify %s reduct' % (year,fuel)] = target['fuel prop'] * fuel_amt
                    is_neg = data['%d electrify %s reduct' % (year,fuel)] < 0.0
                    data.loc[year_idx & is_neg, '%d electrify %s reduct' % (year,fuel)] = 0.0

                # compute (negative) electric reductions using (positive) non-electric reductions
                # - only for buildings that electrify this year
                # - use coefficient of performance to replace non-electric with electric
                data.loc[year_idx, '%d electrify elec reduct' % year] = 0.0
                for fuel in filter(lambda f: f != 'elec', fuels):
                    fuel_reduct = data.loc[year_idx, '%d electrify %s reduct' % (year,fuel)]
                    data.loc[year_idx, '%d electrify elec reduct' % year] -= fuel_reduct / float(target['coef of perf'])

        # propogate start years for non-electrify policies
        for policy in ['tuneup','eui','ghg']:
            data['%s start year' % policy] = data['next %s start year' % policy]

        # compute reductions due to each fuel
        for fuel in fuels:
            data['%d %s reduct' % (year,fuel)] = 0.0
            for policy in policies:
                data['%d %s reduct' % (year,fuel)] += data['%d %s %s reduct' % (year,policy,fuel)]

        # compute reductions due to each policy
        for policy in policies:
            data['%d %s reduct' % (year,policy)] = 0.0
            for fuel in fuels:
                data['%d %s reduct' % (year,policy)] += data['%d %s %s reduct' % (year,policy,fuel)]

        # compute new energy use
        for fuel in fuels:
            data['%d %s' % (year,fuel)] = data['%d %s' % (year-1,fuel)] - data['%d %s reduct' % (year,fuel)]

    # check for nans
    for col in filter(lambda c: c != 'elec year', data.columns):
        idx = data[col].isnull()
        if idx.any():
            print('found %d bldgs with nan in column "%s"' % (idx.sum(),col))

    # check for negative energy use
    approx_zero = -1e-6
    for year in years:
        for fuel in fuels:
            col = '%d %s' % (year,fuel)
            idx = data[col] < approx_zero
            if idx.any():
                print('found %d bldgs with negatives in column "%s"' % (idx.sum(),col))

    # check for negative non-electric reductions
    approx_zero = -1e-6
    for year in years[1:]:
        for policy in policies:
            for fuel in filter(lambda f: f != 'elec', fuels):
                col = '%d %s %s reduct' % (year,policy,fuel)
                idx = data[col] < approx_zero
                if idx.any():
                    print('found %d bldgs with negatives in column "%s"' % (idx.sum(),col))

    # write data to file
    data.to_csv(os.path.join('results','%s.csv' % scenario.replace(' ','-')), index=False)


if __name__ == '__main__':
    main()
