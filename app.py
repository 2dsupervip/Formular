import streamlit as st
import pandas as pd
import io
import itertools
import re
from collections import Counter

# ==========================================
# PAGE CONFIG & PREMIUM DARK-THEME STYLE
# ==========================================
# ဖုန်းနဲ့ ကြည့်ရလွယ်အောင် layout="centered" သို့ ပြောင်းထားပါသည်
st.set_page_config(page_title="2D AI Master V35.3 All-in-One", layout="centered", page_icon="🤖")

st.markdown("""
<style>
    .stApp { background-color: #0B031A; color: #E0D5FA; }
    .main-title { color: #A078FF; font-size: 32px; font-weight: bold; text-align: center; margin-bottom: 5px; text-shadow: 0 0 10px rgba(160,120,255,0.5); }
    .sub-title { color: #8F72D6; font-size: 14px; text-align: center; margin-bottom: 30px; }
    
    .card { background-color: #170E2B; padding: 20px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); margin-bottom: 15px; border: 1px solid #2D1B4E; }
    .card-live { border-left: 6px solid #3498db; background-color: #0E1A2F; margin-bottom: 15px; }
    .card-hp { border-left: 6px solid #2ecc71; background-color: #0D2216; }
    .card-deadline { border-left: 6px solid #e74c3c; background-color: #31151A; margin-bottom: 10px; }
    
    .line-trigger { font-size: 16px; font-weight: bold; color: #E0D5FA; margin-bottom: 6px; display: block; }
    .line-formula { font-size: 20px; font-weight: bold; color: #FFD700; margin-bottom: 6px; display: block; }
    .line-history { font-size: 14px; color: #A294C7; display: block; }
    .line-advisor { font-size: 14px; color: #00FFCC; font-style: italic; margin-top: 10px; display: block; border-top: 1px dashed #3D2B5E; padding-top: 8px; }
    
    .badge-super { background-color: #FFD700; color: #000; padding: 4px 10px; border-radius: 6px; font-weight: bold; font-size: 16px; display: block; text-align: center; margin-bottom: 10px;}
    .section-title { color: #00FFCC; font-size: 20px; border-bottom: 2px solid #3D2B5E; padding-bottom: 8px; margin-top: 20px; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🤖 THE PERFECT 2D AI MASTER (V35.3)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">All-in-One Search Expansion | True Deadline Logic | Engine Sync</div>', unsafe_allow_html=True)

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
    except Exception as e:
        # Error တိတ်တဆိတ်ကျော်မသွားစေရန် Warning ပြပေးမည်
        st.warning(f"Error parsing formula for {mu_k}: {e}")
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

def execute_analysis(target_hits, full_draws, requested_max_step, is_custom_tab=False, search_session="All", custom_trigger="", mode="AI Trend", is_research_mode=False):
    step_buckets = {step: {} for step in range(1, requested_max_step + 1)}
    current_latest_idx = len(full_draws) - 1
    total_count = len(target_hits)
    if total_count == 0: return step_buckets, []

    recovery_pool = [] 
    calendar_candidates = get_hybrid_candidates(target_hits, full_draws, requested_max_step) if mode == "Calendar သီးသန့်မူများ (Fixed Pattern)" else {}

    label_space = "နံနက်ပိုင်း " if search_session == "AM သီးသန့်" else ("ညနေပိုင်း " if search_session == "PM သီးသန့်" else "")

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
                    
                    if "သီးသန့်" in search_session:
                        req_time_str = "AM" if "AM" in search_session else "PM"
                        if full_draws[t_idx]['time'] != req_time_str: continue

                    is_hit, matched_draw = is_already_hit(mu_k, current_val, t_idx, t_idx, full_draws)
                    if is_hit:
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
                
                if "သီးသန့်" in search_session:
                    req_t = "AM" if "AM" in search_session else "PM"
                    elapsed_filtered = sum(1 for d in full_draws[last_hit_global_idx + 1 : current_latest_idx + 1] if d['time'] == req_t)
                else:
                    elapsed_filtered = current_latest_idx - last_hit_global_idx
                    
                rem_steps = max_required_span - elapsed_filtered
                
                if rem_steps == 1: 
                    is_deadline_flag = True
                
                if not is_research_mode:
                    if rem_steps < 1: continue 
                    if elapsed_filtered > 0 and is_already_hit(mu_k, last_generated_val, last_hit_global_idx + 1, current_latest_idx, full_draws)[0]: 
                        continue

            sniper_note = f"💡 အဖြစ်နိုင်ဆုံး ၃/၄ ကွက်: {', '.join([x[0] for x in Counter(actual_hit_combinations).most_common(4)])}" if actual_hit_combinations else ""

            card_payload = {
                "top": f"🔮 [{lbl_prefix}] ထွက်ပြီးလျှင်", 
                "formula": f"{last_generated_val} {'100%' if rate == 100.0 else f'{rate:.1f}%'}", 
                "bottom": f"မှန်ကန်မှု: ({total_count} ကြိမ်မှာ {successful_hits} ကြိမ်မှန်)", 
                "is_deadline": is_deadline_flag, 
                "pure": last_generated_val, 
                "mu_k": mu_k, 
                "advisor": sniper_note, 
                "rate": rate, 
                "max_span": max_required_span, 
                "lbl_prefix": lbl_prefix,
                "label_space": label_space
            }
            
            if is_research_mode or is_deadline_flag:
                step_buckets[max_required_span][last_generated_val if mode == "Calendar သီးသန့်မူများ (Fixed Pattern)" else mu_k] = card_payload
            
            if not is_research_mode and rem_steps in [2, 3]:
                recovery_pool.append({
                    "key": last_generated_val, 
                    "lbl_prefix": lbl_prefix, 
                    "rem_steps": rem_steps, 
                    "score": 80 if rem_steps == 2 else 50, 
                    "card": card_payload
                })

    return step_buckets, recovery_pool

# ==========================================
# FILE UPLOAD & UI
# ==========================================
uploaded_file = st.file_uploader("Bro ရဲ့ 2D CSV သို့မဟုတ် Excel ဖိုင်ကို ရွေးချယ်တင်ပေးပါ...", type=['csv', 'xlsx', 'xls'])

if uploaded_file:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip().str.lower()
    
    if not all(col in df.columns for col in ['year', 'day', 'am1', 'am2', 'pm1', 'pm2']):
        st.error("⚠️ ဖိုင်ထဲတွင် လိုအပ်သော ကော်လံများ (year, day, am1, am2, pm1, pm2) မပြည့်စုံပါ!")
    else:
        for col in ['year', 'am1', 'am2', 'pm1', 'pm2']: df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df.dropna(subset=['year', 'day']).reset_index(drop=True)
        df['day'] = df['day'].astype(str).str.strip().str.capitalize()

        full_days = ["Mon", "Tue", "Wed", "Thur", "Fri"]
        existing_days = set(df['day'].unique())
        off_days = [d for d in full_days if d not in existing_days]

        full_draws = []
        # iterrows အစား itertuples ပြောင်းသုံးထားသဖြင့် အကြိမ်ပေါင်းများစွာ ပိုမြန်ပါမည်
        for row in df.itertuples():
            if pd.notna(row.am1) and pd.notna(row.am2):
                full_draws.append({'draw': f"{int(row.am1)}{int(row.am2)}", 'time': 'AM', 'day': row.day, 'row_idx': row.Index})
            if pd.notna(row.pm1) and pd.notna(row.pm2):
                full_draws.append({'draw': f"{int(row.pm1)}{int(row.pm2)}", 'time': 'PM', 'day': row.day, 'row_idx': row.Index})

        for i, d in enumerate(full_draws): d['index'] = i
        last_recorded_draw = full_draws[-1]
        active_days_cycle = [d for d in full_days if d not in off_days]
        
        target_day_name = last_recorded_draw['day'] if last_recorded_draw['time'] == 'AM' else active_days_cycle[(active_days_cycle.index(last_recorded_draw['day']) + 1) % len(active_days_cycle)]
        target_time_name = "PM" if last_recorded_draw['time'] == 'AM' else "AM"
            
        st.success(f"🔮 ဒေတာပွဲစဉ်ပေါင်း {len(full_draws)} ခု ဖတ်ပြီးပါပြီ။ [{target_day_name} {target_time_name}] အတွက် တွက်ချက်မည်ဖြစ်ပါသည်။")
        st.write("---")

        tab_live, tab_custom = st.tabs(["⚡ တွက်ချက်မည် (ယခုပွဲစဉ်)", "🔍 2D Formulas (Custom သုတေသန)"])

        # ------------------------------------------
        # TAB 1: LIVE AUTO TRACKER
        # ------------------------------------------
        with tab_live:
            st.markdown("#### ⚙️ VIP ရှာဖွေမှု သတ်မှတ်ချက်များ (Inputs)")
            c1, c2 = st.columns(2)
            with c1:
                anchor_count = st.number_input("📌 အနှစ်ချုပ်ကြည့်ရှုလိုသော မူအရေအတွက် (Default: 10):", min_value=1, max_value=50, value=10)
            with c2:
                # Dynamic ဖြစ်စေရန် live_max_tf ကို ပြောင်းလဲအသုံးပြုနိုင်ပါသည်
                live_max_tf = st.number_input("⏳ စစ်ဆေးမည့် ပွဲစဉ်အရေအတွက် [Max Span] (Default: 20):", min_value=1, max_value=50, value=20)
                
            custom_anchors_str = st.text_input("🎯 စိတ်ကြိုက် အမာခံဂဏန်းများ (ဥပမာ - 48, 60, 62) [ရိုက်ထည့်ပါက Auto စနစ်ကို ကျော်လွန်မည်]:", value="")
            
            c1_mode, _ = st.columns([1, 1])
            with c1_mode:
                live_mode = st.radio("🧠 AI တွက်ချက်မှုစနစ် ရွေးချယ်ရန်:", ["AI Trend (ရှေ့သမိုင်း ၅၀ အထိုင်)", "Calendar သီးသန့်မူများ (Fixed Pattern)"], horizontal=True, key="live_mode")

            # --- အောက်ဆုံးတွင် ပြတ်တောက်သွားသော အပိုင်းအား ပြည့်စုံအောင် ရေးသားထားခြင်း ---
            if st.button("VIP ကို ယခုရှာဖွေမည် ⚡", key="btn_auto"):
                selected_anchors = []
                
                # Custom Input ထည့်ထားပါက ယင်းတို့ကိုသာ ရှာဖွေမည်၊ မရှိပါက နောက်ဆုံးထွက်ခဲ့သော ပွဲစဉ်များကိုသာ ယူမည်
                if custom_anchors_str.strip():
                    raw_nums = [x.strip() for x in custom_anchors_str.split(',') if x.strip().isdigit()]
                    for num in raw_nums:
                        # ယင်းဂဏန်း ထွက်ခဲ့သော အကြိမ်များကို ရှာမည်
                        hits = [d for d in full_draws if d['draw'] == num]
                        if hits:
                            selected_anchors.append(hits)
                else:
                    # နောက်ဆုံးပွဲစဉ် anchor_count ခုကို ဆွဲထုတ်မည်
                    last_draws = full_draws[-anchor_count:]
                    for d in last_draws:
                        hits = [x for x in full_draws if x['draw'] == d['draw']]
                        if hits:
                            selected_anchors.append(hits)
                
                if not selected_anchors:
                    st.warning("⚠️ ရှာဖွေရန် အချက်အလက် မရှိပါ။")
                else:
                    with st.spinner("AI Engine တွက်ချက်နေပါသည်..."):
                        all_vip_results = []
                        for target_hits in selected_anchors:
                            # Dynamic ဖြစ်သော live_max_tf ကို အသုံးပြု၍ execute_analysis ကို ခေါ်မည်
                            step_buckets, recovery_pool = execute_analysis(
                                target_hits=target_hits, 
                                full_draws=full_draws, 
                                requested_max_step=live_max_tf, 
                                mode=live_mode
                            )
                            
                            for step, mu_dict in step_buckets.items():
                                for mu_k, card in mu_dict.items():
                                    if card['is_deadline']:
                                        all_vip_results.append(card)
                        
                        st.write("---")
                        if all_vip_results:
                            st.markdown('<div class="section-title">🌟 SUPER VIP ရလဒ်များ (ယခုပွဲစဉ်အတွက်)</div>', unsafe_allow_html=True)
                            
                            # Overlap ဖြစ်သော (ထပ်နေသော) Formula များကို စစ်ထုတ်ခြင်း
                            formulas_count = Counter([card['formula'] for card in all_vip_results])
                            
                            for card in all_vip_results:
                                # အကြိမ်ရေများစွာ ထပ်နေပါက SUPER VIP အဖြစ် သတ်မှတ်ပြသမည်
                                overlap_badge = f'<div class="badge-super">🔥 Super VIP (ထပ်နေသောမူ)</div>' if formulas_count[card['formula']] > 1 else ""
                                
                                st.markdown(f"""
                                <div class="card card-deadline">
                                    {overlap_badge}
                                    <span class="line-trigger">{card['top']}</span>
                                    <span class="line-formula">{card['formula']}</span>
                                    <span class="line-history">{card['bottom']}</span>
                                    <span class="line-advisor">{card['advisor']}</span>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.info("ယခုပွဲစဉ်အတွက် Deadline ရောက်နေသော 90% အထက် VIP ရလဒ်များ မတွေ့ရှိပါ။")
