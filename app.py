import streamlit as st
import pandas as pd
import io
import itertools
import re
from collections import Counter

# ==========================================
# PAGE CONFIG & PREMIUM DARK-THEME STYLE
# ==========================================
st.set_page_config(page_title="2D AI Master V34.1 Priority", layout="wide", page_icon="🤖")

st.markdown("""
<style>
    .stApp { background-color: #0B031A; color: #E0D5FA; }
    .main-title { color: #A078FF; font-size: 40px; font-weight: bold; text-align: center; margin-bottom: 5px; text-shadow: 0 0 10px rgba(160,120,255,0.5); }
    .sub-title { color: #8F72D6; font-size: 16px; text-align: center; margin-bottom: 30px; }
    
    .card { background-color: #170E2B; padding: 20px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); margin-bottom: 15px; border: 1px solid #2D1B4E; }
    .card-live { border-left: 6px solid #3498db; background-color: #0E1A2F; margin-bottom: 15px; }
    .card-hp { border-left: 6px solid #2ecc71; background-color: #0D2216; }
    .card-deadline { border-left: 6px solid #e74c3c; background-color: #31151A; margin-bottom: 10px; }
    .card-sniper { border-left: 6px solid #9b59b6; background-color: #201135; }
    .card-recovery { border-left: 6px solid #e67e22; background-color: #2D1A0E; margin-bottom: 10px; }
    .card-intersection { border: 2px dashed #FFD700; background-color: #1A180B; text-align: center; padding: 20px; border-radius: 12px; box-shadow: 0 0 15px rgba(255,215,0,0.15); margin-top: 15px;}
    
    .line-trigger { font-size: 18px; font-weight: bold; color: #E0D5FA; margin-bottom: 6px; display: block; }
    .line-formula { font-size: 22px; font-weight: bold; color: #FFD700; margin-bottom: 6px; display: block; }
    .line-history { font-size: 15px; color: #A294C7; display: block; }
    .line-advisor { font-size: 16px; color: #00FFCC; font-style: italic; margin-top: 10px; display: block; border-top: 1px dashed #3D2B5E; padding-top: 8px; }
    
    .badge-inline { padding: 2px 10px; border-radius: 6px; font-size: 14px; font-weight: bold; margin-left: 6px; margin-right: 6px; display: inline-block; vertical-align: middle; }
    .badge-inline-sniper { background-color: #9b59b6; color: white; }
    .badge-inline-hp { background-color: #2ecc71; color: #0D2216; }
    .badge-inline-danger { background-color: #e74c3c; color: white; }
    .badge-super { background-color: #FFD700; color: #000; padding: 3px 8px; border-radius: 5px; font-weight: bold; }
    .badge-second { background-color: #C0C0C0; color: #000; padding: 3px 8px; border-radius: 5px; font-weight: bold; }
    
    .final-digits { font-size: 26px; font-weight: bold; color: #FFD700; display: block; margin-top: 15px; line-height: 1.5; }
    .score-badge { background-color: #333; color: #fff; font-size: 16px; padding: 4px 8px; border-radius: 6px; margin-left: 8px; margin-right: 15px; vertical-align: middle; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🤖 THE PERFECT 2D AI MASTER (V34.1)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Custom Anchor | Auto-R Day System | Deadline Priority Dashboard</div>', unsafe_allow_html=True)

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
# HELPER: NORMALIZE & CHECK FORMULAS
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
    all_heads = [d[0] for d in analysis_pool]
    all_tails = [d[1] for d in analysis_pool]
    all_breaks = [str((int(d[0]) + int(d[1])) % 10) for d in analysis_pool]

    top_single = Counter(all_singles).most_common(1)[0][0] if all_singles else ""
    top_oc = "".join([x[0] for x in Counter(all_singles).most_common(2)]) if len(Counter(all_singles)) >= 2 else top_single
    top_key3 = "".join([x[0] for x in Counter(all_singles).most_common(3)]) if len(Counter(all_singles)) >= 3 else top_oc
    top_k4 = "".join([x[0] for x in Counter(all_singles).most_common(4)]) if len(Counter(all_singles)) >= 4 else top_key3
    
    top_h3 = [x[0] for x in Counter(all_heads).most_common(3)]
    best_tails = [x[0] for x in Counter([d[1] for d in analysis_pool if d[0] in top_h3]).most_common(5)][:4]
    head_formula_str = f"{''.join(top_h3)} ထိပ် / {','.join(best_tails)} ကပ်" if top_h3 else "-"

    top_t3 = [x[0] for x in Counter(all_tails).most_common(3)]
    best_heads = [x[0] for x in Counter([d[0] for d in analysis_pool if d[1] in top_t3]).most_common(5)][:4]
    tail_formula_str = f"{''.join(top_t3)} ပိတ် / {','.join(best_heads)} ကပ်" if top_t3 else "-"

    top_brk2 = [x[0] for x in Counter(all_breaks).most_common(2)]
    if len(top_brk2) < 2 and top_brk2: top_brk2.append(str((int(top_brk2[0])+1)%10))
    
    e_sc = sum(1 for d in analysis_pool if top_single in d and int(d.replace(top_single,'',1) or top_single) % 2 == 0)
    o_sc = sum(1 for d in analysis_pool if top_single in d and int(d.replace(top_single,'',1) or top_single) % 2 != 0)
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

# ==========================================
# HYBRID PRE-FILTERING
# ==========================================
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

# ==========================================
# MASTER ROUTINE: INSTANCE WIN-RATE ENGINE
# ==========================================
def execute_analysis(target_hits, full_draws, requested_max_step, is_custom_tab=False, sel_session="All", custom_trigger="", strict_day_mode=False, mode="AI Trend", is_research_mode=False):
    step_buckets = {step: {} for step in range(1, requested_max_step + 1)}
    current_latest_idx = len(full_draws) - 1
    total_count = len(target_hits)
    if total_count == 0: return step_buckets, []

    recovery_pool = [] 
    calendar_candidates = get_hybrid_candidates(target_hits, full_draws, requested_max_step) if mode == "Calendar သီးသန့်မူများ (Fixed Pattern)" else {}

    for mu_k in mu_keys_list:
        cand_list = calendar_candidates.get(mu_k, []) if mode == "Calendar သီးသန့်မူများ (Fixed Pattern)" else ["DYNAMIC_AI"]
        
        for cand_val in cand_list:
            hit_steps_across_history = []
            actual_hit_combinations = []
            last_generated_val = cand_val

            for hit in target_hits:
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
                    is_hit, matched_draw = is_already_hit(mu_k, current_val, t_idx, t_idx, full_draws)
                    if is_hit:
                        if is_custom_tab and "သီးသန့်" in sel_session and full_draws[t_idx]['time'] != ("AM" if "AM" in sel_session else "PM"): continue 
                        found_hit_step = step_check
                        actual_hit_combinations.append(matched_draw)
                        break
                hit_steps_across_history.append(found_hit_step if found_hit_step is not None else 999)

            valid_spans = [s for s in hit_steps_across_history if s <= requested_max_step]
            if not valid_spans or last_generated_val == "-": continue
            
            max_required_span = max(valid_spans)
            successful_hits = sum(1 for s in hit_steps_across_history if s <= max_required_span)
            rate = (successful_hits / total_count) * 100

            if rate < 90.0 or total_count < 10: continue

            lbl_prefix = custom_trigger if is_custom_tab else f"{target_hits[-1]['draw']} {target_hits[-1]['time']}"
            
            is_deadline_flag = False
            rem_steps = 999
            if target_hits:
                last_hit_global_idx = target_hits[-1]['index']
                elapsed_draws = current_latest_idx - last_hit_global_idx
                rem_steps = max_required_span - elapsed_draws - 1
                if rem_steps == 0: is_deadline_flag = True
                
                if not is_research_mode:
                    if elapsed_draws >= max_required_span: continue 
                    if elapsed_draws > 0 and is_already_hit(mu_k, last_generated_val, last_hit_global_idx + 1, current_latest_idx, full_draws)[0]: continue

            sniper_note = f"💡 အဖြစ်နိုင်ဆုံး ၃/၄ ကွက်: {', '.join([x[0] for x in Counter(actual_hit_combinations).most_common(4)])}" if actual_hit_combinations else ""

            card_payload = {
                "top": f"🔮 [{lbl_prefix}] ထွက်ပြီးလျှင်", "formula": f"{last_generated_val} {'100%' if rate == 100.0 else f'{rate:.1f}%'}", 
                "bottom": f"မှန်ကန်မှု: ({total_count} ကြိမ်မှာ {successful_hits} ကြိမ်မှန်)", "is_deadline": is_deadline_flag, 
                "pure": last_generated_val, "mu_k": mu_k, "advisor": sniper_note, "rate": rate, "max_span": max_required_span, "lbl_prefix": lbl_prefix
            }
            
            # Populate step_buckets exclusively for Deadlines (in Tab 1) or All (in Tab 2)
            if is_research_mode or is_deadline_flag:
                step_buckets[max_required_span][last_generated_val if mode == "Calendar သီးသန့်မူများ (Fixed Pattern)" else mu_k] = card_payload
            
            if not is_research_mode and rem_steps in [1, 2]:
                recovery_pool.append({"key": last_generated_val, "lbl_prefix": lbl_prefix, "rem_steps": rem_steps, "score": 80 if rem_steps == 1 else 50, "card": card_payload})

    return step_buckets, recovery_pool

# ==========================================
# FILE UPLOAD & UI
# ==========================================
uploaded_file = st.file_uploader("Bro ရဲ့ 2D CSV သို့မဟုတ် Excel ဖိုင်ကို ရွေးချယ်တင်ပေးပါ...", type=['csv', 'xlsx', 'xls'])

if uploaded_file:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip().str.lower()
    
    if not all(col in df.columns for col in ['year', 'day', 'am1', 'am2', 'pm1', 'pm2']):
        st.error("⚠️ Phineထဲတွင် လိုအပ်သော ကော်လံများ (year, day, am1, am2, pm1, pm2) မပြည့်စုံပါ!")
    else:
        for col in ['year', 'am1', 'am2', 'pm1', 'pm2']: df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df.dropna(subset=['year', 'day']).reset_index(drop=True)
        df['day'] = df['day'].astype(str).str.strip().str.capitalize()

        full_days = ["Mon", "Tue", "Wed", "Thur", "Fri"]
        existing_days = set(df['day'].unique())
        off_days = [d for d in full_days if d not in existing_days]
        if off_days: st.info(f"ℹ️ သတိပြုရန်: ဒေတာထဲတွင် {', '.join(off_days)} ကို ပိတ်ရက်အဖြစ် သတ်မှတ်ထားပါသည်။")

        full_draws = []
        for idx, row in df.iterrows():
            if pd.notna(row['am1']) and pd.notna(row['am2']):
                full_draws.append({'draw': f"{int(row['am1'])}{int(row['am2'])}", 'time': 'AM', 'day': row['day'], 'row_idx': idx})
            if pd.notna(row['pm1']) and pd.notna(row['pm2']):
                full_draws.append({'draw': f"{int(row['pm1'])}{int(row['pm2'])}", 'time': 'PM', 'day': row['day'], 'row_idx': idx})

        for i, d in enumerate(full_draws): d['index'] = i
        last_recorded_draw = full_draws[-1]
        active_days_cycle = [d for d in full_days if d not in off_days]
        
        target_day_name = last_recorded_draw['day'] if last_recorded_draw['time'] == 'AM' else active_days_cycle[(active_days_cycle.index(last_recorded_draw['day']) + 1) % len(active_days_cycle)]
        target_time_name = "PM" if last_recorded_draw['time'] == 'AM' else "AM"
            
        st.success(f"🔮 ဒေတာပွဲစဉ်ပေါင်း {len(full_draws)} ခု ဖတ်ပြီးပါပြီ။ [{target_day_name} {target_time_name}] အတွက် တွက်ချက်မည်ဖြစ်ပါသည်။")
        st.write("---")

        tab_live, tab_custom = st.tabs(["⚡ တွက်ချက်မည် (ယခုပွဲစဉ်)", "🔍 2D Formulas (Custom)"])

        # ------------------------------------------
        # TAB 1: LIVE AUTO TRACKER (3 Inputs System + Auto-R)
        # ------------------------------------------
        with tab_live:
            st.markdown("#### ⚙️ VIP ရှာဖွေမှု သတ်မှတ်ချက်များ (Inputs)")
            c1, c2 = st.columns(2)
            with c1:
                anchor_count = st.number_input("📌 အနှစ်ချုပ်ကြည့်ရှုလိုသော မူအရေအတွက် (Default: 10):", min_value=1, max_value=50, value=10)
            with c2:
                live_max_tf = st.number_input("⏳ စစ်ဆေးမည့် ပွဲစဉ်အရေအတွက် [Max Span] (Default: 20):", min_value=1, max_value=50, value=20)
                
            custom_anchors_str = st.text_input("🎯 စိတ်ကြိုက် အမာခံဂဏန်းများ (ဥပမာ - 48, 60, 62) [ရိုက်ထည့်ပါက Auto စနစ်ကို ကျော်လွန်မည်]:", value="")
            
            c1_mode, _ = st.columns([1, 1])
            with c1_mode:
                live_mode = st.radio("🧠 AI တွက်ချက်မှုစနစ် ရွေးချယ်ရန်:", ["AI Trend (ရှေ့သမိုင်း ၅၀ အထိုင်)", "Calendar သီးသန့်မူများ (Fixed Pattern)"], horizontal=True, key="live_mode")

            if st.button("VIP ကို ယခုရှာဖွေမည် ⚡", key="btn_auto"):
                selected_anchors = []
                
                # Auto Clean-up & Fetch Latest Occurrences
                if custom_anchors_str.strip():
                    raw_nums = [x.strip() for x in custom_anchors_str.split(',') if x.strip().isdigit()]
                    if not raw_nums:
                        st.warning("⚠️ စိတ်ကြိုက် ဂဏန်းများ မှားယွင်းနေပါသည်။ Auto စနစ်ဖြင့် ဆက်လက်တွက်ချက်ပါမည်။")
                        selected_anchors = full_draws[-anchor_count:]
                    else:
                        for n in raw_nums:
                            latest_hit = next((d for d in reversed(full_draws) if d['draw'] == n), None)
                            if latest_hit: selected_anchors.append(latest_hit)
                        st.info(f"🎯 ရွေးချယ်ထားသော အမာခံ (နောက်ဆုံးထွက်ခဲ့သည့် အကြိမ်များ): {', '.join([d['draw'] for d in selected_anchors])}")
                else:
                    selected_anchors = full_draws[-anchor_count:]
                
                if not selected_anchors:
                    st.error("⚠️ အမာခံ ဂဏန်းများ ရှာမတွေ့ပါ။")
                else:
                    scoring_pool = {}
                    global_recovery = {}
                    
                    for past_obj in selected_anchors:
                        past_val = past_obj['draw']
                        past_val_r = past_val[::-1]  # Auto R variable
                        past_time = past_obj['time']
                        past_day = past_obj['day']
                        
                        condition_pools = [
                            {"hits": [d for d in full_draws if d['draw'] == past_val and d['time'] == past_time], "lbl": f"{past_val} {past_time} စစ်စစ်"},
                            {"hits": [d for d in full_draws if d['draw'] == past_val], "lbl": f"{past_val} ပေါင်းချုပ်"},
                            {"hits": [d for d in full_draws if (d['draw'] == past_val or d['draw'] == past_val_r) and d['day'] == past_day], "lbl": f"{past_val}R {past_day} သီးသန့်"}
                        ]
                        
                        for pool in condition_pools:
                            if not pool['hits']: continue
                            
                            step_res, rec_pool = execute_analysis(
                                pool['hits'], full_draws, live_max_tf, 
                                is_custom_tab=True, sel_session="All", 
                                custom_trigger=pool['lbl'], mode=live_mode, is_research_mode=False
                            )
                            
                            # Deadline hits are collected here
                            for step_dist, formulas_dict in step_res.items():
                                for mk, mv in formulas_dict.items():
                                    f_key = mv['pure']
                                    if f_key not in scoring_pool:
                                        scoring_pool[f_key] = {'count': 0, 'details': [], 'mu_k': mv['mu_k']}
                                    
                                    existing_lbls = [d['top'] for d in scoring_pool[f_key]['details']]
                                    if mv['top'] not in existing_lbls:
                                        scoring_pool[f_key]['details'].append(mv)
                                        scoring_pool[f_key]['count'] += 1

                            for rp in rec_pool:
                                r_key = rp['key']
                                if r_key not in global_recovery:
                                    global_recovery[r_key] = {'score': 0, 'rem_steps': rp['rem_steps'], 'details': []}
                                
                                existing_r_lbls = [d['top'] for d in global_recovery[r_key]['details']]
                                if rp['card']['top'] not in existing_r_lbls:
                                    global_recovery[r_key]['details'].append(rp['card'])
                                    global_recovery[r_key]['score'] += rp['score']
                                    if len(global_recovery[r_key]['details']) >= 2:
                                        global_recovery[r_key]['score'] = global_recovery[r_key]['score'] * 2

                    # Separate Overlaps from Standalone Deadline Hits
                    valid_vips = {k: v for k, v in scoring_pool.items() if v['count'] >= 2}
                    deadline_singles = {k: v for k, v in scoring_pool.items() if v['count'] == 1}
                    
                    st.write("---")
                    st.markdown("#### 🏆 VIP ဆုံးဖြတ်ချက် (Super & Second Overlaps)")
                    
                    if valid_vips:
                        sorted_scores = sorted(valid_vips.items(), key=lambda x: x[1]['count'], reverse=True)
                        for b_val, b_data in sorted_scores:
                            tier = "Super VIP" if b_data['count'] >= 3 else "Second VIP"
                            badge = "badge-super" if tier == "Super VIP" else "badge-second"
                                
                            with st.expander(f"⭐ {tier}: {b_val} (တူညီမှု: {b_data['count']} ခု)", expanded=False):
                                st.markdown(f"<span class='{badge}'>{tier}</span><div style='color:#00FFCC; font-size:14px; margin-top:10px; margin-bottom:10px;'>💡 ဤမူကို အောက်ပါ ထောက်တိုင်များက ဘုံတူညီစွာ ညွှန်ပြနေပါသည်-</div>", unsafe_allow_html=True)
                                for d_detail in b_data['details']:
                                    span_class = "badge-inline-sniper" if d_detail['rate'] == 100.0 else "badge-inline-hp"
                                    st.markdown(f"""
                                    <div class="card card-live" style="padding:10px; margin-bottom:10px;">
                                        <span style="font-size:16px; font-weight:bold; color:#E0D5FA;">{d_detail['top']}</span>
                                        <span class='badge-inline {span_class}'>{d_detail['max_span']} ပွဲအတွင်း (ယခုပွဲစဉ် ရက်ချိန်းပြည့်)</span>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                        st.write("---")
                        st.markdown("#### 🎯 အတိကျဆုံး အကြံပြု Final ဂဏန်းများ (Weighted Scoring)")
                        
                        final_scores = {f"{i:02d}": 0 for i in range(100)}
                        for b_val, b_data in sorted_scores:
                            weight = b_data['count']
                            mu_k = b_data['mu_k']
                            for d in final_scores.keys():
                                if check_single_draw_against_formula(d, mu_k, b_val):
                                    final_scores[d] += weight
                                    
                        sorted_final_digits = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
                        top_scoring_digits = [k for k, v in sorted_final_digits[:5] if v > 0]
                        
                        if top_scoring_digits:
                            digit_display = ""
                            for d, s in sorted_final_digits[:5]:
                                if s > 0: digit_display += f"<span style='display:inline-block; margin-bottom: 8px;'>{d} <span class='score-badge'>Score: {s}</span></span>"
                            st.markdown(f"""
                            <div class="card card-intersection">
                                <span style="color:#A294C7; font-size:15px; display:block;">VIP မူများအားလုံးကို အမှတ်ပေး ချိန်ခွင်လျှာညှိပြီး ရွေးချယ်ထားသော (Top 5) အကွက်များ:</span>
                                <div class="final-digits">{digit_display}</div>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.info("Intersection အမှတ်ပေးစနစ်ဖြင့် ရွေးချယ်ရန် လုံလောက်သော VIP မူ မရှိပါ။")
                            
                    else:
                        st.markdown("<div style='font-size:15px; font-weight:bold; color:#A294C7; padding:10px;'>ခိုင်မာသော VIP တူညီမှု ရလဒ်မရှိပါ (အနည်းဆုံး တိုက်ဆိုင်မှု ၂ ခု လိုအပ်ပါသည်)</div>", unsafe_allow_html=True)

                    st.write("---")
                    st.markdown("#### ⚠️ ရက်ချိန်းပြည့် မူများ (Standalone Deadline Hits)")
                    if deadline_singles:
                        for d_key, d_data in deadline_singles.items():
                            item = d_data['details'][0]
                            st.markdown(f"""
                            <div class="card card-deadline" style="padding:12px;">
                                <span style="font-size:16px; font-weight:bold; color:#fff;">🔴 [{item['lbl_prefix']}] {d_key}</span><br/>
                                <span style="font-size:14px; color:#e74c3c; margin-top:5px; display:block;">
                                    ⏳ သမိုင်းစံချိန်အရ ယခုပွဲစဉ် ရက်ချိန်းကွက်တိပြည့်နေပါသည် ({item['max_span']} ပွဲမြောက်)
                                </span>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("ယခုပွဲစဉ်အတွက် သီးသန့် ရက်ချိန်းပြည့်နေသော မူများ မရှိပါ။")

                    st.write("---")
                    st.markdown("#### 🛡️ Recovery & စောင့်ကြည့်ရမည့် မူကျန်များ (Top 5)")
                    if global_recovery:
                        sorted_recovery = sorted(global_recovery.items(), key=lambda x: x[1]['score'], reverse=True)[:5]
                        for r_key, r_data in sorted_recovery:
                            rem_txt = "၁ ပွဲသာ လိုတော့သည်" if r_data['rem_steps'] == 1 else "၂ ပွဲ လိုသေးသည်"
                            overlap_txt = f" (ထောက်တိုင် {len(r_data['details'])} ခုငြိနေသည်)" if len(r_data['details']) > 1 else ""
                            icon = "🟠" if r_data['score'] >= 80 else "🟡"
                            
                            display_lbl = r_data['details'][0]['lbl_prefix']
                            
                            st.markdown(f"""
                            <div class="card card-recovery" style="padding:12px;">
                                <span style="font-size:16px; font-weight:bold; color:#fff;">{icon} Score: {r_data['score']} | [{display_lbl}] {r_key}</span><br/>
                                <span style="font-size:14px; color:#f39c12; margin-top:5px; display:block;">⏳ {rem_txt} {overlap_txt}</span>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("၁ ပွဲ သို့မဟုတ် ၂ ပွဲ အလိုရှိသော ခိုင်မာသည့် မူကျန်များ မရှိပါ။")

        # ------------------------------------------
        # TAB 2: CUSTOM FORMULAS ENGINE (Research Lab)
        # ------------------------------------------
        with tab_custom:
            st.markdown("##### 🧠 တွက်ချက်မှုစနစ် (Mode) ရွေးချယ်ရန်")
            custom_mode = st.radio("", ["AI Trend (ရှေ့သမိုင်း ၅၀ အထိုင်)", "Calendar သီးသန့်မူများ (Fixed Pattern)"], horizontal=True, key="custom_mode_tab2")
            st.write("---")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                trigger_day = st.selectbox("📆 Trigger Day:", ["All"] + active_days_cycle, index=0)
                trigger_num = st.text_input("🔍 ရှာလိုသောဂဏန်း ရိုက်ထည့်ပါ:", value="01", max_chars=7)
            with c2:
                if trigger_day != "All":
                    st.markdown("<span style='color:#00FFCC; font-size:13px;'>ℹ️ Day စနစ်သုံးထားသဖြင့် အကြိမ်ရေပြည့်မီစေရန် R-စနစ် နှင့် AM+PM ပေါင်းချုပ် စနစ်ကို Backend က Auto Lock ချပေးထားပါသည်။</span>", unsafe_allow_html=True)
                    target_session_custom = "AM+PM ပေါင်းချုပ်"
                else:
                    target_session_custom = st.selectbox("⏱️ Target ပွဲစဉ် အခြေအနေ ရွေးရန်:", ["AM+PM ပေါင်းချုပ်", "AM သီးသန့်", "PM သီးသန့်"], index=2)
            with c3:
                custom_max_tf = st.number_input("⏳ စစ်ဆေးမည့် ပွဲစဉ်အရေအတွက်", min_value=1, max_value=25, value=16, key="custom_input_tf2")

            if st.button("ရှာဖွေမည် 🚀", key="btn_custom_tab2"):
                target_hits = []
                clean_trigger = trigger_num.strip().upper()
                is_composite = "+" in clean_trigger or "R" in clean_trigger or (trigger_day != "All")
                digits_found = re.findall(r'\d+', clean_trigger)
                
                if digits_found:
                    primary_digit = digits_found[0]
                    if trigger_day == "All":
                        if is_composite:
                            secondary_digit = digits_found[1] if len(digits_found) > 1 else primary_digit[::-1]
                            target_hits = [d for d in full_draws if d['draw'] == primary_digit or d['draw'] == secondary_digit]
                        else:
                            if target_session_custom != "AM+PM ပေါင်းချုပ်" and "သီးသန့်" in target_session_custom:
                                req_time_init = "AM" if "AM" in target_session_custom else "PM"
                                target_hits = [d for d in full_draws if d['draw'] == primary_digit and d['time'] == req_time_init]
                            else:
                                target_hits = [d for d in full_draws if d['draw'] == primary_digit]
                    else:
                        secondary_digit = digits_found[1] if len(digits_found) > 1 else primary_digit[::-1]
                        matched_weeks = {d['row_idx'] for d in full_draws if d['day'] == trigger_day and (d['draw'] == primary_digit or d['draw'] == secondary_digit)}
                        for d in full_draws:
                            if d['row_idx'] in matched_weeks:
                                target_hits.append(d)
                
                if trigger_day == "All" and target_session_custom != "AM+PM ပေါင်းချုပ်" and len(target_hits) > 0:
                    req_time_filter = "AM" if "AM" in target_session_custom else "PM"
                    target_hits = [h for h in target_hits if h['time'] == req_time_filter]

                r_val = "R" if (trigger_day != "All" and "R" not in trigger_num) else ""
                d_val = trigger_day if trigger_day != "All" else ""
                t_time_label = "PM" if target_session_custom == "PM သီးသန့်" else "AM" if target_session_custom == "AM သီးသန့်" else ""
                lbl_prefix_custom = f"{trigger_num}{r_val} {d_val} {t_time_label}".strip()

                if not target_hits:
                    st.error("⚠️ သတ်မှတ်ချက်များနှင့် ကိုက်ညီသော သမိုင်းကြောင်းမှတ်တမ်း မရှိပါ Bro!")
                else:
                    st.write("---")
                    st.markdown(f"#### 📋 အသေးစိတ်အချက်အလက် (Window အလိုက် ခေါက်သိမ်းစနစ် - {custom_mode})")
                    
                    master_step_res, _ = execute_analysis(
                        target_hits, full_draws, custom_max_tf, 
                        is_custom_tab=True, sel_session=target_session_custom, 
                        custom_trigger=lbl_prefix_custom, strict_day_mode=(trigger_day != "All"),
                        mode=custom_mode, is_research_mode=True
                    )
                    
                    has_any_tab2_data = any(master_step_res[sk] for sk in master_step_res if sk <= custom_max_tf)
                    
                    if not has_any_tab2_data:
                        st.info("သတ်မှတ်ထားသော ၉၀% အထက် ရက်ချိန်းနယ်ကုန် သတ်မှတ်ချက်အတွင်း ကိုက်ညီမည့် မူရင်းမှတ်တမ်း မတွေ့ရှိပါ Bro!")
                    else:
                        for step in sorted(master_step_res.keys()):
                            if step > custom_max_tf: continue 
                            formulas_dict = master_step_res[step]
                            if not formulas_dict: continue
                            
                            is_step_deadline = any(v['is_deadline'] for v in formulas_dict.values())
                            tab2_header = f"⚠️ {step} ပွဲအတွင်း မူများ [ရက်ချိန်းပြည့်]" if is_step_deadline else f"🔽 {step} ပွဲအတွင်း မူများ"
                                
                            with st.expander(tab2_header, expanded=True):
                                for mu_name, data in formulas_dict.items():
                                    card_border_class = "card-sniper" if "100%" in data['formula'] else "card-hp"
                                    badge_class = "badge-inline-sniper" if "100%" in data['formula'] else "badge-inline-hp"
                                    span_tag = f"<span class='badge-inline {badge_class}'>{step} ပွဲအတွင်း</span>"
                                    
                                    st.markdown(f"""
                                    <div class="card {card_border_class}">
                                        <span class="line-trigger">{data['top']} {span_tag}</span>
                                        <span class="line-formula">{data['formula']}</span>
                                        <span class="line-history">{data['bottom']}</span>
                                        <span class="line-advisor">{data['advisor']}</span>
                                    </div>
                                    """, unsafe_allow_html=True)
else:
    st.info("စတင်ရန်အတွက် Bro ရဲ့ 2D CSV သို့မဟုတ် Excel ဒေတာဖိုင်ကို အပေါ်တွင် အရင် တင်ပေးပါဦး။")
