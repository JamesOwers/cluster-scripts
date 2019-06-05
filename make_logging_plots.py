#!/usr/bin/env python

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms
import seaborn as sns

import sys
import os
from glob import glob
import random

log_home = os.path.expanduser('~/logging')

gpu_usage_files = glob(f'{log_home}/gpu-usage__*.txt')
df_list = []
for ff in gpu_usage_files:
    df = pd.read_csv(ff, header=None, names=['in_use', 'usable', 'total'])
    df['datetime'] = pd.to_datetime(
        ff.split('__')[-1].split('.')[0],
        format='%d-%m-%Y_%H-%M-%S'
    )
    df.set_index('datetime', inplace=True)
    df_list += [df]
gpu_usage_df = pd.concat(df_list, axis=0)
gpu_usage_df.sort_index(inplace=True)
plt.figure(figsize=(12, 4))
gpu_usage_df.plot(ax=plt.gca())
lines = plt.gca().get_lines()
usable = lines[1]
usable.set_linestyle('--')
total = lines[2]
total.set_linestyle(':')
ylims = plt.ylim()
plt.ylim([0, ylims[1]])
ymin, ymax = plt.ylim()
xx = gpu_usage_df.index.values
hour = gpu_usage_df.index.hour
day = gpu_usage_df.index.dayofweek
ax = plt.gca()
trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
boxes = ax.fill_between(xx, ymin, ymax, where=(hour >= 9) * (hour <= 17) * (day <= 4),
                        facecolor='gray', alpha=0.2, transform=trans, label='working day')
plt.legend()
plt.savefig('./gpu-usage.pdf', dpi=300, bbox_inches='tight')

whoson_files = glob(f'{log_home}/whoson__*.txt')
df_list = []
for ff in whoson_files:
    df = pd.read_csv(ff, sep='\s{2,}', engine='python')
    try:
        split_cols = df['jobs(running/pending/total)'].str.split('/', expand=True)
    except AttributeError as e:
        print(f'WARNING: import failed for: {ff}')
        print(df)
        print(df.dtypes)
        continue
    df['running'] = split_cols[0].astype('int')
    df['pending'] = split_cols[1].astype('int')
    df['total'] = split_cols[2].astype('int')
    df['datetime'] = pd.to_datetime(
        ff.split('__')[-1].split('.')[0],
        format='%d-%m-%Y_%H-%M-%S'
    )
    df.set_index('datetime', inplace=True)
    df_list += [df]
whoson_df = pd.concat(df_list, axis=0)
fig = plt.figure(figsize=(12, 4))
df = whoson_df[['name', 'running']].reset_index().pivot(index='datetime', columns='name')
# df.plot(ax=plt.gca())
df.plot.area(ax=plt.gca(), linewidth=0))
# lines = plt.gca().get_lines()
# for ii, line in enumerate(lines):
#     linestyle = [':', '-.', '--'][ii//10]
#     line.set_linestyle(linestyle)
#     line.set_alpha(.95)
polys = [pp for pp in plt.gca().get_children() if isinstance(pp, matplotlib.collections.PolyCollection)]
ax = plt.gca()
for ii, poly in enumerate(polys):
    hatch = [None, '//', '\\\\'][ii//10]
    poly.set_edgecolor('k')
    poly.set_linewidth(0)
    poly.set_hatch(hatch)
    poly.set_alpha(.9)
xx = df.index.values
hour = df.index.hour
day = df.index.dayofweek
ax = plt.gca()
trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
ymin, ymax = plt.ylim()
boxes = ax.fill_between(xx, ymin, ymax, where=(hour >= 9) * (hour <= 17) * (day <= 4),
                        facecolor='gray', alpha=0.2, transform=trans, label='working day')
handles, labels = ax.get_legend_handles_labels()
plt.legend(handles[::-1], labels[::-1], bbox_to_anchor=(1.1, 1.05))
plt.savefig('./whoson.pdf', dpi=300, bbox_inches='tight')

top_users = whoson_df.groupby('name').sum().sort_values('running', ascending=False) / len(whoson_files)
print(top_users)
top_users.to_html('top_users.html')

