import os
import re
import io
import time
import shutil
import random
import datetime
import tempfile
import subprocess
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# =============================================================================
# STREAMLIT CONFIG
# =============================================================================
st.set_page_config(
    page_title="QTL-seq / BSA Analysis",
    page_icon="🧬",
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500&display=swap');

:root {
    --sky:    #0EA5E9;
    --crimson:#E11D48;
    --orange: #F97316;
    --lime:   #22C55E;
    --violet: #7C3AED;
    --ink:    #12172B;
    --mist:   #64748B;
}

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.main { background:#F8F9FF; }
.block-container { max-width:1500px; padding-top:1.2rem; }
h1, h2, h3 { font-family: 'Space Grotesk', sans-serif !important; }

/* ---------- Hero ---------- */
@keyframes gradientShift {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
.header {
    position: relative;
    overflow: hidden;
    background: linear-gradient(115deg, var(--violet), var(--crimson) 35%, var(--orange) 65%, var(--sky));
    background-size: 300% 300%;
    animation: gradientShift 14s ease infinite;
    border-radius: 16px;
    padding: 30px 34px;
    margin-bottom: 22px;
    box-shadow: 0 12px 32px -8px rgba(124, 58, 237, 0.45);
}
.header h1 {
    margin: 0 0 8px; color:#FFFFFF !important; font-size: 2.15rem;
    font-weight: 700; letter-spacing: -0.5px;
    text-shadow: 0 2px 12px rgba(0,0,0,0.18);
}
.header p { margin:3px 0; color: rgba(255,255,255,0.92); font-size: 0.98rem; font-weight: 500; }
.header .tag {
    display:inline-block; margin-top:12px; margin-right:8px;
    background: rgba(255,255,255,0.18); backdrop-filter: blur(6px);
    border: 1px solid rgba(255,255,255,0.35); color:#fff;
    padding: 4px 12px; border-radius: 999px; font-size: 0.76rem; font-weight:600;
}

/* ---------- Section labels ---------- */
.section {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.95rem; font-weight: 700; color: var(--ink);
    margin: 22px 0 14px; padding-left: 12px;
    border-left: 4px solid var(--violet);
}
.small-note { color: var(--mist); font-size:.84rem; }

/* ---------- Step chips (getting started) ---------- */
.steps-row { display:flex; gap:12px; flex-wrap:wrap; margin-bottom: 6px; }
.step-chip {
    flex:1; min-width:190px; background:#fff; border-radius:14px;
    padding:16px 18px; border:1px solid #E7E9F5;
    border-top:4px solid var(--accent, var(--violet));
    box-shadow: 0 2px 10px rgba(18,23,43,0.04);
    transition: transform .18s ease, box-shadow .18s ease;
}
.step-chip:hover { transform: translateY(-4px); box-shadow: 0 10px 24px rgba(18,23,43,0.12); }
.step-chip .num {
    display:inline-flex; align-items:center; justify-content:center;
    width:26px; height:26px; border-radius:50%; color:#fff; font-weight:700;
    font-size:0.78rem; background: var(--accent, var(--violet)); margin-bottom:8px;
}
.step-chip h4 { margin:2px 0 4px; font-family:'Space Grotesk',sans-serif; font-size:0.95rem; color:var(--ink); }
.step-chip p { margin:0; font-size:0.8rem; color: var(--mist); line-height:1.35; }

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #14172E 0%, #1B1F3B 100%);
}
[data-testid="stSidebar"] * { color: #E7E9F5 !important; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    font-family:'Space Grotesk', sans-serif !important; color:#fff !important;
}
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.14); }
[data-testid="stFileUploaderDropzone"] {
    background: rgba(124,58,237,0.12) !important;
    border: 1.5px dashed #A78BFA !important; border-radius: 12px !important;
    transition: background .15s ease, border-color .15s ease;
}
[data-testid="stFileUploaderDropzone"]:hover {
    background: rgba(124,58,237,0.24) !important; border-color: #F97316 !important;
}

/* ---------- Buttons ---------- */
.stButton>button, .stDownloadButton>button {
    background: linear-gradient(100deg, var(--violet), var(--crimson));
    color: #fff !important; border: none !important; border-radius: 10px !important;
    font-weight: 700 !important; letter-spacing: .2px;
    box-shadow: 0 4px 14px rgba(124,58,237,0.35);
    transition: transform .15s ease, box-shadow .15s ease, filter .15s ease;
}
.stButton>button:hover, .stDownloadButton>button:hover {
    transform: translateY(-2px) scale(1.01);
    box-shadow: 0 8px 22px rgba(225,29,72,0.4);
    filter: brightness(1.06);
}
.stButton>button:active, .stDownloadButton>button:active { transform: translateY(0) scale(0.99); }

/* ---------- Metrics ---------- */
[data-testid="stMetric"] {
    background:#fff; border-radius:14px; padding:14px 16px 10px;
    border:1px solid #E7E9F5; border-bottom:4px solid var(--sky);
    box-shadow: 0 2px 10px rgba(18,23,43,0.05);
    transition: transform .15s ease, box-shadow .15s ease;
}
[data-testid="stMetric"]:hover { transform: translateY(-3px); box-shadow: 0 10px 22px rgba(18,23,43,0.1); }
[data-testid="stMetricLabel"] { color: var(--mist) !important; font-weight:600 !important; }
[data-testid="stMetricValue"] { color: var(--ink) !important; font-family:'Space Grotesk',sans-serif !important; }

