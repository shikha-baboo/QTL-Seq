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

/* ---------- File uploader styling ---------- */
[data-testid="stFileUploaderDropzone"] {
    background: rgba(124,58,237,0.06) !important;
    border: 1.5px dashed #A78BFA !important; border-radius: 12px !important;
    transition: background .15s ease, border-color .15s ease;
}
[data-testid="stFileUploaderDropzone"]:hover {
    background: rgba(124,58,237,0.14) !important; border-color: #F97316 !important;
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


def validate_fastq_gz(fastq_gz):
    """Validate that a file appears to be a valid FASTQ.gz file."""
    if fastq_gz is None:
        return False, "No file provided"
    
    # Check file extension
    if not fastq_gz.name.endswith(('.fastq.gz', '.fq.gz')):
        return False, f"File {fastq_gz.name} does not have .fastq.gz or .fq.gz extension"
    
    # Check if it's valid gzip by trying to read first few lines
    try:
        import gzip
        with gzip.open(fastq_gz, 'rb') as f:
            # Try to read first 4 lines (one read)
            lines = []
            for _ in range(4):
                line = f.readline()
                if line:
                    lines.append(line.decode('utf-8', errors='ignore'))
                else:
                    break
            
            if len(lines) < 4:
                return False, "File appears to be truncated or not a valid FASTQ file"
            
            # Check FASTQ format: first line should start with @
            if not lines[0].startswith('@'):
                return False, "File does not appear to be in FASTQ format (first line should start with @)"
            
            return True, "FASTQ.gz file appears valid"
    except Exception as e:
        return False, f"Error validating FASTQ.gz: {str(e)}"


def align_fastq_to_bam(ref, fastq_gz_path, output_bam_path, sample_name, progress=None):
    """
    Align FASTQ reads to reference genome and produce sorted BAM file.
    Uses BWA mem for alignment.
    """
    # Check for required tools
    bwa = command_for("bwa")
    samtools = command_for("samtools")
    
    if not bwa:
        raise RuntimeError("bwa is required for alignment but was not found. Please install bwa.")
    if not samtools:
        raise RuntimeError("samtools is required for alignment but was not found.")
    
    # Index reference if needed
    if progress:
        progress(f"Indexing reference genome for sample {sample_name}...")
    
    # Check if reference is indexed by bwa
    if not os.path.exists(ref + ".bwt"):
        bwa_index_cmd = bwa + ["index", ref]
        result = run_cmd(bwa_index_cmd, timeout=3600)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to index reference genome: {result.stderr}")
    
    if progress:
        progress(f"Aligning {sample_name} FASTQ to reference genome...")
    
    # Align with BWA mem
    sam_file = output_bam_path.replace('.bam', '.sam')
    bwa_cmd = bwa + ["mem", "-t", "4", ref, fastq_gz_path]
    
    with open(sam_file, 'w') as sam_out:
        result = subprocess.run(
            bwa_cmd,
            stdout=sam_out,
            stderr=subprocess.PIPE,
            text=True,
            timeout=7200  # 2 hours for large files
        )
    
    if result.returncode != 0:
        raise RuntimeError(f"BWA alignment failed for {sample_name}: {result.stderr}")
    
    if progress:
        progress(f"Converting SAM to BAM and sorting for {sample_name}...")
    
    # Convert SAM to BAM, sort, and index
    # Sort and convert in one go
    sort_cmd = samtools + ["sort", "-@", "4", "-o", output_bam_path, sam_file]
    result = run_cmd(sort_cmd, timeout=3600)
    
    if result.returncode != 0:
        raise RuntimeError(f"Failed to sort BAM for {sample_name}: {result.stderr}")
    
    # Clean up SAM file
    if os.path.exists(sam_file):
        os.remove(sam_file)
    
    # Index the BAM
    index_cmd = samtools + ["index", output_bam_path]
    result = run_cmd(index_cmd, timeout=600)
    
    if result.returncode != 0:
        raise RuntimeError(f"Failed to index BAM for {sample_name}: {result.stderr}")
    
    return output_bam_path


def validate_bam(bam):
    samtools = command_for("samtools")
    if not samtools:
        return False, "samtools is not installed."

    r = run_cmd(samtools + ["quickcheck", bam], timeout=300)
    if r.returncode != 0:
        return False, r.stderr.strip() or "BAM failed samtools quickcheck."
    return True, "BAM passed samtools quickcheck."


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
        f"  Minimum depth filter: {min_depth}",]
