#!/usr/bin/env python

import os
import matplotlib.pyplot as plt
plt.rcParams.update({'mathtext.default': 'regular'})
import numpy as np
import pandas as pd
from config import *


if not os.path.isdir('plots'):
    os.mkdir('plots')

png_res = 300 # dpi
alpha = 0.5

num_types = 7

colors = ['red',
          'blue',
          'green',
          'magenta',
          'yellow',
          'navy',
          'orange',
          'purple',
          'maroon',
          'sienna',
          'gold',
          'seagreen',
          'cyan',
          'lime',
          'skyblue',
          'cornflowerblue',
          'plum',
          'pink',
          'olive',
          'mediumorchid',
          'darkkhaki',
          'tan']
assert len(colors)==len(bldg_types)

def main():

    all_data = {}
    for scenario in scenarios:
        scen_data = pd.read_csv(os.path.join('results','%s.csv' % scenario.replace(' ','-')))
        all_data[scenario] = scen_data

        quantity_by_policy(scen_data, scenario, 'energy')
        quantity_by_policy(scen_data, scenario, 'emissions')

        quantity_by_type(scen_data, scenario, 'energy')
        quantity_by_type(scen_data, scenario, 'emissions')

        quantity_by_area(scen_data, scenario, 'energy')
        quantity_by_area(scen_data, scenario, 'emissions')

    for cumulative in [True,False]:
        quantity_by_scenario(all_data, 'energy', cumulative)
        quantity_by_scenario(all_data, 'emissions', cumulative)

    histogram_type(all_data[scenarios[0]])
    quantity_type_bars(all_data[scenarios[0]], 'energy')
    quantity_type_bars(all_data[scenarios[0]], 'emissions')

    histogram_area(all_data[scenarios[0]])
    quantity_area_bars(all_data[scenarios[0]], 'energy')
    quantity_area_bars(all_data[scenarios[0]], 'emissions')


def quantity_by_policy(data, scenario, quantity):

    if quantity == 'energy':
        weights = {}
        for fuel in fuels:
            weights[fuel] = 1.0
    elif quantity == 'emissions':
        weights = ghg_factors

    init_val = 0.0
    for fuel in fuels:
        init_val += data['%d %s' % (years[0],fuel)].sum() * weights[fuel]

    values = {}
    for p in range(len(policies)):
        vals = [init_val]
        for y in range(1,len(years)):
            val = vals[y-1]
            for i in range(p+1):
                for fuel in fuels:
                    val -= data['%d %s %s reduct' % (years[y],policies[i],fuel)].sum() * weights[fuel]
            vals.append(val)
        vals = [100*val/init_val for val in vals]
        values[policies[p]] = vals

    fig, ax = plt.subplots()

    ax.fill_between(years, values[policies[0]], 100, label=policy_labels[0], color=colors[0], alpha=alpha, linewidth=0)
    for p in range(1,len(policies)):
        ax.fill_between(years, values[policies[p]], values[policies[p-1]], label=policy_labels[p], color=colors[p], alpha=alpha, linewidth=0)
    ax.fill_between(years, 0, values[policies[-1]], color='grey', alpha=alpha, linewidth=0)

    ax.yaxis.set_label_position('right')
    ax.yaxis.tick_right()
    ax.set_xlim(years[0], years[-1])
    ax.set_ylim(0, 105)
    ax.set_xticks(years)
    ax.set_xticklabels([str(y) if (y%5==0) else '' for y in years])
    ax.set_yticks(range(0,100+1,10))
    ax.set_xlabel('year')
    ax.set_ylabel('%s (%% of 2020)' % quantity)
    ax.legend(loc='lower left', fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join('plots','%s-by-policy_%s.png' % (quantity,scenario.replace(' ','-'))), dpi=png_res)
    plt.close()


