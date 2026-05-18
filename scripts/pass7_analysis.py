# -*- coding: utf-8 -*-
import json
import os
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

with open(os.path.join(BASE_DIR, 'results/multi_scenario_results.json')) as f:
    data = json.load(f)

# Q1: S1 Phase II iterations
s1 = [d for d in data if d['scenario'] == 'S1_Standard']
s1p2 = [d for d in s1 if d['phase'] == 2]
iters1 = [d['n_iter_conv'] for d in s1p2]
print("S1 Phase II Iters: min={}, max={}, mean={:.2f}, sum={}".format(min(iters1), max(iters1), sum(iters1)/len(iters1), sum(iters1)))

s3 = [d for d in data if d['scenario'] == 'S3_MECBiased']
s3p2 = [d for d in s3 if d['phase'] == 2]
iters3 = [d['n_iter_conv'] for d in s3p2]
print("S3 Phase II Iters sum={}".format(sum(iters3)))

s4 = [d for d in data if d['scenario'] == 'S4_CCOverload']
s4p2 = [d for d in s4 if d['phase'] == 2]
iters4 = [d['n_iter_conv'] for d in s4p2]
print("S4 Phase II Iters sum={}".format(sum(iters4)))

# Check the first step of Phase II iterations (could be the cold-start count referenced)
print(f"S1 Phase II first step iters: {iters1[0]}")
print(f"S3 Phase II first step iters: {iters3[0]}")
print(f"S4 Phase II first step iters: {iters4[0]}")

# Q2: S2 eMBB Violations Phase II
s2 = [d for d in data if d['scenario'] == 'S2_ExtremePeak']
s2p2 = [d for d in s2 if d['phase'] == 2]
s2_embb_vio = sum(d['vio_eMBB'] for d in s2p2)
s2_total_embb_steps = len(s2p2) * 800  # 135 * 800 = 108000
steps_with_vio = sum(1 for d in s2p2 if d['vio_eMBB'] > 0)
print(f"S2 eMBB violations: {s2_embb_vio} out of {s2_total_embb_steps} UE-steps ({s2_embb_vio/s2_total_embb_steps*100:.2f}%)")
print(f"S2 steps with eMBB violations: {steps_with_vio} out of {len(s2p2)} timesteps ({steps_with_vio/len(s2p2)*100:.2f}%)")