/* ---------- Tabs ---------- */
[data-baseweb="tab-list"] { gap: 6px; border-bottom: 1px solid #E7E9F5; }
[data-baseweb="tab"] {
    border-radius: 10px 10px 0 0 !important; font-weight:600 !important;
    padding: 8px 16px !important; transition: background .15s ease, color .15s ease;
}
[data-baseweb="tab"]:hover { background: rgba(124,58,237,0.08); }
[aria-selected="true"][data-baseweb="tab"] {
    background: linear-gradient(100deg, var(--violet), var(--crimson)) !important;
    color: #fff !important;
}

/* ---------- Expander / dataframe / alerts ---------- */
[data-testid="stExpander"] {
    border-radius: 12px !important; border:1px solid #E7E9F5 !important; overflow:hidden;
}
[data-testid="stDataFrame"] { border-radius: 12px; overflow:hidden; border:1px solid #E7E9F5; }
div[data-baseweb="notification"] { border-radius: 12px !important; }

/* ---------- Slider accent ---------- */
[data-testid="stSlider"] [role="slider"] { background: var(--orange) !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header">
<h1>🧬 QTL-seq / Bulk Segregant Analysis Pipeline</h1>
<p>QTL-seq · Δ(SNP-index) · sliding-window analysis · confidence intervals</p>
<p>Automated QTL-seq with manual BSA fallback · interactive chromosome plots · downloadable results</p>
<span class="tag">⚡ Automated pipeline</span>
<span class="tag">📊 Live chromosome plots</span>
<span class="tag">📦 One-click downloads</span>
</div>
""", unsafe_allow_html=True)


# =============================================================================
# TOOL DISCOVERY
# =============================================================================
def find_executable(name):
    """Find a command in PATH and common conda locations."""
    found = shutil.which(name)
    if found:
        return found

    candidates = [
        f"/usr/local/bin/{name}",
        f"/opt/conda/bin/{name}",
        f"/usr/bin/{name}",
        f"/usr/local/envs/qtlseq/bin/{name}",
        f"/opt/conda/envs/qtlseq/bin/{name}",
    ]
    for p in candidates:
        if os.path.exists(p) and os.access(p, os.X_OK):
            return p

    # qtlseq is commonly installed inside a conda environment.
    conda = shutil.which("conda") or "/usr/local/bin/conda"
    if os.path.exists(conda):
        try:
            r = subprocess.run(
                [conda, "run", "-n", "qtlseq", "which", name],
                capture_output=True, text=True, timeout=30
            )
            if r.returncode == 0 and r.stdout.strip():
                p = r.stdout.strip().splitlines()[-1]
                if os.path.exists(p):
                    return p
        except Exception:
            pass
    return None


def command_for(name):
    """Return a runnable command list for a tool."""
    direct = find_executable(name)
    if direct:
        return [direct]

    conda = shutil.which("conda") or "/usr/local/bin/conda"
    if os.path.exists(conda):
        try:
            r = subprocess.run(
                [conda, "run", "-n", "qtlseq", "which", name],
                capture_output=True, text=True, timeout=30
            )
            if r.returncode == 0:
                return [conda, "run", "-n", "qtlseq", name]
        except Exception:
            pass
    return None


def run_cmd(cmd, timeout=1800, cwd=None):
    return subprocess.run(
        cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd
    )


# =============================================================================
# FILE HANDLING
# =============================================================================
def save_uploaded(uploaded_file, directory):
    if uploaded_file is None:
        return None
    path = os.path.join(directory, os.path.basename(uploaded_file.name))
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return path


def ensure_bam_index(bam):
    samtools = command_for("samtools")
    if not samtools:
        return False, "samtools is not installed."

    bai = bam + ".bai"
    if os.path.exists(bai):
        return True, f"Index found: {os.path.basename(bai)}"

    r = run_cmd(samtools + ["index", bam], timeout=1800)
    if r.returncode != 0:
        return False, r.stderr.strip() or "samtools index failed."
    return True, f"Created index: {os.path.basename(bai)}"


def validate_bam(bam):
    samtools = command_for("samtools")
    if not samtools:
        return False, "samtools is not installed."

    r = run_cmd(samtools + ["quickcheck", bam], timeout=300)
    if r.returncode != 0:
        return False, r.stderr.strip() or "BAM failed samtools quickcheck."
    return True, "BAM passed samtools quickcheck."


def reference_length(ref):
    samtools = command_for("samtools")
    if not samtools:
        return None

    r = run_cmd(samtools + ["faidx", ref], timeout=600)
    if r.returncode != 0:
        return None

    fai = ref + ".fai"
    if not os.path.exists(fai):
        return None

    total = 0
    with open(fai, "r", encoding="utf-8") as f:
        for line in f:
            fields = line.rstrip("\n").split("\t")
            if len(fields) >= 2:
                try:
                    total += int(fields[1])
                except ValueError:
                    pass
    return total or None


# =============================================================================
# QTL-seq / MANUAL BSA CORE
# =============================================================================
def sliding_window_analysis(df, window_size, step_size):
    windows = []

    for chrom in df["CHROM"].unique():
        chrom_data = df[df["CHROM"] == chrom].copy()
        if len(chrom_data) == 0:
            continue

        chrom_data = chrom_data.sort_values("POS")
        max_pos = chrom_data["POS"].max()
        min_pos = chrom_data["POS"].min()
        start = min_pos

        while start <= max_pos:
            end = start + window_size
            window_snps = chrom_data[
                (chrom_data["POS"] >= start) &
                (chrom_data["POS"] < end)
            ]

            if len(window_snps) >= 1:
                mean_delta = window_snps["deltaSNP"].mean()
                std_delta = (
                    window_snps["deltaSNP"].std()
                    if len(window_snps) > 1 else 0
                )
                n_snps = len(window_snps)
                se = std_delta / np.sqrt(n_snps) if n_snps > 1 else 0

                windows.append({
                    "CHROM": chrom,
                    "START": start,
                    "END": end,
                    "WINDOW_CENTER": start + window_size // 2,
                    "N_SNPS": n_snps,
                    "deltaSNP": mean_delta,
                    "tricubeDeltaSNP": mean_delta,
                    "CI_95": 1.96 * se,
                    "CI_99": 2.58 * se,
                    "STD": std_delta,
                })

            start += step_size

        # Preserve notebook behavior for chromosomes without generated windows.
        if not any(w["CHROM"] == chrom for w in windows):
            windows.append({
                "CHROM": chrom,
                "START": min_pos,
                "END": min_pos + window_size,
                "WINDOW_CENTER": min_pos + window_size // 2,
                "N_SNPS": 0,
                "deltaSNP": 0,
                "tricubeDeltaSNP": 0,
                "CI_95": 0,
                "CI_99": 0,
                "STD": 0,
            })

    return pd.DataFrame(windows)


def manual_bsa(ref, parent_bam, bulk1_bam, bulk2_bam,
               manual_dir, min_total_depth, ref_allele_freq,
               window_size, step_size, progress=None):
    samtools = command_for("samtools")
    if not samtools:
        raise RuntimeError(
            "samtools is required for manual BSA analysis but was not found."
        )

    mpileup_file = os.path.join(manual_dir, "all_samples.mpileup")

    if progress:
        progress("Step 1/3: generating mpileup...")

    mpileup_cmd = samtools + [
        "mpileup", "-f", ref, "-q", "20", "-Q", "20",
        parent_bam, bulk1_bam, bulk2_bam
    ]

    with open(mpileup_file, "w", encoding="utf-8") as f:
        result = subprocess.run(
            mpileup_cmd, stdout=f, stderr=subprocess.PIPE,
            text=True, timeout=3600
        )

    if result.returncode != 0:
        raise RuntimeError(f"Mpileup failed: {result.stderr}")

    if progress:
        progress("Step 2/3: parsing mpileup and calculating SNP indices...")

    def parse_mpileup_line(line):
        fields = line.strip().split("\t")
        if len(fields) < 12:
            return None

        try:
            chrom, pos, ref_base = fields[0], int(fields[1]), fields[2].upper()
        except Exception:
            return None

        samples = []
        for i in range(3):
            start_idx = 3 + i * 3
            if start_idx + 2 >= len(fields):
                return None

            try:
                depth = int(fields[start_idx])
            except Exception:
                return None

            reads = fields[start_idx + 1]

            if depth < 10:
                return None

            # Preserve the notebook's original SNP-index logic:
            # reference bases are represented by . and ,; all remaining
            # observations are treated as alternative observations.
            ref_count = reads.count(".") + reads.count(",")
            alt_count = depth - ref_count

            if depth > 0:
                ref_freq = ref_count / depth
                alt_freq = alt_count / depth
            else:
                ref_freq = alt_freq = 0

            samples.append({
                "depth": depth,
                "ref_count": ref_count,
                "alt_count": alt_count,
                "ref_freq": ref_freq,
                "alt_freq": alt_freq,
            })

        return {
            "chrom": chrom,
            "pos": pos,
            "ref_base": ref_base,
            "parent": samples[0],
            "bulk1": samples[1],
            "bulk2": samples[2],
        }

    snp_data = []
    with open(mpileup_file, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f):
            parsed = parse_mpileup_line(line)
            if not parsed:
                continue

            bulk1_snp_index = parsed["bulk1"]["alt_freq"]
            bulk2_snp_index = parsed["bulk2"]["alt_freq"]
            delta_snp_index = bulk1_snp_index - bulk2_snp_index

            total_depth = (
                parsed["bulk1"]["depth"] + parsed["bulk2"]["depth"]
            )
            parent_ref_freq = parsed["parent"]["ref_freq"]

            if (
                total_depth >= min_total_depth and
                parent_ref_freq >= ref_allele_freq
            ):
                snp_data.append({
                    "CHROM": parsed["chrom"],
                    "POS": parsed["pos"],
                    "REF": parsed["ref_base"],
                    "PARENT_DEPTH": parsed["parent"]["depth"],
                    "PARENT_REF_FREQ": parent_ref_freq,
                    "BULK1_DEPTH": parsed["bulk1"]["depth"],
                    "BULK1_SNP_INDEX": bulk1_snp_index,
                    "BULK2_DEPTH": parsed["bulk2"]["depth"],
                    "BULK2_SNP_INDEX": bulk2_snp_index,
                    "deltaSNP": delta_snp_index,
                    "TOTAL_DEPTH": total_depth,
                })

            if progress and line_num and line_num % 100000 == 0:
                progress(f"Parsed {line_num:,} mpileup records...")

    if len(snp_data) == 0:
        raise RuntimeError("No SNPs passed the quality filters.")

    snp_df = pd.DataFrame(snp_data)

    if progress:
        progress(
            f"Step 3/3: performing sliding-window analysis on "
            f"{len(snp_df):,} high-quality SNPs..."
        )

    window_df = sliding_window_analysis(
        snp_df, window_size=window_size, step_size=step_size
    )

    snp_path = os.path.join(manual_dir, "snp_data.csv")
    window_path = os.path.join(manual_dir, "window_data.csv")
    snp_df.to_csv(snp_path, index=False)
    window_df.to_csv(window_path, index=False)

    return snp_df, window_df


def locate_result_files(work_dir):
    """Find SNP/window output tables produced by qtlseq or manual analysis."""
    output_files = []
    for root, _, files_list in os.walk(work_dir):
        for filename in files_list:
            lower = filename.lower()
            if (
                filename.endswith((".tsv", ".csv", ".txt"))
                and any(x in lower for x in ["snp", "window", "sliding"])
            ):
                output_files.append(os.path.join(root, filename))

    snp_df = None
    window_df = None

    # Prefer explicit known QTL-seq filenames.
    preferred_snp = [
        p for p in output_files
        if os.path.basename(p).lower() in {
            "snp_index.tsv", "snp_index.txt", "snp_data.csv"
        }
    ]
    preferred_window = [
        p for p in output_files
        if os.path.basename(p).lower() in {
            "sliding_window.tsv", "sliding_window.txt",
            "window_data.csv"
        }
    ]

    def read_table(path):
        return pd.read_csv(
            path,
            sep="\t" if path.lower().endswith(".tsv") else ","
        )

    for path in preferred_snp + output_files:
        try:
            df = read_table(path)
            if len(df.columns) >= 2 and snp_df is None:
                snp_df = df
        except Exception:
            pass

    for path in preferred_window + output_files:
        try:
            df = read_table(path)
            if len(df.columns) >= 2 and window_df is None:
                window_df = df
        except Exception:
            pass

    return snp_df, window_df, output_files


def standardize_results(snp_df, window_df):
    if snp_df is None or window_df is None:
        raise RuntimeError("Could not load both SNP and sliding-window results.")

    for df in [snp_df, window_df]:
        df.columns = [str(c).strip() for c in df.columns]

    # Enhanced duplicate POS handling from the notebook.
    for df_name, df in [("snp", snp_df), ("window", window_df)]:
        pos_candidates = [
            col for col in df.columns
            if any(
                x in col.lower()
                for x in ["pos", "position", "start", "window_center"]
            )
        ]

        if len(pos_candidates) > 1:
            preferred = next(
                (
                    col for col in
                    ["WINDOW_CENTER", "START", "POS"]
                    if col in pos_candidates
                ),
                pos_candidates[0]
            )
            if preferred != "POS":
                df["POS"] = df[preferred]
                df.drop(preferred, axis=1, inplace=True)

            for col in pos_candidates:
                if col != preferred and col in df.columns:
                    df.drop(col, axis=1, inplace=True)

        elif len(pos_candidates) == 1 and pos_candidates[0] != "POS":
            df["POS"] = df[pos_candidates[0]]
            df.drop(pos_candidates[0], axis=1, inplace=True)

        elif len(pos_candidates) == 0:
            df["POS"] = range(1, len(df) + 1)

    mapping = {
        "POSI": "POS",
        "position": "POS",
        "START": "POS",
        "WINDOW_CENTER": "POS",
        "DELTA SNP-index": "deltaSNP",
        "delta_snp": "deltaSNP",
        "DELTA_SNP_INDEX": "deltaSNP",
        "MEAN DELTA SNP-index": "tricubeDeltaSNP",
        "mean_delta_snp": "tricubeDeltaSNP",
        "MEAN p95": "CI_95",
        "mean_p95": "CI_95",
        "p95": "CI_95",
        "MEAN p99": "CI_99",
        "mean_p99": "CI_99",
        "p99": "CI_99",
    }

    for df in [snp_df, window_df]:
        for old_name, new_name in mapping.items():
            if old_name in df.columns and new_name not in df.columns:
                df.rename(columns={old_name: new_name}, inplace=True)

    for name, df in [("snp", snp_df), ("window", window_df)]:
        if "CHROM" not in df.columns:
            candidates = [c for c in df.columns if "chrom" in c.lower()]
            if candidates:
                df["CHROM"] = df[candidates[0]]
            else:
                df["CHROM"] = "1"

        df["POS"] = pd.to_numeric(df["POS"], errors="coerce")
        if df["POS"].isna().all():
            df["POS"] = range(1, len(df) + 1)

        df["POS"] = df["POS"].fillna(method="ffill").fillna(1)
        df["POS_Mb"] = df["POS"] / 1e6

    return snp_df, window_df


def create_plot(snp_df, window_df):
    chroms = sorted(window_df["CHROM"].dropna().unique(), key=str)
    n_chroms = len(chroms)
    ncols = min(4, max(1, n_chroms))
    nrows = (n_chroms + ncols - 1) // ncols

    fig = make_subplots(
        rows=nrows,
        cols=ncols,
        subplot_titles=[f"Chromosome {chrom}" for chrom in chroms],
        horizontal_spacing=0.08,
        vertical_spacing=0.10,
    )

    colors = {
        "raw": "#87CEEB",
        "smooth": "#DC143C",
        "ci95": "#FF8C00",
        "ci99": "#32CD32",
    }

    for i, chrom in enumerate(chroms):
        row = i // ncols + 1
        col = i % ncols + 1

        snp_chrom = (
            snp_df[snp_df["CHROM"] == chrom]
            if "deltaSNP" in snp_df.columns
            else pd.DataFrame()
        )
        win_chrom = window_df[window_df["CHROM"] == chrom]

        if len(snp_chrom) > 0 and "deltaSNP" in snp_chrom.columns:
            fig.add_trace(
                go.Scatter(
                    x=snp_chrom["POS_Mb"],
                    y=snp_chrom["deltaSNP"],
                    mode="markers",
                    name="Raw Δ(SNP-index)",
                    marker=dict(
                        size=1.5,
                        color=colors["raw"],
                        opacity=0.5,
                    ),
                    showlegend=(i == 0),
                    legendgroup="raw",
                ),
                row=row, col=col,
            )

        smooth_col = next(
            (
                c for c in ["tricubeDeltaSNP", "deltaSNP"]
                if c in win_chrom.columns
            ),
            None,
        )

        if len(win_chrom) > 0 and smooth_col:
            fig.add_trace(
                go.Scatter(
                    x=win_chrom["POS_Mb"],
                    y=win_chrom[smooth_col],
                    mode="lines",
                    name="Smoothed Δ(SNP-index)",
                    line=dict(color=colors["smooth"], width=2.5),
                    showlegend=(i == 0),
                    legendgroup="smooth",
                ),
                row=row, col=col,
            )

        for ci_col, color, name in [
            ("CI_95", colors["ci95"], "95% CI"),
            ("CI_99", colors["ci99"], "99% CI"),
        ]:
            if ci_col in win_chrom.columns:
                for sign, show_legend in [(1, i == 0), (-1, False)]:
                    fig.add_trace(
                        go.Scatter(
                            x=win_chrom["POS_Mb"],
                            y=sign * pd.to_numeric(
                                win_chrom[ci_col], errors="coerce"
                            ),
                            mode="lines",
                            name=name,
                            line=dict(
                                color=color,
                                width=1.5,
                                dash="dash",
                            ),
                            showlegend=show_legend,
                            legendgroup=f"ci_{ci_col}",
                        ),
                        row=row, col=col,
                    )

        for y_val, style in [
            (0, dict(color="black", width=2)),
            (0.5, dict(color="gray", width=1, dash="dot")),
            (-0.5, dict(color="gray", width=1, dash="dot")),
        ]:
            fig.add_hline(y=y_val, line=style, row=row, col=col)

    fig.update_layout(
        height=max(300 * nrows, 600),
        width=1200,
        title_text="QTL-seq Analysis: Δ(SNP-index) Manhattan Plot",
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.98,
            xanchor="left",
            x=1.02,
        ),
        template="plotly_white",
    )
    fig.update_xaxes(title_text="Position (Mb)", tickformat=".3f")
    fig.update_yaxes(title_text="Δ(SNP-index)", range=[-1.1, 1.1])

    return fig


def make_summary(snp_df, window_df, ref_len, n1, n2,
                 window_size, step_size, min_depth, ref_freq):
    chroms = sorted(window_df["CHROM"].dropna().unique(), key=str)
    lines = [
        "QTL-seq / BSA Analysis Summary",
        "=" * 55,
        "",
        f"Analysis completed: {datetime.datetime.now():%Y-%m-%d %H:%M:%S}",
        f"Total SNPs analyzed: {len(snp_df)}",
        f"Total windows: {len(window_df)}",
        f"Chromosomes: {', '.join(map(str, chroms))}",
        f"Reference length: {ref_len if ref_len else 'Unknown'} bases",
        "",
        "Parameters Used:",
        f"  Sample sizes: N1={n1}, N2={n2}",
        f"  Window size: {window_size} bp",
        f"  Step size: {step_size} bp",
        f"  Minimum depth filter: {min_depth}",
        f"  Reference allele frequency filter: {ref_freq}",
        "",
        "Chromosome Statistics:",
    ]

    smooth_col = (
        "tricubeDeltaSNP"
        if "tricubeDeltaSNP" in window_df.columns
        else "deltaSNP"
    )

    for chrom in chroms:
        cw = window_df[window_df["CHROM"] == chrom]
        if len(cw) and smooth_col in cw.columns:
            vals = pd.to_numeric(cw[smooth_col], errors="coerce").dropna()
            if len(vals):
                lines.extend([
                    f"  Chromosome {chrom}:",
                    f"    Δ(SNP-index) range: [{vals.min():.3f}, {vals.max():.3f}]",
                    f"    Maximum absolute value: {max(abs(vals.min()), abs(vals.max())):.3f}",
                    f"    Number of windows: {len(cw)}",
                ])

    lines.extend([
        "",
        "Interpretation Guide:",
        "• Positive Δ(SNP-index) values indicate QTL regions favoring bulk 1 phenotype",
        "• Negative Δ(SNP-index) values indicate QTL regions favoring bulk 2 phenotype",
        "• Look for regions where smoothed values exceed confidence intervals",
        "• Higher absolute values indicate stronger QTL effects",
        "• Focus on regions with |Δ(SNP-index)| > 0.3 for potential QTL",
    ])

    return "\n".join(lines)


def create_outputs(snp_df, window_df, fig, outdir, ref_len,
                   n1, n2, window_size, step_size, min_depth, ref_freq):
    os.makedirs(outdir, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    plot_file = os.path.join(
        outdir, f"qtlseq_manhattan_plot_{timestamp}.html"
    )
    snp_file = os.path.join(
        outdir, f"qtlseq_snp_data_{timestamp}.csv"
    )
    window_file = os.path.join(
        outdir, f"qtlseq_window_data_{timestamp}.csv"
    )
    summary_file = os.path.join(
        outdir, f"qtlseq_analysis_summary_{timestamp}.txt"
    )
    combined_file = os.path.join(
        outdir, f"qtlseq_combined_results_{timestamp}.csv"
    )
    zip_file = os.path.join(
        outdir, f"qtlseq_results_{timestamp}.zip"
    )

    fig.write_html(plot_file)
    snp_df.to_csv(snp_file, index=False)
    window_df.to_csv(window_file, index=False)

    summary = make_summary(
        snp_df, window_df, ref_len, n1, n2,
        window_size, step_size, min_depth, ref_freq
    )
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(summary)

    combined = window_df.copy()
    combined["Analysis_Type"] = "Sliding_Window"

    if "deltaSNP" in snp_df.columns:
        top_snps = snp_df.copy()
        top_snps["abs_delta"] = abs(
            pd.to_numeric(top_snps["deltaSNP"], errors="coerce")
        )
        top_snps = top_snps.nlargest(
            min(1000, len(top_snps)), "abs_delta"
        )
        top_snps["Analysis_Type"] = "Individual_SNP"
        top_snps.drop("abs_delta", axis=1, inplace=True)

        common = ["CHROM", "POS", "POS_Mb", "Analysis_Type"]
        snp_cols = [c for c in top_snps.columns if c not in common]
        win_cols = [c for c in combined.columns if c not in common]

        for col in win_cols:
            if col not in top_snps.columns:
                top_snps[col] = np.nan
        for col in snp_cols:
            if col not in combined.columns:
                combined[col] = np.nan

        combined = pd.concat(
            [combined, top_snps],
            ignore_index=True,
            sort=False,
        )

    combined.to_csv(combined_file, index=False)

    output_files = [
        plot_file, snp_file, window_file, summary_file, combined_file
    ]
    with zipfile.ZipFile(
        zip_file, "w", zipfile.ZIP_DEFLATED
    ) as zf:
        for file in output_files:
            if os.path.exists(file):
                zf.write(file, os.path.basename(file))

    return {
        "plot": plot_file,
        "snp": snp_file,
        "window": window_file,
        "summary": summary_file,
        "combined": combined_file,
        "zip": zip_file,
        "summary_text": summary,
    }


# =============================================================================
# SIDEBAR INPUTS
# =============================================================================
st.sidebar.header("Input Files")

ref_upload = st.sidebar.file_uploader(
    "Reference FASTA",
    type=["fasta", "fa", "fna"],
    help="Reference genome used for mpileup/QTL-seq."
)
parent_upload = st.sidebar.file_uploader(
    "Parent sorted BAM",
    type=["bam"],
)
bulk1_upload = st.sidebar.file_uploader(
    "Bulk 1 sorted BAM",
    type=["bam"],
)
bulk2_upload = st.sidebar.file_uploader(
    "Bulk 2 sorted BAM",
    type=["bam"],
)

st.sidebar.markdown("---")
st.sidebar.header("Analysis Parameters")

n1 = st.sidebar.number_input(
    "Bulk 1 sample size (N1)", min_value=1, value=20, step=1
)
n2 = st.sidebar.number_input(
    "Bulk 2 sample size (N2)", min_value=1, value=20, step=1
)

min_total_depth = st.sidebar.number_input(
    "Minimum total bulk depth",
    min_value=1, value=50, step=5,
    help="Original notebook default: 50."
)
ref_allele_freq = st.sidebar.slider(
    "Minimum parent reference allele frequency",
    min_value=0.0, max_value=1.0, value=0.10, step=0.01
)

st.sidebar.markdown("---")
st.sidebar.header("Sliding Window")

window_kb = st.sidebar.number_input(
    "Window size (kb)",
    min_value=1, value=500, step=10
)
step_kb = st.sidebar.number_input(
    "Step size (kb)",
    min_value=1, value=50, step=5
)

use_reference_adaptive = st.sidebar.checkbox(
    "Use reference-length adaptive window",
    value=False,
    help="The original notebook adapted the window to reference length. "
         "When enabled, window=max(20, reference_length/50) and "
         "step=max(2, window/10)."
)

strategy = st.sidebar.radio(
    "Analysis strategy",
    [
        "QTL-seq first → manual BSA fallback",
        "Manual BSA only",
        "QTL-seq only",
    ],
)

run_button = st.sidebar.button(
    "Run QTL-seq / BSA Analysis",
    type="primary",
    use_container_width=True,
)


# =============================================================================
# MAIN APP
# =============================================================================
st.markdown(
    '<div class="section">Pipeline status</div>',
    unsafe_allow_html=True
)

tool_cols = st.columns(3)
for col, name in zip(tool_cols, ["samtools", "qtlseq", "conda"]):
    with col:
        if name == "conda":
            found = shutil.which("conda") or (
                "/usr/local/bin/conda"
                if os.path.exists("/usr/local/bin/conda") else None
            )
        else:
            found = find_executable(name)
        if found:
            st.success(f"{name}: available")
        else:
            st.warning(f"{name}: not found")

st.markdown(
    '<p class="small-note">'
    "This Streamlit version replaces the notebook's Colab upload, shell-magic, "
    "Conda setup, and download cells. The QTL-seq/BSA analysis logic is retained."
    "</p>",
    unsafe_allow_html=True,
)

if run_button:
    if not all([ref_upload, parent_upload, bulk1_upload, bulk2_upload]):
        st.error(
            "Please upload all four required files: reference FASTA, "
            "parent sorted BAM, bulk 1 sorted BAM, and bulk 2 sorted BAM."
        )
        st.stop()

    run_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    run_id += "_" + str(random.randint(10000, 99999))
    work_dir = tempfile.mkdtemp(prefix=f"qtl_analysis_{run_id}_")
    input_dir = os.path.join(work_dir, "inputs")
    os.makedirs(input_dir, exist_ok=True)

    ref = save_uploaded(ref_upload, input_dir)
    parent_bam = save_uploaded(parent_upload, input_dir)
    bulk1_bam = save_uploaded(bulk1_upload, input_dir)
    bulk2_bam = save_uploaded(bulk2_upload, input_dir)

    progress_box = st.empty()
    log_box = st.empty()
    logs = []

    def progress(message):
        logs.append(message)
        progress_box.info(message)
        log_box.code("\n".join(logs[-20:]), language="text")

    try:
        progress("Validating input files...")

        for bam in [parent_bam, bulk1_bam, bulk2_bam]:
            ok, message = validate_bam(bam)
            if not ok:
                raise RuntimeError(f"{os.path.basename(bam)}: {message}")
            logs.append(f"✓ {os.path.basename(bam)}: {message}")

            ok, message = ensure_bam_index(bam)
            if not ok:
                raise RuntimeError(f"{os.path.basename(bam)}: {message}")
            logs.append(f"✓ {message}")

        progress("Checking reference sequence length...")
        ref_len = reference_length(ref)
        if ref_len:
            logs.append(f"Reference length: {ref_len:,} bases")
        else:
            logs.append("Reference length could not be determined.")

        if use_reference_adaptive and ref_len:
            window_size = max(20, ref_len // 50)
            step_size = max(2, window_size // 10)
        else:
            window_size = int(window_kb * 1000)
            step_size = int(step_kb * 1000)

        if step_size >= window_size:
            raise ValueError("Step size must be smaller than window size.")

        logs.append(
            f"Window size: {window_size:,} bp; "
            f"step size: {step_size:,} bp"
        )

        outdir = os.path.join(work_dir, "results")
        os.makedirs(outdir, exist_ok=True)

        snp_df = None
        window_df = None
        used_strategy = None

        # ---------------------------------------------------------------------
        # Strategy 1: qtlseq
        # ---------------------------------------------------------------------
        if strategy in [
            "QTL-seq first → manual BSA fallback",
            "QTL-seq only",
        ]:
            qtlseq_cmd_base = command_for("qtlseq")
            if not qtlseq_cmd_base:
                if strategy == "QTL-seq only":
                    raise RuntimeError(
                        "qtlseq executable was not found. "
                        "Install qtlseq in the deployment environment."
                    )
                logs.append(
                    "qtlseq not found; proceeding directly to manual BSA."
                )
            else:
                progress("Strategy 1: running QTL-seq...")
                qtlseq_variations = [
                    qtlseq_cmd_base + [
                        "-r", ref,
                        "-p", parent_bam,
                        "-b1", bulk1_bam,
                        "-b2", bulk2_bam,
                        "-n1", str(n1),
                        "-n2", str(n2),
                        "-o", outdir,
                        "-t", "2",
                        "--force",
                    ],
                    qtlseq_cmd_base + [
                        "-r", ref,
                        "-p", parent_bam,
                        "-b1", bulk1_bam,
                        "-b2", bulk2_bam,
                        "-n1", str(n1),
                        "-n2", str(n2),
                        "-o", outdir,
                        "-t", "2",
                        "--overwrite",
                    ],
                    qtlseq_cmd_base + [
                        "-r", ref,
                        "-p", parent_bam,
                        "-b1", bulk1_bam,
                        "-b2", bulk2_bam,
                        "-n1", str(n1),
                        "-n2", str(n2),
                        "-t", "2",
                    ],
                ]

                qtl_success = False
                for i, cmd in enumerate(qtlseq_variations, 1):
                    progress(f"Trying QTL-seq command variation {i}/3...")
                    try:
                        result = run_cmd(
                            cmd, timeout=1800, cwd=outdir
                        )
                        if result.returncode == 0:
                            qtl_success = True
                            used_strategy = "QTL-seq"
                            logs.append("✓ QTL-seq completed successfully.")
                            if result.stdout:
                                logs.append(result.stdout[-2000:])
                            break
                        else:
                            logs.append(
                                f"QTL-seq variation {i} failed: "
                                f"{result.stderr[-1000:]}"
                            )
                    except subprocess.TimeoutExpired:
                        logs.append(
                            f"QTL-seq variation {i} timed out after 30 minutes."
                        )

                if qtl_success:
                    snp_df, window_df, discovered = locate_result_files(outdir)
                    logs.append(
                        f"Found {len(discovered)} candidate result files."
                    )

                    if snp_df is None or window_df is None:
                        logs.append(
                            "QTL-seq ran but required SNP/window tables "
                            "were not found; manual fallback will be used."
                        )
                        snp_df = window_df = None
                elif strategy == "QTL-seq only":
                    raise RuntimeError(
                        "All QTL-seq command variations failed."
                    )

        # ---------------------------------------------------------------------
        # Strategy 2: manual BSA
        # ---------------------------------------------------------------------
        if snp_df is None or window_df is None:
            if strategy == "QTL-seq only":
                raise RuntimeError("QTL-seq did not produce usable result tables.")

            manual_dir = os.path.join(work_dir, "manual_bsa")
            os.makedirs(manual_dir, exist_ok=True)

            progress("Strategy 2: running manual BSA analysis...")
            snp_df, window_df = manual_bsa(
                ref=ref,
                parent_bam=parent_bam,
                bulk1_bam=bulk1_bam,
                bulk2_bam=bulk2_bam,
                manual_dir=manual_dir,
                min_total_depth=int(min_total_depth),
                ref_allele_freq=float(ref_allele_freq),
                window_size=window_size,
                step_size=step_size,
                progress=progress,
            )
            used_strategy = "Manual BSA"

        progress("Standardizing result tables...")
        snp_df, window_df = standardize_results(snp_df, window_df)

        progress("Creating interactive chromosome visualization...")
        fig = create_plot(snp_df, window_df)

        files_out = create_outputs(
            snp_df=snp_df,
            window_df=window_df,
            fig=fig,
            outdir=outdir,
            ref_len=ref_len,
            n1=int(n1),
            n2=int(n2),
            window_size=window_size,
            step_size=step_size,
            min_depth=int(min_total_depth),
            ref_freq=float(ref_allele_freq),
        )

        st.session_state["result"] = {
            "snp_df": snp_df,
            "window_df": window_df,
            "fig": fig,
            "files": files_out,
            "strategy": used_strategy,
            "ref_len": ref_len,
            "window_size": window_size,
            "step_size": step_size,
            "logs": logs,
        }

        progress("✓ Analysis completed successfully.")
        st.success(f"Analysis completed using: {used_strategy}")

    except Exception as exc:
        st.error(f"Analysis failed: {exc}")
        with st.expander("Detailed log", expanded=True):
            st.code("\n".join(logs), language="text")


# =============================================================================
# RESULTS
# =============================================================================
if "result" in st.session_state:
    result = st.session_state["result"]
    snp_df = result["snp_df"]
    window_df = result["window_df"]
    fig = result["fig"]
    files_out = result["files"]

    st.markdown(
        '<div class="section">Results overview</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("High-quality SNPs", f"{len(snp_df):,}")
    c2.metric("Sliding windows", f"{len(window_df):,}")
    c3.metric("Chromosomes", f"{window_df['CHROM'].nunique():,}")
    c4.metric("Analysis strategy", result["strategy"])

    st.plotly_chart(fig, use_container_width=True)

    tabs = st.tabs([
        "SNP Results",
        "Window Results",
        "Summary",
        "Downloads",
    ])

    with tabs[0]:
        st.dataframe(snp_df, use_container_width=True, height=500)

    with tabs[1]:
        st.dataframe(window_df, use_container_width=True, height=500)

    with tabs[2]:
        st.code(files_out["summary_text"], language="text")

    with tabs[3]:
        download_specs = [
            (
                "Download all results (ZIP)",
                files_out["zip"],
                "application/zip",
                os.path.basename(files_out["zip"]),
            ),
            (
                "Download SNP data (CSV)",
                files_out["snp"],
                "text/csv",
                os.path.basename(files_out["snp"]),
            ),
            (
                "Download sliding-window data (CSV)",
                files_out["window"],
                "text/csv",
                os.path.basename(files_out["window"]),
            ),
            (
                "Download combined results (CSV)",
                files_out["combined"],
                "text/csv",
                os.path.basename(files_out["combined"]),
            ),
            (
                "Download summary (TXT)",
                files_out["summary"],
                "text/plain",
                os.path.basename(files_out["summary"]),
            ),
            (
                "Download interactive plot (HTML)",
                files_out["plot"],
                "text/html",
                os.path.basename(files_out["plot"]),
            ),
        ]

        for label, path, mime, filename in download_specs:
            if os.path.exists(path):
                with open(path, "rb") as f:
                    st.download_button(
                        label,
                        data=f.read(),
                        file_name=filename,
                        mime=mime,
                        use_container_width=True,
                    )

    with st.expander("Pipeline log"):
        st.code("\n".join(result["logs"]), language="text")