def quantity_by_type(data, scenario, quantity):

    if quantity == 'energy':
        weights = {}
        for fuel in fuels:
            weights[fuel] = 1.0
    elif quantity == 'emissions':
        weights = ghg_factors

    vals = []
    for bldg_type in bldg_types:
        idx = data['type'] == bldg_type
        val = 0.0
        for fuel in fuels:
            val += data.loc[idx,'%d %s' % (years[0],fuel)].sum() * weights[fuel]
        vals.append(val)
    types = [t for v,t in sorted(zip(vals,bldg_types), reverse=True)]
    types = types[:num_types]
    tmp_data = data.copy()
    for typ in set(tmp_data['type']):
        if typ not in types:
            tmp_data.loc[tmp_data['type']==typ, 'type'] = 'All Others Combined'
    types.append('All Others Combined')

    init_val = 0.0
    for fuel in fuels:
        init_val += tmp_data['%d %s' % (years[0],fuel)].sum() * weights[fuel]

    values = {}
    for t in range(len(types)):
        vals = [init_val]
        for y in range(1,len(years)):
            val = vals[y-1]
            for i in range(t+1):
                idx = tmp_data['type'] == types[i]
                for fuel in fuels:
                    for policy in policies:
                        val -= tmp_data.loc[idx, '%d %s %s reduct' % (years[y],policy,fuel)].sum() * weights[fuel]
            vals.append(val)
        vals = [100*val/init_val for val in vals]
        values[types[t]] = vals

    fig, ax = plt.subplots()

    ax.fill_between(years, values[types[0]], 100, label=types[0], color=colors[bldg_types.index(types[0])], alpha=alpha, linewidth=0)
    for t in range(1,len(types)-1):
        ax.fill_between(years, values[types[t]], values[types[t-1]], label=types[t], color=colors[bldg_types.index(types[t])], alpha=alpha, linewidth=0)
    ax.fill_between(years, values[types[t+1]], values[types[t]], label=types[t+1], color=colors[-1], alpha=alpha, linewidth=0)
    ax.fill_between(years, 0, values[types[-1]], color='grey', alpha=alpha, linewidth=0)

    ax.yaxis.set_label_position('right')
    ax.yaxis.tick_right()
    ax.set_xlim(years[0], years[-1])
    ax.set_ylim(0, 105)
    ax.set_xticks(years)
    ax.set_xticklabels([str(y) if (y%5==0) else '' for y in years])
    ax.set_yticks(range(0,100+1,10))
    ax.set_xlabel('year')
    ax.set_ylabel('%s (%% of 2020)' % quantity)
    ax.legend(loc='lower left', fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join('plots','%s-by-type_%s.png' % (quantity,scenario.replace(' ','-'))), dpi=png_res)
    plt.close()


def quantity_by_area(data, scenario, quantity):

    if quantity == 'energy':
        weights = {}
        for fuel in fuels:
            weights[fuel] = 1.0
    elif quantity == 'emissions':
        weights = ghg_factors

    init_val = 0.0
    for fuel in fuels:
        init_val += data['%d %s' % (years[0],fuel)].sum() * weights[fuel]

    values = {}
    for a in range(len(areas)):
        vals = [init_val]
        for y in range(1,len(years)):
            val = vals[y-1]
            for i in range(a+1):
                idx = (data['area'] >= areas[i][1]) & (data['area'] < areas[i][2])
                for fuel in fuels:
                    for policy in policies:
                        val -= data.loc[idx, '%d %s %s reduct' % (years[y],policy,fuel)].sum() * weights[fuel]
            vals.append(val)
        vals = [100*val/init_val for val in vals]
        values[areas[a][0]] = vals

    fig, ax = plt.subplots()

    ax.fill_between(years, values[areas[0][0]], 100, label=areas[0][0], color=colors[0], alpha=alpha, linewidth=0)
    for a in range(1,len(areas)):
        ax.fill_between(years, values[areas[a][0]], values[areas[a-1][0]], label=areas[a][0], color=colors[a], alpha=alpha, linewidth=0)
    ax.fill_between(years, 0, values[areas[-1][0]], color='grey', alpha=alpha, linewidth=0)

    ax.yaxis.set_label_position('right')
    ax.yaxis.tick_right()
    ax.set_xlim(years[0], years[-1])
    ax.set_ylim(0, 105)
    ax.set_xticks(years)
    ax.set_xticklabels([str(y) if (y%5==0) else '' for y in years])
    ax.set_yticks(range(0,100+1,10))
    ax.set_xlabel('year')
    ax.set_ylabel('%s (%% of 2020)' % quantity)
    ax.legend(loc='lower left', fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join('plots','%s-by-area_%s.png' % (quantity,scenario.replace(' ','-'))), dpi=png_res)
    plt.close()


