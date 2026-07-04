import streamlit as st
import pandas as pd
import io
import itertools
import re
from collections import Counter

# ==========================================
# PAGE CONFIG & PREMIUM DARK-THEME STYLE
# ==========================================
st.set_page_config(page_title="2D AI Master V35.10 Master-Lab", layout="centered", page_icon="🤖")

st.markdown("""
<style>
    .stApp { background-color: #0B031A; color: #E0D5FA; }
    .main-title { color: #A078FF; font-size: 32px; font-weight: bold; text-align: center; margin-bottom: 5px; text-shadow: 0 0 10px rgba(160,120,255,0.5); }
    .sub-title { color: #8F72D6; font-size: 14px; text-align: center; margin-bottom: 30px; }
    .card { background-color: #170E2B; padding: 20px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); margin-bottom: 15px; border: 1px solid #2D1B4E; }
    .card-live { border-left: 6px solid #3498db; background-color: #0E1A2F; margin-bottom: 15px; }
    .card-hp { border-left: 6px solid #2ecc71; background-color: #0D2216; margin-bottom: 15px; }
    .card-deadline { border-left: 6px solid #e74c3c; background-color: #31151A; margin-bottom: 10px; }
    .card-recovery { border-left: 6px solid #e67e22; background-color: #2D1A0E; margin-bottom: 10px; }
    .line-trigger { font-size: 16px; font-weight: bold; color: #E0D5FA; margin-bottom: 6px; display: block; }
    .line-formula { font-size: 20px; font-weight: bold; color: #FFD700; margin-bottom: 6px; display: block; }
    .line-history { font-size: 14px; color: #A294C7; display: block; }
    .line-focus { font-size: 14px; color: #f1c40f; font-weight: bold; display: block; margin-top: 5px; margin-bottom: 5px;}
    .line-advisor { font-size: 14px; color: #00FFCC; font-style: italic; margin-top: 10px; display: block; border-top: 1px dashed #3D2B5E; padding-top: 8px; margin-bottom: 8px;}
    .badge-inline { padding: 2px 10px; border-radius: 6px; font-size: 14px; font-weight: bold; margin-left: 6px; margin-right: 6px; display: inline-block; vertical-align: middle; }
    .badge-inline-sniper { background-color: #9b59b6; color: white; }
    .badge-inline-hp { background-color: #2ecc71; color: #0D2216; }
    .badge-super { background-color: #FFD700; color: #000; padding: 4px 10px; border-radius: 6px; font-weight: bold; font-size: 16px; display: block; text-align: center; margin-bottom: 10px;}
    .badge-second { background-color: #C0C0C0; color: #000; padding: 3px 8px; border-radius: 5px; font-weight: bold; }
    .section-title { color: #00FFCC; font-size: 20px; border-bottom: 2px solid #3D2B5E; padding-bottom: 8px; margin-top: 20px; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🤖 THE PERFECT 2D AI MASTER (V35.10)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Ultimate Risk-Warning Engine | Smart Pattern Classifier</div>', unsafe_allow_html=True)

# Session State Memory Setup
if 'full_draws' not in st.session_state: st.session_state.full_draws = None
if 'active_days' not in st.session_state: st.session_state.active_days = []
if 'day_pairs' not in st.session_state: st.session_state.day_pairs = {}

special_groups = {
    "ညီကို": {"01","10","12","21","23","32","34","43","45","54","56","65","67","76","78","87","89","98","90","09"},
    "ပါဝါ": {"05","50","16","61","27","72","38","83","49","94"},
    "နက္ခတ်": {"07","70","18","81","24","42","35","53","69","96"},
    "ထိုင်းပါဝါ": {"09","90","13","31","26","62","47","74","58","85"},
    "အပူး": {"00","11","22","33","44","55","66","77","88","99"},
    "ဆယ်ပြည့်": {"10","01","20","02","30","03","40","04","50","05","60","06","70","07","80","08","90","09"}
}
mu_keys_list = ["လုံးဘိုင်", "One Change", "key", "အပူးပါခွေ", "ထိပ်စီးစနစ်သစ်", "နောက်ပိတ်စနစ်သစ်", "ဘရိတ်", "စုံ/မ ကပ်", "အုပ်စု သီးသန့်", "အုပ်စုတွဲ"]

# ==========================================
# HELPER FUNCTIONS & FAIL-SAFE LOGIC
# ==========================================
def normalize_formula(mu_k, mu_val):
    if mu_val == "-" or not mu_val: return mu_val
    try:
        if mu_k in ["One Change", "key", "အပူးပါခွေ"]:
            parts = mu_val.split()
            if len(parts) > 1: return f"{''.join(sorted(parts[0]))} {' '.join(parts[1:])}"
        elif mu_k == "ဘရိတ်":
            match = re.match(r'([0-9]+)\s*,\s*([0-9]+)\s*ဘရိတ်', mu_val)
            if match: return f"{sorted([match.group(1), match.group(2)])[0]}, {sorted([match.group(1), match.group(2)])[1]} ဘရိတ်"
        elif mu_k == "အုပ်စုတွဲ":
            gps = mu_val.split('+')
            if len(gps) == 2: return f"{sorted([g.strip() for g in gps])[0]}+{sorted([g.strip() for g in gps])[1]}"
    except: pass
    return mu_val

def check_single_draw_against_formula(d, mu_k, mu_val):
    if mu_val == "-" or not mu_val or len(d) < 2: return False
    d_break = str((int(d[0]) + int(d[1])) % 10)
    if mu_k == "လုံးဘိုင်": return mu_val.split()[0] in d
    elif mu_k in ["One Change", "key"]: return any(x in d for x in mu_val.split()[0])
    elif mu_k == "အပူးပါခွေ": pure_k4 = mu_val.split()[0]; return d[0] in pure_k4 and d[1] in pure_k4
    elif mu_k == "ထိပ်စီးစနစ်သစ်":
        match = re.search(r'([0-9]+)\s*ထိပ်\s*/\s*([0-9,]+)\s*ကပ်', mu_val)
        if match: return d[0] in match.group(1) and d[1] in [t.strip() for t in match.group(2).split(',')]
    elif mu_k == "နောက်ပိတ်စနစ်သစ်":
        match = re.search(r'([0-9]+)\s*ပိတ်\s*/\s*([0-9,]+)\s*ကပ်', mu_val)
        if match: return d[1] in match.group(1) and d[0] in [h.strip() for h in match.group(2).split(',')]
    elif mu_k == "ဘရိတ်": pure_brk = mu_val.split()[0].split(','); return d_break in [b.strip() for b in pure_brk]
    elif mu_k == "စုံ/မ ကပ်":
        match = re.search(r'\[(\d+)\]\s*"([^"]+)"ကပ်', mu_val)
        if match:
            b1, is_even = match.group(1), "စုံ" in match.group(2)
            if b1 in d:
                rem_digit = int(d.replace(b1, '', 1) or b1)
                return (is_even and rem_digit % 2 == 0) or (not is_even and rem_digit % 2 != 0)
    elif mu_k == "အုပ်စု သီးသန့်": return d in special_groups.get(mu_val, set())
    elif mu_k == "အုပ်စုတွဲ": return any(d in special_groups.get(g.strip(), set()) for g in mu_val.split('+'))
    return False

def is_already_hit(mu_name, mu_val, start_idx, end_idx, full_draws_list):
    if start_idx >= len(full_draws_list): return False, ""
    for d in [x['draw'] for x in full_draws_list[start_idx : min(end_idx + 1, len(full_draws_list))]]:
        if check_single_draw_against_formula(d, mu_name, mu_val): return True, d
    return False, ""

def generate_formula_from_pool(analysis_pool):
    if not analysis_pool: return {k: "-" for k in mu_keys_list}
    all_singles = "".join(analysis_pool)
    if not all_singles: return {k: "-" for k in mu_keys_list}
    all_heads = [d[0] for d in analysis_pool if len(d) >= 2]
    all_tails = [d[1] for d in analysis_pool if len(d) >= 2]
    all_breaks = [str((int(d[0]) + int(d[1])) % 10) for d in analysis_pool if len(d) >= 2]

    mc_single = Counter(all_singles).most_common(1)
    top_single = mc_single[0][0] if mc_single else ""
    top_oc = "".join([x[0] for x in Counter(all_singles).most_common(2)]) if len(Counter(all_singles)) >= 2 else top_single
    top_key3 = "".join([x[0] for x in Counter(all_singles).most_common(3)]) if len(Counter(all_singles)) >= 3 else top_oc
    top_k4 = "".join([x[0] for x in Counter(all_singles).most_common(4)]) if len(Counter(all_singles)) >= 4 else top_key3
    top_h3 = [x[0] for x in Counter(all_heads).most_common(3)]
    best_tails = [x[0] for x in Counter([d[1] for d in analysis_pool if len(d)>=2 and d[0] in top_h3]).most_common(4)]
    head_formula_str = f"{''.join(top_h3)} ထိပ် / {','.join(best_tails)} ကပ်" if top_h3 else "-"
    top_t3 = [x[0] for x in Counter(all_tails).most_common(3)]
    best_heads = [x[0] for x in Counter([d[0] for d in analysis_pool if len(d)>=2 and d[1] in top_t3]).most_common(4)]
    tail_formula_str = f"{''.join(top_t3)} ပိတ် / {','.join(best_heads)} ကပ်" if top_t3 else "-"
    top_brk2 = [x[0] for x in Counter(all_breaks).most_common(2)]
    if len(top_brk2) < 2 and top_brk2: top_brk2.append(str((int(top_brk2[0])+1)%10))
    e_sc = sum(1 for d in analysis_pool if len(d)>=2 and top_single in d and int(d.replace(top_single,'',1) or top_single) % 2 == 0)
    o_sc = sum(1 for d in analysis_pool if len(d)>=2 and top_single in d and int(d.replace(top_single,'',1) or top_single) % 2 != 0)
    kap_label = f'[{top_single}] "စုံ"ကပ်' if e_sc >= o_sc else f'[{top_single}] "မ"ကပ်'
    best_sgp = max(special_groups.keys(), key=lambda g: sum(1 for d in analysis_pool if d in special_groups[g]), default="-")
    if sum(1 for d in analysis_pool if d in special_groups.get(best_sgp, set())) == 0: best_sgp = "-"
    best_gp, max_gp_c = "-", 0
    for combo in itertools.combinations(special_groups.keys(), 2):
        c = sum(1 for d in analysis_pool if d in special_groups[combo[0]] or d in special_groups[combo[1]])
        if c > max_gp_c: max_gp_c = c; best_gp = f"{combo[0]}+{combo[1]}"

    res = {
        "လုံးဘိုင်": f"{top_single} လုံးဘိုင်" if top_single else "-", "One Change": f"{top_oc} One Change" if top_oc else "-",
        "key": f"{top_key3} key" if top_key3 else "-", "အပူးပါခွေ": f"{top_k4} အပူးပါခွေ" if top_k4 else "-",
        "ထိပ်စီးစနစ်သစ်": head_formula_str, "နောက်ပိတ်စနစ်သစ်": tail_formula_str,
        "ဘရိတ်": f"{top_brk2[0]}, {top_brk2[1]} ဘရိတ်" if len(top_brk2) == 2 else "-", 
        "စုံ/မ ကပ်": kap_label if top_single else "-", "အုပ်စု သီးသန့်": best_sgp, "အုပ်စုတွဲ": best_gp
    }
    return {k: normalize_formula(k, v) for k, v in res.items()}

def get_hybrid_candidates(target_hits, full_draws, max_step):
    candidates = {k: [] for k in mu_keys_list}
    for i in range(10): candidates["လုံးဘိုင်"].append(f"{i} လုံးဘိုင်")
    for b in itertools.combinations([str(x) for x in range(10)], 2): 
        cand = normalize_formula("ဘရိတ်", f"{b[0]}, {b[1]} ဘရိတ်")
        if cand not in candidates["ဘရိတ်"]: candidates["ဘရိတ်"].append(cand)
    for g in special_groups.keys(): candidates["အုပ်စု သီးသန့်"].append(g)
    for combo in itertools.combinations(special_groups.keys(), 2): 
        cand = normalize_formula("အုပ်စုတွဲ", f"{combo[0]}+{combo[1]}")
        if cand not in candidates["အုပ်စုတွဲ"]: candidates["အုပ်စုတွဲ"].append(cand)
        
    analysis_pool = [full_draws[h['index'] + s]['draw'] for h in target_hits for s in range(1, max_step + 1) if h['index'] + s < len(full_draws)]
    complex_formulas = generate_formula_from_pool(analysis_pool)
    for k in ["One Change", "key", "အပူးပါခွေ", "ထိပ်စီးစနစ်သစ်", "နောက်ပိတ်စနစ်သစ်", "စုံ/မ ကပ်"]:
        if complex_formulas[k] != "-": candidates[k].append(complex_formulas[k])
    return candidates

def get_brk(draw_dict):
    if draw_dict and 'draw' in draw_dict and len(draw_dict['draw']) >= 2:
        return str((int(draw_dict['draw'][0]) + int(draw_dict['draw'][1])) % 10)
    return None

# ==========================================
# MASTER ROUTINE: V35.10 INTERSECTION ENGINE (WITH RISK-NOTE)
# ==========================================
def execute_analysis(target_hits, full_draws, requested_max_step, is_custom_tab=False, search_session="All", custom_trigger="", mode="AI Trend", is_research_mode=False, min_rate_threshold=90.0):
    step_buckets = {step: {} for step in range(1, requested_max_step + 1)}
    current_latest_idx = len(full_draws) - 1
    MAX_RECENT_HITS_CAP = 50
    recent_target_hits = target_hits[-MAX_RECENT_HITS_CAP:] if len(target_hits) > MAX_RECENT_HITS_CAP else target_hits
    total_recent_count = len(recent_target_hits)
    
    if total_recent_count == 0: return step_buckets, []
    min_required_hits = max(10, int(total_recent_count * 0.3))
    if total_recent_count < min_required_hits and not is_research_mode: return step_buckets, []

    recovery_pool = [] 
    calendar_candidates = get_hybrid_candidates(recent_target_hits, full_draws, requested_max_step) if mode == "Calendar သီးသန့်မူများ (Fixed Pattern)" else {}
    label_space = "နံနက်ပိုင်း " if search_session == "AM သီးသန့်" else ("ညနေပိုင်း " if search_session == "PM သီးသန့်" else "")

    for mu_k in mu_keys_list:
        cand_list = calendar_candidates.get(mu_k, []) if mode == "Calendar သီးသန့်မူများ (Fixed Pattern)" else ["DYNAMIC_AI"]
        for cand_val in cand_list:
            hit_steps_across_history = []
            actual_hit_combinations = []
            last_generated_val = cand_val

            for hit in recent_target_hits:
                hit_idx = hit['index']
                current_val = cand_val
                if mode != "Calendar သီးသန့်မူများ (Fixed Pattern)":
                    pool = [d['draw'] for d in full_draws[max(0, hit_idx - 50) : hit_idx]]
                    current_val = generate_formula_from_pool(pool).get(mu_k, "-")
                    last_generated_val = current_val

                if current_val == "-" or not current_val: hit_steps_across_history.append(999); continue

                found_hit_step = None
                for step_check in range(1, requested_max_step + 1):
                    t_idx = hit_idx + step_check
                    if t_idx >= len(full_draws): break
                    if "သီးသန့်" in search_session:
                        if full_draws[t_idx]['time'] != ("AM" if "AM" in search_session else "PM"): continue
                    is_hit, matched_draw = is_already_hit(mu_k, current_val, t_idx, t_idx, full_draws)
                    if is_hit:
                        found_hit_step = step_check
                        actual_hit_combinations.append(matched_draw)
                        break
                hit_steps_across_history.append(found_hit_step if found_hit_step is not None else 999)

            valid_spans = sorted([s for s in hit_steps_across_history if s <= requested_max_step])
            if not valid_spans or last_generated_val == "-": continue
            
            max_required_span = max(valid_spans)
            successful_hits = len(valid_spans)
            rate = (successful_hits / total_recent_count) * 100

            if rate < min_rate_threshold: continue

            # --- [NEW] ALL-TIME MAX SPAN BACKTESTING ---
            all_time_max_span = max_required_span
            if len(target_hits) > MAX_RECENT_HITS_CAP:
                for hit in target_hits:
                    h_idx = hit['index']
                    found_step = None
                    for step_check in range(1, 150): # Safe bound search
                        t_idx = h_idx + step_check
                        if t_idx >= len(full_draws): break
                        if "သီးသန့်" in search_session:
                            if full_draws[t_idx]['time'] != ("AM" if "AM" in search_session else "PM"): continue
                        is_h, _ = is_already_hit(mu_k, last_generated_val, t_idx, t_idx, full_draws)
                        if is_h:
                            found_step = step_check
                            break
                    if found_step is not None and found_step > all_time_max_span:
                        all_time_max_span = found_step

            if len(valid_spans) > 1:
                q1_idx, q3_idx = int(len(valid_spans) * 0.25), min(int(len(valid_spans) * 0.75), len(valid_spans) - 1)
                focus_start, focus_end = valid_spans[q1_idx], valid_spans[q3_idx]
                focus_str = f"အများဆုံး {focus_start} ပွဲမြောက်တွင် လာတတ်သည်" if focus_start == focus_end else f"ပျမ်းမျှ 🎯 {focus_start} မှ {focus_end} ပွဲအတွင်း အများဆုံး လာတတ်သည်"
            else:
                focus_str = f"အများဆုံး {valid_spans[0]} ပွဲမြောက်တွင် လာတတ်သည်"

            lbl_prefix = custom_trigger if is_custom_tab else f"{recent_target_hits[-1]['draw']} {recent_target_hits[-1]['time']}"
            is_deadline_flag, rem_steps = False, 999
            
            if recent_target_hits:
                last_hit_global_idx = recent_target_hits[-1]['index']
                elapsed_filtered = sum(1 for d in full_draws[last_hit_global_idx + 1 : current_latest_idx + 1] if d['time'] == ("AM" if "AM" in search_session else "PM")) if "သီးသန့်" in search_session else (current_latest_idx - last_hit_global_idx)
                rem_steps = max_required_span - elapsed_filtered
                if rem_steps == 1: is_deadline_flag = True
                
                if not is_research_mode:
                    if rem_steps < 1: continue 
                    if elapsed_filtered > 0 and is_already_hit(mu_k, last_generated_val, last_hit_global_idx + 1, current_latest_idx, full_draws)[0]: continue

            sniper_note = f"💡 အဖြစ်နိုင်ဆုံး ၃/၄ ကွက်: {', '.join([x[0] for x in Counter(actual_hit_combinations).most_common(4)])}" if actual_hit_combinations else ""
            
            risk_note_html = ""
            if all_time_max_span > max_required_span:
                risk_note_html = f'<div style="color: #ff4b4b; font-size: 14px; margin-top: 10px; font-weight: bold; background: rgba(255,0,0,0.15); padding: 8px; border-radius: 6px; border-left: 4px solid #ff4b4b;">⚠️ Risk Note: ယခု ({max_required_span}) ပွဲဖြစ်သော်လည်း၊ သမိုင်းတစ်လျှောက် ({all_time_max_span}) ပွဲ ကြာဖူးသည်။</div>'

            card_payload = {
                "top": f"🔮 [{lbl_prefix}] ထွက်ပြီးလျှင်", "formula": f"{last_generated_val} {'100%' if rate == 100.0 else f'{rate:.1f}%'}", 
                "focus_range": focus_str, "bottom": f"မှန်ကန်မှု: (လတ်တလော {total_recent_count} ကြိမ်မှာ {successful_hits} ကြိမ်မှန်)", 
                "success_hits": successful_hits, "total_hits": total_recent_count, "is_deadline": is_deadline_flag, 
                "pure": last_generated_val, "mu_k": mu_k, "advisor": sniper_note, "rate": rate, 
                "max_span": max_required_span, "lbl_prefix": lbl_prefix, "label_space": label_space,
                "risk_note": risk_note_html
            }
            
            if is_research_mode or is_deadline_flag: step_buckets[max_required_span][last_generated_val if mode == "Calendar သီးသန့်မူများ (Fixed Pattern)" else mu_k] = card_payload
            if not is_research_mode and rem_steps in [2, 3]:
                coverage_count = max(1, sum(1 for i in range(100) if check_single_draw_against_formula(f"{i:02d}", mu_k, last_generated_val)))
                recovery_pool.append({"key": last_generated_val, "lbl_prefix": lbl_prefix, "rem_steps": rem_steps, "score": round(((rate / 100.0) * successful_hits) * (1.5 if rem_steps == 2 else 1.0) * (100.0 / coverage_count), 1), "card": card_payload})

    return step_buckets, recovery_pool

# ==========================================
# FILE UPLOAD & PROCESS LOGIC
# ==========================================
def load_and_process_data(file_bytes, file_name):
    try:
        df = pd.read_csv(io.BytesIO(file_bytes)) if file_name.endswith('.csv') else pd.read_excel(io.BytesIO(file_bytes))
        df.columns = df.columns.str.strip().str.lower()
        if not all(col in df.columns for col in ['year', 'day', 'am1', 'am2', 'pm1', 'pm2']): return "⚠️ ဖိုင်ထဲတွင် လိုအပ်သော ကော်လံများ (year, day, am1, am2, pm1, pm2) မပြည့်စုံပါ!"
        for col in ['year', 'am1', 'am2', 'pm1', 'pm2']: df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df.dropna(subset=['year', 'day']).reset_index(drop=True)
        df['day'] = df['day'].astype(str).str.strip().str.capitalize()
        full_days = ["Mon", "Tue", "Wed", "Thur", "Fri"]
        off_days = [d for d in full_days if d not in set(df['day'].unique())]
        full_draws = []
        for row in df.itertuples():
            if pd.notna(row.am1) and pd.notna(row.am2): full_draws.append({'draw': f"{int(row.am1)}{int(row.am2)}", 'time': 'AM', 'day': row.day, 'row_idx': row.Index})
            if pd.notna(row.pm1) and pd.notna(row.pm2): full_draws.append({'draw': f"{int(row.pm1)}{int(row.pm2)}", 'time': 'PM', 'day': row.day, 'row_idx': row.Index})
        for i, d in enumerate(full_draws): d['index'] = i
        if not full_draws: return "⚠️ ဒေတာ အလွတ်ဖြစ်နေပါသည်။"
        
        st.session_state.full_draws = full_draws
        st.session_state.active_days = [d for d in full_days if d not in off_days]
        day_pairs = {}
        for d in full_draws:
            r = d['row_idx']
            if r not in day_pairs: day_pairs[r] = {'AM': None, 'PM': None, 'day': d['day']}
            day_pairs[r][d['time']] = d
        st.session_state.day_pairs = day_pairs
        return None
    except Exception as e: return f"⚠️ Data Process အမှားအယွင်း: {e}"

# ==========================================
# UI DASHBOARD DISPLAY
# ==========================================
uploaded_file = st.file_uploader("Bro ရဲ့ 2D CSV သို့မဟုတ် Excel ဖိုင်ကို တင်ပေးပါ...", type=['csv', 'xlsx', 'xls'])

if uploaded_file:
    err = load_and_process_data(uploaded_file.getvalue(), uploaded_file.name)
    if err: st.error(err)

if st.session_state.full_draws:
    last_val = st.session_state.full_draws[-1]['draw']
    last_time = st.session_state.full_draws[-1]['time']
    st.markdown(f"""
    <div style="background-color: #0E2F1D; border-left: 5px solid #2ecc71; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
        <div style="color: #2ecc71; font-size: 16px; font-weight: bold; margin-bottom: 5px;">✅ Data ({len(st.session_state.full_draws)}) ပွဲ ဝင်ရောက်ပါပြီ။</div>
        <div style="color: #E0D5FA; font-size: 15px;">နောက်ဆုံးထွက်: [ <span style="color:#FFD700; font-size:18px; font-weight:bold;">{last_val}</span> ] ({last_time})</div>
    </div>
    """, unsafe_allow_html=True)
    st.write("---")

    tab_live, tab_custom = st.tabs(["⚡ VIP Tracker (ယခုပွဲစဉ်)", "🔍 Pair-Engine (Custom သုတေသန)"])

    # ------------------------------------------
    # TAB 1: LIVE AUTO TRACKER 
    # ------------------------------------------
    with tab_live:
        st.markdown("#### ⚙️ VIP ရှာဖွေမှု ကန့်သတ်ချက်များ")
        with st.form("live_tracker_form"):
            c1, c2 = st.columns(2)
            with c1: anchor_count = st.number_input("📌 အနှစ်ချုပ်ကြည့်မည့် မူအရေအတွက်:", min_value=1, max_value=50, value=10)
            with c2: live_max_tf = st.number_input("⏳ စစ်ဆေးမည့် ပွဲစဉ်အရေအတွက် [Max Span]:", min_value=1, max_value=50, value=20)
            custom_anchors_str = st.text_input("🎯 စိတ်ကြိုက် အမာခံဂဏန်းများ (ဥပမာ - 48, 60) [မရိုက်ပါက Auto ရှာမည်]:", value="")
            live_mode = st.radio("🧠 AI တွက်ချက်မှုစနစ်:", ["AI Trend (ရှေ့သမိုင်း ၅၀ အထိုင်)", "Calendar သီးသန့်မူများ (Fixed Pattern)"], horizontal=True)
            submit_live = st.form_submit_button("VIP ကို ယခုရှာဖွေမည် ⚡")

        if submit_live:
            with st.spinner("⚡ AI အရည်အသွေး အမှတ်ပေးစနစ်ဖြင့် တွက်ချက်နေပါသည်..."):
                selected_anchors = []
                if custom_anchors_str.strip():
                    raw_nums = [x.strip() for x in custom_anchors_str.split(',') if x.strip().isdigit()]
                    for n in raw_nums:
                        hit = next((d for d in reversed(st.session_state.full_draws) if d['draw'] == n), None)
                        if hit: selected_anchors.append(hit)
                else:
                    selected_anchors = st.session_state.full_draws[-anchor_count:]
                
                if not selected_anchors:
                    st.error("⚠️ အမာခံဂဏန်းများ ရှာမတွေ့ပါ။")
                else:
                    scoring_pool, global_recovery = {}, {}
                    for past_obj in selected_anchors:
                        p_val, p_time, p_day = past_obj['draw'], past_obj['time'], past_obj['day']
                        condition_pools = [
                            {"hits": [d for d in st.session_state.full_draws if d['draw'] == p_val and d['time'] == p_time], "lbl": f"{p_val} {p_time} စစ်စစ်"},
                            {"hits": [d for d in st.session_state.full_draws if d['draw'] == p_val], "lbl": f"{p_val} ပေါင်းချုပ်"},
                            {"hits": [d for d in st.session_state.full_draws if (d['draw'] == p_val or d['draw'] == p_val[::-1]) and d['day'] == p_day], "lbl": f"{p_val}R {p_day} သီးသန့်"}
                        ]
                        for p in condition_pools:
                            if not p['hits']: continue
                            step_res, rec_pool = execute_analysis(p['hits'], st.session_state.full_draws, live_max_tf, is_custom_tab=True, search_session="AM+PM ပေါင်းချုပ်", custom_trigger=p['lbl'], mode=live_mode, min_rate_threshold=90.0)
                            
                            for step_dist, formulas_dict in step_res.items():
                                for mk, mv in formulas_dict.items():
                                    f_key = mv['pure']
                                    if f_key not in scoring_pool:
                                        cov = max(1, sum(1 for i in range(100) if check_single_draw_against_formula(f"{i:02d}", mv['mu_k'], f_key)))
                                        scoring_pool[f_key] = {'count': 0, 'details': [], 'mu_k': mv['mu_k'], 'quality_score': 0.0, 'coverage': cov}
                                    if mv['top'] not in [d['top'] for d in scoring_pool[f_key]['details']]:
                                        scoring_pool[f_key]['details'].append(mv)
                                        scoring_pool[f_key]['count'] += 1
                                        scoring_pool[f_key]['quality_score'] += (mv['rate'] / 100.0) * mv['success_hits']

                            for rp in rec_pool:
                                r_key = rp['key']
                                if r_key not in global_recovery: global_recovery[r_key] = {'score': 0.0, 'rem_steps': rp['rem_steps'], 'details': []}
                                if rp['card']['top'] not in [d['top'] for d in global_recovery[r_key]['details']]:
                                    global_recovery[r_key]['details'].append(rp['card'])
                                    global_recovery[r_key]['score'] += rp['score']

                    valid_vips = {k: v for k, v in scoring_pool.items() if v['count'] >= 2}
                    deadline_singles = {k: v for k, v in scoring_pool.items() if v['count'] == 1}
                    
                    st.markdown("#### 🏆 VIP ဆုံးဖြတ်ချက် (Overlaps Match)")
                    if valid_vips:
                        for i, (b_val, b_data) in enumerate(sorted(valid_vips.items(), key=lambda x: x[1]['quality_score'], reverse=True)):
                            is_super = i < 3
                            badge = "badge-super" if is_super else "badge-second"
                            with st.expander(f"⭐ {'Super VIP' if is_super else 'Second VIP'}: {b_val} (Score: {b_data['quality_score']:.1f})", expanded=is_super):
                                st.markdown(f"<span class='{badge}'>{'Super VIP' if is_super else 'Second VIP'}</span> <span style='float:right;'>ကွက်ရေ: {b_data['coverage']} ကွက်</span>", unsafe_allow_html=True)
                                for d_detail in b_data['details']:
                                    s_class = "badge-inline-sniper" if d_detail['rate'] == 100.0 else "badge-inline-hp"
                                    st.markdown(f'<div class="card card-live" style="padding:10px; margin-bottom:10px;"><b>{d_detail["top"]}</b> <span class="badge-inline {s_class}">{d_detail["label_space"]}{d_detail["max_span"]} ပွဲအတွင်း</span><br/><span class="line-formula" style="font-size:16px;">{d_detail["formula"]}</span><br/><small style="color:#f39c12;">{d_detail["focus_range"]}</small><br/><small>{d_detail["bottom"]}</small>{d_detail.get("risk_note", "")}</div>', unsafe_allow_html=True)
                    else:
                        st.info("ခိုင်မာသော VIP တူညီမှုရလဒ် ယခုပွဲစဉ်တွင် မရှိသေးပါ။")

                    if deadline_singles:
                        st.markdown("#### ⚠️ ရက်ချိန်းပြည့် မူများ (Standalone)")
                        for d_key, d_data in deadline_singles.items():
                            item = d_data['details'][0]
                            st.markdown(f'<div class="card card-deadline">🔴 <b>[{item["lbl_prefix"]}] {d_key}</b><br/><small>⏳ ယခုပွဲစဉ် ရက်ချိန်းကွက်တိပြည့် ({item["label_space"]}{item["max_span"]} ပွဲမြောက်)</small><br/><span class="line-focus">{item["focus_range"]}</span>{item.get("risk_note", "")}</div>', unsafe_allow_html=True)

                    if global_recovery:
                        st.markdown("#### 🛡️ Recovery မူကျန်စောင့်ကြည့်ရန် (Top 3)")
                        for r_key, r_data in sorted(global_recovery.items(), key=lambda x: x[1]['score'], reverse=True)[:3]:
                            item = r_data['details'][0]
                            st.markdown(f'<div class="card card-recovery">🔥 <b>Score: {r_data["score"]:.1f} | [{item["lbl_prefix"]}] {r_key}</b><br/><small>⏳ {item["label_space"]}{"၁ ပွဲသာ လိုတော့သည်" if r_data["rem_steps"]==2 else "၂ ပွဲ လိုသေးသည်"}</small><br/><span class="line-focus">{item["focus_range"]}</span>{item.get("risk_note", "")}</div>', unsafe_allow_html=True)

    # ------------------------------------------
    # TAB 2: ADVANCED PAIR-ENGINE LAB
    # ------------------------------------------
    with tab_custom:
        st.markdown("##### 🧠 Custom Search Advanced Engine")
        with st.form("custom_research_form"):
            custom_mode = st.radio("တွက်ချက်မှုမုဒ်:", ["AI Trend (ရှေ့သမိုင်း ၅၀ အထိုင်)", "Calendar သီးသန့်မူများ (Fixed Pattern)"])
            c1, c2 = st.columns(2)
            with c1: trigger_day = st.selectbox("📆 Trigger Day:", ["All"] + st.session_state.active_days)
            with c2: trigger_num = st.text_input("🔍 အစပြုဂဏန်း/Keyword (စာရိုက်ထည့်ပါ):", value="30 အလယ်")
            
            c3, c4 = st.columns(2)
            with c3: target_session_trigger = st.selectbox("🎯 ၁။ အစ (Trigger) ကောက်ယူမည့် အချိန်:", ["AM+PM ပေါင်းချုပ်", "AM သီးသန့်", "PM သီးသန့်"], index=2)
            with c4: search_space = st.selectbox("🔍 ၂။ မူများရှာဖွေမည့် Space:", ["All", "AM+PM ပေါင်းချုပ်", "AM သီးသန့်", "PM သီးသန့်"], index=0)
            
            c5, c6 = st.columns(2)
            with c5: custom_max_tf = st.number_input("⏳ စစ်ဆေးမည့်ပွဲစဉ်:", min_value=1, max_value=40, value=20)
            with c6: min_rate_param = st.number_input("📈 အနည်းဆုံး ကိုက်ညီမှုနှုန်း (n% မှ 100%):", min_value=1, max_value=100, value=90, step=5)
            
            submit_custom = st.form_submit_button("ရှာဖွေမည် 🚀")

        with st.expander("💡 အသုံးပြုနိုင်သော Keyword စာရင်းများ (ဒီမှာနှိပ်ကြည့်ပါ)"):
            st.markdown("""
            | အမျိုးအစား | ရိုက်ထည့်ရန် Keyword (ဥပမာ) | ရှင်းလင်းချက် |
            | :--- | :--- | :--- |
            | 🔢 **ရိုးရိုးဂဏန်းများ** | `12 ဒဲ့`, `12 R`, `12` | `ဒဲ့` (တိုက်ရိုက်)၊ `R` (အလှည့်) စနစ်ဖြင့် ရှာဖွေနိုင်သည် |
            | 🔗 **အလယ်တွဲများ** | `37 အလယ်`, `အလယ် ပါဝါ` | (Auto AM+PM ပေါင်းချုပ်) မနက်ပိတ်/ညနေထိပ် တွဲခြင်း |
            | 🛑 **ဘရိတ်များ** | `5 ဘရိတ်`, `0 ဘရိတ်` | (Manual ရွေးချယ်ရန်) ဂဏန်းအတိအကျပါသော ဘရိတ် |
            | 📦 **ဘရိတ်အုပ်စု** | `ဘရိတ်တူ`, `ဘရိတ် ပါဝါ` | (Auto AM+PM ပေါင်းချုပ်) ဘရိတ်တူ နှင့် ဘရိတ်အုပ်စုများ |
            | ↗️ **ဘရိတ် ဇောင်းတူ** | `ဘရိတ် ဇောင်းတူ`, `ဘရိတ် ဇောင်း ပါဝါ` | (Auto AM+PM ပေါင်းချုပ်) ရက်ဆက် ဒေါင့်ဖြတ်ဘရိတ်တူခြင်း |
            | ↕️ **ဘရိတ် ထက်အောက်**| `ဘရိတ် ထက်အောက်တူ`, `ဘရိတ် ထက်အောက် ညီကို`| (Manual ရွေးချယ်ရန်) ရက်ဆက် AM/PM အချင်းချင်း ဘရိတ်တူခြင်း |
            | 📐 **ဘရိတ် တြိဂံ** | `ဘရိတ် တြိဂံ` | (Auto AM+PM ပေါင်းချုပ်) ၄ ကြိမ်တွင် ၃ ကြိမ် ဘရိတ်တူညီခြင်း |
            | ⬆️ **ထိပ်/ပိတ်များ** | `6 ထိပ်`, `4 ပိတ်` | (Manual ရွေးချယ်ရန်) ရှေ့ဂဏန်း သို့မဟုတ် နောက်ဂဏန်း သတ်မှတ်ခြင်း |
            | 📦 **အုပ်စုများ** | `အပူး`, `ပါဝါ`, `နက္ခတ်`, `ညီကို` | (Manual ရွေးချယ်ရန်) အုပ်စုဝင် ဂဏန်းများ အားလုံးကို ရှာဖွေခြင်း |
            | 🧮 **သုံးလုံးတွဲ** | `139`, `058`, `442` | (Auto AM+PM ပေါင်းချုပ်) တစ်နေ့တာ ၄ လုံးထဲတွင် ၃ လုံးပါဝင်ခြင်း |
            """)

        if submit_custom:
            with st.spinner("🔍 အဆင့်မြင့် Data Mining Engine ဖြင့် သုတေသန ပြုလုပ်နေပါသည်..."):
                target_hits = []
                clean_trigger = trigger_num.strip()
                override_session = None

                # --- 1. MIDDLE GROUPS & MIDDLE PAIRS ---
                if "အလယ်" in clean_trigger:
                    override_session = "AM+PM ပေါင်းချုပ်"
                    grp_name = clean_trigger.replace("အလယ်", "").strip()
                    if grp_name in special_groups:
                        for r, pair in st.session_state.day_pairs.items():
                            if pair['AM'] and pair['PM'] and len(pair['AM']['draw']) >= 2 and len(pair['PM']['draw']) >= 2:
                                mid_pair = pair['AM']['draw'][1] + pair['PM']['draw'][0]
                                if mid_pair in special_groups[grp_name] or mid_pair[::-1] in special_groups[grp_name]:
                                    target_hits.append(pair['PM'])
                    else:
                        digits = "".join(re.findall(r'\d+', clean_trigger))
                        if len(digits) == 2:
                            for r, pair in st.session_state.day_pairs.items():
                                if pair['AM'] and pair['PM'] and len(pair['AM']['draw']) >= 2 and len(pair['PM']['draw']) >= 2:
                                    mid_pair = pair['AM']['draw'][1] + pair['PM']['draw'][0]
                                    if mid_pair == digits or mid_pair == digits[::-1]:
                                        target_hits.append(pair['PM'])

                # --- 2. BREAK TRIANGLE ---
                elif "တြိဂံ" in clean_trigger and "ဘရိတ်" in clean_trigger:
                    override_session = "AM+PM ပေါင်းချုပ်"
                    sorted_rows = sorted(st.session_state.day_pairs.keys())
                    for i in range(1, len(sorted_rows)):
                        prv = st.session_state.day_pairs[sorted_rows[i-1]]
                        cur = st.session_state.day_pairs[sorted_rows[i]]
                        b_list = [get_brk(prv['AM']), get_brk(prv['PM']), get_brk(cur['AM']), get_brk(cur['PM'])]
                        valid_b = [b for b in b_list if b is not None]
                        if len(valid_b) >= 3:
                            counts = Counter(valid_b)
                            if counts and max(counts.values()) >= 3: target_hits.append(cur['PM'])

                # --- 3. BREAK DIAGONAL (ဇောင်း) ---
                elif "ဇောင်း" in clean_trigger and "ဘရိတ်" in clean_trigger:
                    override_session = "AM+PM ပေါင်းချုပ်"
                    grp_name = clean_trigger.replace("ဘရိတ်", "").replace("ဇောင်း", "").replace("တူ", "").strip()
                    sorted_rows = sorted(st.session_state.day_pairs.keys())
                    for i in range(1, len(sorted_rows)):
                        prv = st.session_state.day_pairs[sorted_rows[i-1]]
                        cur = st.session_state.day_pairs[sorted_rows[i]]
                        am1, pm1 = get_brk(prv['AM']), get_brk(prv['PM'])
                        am2, pm2 = get_brk(cur['AM']), get_brk(cur['PM'])
                        
                        hit = False
                        if am1 and pm2:
                            if grp_name == "" and am1 == pm2: hit = True
                            elif grp_name in special_groups and ((am1 + pm2) in special_groups[grp_name] or (pm2 + am1) in special_groups[grp_name]): hit = True
                        if pm1 and am2:
                            if grp_name == "" and pm1 == am2: hit = True
                            elif grp_name in special_groups and ((pm1 + am2) in special_groups[grp_name] or (am2 + pm1) in special_groups[grp_name]): hit = True
                        if hit: target_hits.append(cur['PM'])

                # --- 4. BREAK VERTICAL (ထက်အောက်) ---
                elif "ထက်အောက်" in clean_trigger and "ဘရိတ်" in clean_trigger:
                    grp_name = clean_trigger.replace("ဘရိတ်", "").replace("ထက်အောက်", "").replace("တူ", "").strip()
                    sorted_rows = sorted(st.session_state.day_pairs.keys())
                    req_am = target_session_trigger in ["AM သီးသန့်", "AM+PM ပေါင်းချုပ်", "All"]
                    req_pm = target_session_trigger in ["PM သီးသန့်", "AM+PM ပေါင်းချုပ်", "All"]
                    
                    for i in range(1, len(sorted_rows)):
                        prv = st.session_state.day_pairs[sorted_rows[i-1]]
                        cur = st.session_state.day_pairs[sorted_rows[i]]
                        am1, pm1 = get_brk(prv['AM']), get_brk(prv['PM'])
                        am2, pm2 = get_brk(cur['AM']), get_brk(cur['PM'])
                        
                        if req_am and am1 and am2:
                            if grp_name == "" and am1 == am2: target_hits.append(cur['AM'])
                            elif grp_name in special_groups and ((am1 + am2) in special_groups[grp_name] or (am2 + am1) in special_groups[grp_name]): target_hits.append(cur['AM'])
                        if req_pm and pm1 and pm2:
                            if grp_name == "" and pm1 == pm2: target_hits.append(cur['PM'])
                            elif grp_name in special_groups and ((pm1 + pm2) in special_groups[grp_name] or (pm2 + pm1) in special_groups[grp_name]): target_hits.append(cur['PM'])

                # --- 5. BREAK GROUPS & SAME BREAK (Auto AM+PM) ---
                elif clean_trigger.startswith("ဘရိတ်") and not any(char.isdigit() for char in clean_trigger):
                    override_session = "AM+PM ပေါင်းချုပ်"
                    grp_name = clean_trigger.replace("ဘရိတ်", "").replace("တူ", "").strip()
                    for r, pair in st.session_state.day_pairs.items():
                        am, pm = get_brk(pair['AM']), get_brk(pair['PM'])
                        if am and pm:
                            if grp_name == "" and am == pm: target_hits.append(pair['PM'])
                            elif grp_name in special_groups and ((am + pm) in special_groups[grp_name] or (pm + am) in special_groups[grp_name]): target_hits.append(pair['PM'])
                
                # --- 6. STANDARD SINGLE BREAK (Manual Session) ---
                elif clean_trigger.endswith("ဘရိတ်") and clean_trigger.replace("ဘရိတ်", "").strip().isdigit():
                    b_val = clean_trigger.replace("ဘရိတ်", "").strip()
                    for d in st.session_state.full_draws:
                        if get_brk({'draw': d['draw']}) == b_val:
                            if target_session_trigger == "AM+PM ပေါင်းချုပ်" or "All" in target_session_trigger: target_hits.append(d)
                            elif "AM" in target_session_trigger and d['time'] == "AM": target_hits.append(d)
                            elif "PM" in target_session_trigger and d['time'] == "PM": target_hits.append(d)

                # --- 7. HEAD / TAIL ---
                elif "ထိပ်" in clean_trigger:
                    d_match = "".join(re.findall(r'\d+', clean_trigger))
                    if d_match: 
                        for d in st.session_state.full_draws:
                            if d['draw'].startswith(d_match):
                                if target_session_trigger == "AM+PM ပေါင်းချုပ်" or "All" in target_session_trigger: target_hits.append(d)
                                elif "AM" in target_session_trigger and d['time'] == "AM": target_hits.append(d)
                                elif "PM" in target_session_trigger and d['time'] == "PM": target_hits.append(d)
                                
                elif "ပိတ်" in clean_trigger:
                    d_match = "".join(re.findall(r'\d+', clean_trigger))
                    if d_match: 
                        for d in st.session_state.full_draws:
                            if d['draw'].endswith(d_match):
                                if target_session_trigger == "AM+PM ပေါင်းချုပ်" or "All" in target_session_trigger: target_hits.append(d)
                                elif "AM" in target_session_trigger and d['time'] == "AM": target_hits.append(d)
                                elif "PM" in target_session_trigger and d['time'] == "PM": target_hits.append(d)

                # --- 8. 3 DIGITS TODAY (Auto AM+PM) ---
                elif len(clean_trigger) == 3 and clean_trigger.isdigit():
                    override_session = "AM+PM ပေါင်းချုပ်"
                    req_set = set(clean_trigger)
                    for r, pair in st.session_state.day_pairs.items():
                        if pair['AM'] and pair['PM']:
                            if req_set.issubset(set(pair['AM']['draw'] + pair['PM']['draw'])): target_hits.append(pair['PM'])

                # --- 9. GROUPS ---
                elif clean_trigger in special_groups:
                    for d in st.session_state.full_draws:
                        if d['draw'] in special_groups[clean_trigger]:
                            if target_session_trigger == "AM+PM ပေါင်းချုပ်" or "All" in target_session_trigger: target_hits.append(d)
                            elif "AM" in target_session_trigger and d['time'] == "AM": target_hits.append(d)
                            elif "PM" in target_session_trigger and d['time'] == "PM": target_hits.append(d)

                # --- 10. EXACT MATCH (ဒဲ့ / R) ---
                else:
                    is_straight = "ဒဲ့" in clean_trigger
                    is_r = "R" in clean_trigger or "r" in clean_trigger.lower()
                    digits = "".join(re.findall(r'\d+', clean_trigger))
                    
                    if digits:
                        for d in st.session_state.full_draws:
                            match = False
                            if is_straight:
                                if d['draw'] == digits: match = True
                            elif is_r:
                                if d['draw'] == digits or d['draw'] == digits[::-1]: match = True
                            else:
                                if d['draw'] == digits or d['draw'] == digits[::-1]: match = True
                                
                            if match:
                                if target_session_trigger == "AM+PM ပေါင်းချုပ်" or "All" in target_session_trigger: target_hits.append(d)
                                elif "AM" in target_session_trigger and d['time'] == "AM": target_hits.append(d)
                                elif "PM" in target_session_trigger and d['time'] == "PM": target_hits.append(d)

                # Post Process Targets
                final_hits = {}
                for h in target_hits:
                    if trigger_day == "All" or h['day'] == trigger_day:
                        final_hits[h['index']] = h
                target_hits = [final_hits[k] for k in sorted(final_hits.keys())]

                if not target_hits:
                    st.error("⚠️ သတ်မှတ်ချက်များနှင့် ကိုက်ညီသော သမိုင်းကြောင်းမှတ်တမ်း မရှိပါ Bro!")
                else:
                    lbl_custom = f"{trigger_num} ({trigger_day if trigger_day != 'All' else 'ပေါင်းချုပ်'})"
                    
                    if override_session:
                        sessions_to_run = [override_session]
                    else:
                        sessions_to_run = ["AM+PM ပေါင်းချုပ်", "AM သီးသန့်", "PM သီးသန့်"] if search_space == "All" else [search_space]
                    
                    for current_session in sessions_to_run:
                        st.markdown(f"<div class='section-title'>📊 {current_session} ရလဒ်များ ({min_rate_param}% - 100%)</div>", unsafe_allow_html=True)
                        master_step_res, _ = execute_analysis(target_hits, st.session_state.full_draws, custom_max_tf, is_custom_tab=True, search_session=current_session, custom_trigger=lbl_custom, mode=custom_mode, is_research_mode=True, min_rate_threshold=float(min_rate_param))
                        
                        has_data = any(master_step_res[sk] for sk in master_step_res if sk <= custom_max_tf)
                        if not has_data:
                            st.info(f"[{current_session}] အတွင်း သတ်မှတ် % ဖြင့် ကိုက်ညီမည့်မူ မတွေ့ပါ။")
                        else:
                            for step in sorted(master_step_res.keys()):
                                if step > custom_max_tf: continue
                                formulas_dict = master_step_res[step]
                                if not formulas_dict: continue
                                
                                is_step_deadline = any(v['is_deadline'] for v in formulas_dict.values())
                                h_space = "နံနက်ပိုင်း " if current_session == "AM သီးသန့်" else ("ညနေပိုင်း " if current_session == "PM သီးသန့်" else "")
                                tab2_header = f"⚠️ {h_space}{step} ပွဲအတွင်း မူများ [ရက်ချိန်းပြည့်]" if is_step_deadline else f"🔽 {h_space}{step} ပွဲအတွင်း မူများ"
                                
                                with st.expander(tab2_header, expanded=True):
                                    for mu_name, data in formulas_dict.items():
                                        card_border = "card-sniper" if "100%" in data['formula'] else "card-hp"
                                        badge_class = "badge-inline-sniper" if "100%" in data['formula'] else "badge-inline-hp"
                                        st.markdown(f"""
                                        <div class="card {card_border}">
                                            <span class="line-trigger">{data["top"]} <span class='badge-inline {badge_class}'>{data['label_space']}{step} ပွဲအတွင်း</span></span>
                                            <span class="line-formula">{data["formula"]}</span>
                                            <span class="line-focus">{data["focus_range"]}</span>
                                            <span class="line-history">{data["bottom"]}</span>
                                            <span class="line-advisor">{data["advisor"]}</span>
                                            {data.get('risk_note', '')}
                                        </div>
                                        """, unsafe_allow_html=True)
else:
    st.info("စတင်ရန်အတွက် Bro ရဲ့ 2D CSV သို့မဟုတ် Excel ဒေတာဖိုင်ကို အပေါ်တွင် တင်ပေးပါ။")
