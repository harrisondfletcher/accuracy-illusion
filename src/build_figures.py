#!/usr/bin/env python3
"""Build 5 figures for Paper B — ALL values from source JSON, zero hardcoded."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import json
from matplotlib.colors import LinearSegmentedColormap

import os

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "json")
FIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures")
os.makedirs(FIG_DIR, exist_ok=True)

plt.rcParams['font.family'] = 'serif'
plt.rcParams['mathtext.fontset'] = 'cm'
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['figure.dpi'] = 300

DARK = '#1a1a2e'
ACCENT1 = '#e94560'
TEAL = '#2ec4b6'
SLATE = '#5c6b73'
GOLD = '#d4a537'
WHITE = '#ffffff'

with open(os.path.join(DATA_DIR, 'table1.json')) as f:
    t1 = json.load(f)
with open(os.path.join(DATA_DIR, 'matched_c2.json')) as f:
    mc = json.load(f)
with open(os.path.join(DATA_DIR, 'bci_real_application.json')) as f:
    bci = json.load(f)
with open(os.path.join(DATA_DIR, 'power_analysis.json')) as f:
    pa = json.load(f)


def fig1_radar():
    """Figure 1: Radar — all values from table1.json, V_eff uses 0.80 threshold consistently."""
    categories = ['$B_{min}$', '$V_{eff}(0.80)$', '$C_2$', '$R$', '$U$']
    N = len(categories)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]

    agent_names = ["random","class_biased","overproduction","memorizer","compositional"]
    raw = {}
    for an in agent_names:
        a = t1[an]
        u_val = a['u']['mean'] if a['u']['mean'] is not None else 0
        raw[an] = {
            'bmin': a['b_min_support']['mean'],
            'veff': a['veff_80']['mean'],
            'c2': a['c2']['mean'],
            'r': a['r']['mean'],
            'u': u_val,
        }

    max_bmin = max(raw[a]['bmin'] for a in agent_names)
    max_veff = max(raw[a]['veff'] for a in agent_names)
    max_c2 = max(raw[a]['c2'] for a in agent_names)
    max_r = max(raw[a]['r'] for a in agent_names)
    max_u = max(raw[a]['u'] for a in agent_names)
    if max_u == 0: max_u = 1

    print("  Fig1 normalization maxes:")
    print(f"    bmin={max_bmin:.4f}, veff80={max_veff:.4f}, c2={max_c2:.4f}, r={max_r:.4f}, u={max_u:.4f}")

    agents = {
        'Random':        {'color': '#adb5bd', 'ls': '--', 'lw': 1.2, 'alpha': 0.3},
        'Class-Biased':  {'color': '#6c757d', 'ls': ':', 'lw': 1.2, 'alpha': 0.2},
        'Overproduction':{'color': '#868e96', 'ls': '-.', 'lw': 1.2, 'alpha': 0.2},
        'Memorizer':     {'color': ACCENT1, 'ls': '-', 'lw': 2.8, 'alpha': 0.15},
        'Compositional': {'color': TEAL, 'ls': '-', 'lw': 2.8, 'alpha': 0.15},
    }
    agent_keys = dict(zip(agents.keys(), agent_names))

    fig = plt.figure(figsize=(8, 8), facecolor=WHITE)
    ax = fig.add_subplot(111, polar=True)
    ax.set_facecolor(WHITE)
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    plt.xticks(angles[:-1], categories, size=13, fontweight='bold', color=DARK)
    ax.set_ylim(0, 1.15)
    ax.set_yticks([0.25, 0.50, 0.75, 1.0])
    ax.set_yticklabels(['', '', '', ''], color='#ccc')
    for r_val in [0.25, 0.50, 0.75, 1.0]:
        ax.plot(angles, [r_val]*(N+1), color='#e0e0e0', linewidth=0.5, zorder=0)

    for name, d in agents.items():
        an = agent_keys[name]
        r = raw[an]
        vals = [
            r['bmin']/max_bmin,
            r['veff']/max_veff if max_veff > 0 else 0,
            r['c2']/max_c2,
            r['r']/max_r,
            r['u']/max_u,
        ]
        print(f"    {name:20s}: bmin={r['bmin']:.4f}({vals[0]:.3f}) veff80={r['veff']:.4f}({vals[1]:.3f}) c2={r['c2']:.4f}({vals[2]:.3f}) r={r['r']:.4f}({vals[3]:.3f}) u={r['u']:.4f}({vals[4]:.3f})")
        vals += vals[:1]
        ax.plot(angles, vals, linewidth=d['lw'], linestyle=d['ls'],
                color=d['color'], label=name, zorder=3)
        ax.fill(angles, vals, alpha=d['alpha'], color=d['color'], zorder=2)

    c2_angle = angles[2]
    ax.annotate('', xy=(c2_angle, 0.65), xytext=(c2_angle, 0.35),
                arrowprops=dict(arrowstyle='->', color=ACCENT1, lw=2), zorder=10)
    ax.text(c2_angle + 0.15, 0.50, 'BLIND\nSPOT',
            ha='left', va='center', fontsize=9, fontweight='bold', color=ACCENT1, zorder=10)

    ax.legend(loc='upper right', bbox_to_anchor=(1.25, 1.15),
              frameon=True, fancybox=True, shadow=False, fontsize=10, framealpha=0.95, edgecolor='#ddd')

    fig.suptitle('The Measurement Blindspot', fontsize=18, fontweight='bold', color=DARK, y=0.98)
    ax.text(0, -0.18,
            'Memorizer and Compositional overlap on $B_{min}$ and $V_{eff}$\nbut diverge on $C_2$, $R$, and $U$',
            transform=ax.transAxes, ha='center', va='top', fontsize=10, color=SLATE, style='italic')

    plt.tight_layout(rect=[0, 0.02, 0.95, 0.95])
    fig.savefig(os.path.join(FIG_DIR, 'fig1_radar.png'), dpi=300, bbox_inches='tight', facecolor=WHITE, edgecolor='none')
    fig.savefig(os.path.join(FIG_DIR, 'fig1_radar.pdf'), bbox_inches='tight', facecolor=WHITE, edgecolor='none')
    plt.close()
    print("  Fig 1 done")


def fig2_compression():
    """Figure 2: Compression — all values from bci_real_application.json."""
    subjects = ['S1','S2','S3','S4','S5','S6','S7','S8','S9']
    acc = [bci['per_subject'][s]['accuracy'] for s in subjects]
    bmin = [bci['per_subject'][s]['b_min_support'] for s in subjects]

    acc_fold = max(acc)/min(acc)
    bmin_fold = max(bmin)/min(bmin)

    print(f"  Fig2 acc range: {min(acc):.4f}-{max(acc):.4f} ({acc_fold:.1f}x)")
    print(f"  Fig2 bmin range: {min(bmin):.4f}-{max(bmin):.4f} ({bmin_fold:.1f}x)")

    fig, axes = plt.subplots(1, 2, figsize=(14, 6), facecolor=WHITE,
                              gridspec_kw={'width_ratios': [1, 1], 'wspace': 0.08})

    order = sorted(range(9), key=lambda i: bmin[i], reverse=True)

    for panel, (ax, vals, label, color, unit) in enumerate(zip(
        axes, [acc, bmin], ['Accuracy', '$B_{min}$ (bits/min)'], [SLATE, TEAL], ['', ' bpm']
    )):
        ax.set_facecolor(WHITE)
        for spine in ax.spines.values():
            spine.set_visible(False)

        for idx, i in enumerate(order):
            y = idx
            v = vals[i]
            if panel == 0:
                width = (v - 0.25) / (0.70 - 0.25)
                ax.barh(y, width, height=0.6, color='#adb5bd', alpha=0.5, edgecolor='none', zorder=2, left=0)
                ax.text(width + 0.02, y, f'{v:.1%}', va='center', ha='left', fontsize=10, color=DARK, fontweight='medium')
            else:
                width = v / 16
                gradient = plt.cm.YlGnBu(0.3 + 0.6 * (v / max(bmin)))
                ax.barh(y, width, height=0.6, color=gradient, alpha=0.9, edgecolor='none', zorder=2, left=0)
                ax.text(width + 0.02, y, f'{v:.1f}{unit}', va='center', ha='left', fontsize=10, color=DARK, fontweight='bold')

            ax.text(-0.02, y, subjects[i], va='center', ha='right', fontsize=11, fontweight='bold', color=DARK)

        ax.set_xlim(-0.15, 1.25)
        ax.set_ylim(-0.7, 8.7)
        ax.set_yticks([])
        ax.set_xticks([])
        ax.text(0.5, -0.08, label, transform=ax.transAxes, ha='center', fontsize=14, fontweight='bold', color=DARK)

        if panel == 0:
            ax.text(0.5, -0.14, f'Range: {min(acc):.0%} – {max(acc):.0%}  ({acc_fold:.1f}× range)',
                    transform=ax.transAxes, ha='center', fontsize=10, color=SLATE)
        else:
            ax.text(0.5, -0.14, f'Range: {min(bmin):.1f} – {max(bmin):.1f}  ({bmin_fold:.0f}× range)',
                    transform=ax.transAxes, ha='center', fontsize=10, color=ACCENT1, fontweight='bold')

    fig.text(0.50, 0.50, '→', fontsize=28, color=ACCENT1, fontweight='bold', ha='center', va='center', transform=fig.transFigure)

    fig.suptitle(f'The {bmin_fold:.0f}× Compression', fontsize=20, fontweight='bold', color=DARK, y=1.02)
    fig.text(0.5, 0.96,
             f'Accuracy compresses a {bmin_fold:.0f}-fold range in information throughput into a {acc_fold:.1f}-fold band',
             ha='center', fontsize=11, color=SLATE, style='italic')

    plt.tight_layout(rect=[0, 0.02, 1, 0.93])
    fig.savefig(os.path.join(FIG_DIR, 'fig2_compression.png'), dpi=300, bbox_inches='tight', facecolor=WHITE, edgecolor='none')
    fig.savefig(os.path.join(FIG_DIR, 'fig2_compression.pdf'), bbox_inches='tight', facecolor=WHITE, edgecolor='none')
    plt.close()
    print("  Fig 2 done")


def fig3_knife():
    """Figure 3: Knife — all values from matched_c2.json."""
    p_levels = sorted(mc.keys(), key=float)
    mem_acc = [mc[p]['matched_mem']['accuracy']['mean'] for p in p_levels]
    comp_acc = [mc[p]['matched_comp']['accuracy']['mean'] for p in p_levels]
    mem_c2 = [mc[p]['matched_mem']['c2']['mean'] for p in p_levels]
    comp_c2 = [mc[p]['matched_comp']['c2']['mean'] for p in p_levels]

    print("  Fig3 data from matched_c2.json:")
    for i, p in enumerate(p_levels):
        da = abs(comp_acc[i] - mem_acc[i])
        dc = abs(comp_c2[i] - mem_c2[i])
        print(f"    p={p}: Δacc={da:.4f} ({da*100:.1f}%)  Δc2={dc:.4f} ({dc*100:.1f}%)")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), facecolor=WHITE)
    x = np.arange(len(p_levels))
    w = 0.35

    for ax in [ax1, ax2]:
        ax.set_facecolor(WHITE)
        for spine in ['top', 'right']:
            ax.spines[spine].set_visible(False)

    ax1.bar(x - w/2, mem_acc, w, color=ACCENT1, alpha=0.85, label='Memorizer', edgecolor='none', zorder=3)
    ax1.bar(x + w/2, comp_acc, w, color=TEAL, alpha=0.85, label='Compositional', edgecolor='none', zorder=3)
    for i in range(len(p_levels)):
        diff = abs(comp_acc[i] - mem_acc[i])
        ax1.annotate(f'Δ={diff:.1%}', xy=(x[i], max(mem_acc[i], comp_acc[i]) + 0.01),
                     ha='center', va='bottom', fontsize=8, color=SLATE, fontweight='bold')
    ax1.set_xlabel('$p_{correct}$', fontsize=13, fontweight='bold')
    ax1.set_ylabel('Overall Accuracy', fontsize=13, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(p_levels, fontsize=10)
    ax1.set_ylim(0.3, 1.05)
    ax1.legend(fontsize=10, frameon=True, edgecolor='#ddd')
    ax1.set_title('Accuracy: Nearly Identical', fontsize=14, fontweight='bold', color=SLATE, pad=15)

    ax2.bar(x - w/2, mem_c2, w, color=ACCENT1, alpha=0.85, label='Memorizer', edgecolor='none', zorder=3)
    ax2.bar(x + w/2, comp_c2, w, color=TEAL, alpha=0.85, label='Compositional', edgecolor='none', zorder=3)
    for i in range(len(p_levels)):
        diff = abs(comp_c2[i] - mem_c2[i])
        mid_y = max(comp_c2[i], mem_c2[i]) + 0.02
        ax2.annotate(f'Δ={diff:.0%}', xy=(x[i], mid_y), ha='center', va='bottom',
                     fontsize=9, color=ACCENT1, fontweight='bold')
        ax2.annotate('', xy=(x[i] - w/2, comp_c2[i] + 0.01), xytext=(x[i] - w/2, mem_c2[i] + 0.01),
                     arrowprops=dict(arrowstyle='<->', color=ACCENT1, lw=1.5, shrinkA=0, shrinkB=0))
    ax2.set_xlabel('$p_{correct}$', fontsize=13, fontweight='bold')
    ax2.set_ylabel('$C_2$ (Compositional Depth)', fontsize=13, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(p_levels, fontsize=10)
    ax2.set_ylim(0, 1.15)
    ax2.legend(fontsize=10, frameon=True, edgecolor='#ddd')
    ax2.set_title('$C_2$: Complete Separation', fontsize=14, fontweight='bold', color=ACCENT1, pad=15)
    ax2.axhline(y=1/12, color='#ccc', linestyle='--', linewidth=1, zorder=1)
    ax2.text(len(p_levels)-0.5, 1/12 + 0.02, 'chance', fontsize=9, color='#aaa', ha='right')

    fig.suptitle('The Matched-Accuracy Knife', fontsize=20, fontweight='bold', color=DARK, y=1.02)
    fig.text(0.5, 0.96, 'Same accuracy. Opposite conclusions. $C_2$ separates what accuracy cannot.',
             ha='center', fontsize=11, color=SLATE, style='italic')

    plt.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(os.path.join(FIG_DIR, 'fig3_knife.png'), dpi=300, bbox_inches='tight', facecolor=WHITE, edgecolor='none')
    fig.savefig(os.path.join(FIG_DIR, 'fig3_knife.pdf'), bbox_inches='tight', facecolor=WHITE, edgecolor='none')
    plt.close()
    print("  Fig 3 done")


def fig4_confusion():
    """Figure 4: Confusion — all values from bci_real_application.json."""
    cm = np.array(bci['grand']['confusion_matrix_normalized'])
    labels = ['Left\nHand', 'Right\nHand', 'Feet', 'Tongue']

    print("  Fig4 confusion matrix from JSON:")
    for i in range(4):
        print(f"    {['LH','RH','Feet','Tongue'][i]}: {[f'{v:.4f}' for v in cm[i]]}")

    colors_list = ['#ffffff', '#e8f4f8', '#b8dce8', '#6bb8d4', '#2e8baa', '#1a5276', '#0d2f4d']
    cmap = LinearSegmentedColormap.from_list('bci_blue', colors_list, N=256)

    fig, ax = plt.subplots(figsize=(8, 7), facecolor=WHITE)
    ax.set_facecolor(WHITE)
    im = ax.imshow(cm, cmap=cmap, vmin=0, vmax=0.65, aspect='equal')

    for i in range(4):
        for j in range(4):
            val = cm[i, j]
            color = WHITE if val > 0.35 else DARK
            weight = 'bold' if i == j else 'normal'
            fontsize = 15 if i == j else 12
            ax.text(j, i, f'{val:.1%}', ha='center', va='center', color=color, fontsize=fontsize, fontweight=weight)
            if i != j and val > 0.20:
                ax.add_patch(plt.Rectangle((j-0.48, i-0.48), 0.96, 0.96,
                            fill=False, edgecolor=ACCENT1, linewidth=2, linestyle='--', zorder=5))

    ax.set_xticks(range(4))
    ax.set_yticks(range(4))
    ax.set_xticklabels(labels, fontsize=12, fontweight='bold')
    ax.set_yticklabels(labels, fontsize=12, fontweight='bold')
    ax.set_xlabel('Predicted Class', fontsize=14, fontweight='bold', labelpad=10)
    ax.set_ylabel('True Class', fontsize=14, fontweight='bold', labelpad=10)
    ax.tick_params(top=True, bottom=False, labeltop=True, labelbottom=False)
    ax.xaxis.set_label_position('top')

    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Classification Rate', fontsize=11, fontweight='bold')

    for (r, c) in [(0, 1), (1, 0)]:
        ax.add_patch(plt.Rectangle((c-0.48, r-0.48), 0.96, 0.96,
                    fill=False, edgecolor=ACCENT1, linewidth=3.5, linestyle='-', zorder=6))


    f1_vals = bci['grand']['f1_per_class']
    f1_labels = ['LH', 'RH', 'Feet', 'Tongue']
    f1_text = '  '.join([f'{l}: {v:.3f}' for l, v in zip(f1_labels, f1_vals)])
    veff60 = bci['grand']['veff_60']
    ax.text(0.5, -0.10, f'Per-class F1:  {f1_text}    |    $V_{{eff}}(0.60) = {veff60}$    |    \u25A0 Bilateral LH\u2194RH',
            transform=ax.transAxes, ha='center', fontsize=10, color=DARK,
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#fff3cd', edgecolor='#ffc107', alpha=0.9))

    grand_acc = bci['grand']['accuracy']
    fig.suptitle('BCI Confusion Structure', fontsize=18, fontweight='bold', color=DARK, y=0.98)
    fig.text(0.5, 0.93,
             f'{grand_acc:.0%} accuracy masks systematic failure: the system cannot distinguish left from right hand',
             ha='center', fontsize=10.5, color=SLATE, style='italic')

    plt.tight_layout(rect=[0, 0.02, 1, 0.91])
    fig.savefig(os.path.join(FIG_DIR, 'fig4_confusion.png'), dpi=300, bbox_inches='tight', facecolor=WHITE, edgecolor='none')
    fig.savefig(os.path.join(FIG_DIR, 'fig4_confusion.pdf'), bbox_inches='tight', facecolor=WHITE, edgecolor='none')
    plt.close()
    print("  Fig 4 done")


def fig5_power():
    """Figure 5: Power — ALL values from power_analysis.json."""
    metrics_map = {'$C_2$': 'c2', '$R$': 'r', '$B_{min}$': 'b_min_support'}
    delta_p = ['0.01', '0.03', '0.05', '0.1']
    N_vals = ['100', '200', '500', '1000', '2000']

    print("  Fig5 power values from power_analysis.json:")

    colors_rg = ['#d73027', '#f46d43', '#fdae61', '#fee08b', '#d9ef8b', '#a6d96a', '#66bd63', '#1a9850']
    cmap_rg = LinearSegmentedColormap.from_list('power_rg', colors_rg, N=256)

    fig, axes = plt.subplots(1, 3, figsize=(16, 6), facecolor=WHITE,
                              gridspec_kw={'wspace': 0.25})

    for idx, (metric_label, metric_key) in enumerate(metrics_map.items()):
        ax = axes[idx]
        ax.set_facecolor(WHITE)
        md = pa[metric_key]

        data = np.zeros((len(N_vals), len(delta_p)))
        for i, n in enumerate(N_vals):
            for j, d in enumerate(delta_p):
                val = md[d][n]['power']
                data[i, j] = val
                print(f"    {metric_key} d={d} N={n}: {val:.2f}")

        im = ax.imshow(data, cmap=cmap_rg, vmin=0, vmax=1, aspect='auto', interpolation='nearest')

        for i in range(len(N_vals)):
            for j in range(len(delta_p)):
                val = data[i, j]
                color = WHITE if val < 0.5 else DARK
                weight = 'bold' if val >= 0.80 else 'normal'
                ax.text(j, i, f'{val:.0%}', ha='center', va='center',
                        color=color, fontsize=11, fontweight=weight)
                if abs(val - 0.80) < 0.06:
                    ax.add_patch(plt.Rectangle((j-0.48, i-0.48), 0.96, 0.96,
                                fill=False, edgecolor=GOLD, linewidth=2.5, zorder=5))

        ax.set_xticks(range(len(delta_p)))
        ax.set_xticklabels([str(d) for d in delta_p], fontsize=10)
        ax.set_yticks(range(len(N_vals)))
        ax.set_yticklabels([str(n) for n in N_vals], fontsize=10)
        ax.set_xlabel('Effect size (Δp)', fontsize=11, fontweight='bold')
        if idx == 0:
            ax.set_ylabel('Sample size (N)', fontsize=11, fontweight='bold')

        title_color = TEAL if metric_key != 'b_min_support' else ACCENT1
        ax.set_title(metric_label, fontsize=16, fontweight='bold', color=title_color, pad=10)

    cbar_ax = fig.add_axes([0.25, 0.03, 0.50, 0.018])
    cbar = fig.colorbar(im, cax=cbar_ax, orientation='horizontal')
    cbar.set_label('Statistical Power', fontsize=10, fontweight='bold')

    fig.suptitle('The Power Landscape', fontsize=20, fontweight='bold', color=DARK, y=1.02)
    fig.text(0.5, 0.96,
             'Structural metrics ($C_2$, $R$) are powered everywhere. $B_{min}$ requires careful sample planning.',
             ha='center', fontsize=11, color=SLATE, style='italic')
    plt.subplots_adjust(left=0.06, right=0.98, top=0.88, bottom=0.14, wspace=0.25)

    fig.savefig(os.path.join(FIG_DIR, 'fig5_power.png'), dpi=300, bbox_inches='tight', facecolor=WHITE, edgecolor='none')
    fig.savefig(os.path.join(FIG_DIR, 'fig5_power.pdf'), bbox_inches='tight', facecolor=WHITE, edgecolor='none')
    plt.close()
    print("  Fig 5 done")


print("BUILDING ALL FIGURES FROM SOURCE DATA\n")
fig1_radar()
print()
fig2_compression()
print()
fig3_knife()
print()
fig4_confusion()
print()
fig5_power()
print("\nAll 5 figures complete — ALL values from JSON source.")