def quantity_by_scenario(all_data, quantity, cumulative):

    scens_dict = {'amount': {'Basecase': 'basecase',
                             'Phasing-Option A': 'nominal (20% from 2020)',
                             'Phasing-Option A2': '30% from 2020',
                             'Phasing-Option A3': 'modeled target'},
                  'timing': {'Basecase': 'basecase',
                             'Phasing-Option A': 'nominal',
                             'Phasing-Option B': '5 year delay',
                             'Phasing-Option E': '5 year electrification'},
                  'area': {'Basecase': 'basecase',
                           'Phasing-Option A': 'nominal (>50k ft$^2$)',
                           'Phasing-Option C': '>20k ft$^2$',
                           'Phasing-Option D': 'all areas'},
                  'exempt': {'Basecase': 'basecase',
                             'Phasing-Option A': 'nominal',
                             'Phasing-Option F': 'hospitals exempt',
                             'Phasing-Option G': 'hotels exempt',
                             'Phasing-Option H': 'restaurants exempt',
                             'Phasing-Option I': 'hospitals, hotels, and restaurants exempt'}}

    for scens_name in scens_dict.keys():
        scenarios = sorted(scens_dict[scens_name].keys())

        if quantity == 'energy':
            weights = {}
            for fuel in fuels:
                weights[fuel] = 1.0
        elif quantity == 'emissions':
            weights = ghg_factors

        scenario = scenarios[0]
        scen_data = all_data[scenario]
        init_val = 0.0
        for fuel in fuels:
            init_val += scen_data['%d %s' % (years[0],fuel)].sum() * weights[fuel]

        values = {}
        for scenario in scenarios:
            scen_data = all_data[scenario]
            vals = [init_val]
            for y in range(1,len(years)):
                val = vals[y-1]
                for fuel in fuels:
                    val -= scen_data['%d %s reduct' % (years[y],fuel)].sum() * weights[fuel]
                vals.append(val)
            if cumulative:
                vals = list(np.cumsum(vals))
                for y in range(len(years)):
                    vals[y] = init_val*(y+1) - vals[y]
                    if quantity == 'energy':
                        vals[y] /= 1.0e9 # kBtu to billion kBtu
                    elif quantity == 'emissions':
                        vals[y] /= 1.0e9 # kgCO2e to million MtCO2e
            else:
                vals = [100.0*val/init_val for val in vals]
            values[scenario] = vals

        labels = []
        for s in range(len(scenarios)):
            labels.append(scens_dict[scens_name][scenarios[s]])

        fig, ax = plt.subplots()

        for s in range(len(scenarios)):
            ax.plot(years, values[scenarios[s]], label=labels[s], color=colors[s], linewidth=2)

        ax.set_xlim(years[0], years[-1])
        ax.set_xticks(years)
        ax.set_xticklabels([str(y) if (y%5==0) else '' for y in years])
        ax.set_xlabel('year')
        ax.yaxis.set_label_position('right')
        ax.yaxis.tick_right()
        if not cumulative:
            ax.set_ylim(0, 105)
            ax.set_yticks(range(0,100+1,10))
        if cumulative:
            if quantity == 'energy':
                units = 'billion kBtu'
            elif quantity == 'emissions':
                units = 'million MtCO2e'
            ax.set_ylabel('%s savings (%s)' % (quantity,units))
            ax.legend(loc='upper left', fontsize=12)
            plt.tight_layout()
            plt.savefig(os.path.join('plots','%s-cumulative-savings-by-scenario-%s.png' % (quantity,scens_name)), dpi=png_res)
        else:
            ax.set_ylabel('%s (%% of 2020)' % quantity)
            ax.legend(loc='lower left', fontsize=12)
            plt.tight_layout()
            plt.savefig(os.path.join('plots','%s-by-scenario-%s.png' % (quantity,scens_name)), dpi=png_res)
        plt.close()


def histogram_type(data):

    fig, ax = plt.subplots()

    for t in range(len(bldg_types)):
        typ = bldg_types[t]
        idx = data['type'] == typ
        ax.barh(t, idx.sum() / float(len(idx)) * 100.0, align='center')

    ax.set_ylim(-0.5, len(bldg_types)-0.5)
    ax.set_yticks(range(len(bldg_types)))
    ax.set_yticklabels(bldg_types)
    ax.set_ylabel('building type')
    ax.set_xlabel('% of buildings')
    plt.tight_layout()
    plt.savefig(os.path.join('plots','type-histogram.png'), dpi=png_res)
    plt.close()


def histogram_area(data):

    fig, ax = plt.subplots()

    area_labs = []
    for a in range(len(areas)):
        area_lab, area_min, area_max = areas[a]
        area_labs.append(area_lab[:-len(' ft$^2$')])
        idx = (data['area'] >= area_min) & (data['area'] < area_max)
        ax.bar(a, idx.sum() / float(len(idx)) * 100.0, align='center')

    ax.set_xlim(-0.5, len(areas)-0.5)
    ax.set_xticks(range(len(areas)))
    ax.set_xticklabels(area_labs)
    ax.set_xlabel('floor area (ft$^2$)')
    ax.set_ylabel('% of buildings')
    plt.tight_layout()
    plt.savefig(os.path.join('plots','area-histogram.png'), dpi=png_res)
    plt.close()


def quantity_type_bars(data, quantity):

    if quantity == 'energy':
        weights = {}
        for fuel in fuels:
            weights[fuel] = 1.0
    elif quantity == 'emissions':
        weights = ghg_factors

    vals = pd.Series(index=data.index, data=0.0)
    for fuel in fuels:
        vals += data['%d %s' % (years[0],fuel)] * weights[fuel]

    fig, ax = plt.subplots()

    for t in range(len(bldg_types)):
        typ = bldg_types[t]
        idx = data['type'] == typ
        ax.barh(t, vals.loc[idx].sum() / vals.sum() * 100.0, align='center')

    ax.set_ylim(-0.5, len(bldg_types)-0.5)
    ax.set_yticks(range(len(bldg_types)))
    ax.set_yticklabels(bldg_types)
    ax.set_ylabel('building type')
    ax.set_xlabel('%s (%% of total)' % quantity)
    plt.tight_layout()
    plt.savefig(os.path.join('plots','%s-type-bars.png' % quantity), dpi=png_res)
    plt.close()


def quantity_area_bars(data, quantity):

    if quantity == 'energy':
        weights = {}
        for fuel in fuels:
            weights[fuel] = 1.0
    elif quantity == 'emissions':
        weights = ghg_factors

    vals = pd.Series(index=data.index, data=0.0)
    for fuel in fuels:
        vals += data['%d %s' % (years[0],fuel)] * weights[fuel]

    fig, ax = plt.subplots()

    area_labs = []
    for a in range(len(areas)):
        area_lab, area_min, area_max = areas[a]
        area_labs.append(area_lab[:-len(' ft$^2$')])
        idx = (data['area'] >= area_min) & (data['area'] < area_max)
        ax.bar(a, vals.loc[idx].sum() / vals.sum() * 100.0, align='center')

    ax.set_xlim(-0.5, len(areas)-0.5)
    ax.set_xticks(range(len(areas)))
    ax.set_xticklabels(area_labs)
    ax.set_xlabel('floor area (ft$^2$)')
    ax.set_ylabel('%s (%% of total)' % quantity)
    plt.tight_layout()
    plt.savefig(os.path.join('plots','%s-area-bars.png' % quantity), dpi=png_res)
    plt.close()


if __name__ == '__main__':
    main()
