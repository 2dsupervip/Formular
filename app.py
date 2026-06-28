import streamlit as st
import pandas as pd
import io
import itertools
import re
from collections import Counter

# ==========================================
# PAGE CONFIG & PREMIUM DARK-THEME STYLE
# ==========================================
st.set_page_config(page_title="2D AI Master V27 Pro", layout="wide", page_icon="🤖")

st.markdown("""
<style>
    .stApp { background-color: #0B031A; color: #E0D5FA; }
    .main-title { color: #A078FF; font-size: 40px; font-weight: bold; text-align: center; margin-bottom: 5px; text-shadow: 0 0 10px rgba(160,120,255,0.5); }
    .sub-title { color: #8F72D6; font-size: 16px; text-align: center; margin-bottom: 30px; }
    
    .card { background-color: #170E2B; padding: 20px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); margin-bottom: 15px; border: 1px solid #2D1B4E; }
    .card-live { border-left: 6px solid #3498db; background-color: #0E1A2F; margin-bottom: 15px; }
    .card-hp { border-left: 6px solid #2ecc71; background-color: #0D2216; }
    .card-sniper { border-left: 6px solid #9b59b6; background-color: #201135; }
    
    .line-trigger { font-size: 18px; font-weight: bold; color: #E0D5FA; margin-bottom: 6px; display: block; }
    .line-formula { font-size: 22px; font-weight: bold; color: #FFD700; margin-bottom: 6px; display: block; }
    .line-history { font-size: 15px; color: #A294C7; display: block; }
    .line-advisor { font-size: 16px; color: #00FFCC; font-style: italic; margin-top: 10px; display: block; border-top: 1px dashed #3D2B5E; padding-top: 8px; }
    
    .badge-inline { padding: 2px 10px; border-radius: 6px; font-size: 14px; font-weight: bold; margin-left: 6px; margin-right: 6px; display: inline-block; vertical-align: middle; }
    .badge-inline-sniper { background-color: #9b59b6; color: white; }
    .badge-inline-hp { background-color: #2ecc71; color: #0D2216; }
    .badge-super { background-color: #FFD700; color: #000; padding: 3px 8px; border-radius: 5px; font-weight: bold; }
    .badge-second { background-color: #C0C0C0; color: #000; padding: 3px 8px; border-radius: 5px; font-weight: bold; }
    .badge-backup { background-color: #cd7f32; color: #fff; padding: 3px 8px; border-radius: 5px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🤖 THE PERFECT 2D AI MASTER (V27 PRO)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Instance Win-Rate Engine | Super VIP Overlap System</div>', unsafe_allow_html=True)

special_groups = {
    "ညီကို": {"01","10","12","21","23","32","34","43","45","54","56","65","67","76","78","87","89","98","90","09"},
    "ပါဝါ": {"05","50","16","61","27","72","38","83","49","94"},
    "နက္ခတ်": {"07","70","18","81","24","42","35","53","69","96"},
    "ထိုင်းပါဝါ": {"09","90","13","31","26","62","47","74","58","85"},
    "အပူး": {"00","11","22","33","44","55","66","77","88","99"},
    "ဆယ်ပြည့်": {"10","01","20","02","30","03","40","04","50","05","60","06","70","07","80","08","90","09"}
}

mu_keys_list = ["လုံးဘိုင်", "One Change", "key", "အပူးပါခွေ", "ထိပ်စီးစနစ်သစ်", "နောက်ပိတ်စနစ်သစ်", "ဘရိတ်", "စုံ/မ ကပ်", "အုပ်စုတွဲ"]

# Helper to check hit against target
def is_already_hit(mu_name, mu_val, start_idx, end_idx, full_draws_list):
    if start_idx >= len(full_draws_list): return False, ""
    check_draws = [d['draw'] for d in full_draws_list[start_idx : min(end_idx + 1, len(full_draws_list))]]
    if not check_draws or mu_val == "-" or not mu_val: return False, ""
    
    for d in check_draws:
        d_break = str((int(d[0]) + int(d[1])) % 10)
        if mu_name == "လုံးဘိုင်":
            pure_num = mu_val.split()[0]
            if pure_num in d: return True, d
        elif mu_name == "One Change" or mu_name == "key":
            pure_val = mu_val.split()[0]
            if any(x in d for x in pure_val): return True, d
        elif mu_name == "အပူးပါခွေ":
            pure_k4 = mu_val.split()[0]
            if d[0] in pure_k4 and d[1] in pure_k4: return True, d
        elif mu_name == "ထိပ်စီးစနစ်သစ်":
            match = re.search(r'([0-9]+)\s*ထိပ်\s*/\s*([0-9,]+)\s*ကပ်', mu_val)
            if match:
                heads, tails = match.group(1), [t.strip() for t in match.group(2).split(',')]
                if d[0] in heads and d[1] in tails: return True, d
        elif mu_name == "နောက်ပိတ်စနစ်သစ်":
            match = re.search(r'([0-9]+)\s*ပိတ်\s*/\s*([0-9,]+)\s*ကပ်', mu_val)
            if match:
                tails, heads = match.group(1), [h.strip() for h in match.group(2).split(',')]
                if d[1] in tails and d[0] in heads: return True, d
        elif mu_name == "ဘရိတ်":
            pure_brk = mu_val.split()[0].split(',')
            if d_break in [b.strip() for b in pure_brk]: return True, d
        elif mu_name == "စုံ/မ ကပ်":
            match = re.search(r'\[(\d+)\]\s*"([^"]+)"ကပ်', mu_val)
            if match:
                b1 = match.group(1)
                is_even = "စုံ" in match.group(2)
                if b1 in d:
                    rem = d.replace(b1, '', 1)
                    rem_digit = int(rem if rem else b1)
                    if (is_even and rem_digit % 2 == 0) or (not is_even and rem_digit % 2 != 0): return True, d
        elif mu_name == "အုပ်စုတွဲ":
            gps = mu_val.split('+')
            for g in gps:
                if d in special_groups.get(g.strip(), set()): return True, d
    return False, ""

# For AI Trend: Generates dynamic predictions based on 50 pre-history
def generate_formula_from_pool(analysis_pool):
    if not analysis_pool: return {k: "-" for k in mu_keys_list}
    
    all_singles = "".join(analysis_pool)
    all_heads = [d[0] for d in analysis_pool]
    all_tails = [d[1] for d in analysis_pool]
    all_breaks = [str((int(d[0]) + int(d[1])) % 10) for d in analysis_pool]

    top_single = Counter(all_singles).most_common(1)[0][0] if all_singles else ""
    top_oc = "".join([x[0] for x in Counter(all_singles).most_common(2)]) if len(Counter(all_singles)) >= 2 else top_single
    top_key3 = "".join([x[0] for x in Counter(all_singles).most_common(3)]) if len(Counter(all_singles)) >= 3 else top_oc
    
    # 4-Digit Fixed Permutation
    top_k4 = "".join([x[0] for x in Counter(all_singles).most_common(4)]) if len(Counter(all_singles)) >= 4 else top_key3
    
    top_h3 = [x[0] for x in Counter(all_heads).most_common(3)]
    attached_tails = [d[1] for d in analysis_pool if d[0] in top_h3]
    best_tails = [x[0] for x in Counter(attached_tails).most_common(5)]
    best_tails = best_tails[:4] if len(best_tails) >= 4 and Counter(attached_tails)[best_tails[2]] - Counter(attached_tails)[best_tails[-1]] > 2 else best_tails
    head_formula_str = f"{''.join(top_h3)} ထိပ် / {','.join(best_tails)} ကပ်" if top_h3 else "-"

    top_t3 = [x[0] for x in Counter(all_tails).most_common(3)]
    attached_heads = [d[0] for d in analysis_pool if d[1] in top_t3]
    best_heads = [x[0] for x in Counter(attached_heads).most_common(5)]
    best_heads = best_heads[:4] if len(best_heads) >= 4 and Counter(attached_heads)[best_heads[2]] - Counter(attached_heads)[best_heads[-1]] > 2 else best_heads
    tail_formula_str = f"{''.join(top_t3)} ပိတ် / {','.join(best_heads)} ကပ်" if top_t3 else "-"

    top_brk2 = [x[0] for x in Counter(all_breaks).most_common(2)]
    if len(top_brk2) < 2 and top_brk2: top_brk2.append(str((int(top_brk2[0])+1)%10))
    brk_label = f"{top_brk2[0]}, {top_brk2[1]}" if len(top_brk2) == 2 else "-"
    
    e_sc = sum(1 for d in analysis_pool if top_single in d and int(d.replace(top_single,'',1) if d.replace(top_single,'',1) else top_single) % 2 == 0)
    o_sc = sum(1 for d in analysis_pool if top_single in d and int(d.replace(top_single,'',1) if d.replace(top_single,'',1) else top_single) % 2 != 0)
    kap_label = f'[{top_single}] "စုံ"ကပ်' if e_sc >= o_sc else f'[{top_single}] "မ"ကပ်'
    
    best_gp = "-"
    max_gp_c = 0
    for combo in itertools.combinations(special_groups.keys(), 2):
        c = sum(1 for d in analysis_pool if d in special_groups[combo[0]] or d in special_groups[combo[1]])
        if c > max_gp_c: max_gp_c = c; best_gp = f"{combo[0]}+{combo[1]}"

    return {
        "လုံးဘိုင်": f"{top_single} လုံးဘိုင်" if top_single else "-", 
        "One Change": f"{top_oc} One Change" if top_oc else "-",
        "key": f"{top_key3} key" if top_key3 else "-", 
        "အပူးပါခွေ": f"{top_k4} အပူးပါခွေ" if top_k4 else "-",
        "ထိပ်စီးစနစ်သစ်": head_formula_str, "နောက်ပိတ်စနစ်သစ်": tail_formula_str,
        "ဘရိတ်": f"{brk_label} ဘရိတ်" if brk_label != "-" else "-", 
        "စုံ/မ ကပ်": kap_label if top_single else "-", "အုပ်စုတွဲ": best_gp
    }

# generates fixed candidates for Calendar Mode
def get_calendar_candidates():
    candidates = {"လုံးဘိုင်": [], "ဘရိတ်": [], "အုပ်စုတွဲ": []}
    for i in range(10): candidates["လုံးဘိုင်"].append(f"{i} လုံးဘိုင်")
    for b in itertools.combinations([str(x) for x in range(10)], 2): candidates["ဘရိတ်"].append(f"{b[0]}, {b[1]} ဘရိတ်")
    for combo in itertools.combinations(special_groups.keys(), 2): candidates["အုပ်စုတွဲ"].append(f"{combo[0]}+{combo[1]}")
    return candidates

# ==========================================
# MASTER ROUTINE: INSTANCE WIN-RATE ENGINE
# ==========================================
def execute_analysis(target_hits, full_draws, requested_max_step, is_custom_tab=False, sel_session="AM+PM ပေါင်းချုပ်", custom_trigger="", strict_day_mode=False, mode="AI Trend"):
    step_buckets = {step: {} for step in range(1, requested_max_step + 1)}
    current_latest_idx = len(full_draws) - 1
    total_count = len(target_hits)
    if total_count == 0: return step_buckets

    calendar_candidates = get_calendar_candidates() if mode == "Calendar သီးသန့်မူများ (Fixed Pattern)" else {}

    # Define formula keys we process
    processing_keys = ["လုံးဘိုင်", "ဘရိတ်", "အုပ်စုတွဲ"] if mode == "Calendar သီးသန့်မူများ (Fixed Pattern)" else mu_keys_list

    for mu_k in processing_keys:
        cand_list = calendar_candidates.get(mu_k, []) if mode == "Calendar သီးသန့်မူများ (Fixed Pattern)" else ["DYNAMIC_AI"]
        
        for cand_val in cand_list:
            hit_steps_across_history = []
            actual_hit_combinations = []
            last_generated_val = cand_val

            for hit in target_hits:
                hit_idx = hit['index']
                current_val = cand_val
                
                # Dynamic Logic for AI Trend
                if mode != "Calendar သီးသန့်မူများ (Fixed Pattern)":
                    start_history_idx = max(0, hit_idx - 50)
                    pool = [d['draw'] for d in full_draws[start_history_idx : hit_idx]]
                    dynamic_formulas = generate_formula_from_pool(pool)
                    current_val = dynamic_formulas.get(mu_k, "-")
                    last_generated_val = current_val

                if current_val == "-" or not current_val:
                    hit_steps_across_history.append(999)
                    continue

                # Check Instance Post-Window
                found_hit_step = None
                for step_check in range(1, requested_max_step + 1):
                    t_idx = hit_idx + step_check
                    if t_idx >= len(full_draws): break
                    
                    is_hit, matched_draw = is_already_hit(mu_k, current_val, t_idx, t_idx, full_draws)
                    if is_hit:
                        if is_custom_tab and sel_session != "AM+PM ပေါင်းချုပ်" and "သီးသန့်" in sel_session:
                            req_time_str = "AM" if "AM" in sel_session else "PM"
                            if full_draws[t_idx]['time'] != req_time_str: continue 
                        found_hit_step = step_check
                        actual_hit_combinations.append(matched_draw)
                        break
                
                hit_steps_across_history.append(found_hit_step if found_hit_step is not None else 999)

            # Win Rate Evaluation (Strictly Instance-Based)
            valid_spans = [s for s in hit_steps_across_history if s <= requested_max_step]
            if not valid_spans or last_generated_val == "-": continue
            
            max_required_span = max(valid_spans)
            successful_hits = sum(1 for s in hit_steps_across_history if s <= max_required_span)
            rate = (successful_hits / total_count) * 100

            # MUST exceed 90% Win-Rate to be considered
            if rate < 90.0 or total_count < 10: continue

            if max_required_span <= requested_max_step:
                is_deadline_flag = False
                if target_hits:
                    last_hit_global_idx = target_hits[-1]['index']
                    elapsed_draws = current_latest_idx - last_hit_global_idx
                    
                    if elapsed_draws + 1 == max_required_span:
                        is_deadline_flag = True
                    elif elapsed_draws >= max_required_span:
                        continue 
                    
                    if not is_custom_tab and elapsed_draws > 0:
                        is_hit, _ = is_already_hit(mu_k, last_generated_val, last_hit_global_idx + 1, current_latest_idx, full_draws)
                        if is_hit: continue

                sniper_note = ""
                if actual_hit_combinations:
                    top_combos = [x[0] for x in Counter(actual_hit_combinations).most_common(4)]
                    sniper_note = f"💡 အဖြစ်နိုင်ဆုံး ၃/၄ ကွက်: {', '.join(top_combos)}"

                lbl_prefix = custom_trigger if is_custom_tab else (f"{target_hits[-1]['draw']} {target_hits[-1]['time']}" if target_hits else "")
                rate_str = "100%" if rate == 100.0 else f"{rate:.1f}%"
                
                # Prevent duplicates in Calendar mode from overwriting
                bucket_key = last_generated_val if mode == "Calendar သီးသန့်မူများ (Fixed Pattern)" else mu_k
                
                card_payload = {
                    "top": f"🔮 [{lbl_prefix}] ထွက်ပြီးလျှင်", 
                    "formula": f"{last_generated_val} {rate_str}", 
                    "bottom": f"မှန်ကန်မှု: ({total_count} ကြိမ်မှာ {successful_hits} ကြိမ်မှန်)", 
                    "is_deadline": is_deadline_flag, 
                    "pure": last_generated_val, 
                    "advisor": sniper_note, 
                    "rate": rate,
                    "max_span": max_required_span
                }
                
                step_buckets[max_required_span][bucket_key] = card_payload

    return step_buckets

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
        for col in ['year', 'am1', 'am2', 'pm1', 'pm2']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df.dropna(subset=['year', 'day']).reset_index(drop=True)
        df['day'] = df['day'].astype(str).str.strip().str.capitalize()

        full_draws = []
        for idx, row in df.iterrows():
            if pd.notna(row['am1']) and pd.notna(row['am2']):
                full_draws.append({'draw': f"{int(row['am1'])}{int(row['am2'])}", 'time': 'AM', 'day': row['day'], 'year': int(row['year']), 'row_idx': idx})
            if pd.notna(row['pm1']) and pd.notna(row['pm2']):
                full_draws.append({'draw': f"{int(row['pm1'])}{int(row['pm2'])}", 'time': 'PM', 'day': row['day'], 'year': int(row['year']), 'row_idx': idx})

        for i, d in enumerate(full_draws): d['index'] = i

        last_recorded_draw = full_draws[-1]
        days_cycle = ["Mon", "Tue", "Wed", "Thur", "Fri"]
        
        if last_recorded_draw['time'] == 'AM':
            target_day_name = last_recorded_draw['day']
            target_time_name = "PM"
        else:
            curr_idx = days_cycle.index(last_recorded_draw['day']) if last_recorded_draw['day'] in days_cycle else 0
            target_day_name = days_cycle[(curr_idx + 1) % 5]
            target_time_name = "AM"
            
        st.success(f"🔮 ဒေတာပွဲစဉ်ပေါင်း {len(full_draws)} ခု ဖတ်ပြီးပါပြီ။ [{target_day_name} {target_time_name}] အတွက် တွက်ချက်မည်ဖြစ်ပါသည်။")
        st.write("---")

        tab_live, tab_custom = st.tabs(["⚡ တွက်ချက်မည် (ယခုပွဲစဉ်)", "🔍 2D Formulas (Custom)"])

        with tab_live:
            input_box_val = st.text_input("⏳ စစ်ဆေးမည့် ပွဲစဉ်အရေအတွက် အတိအကျ (Default: 10):", value="10", key="live_input")
            live_max_tf = int(input_box_val.strip()) if input_box_val.strip().isdigit() else 10
            
            c1_mode, _ = st.columns([1, 1])
            with c1_mode:
                live_mode = st.radio("🧠 AI တွက်ချက်မှုစနစ် ရွေးချယ်ရန်:", ["AI Trend (ရှေ့သမိုင်း ၅၀ အထိုင်)", "Calendar သီးသန့်မူများ (Fixed Pattern)"], horizontal=True, key="live_mode")
            live_session_target = f"{target_time_name} သီးသန့်"

            if st.button("ယခုပွဲအတွက် Auto ရှာဖွေမည် ⚡", key="btn_auto"):
                current_end_idx = len(full_draws) - 1
                compiled_master_buckets = {step: {} for step in range(1, live_max_tf + 1)}
                scoring_pool = {}
                
                for step_dist in range(1, live_max_tf + 1):
                    target_past_idx = current_end_idx - step_dist + 1
                    if target_past_idx < 0: continue
                    
                    past_obj = full_draws[target_past_idx]
                    past_val = past_obj['draw']
                    past_time = past_obj['time']
                    
                    condition_pools = [
                        {"hits": [d for d in full_draws[:target_past_idx+1] if d['draw'] == past_val and d['time'] == past_time], "lbl": f"{past_val} {past_time} စစ်စစ်"},
                        {"hits": [d for d in full_draws[:target_past_idx+1] if d['draw'] == past_val], "lbl": f"{past_val} ပေါင်းချုပ်"}
                    ]
                    
                    for pool in condition_pools:
                        if not pool['hits']: continue
                        
                        step_res = execute_analysis(pool['hits'], full_draws, live_max_tf, is_custom_tab=False, sel_session=live_session_target, mode=live_mode)
                        
                        if step_dist in step_res:
                            for mk, mv in step_res[step_dist].items():
                                f_key = mv['pure']
                                compiled_master_buckets[step_dist][f"{pool['lbl']}_{mk}"] = mv
                                
                                if f_key not in scoring_pool:
                                    scoring_pool[f_key] = {'count': 0, 'details': [], 'is_anchor': False}
                                
                                scoring_pool[f_key]['details'].append(mv)
                                scoring_pool[f_key]['count'] += 1
                                if mv['is_deadline']: scoring_pool[f_key]['is_anchor'] = True

                st.write("---")
                st.markdown("#### 🏆 VIP ဆုံးဖြတ်ချက် (Super, Second & Backup Overlaps)")
                
                sorted_scores = sorted(scoring_pool.items(), key=lambda x: (x[1]['count'], x[1]['is_anchor']), reverse=True)
                
                if sorted_scores:
                    for b_val, b_data in sorted_scores:
                        if b_data['count'] >= 3 or (b_data['count'] >= 2 and b_data['is_anchor']):
                            tier, badge = "Super VIP", "badge-super"
                        elif b_data['count'] == 2:
                            tier, badge = "Second VIP", "badge-second"
                        elif b_data['is_anchor']:
                            tier, badge = "Backup Anchor", "badge-backup"
                        else: continue
                            
                        with st.expander(f"⭐ {tier}: {b_val} (တူညီမှု: {b_data['count']} ခု)", expanded=(tier == "Super VIP")):
                            st.markdown(f"<span class='{badge}'>{tier}</span><div style='color:#00FFCC; font-size:14px; margin-top:10px; margin-bottom:10px;'>💡 ဤမူကို အောက်ပါ ထောက်တိုင်များက ဘုံတူညီစွာ ညွှန်ပြနေပါသည်-</div>", unsafe_allow_html=True)
                            for d_detail in b_data['details']:
                                span_class = "badge-inline-sniper" if d_detail['rate'] == 100.0 else "badge-inline-hp"
                                st.markdown(f"""
                                <div class="card card-live" style="padding:10px; margin-bottom:10px;">
                                    <span style="font-size:16px; font-weight:bold; color:#E0D5FA;">{d_detail['top']}</span>
                                    <span class='badge-inline {span_class}'>{d_detail['max_span']} ပွဲအတွင်း (ယခုပွဲစဉ် ရက်ချိန်းပြည့်)</span>
                                    <span style="font-size:13px; color:#A294C7; display:block; margin-top:5px;">{d_detail['advisor']}</span>
                                </div>
                                """, unsafe_allow_html=True)
                else:
                    st.markdown("<div style='font-size:15px; font-weight:bold; color:#A294C7; padding:10px;'>ခိုင်မာသော VIP တူညီမှု ရလဒ်မရှိပါ (အနည်းဆုံး တိုက်ဆိုင်မှု ၂ ခု လိုအပ်ပါသည်)</div>", unsafe_allow_html=True)

                st.write("---")
                st.markdown("#### 📋 ရက်ချိန်းပြည့် မူများ အသေးစိတ်")
                has_any_output = any(compiled_master_buckets[sk] for sk in compiled_master_buckets)
                
                if not has_any_output:
                    st.info("ယခုပွဲစဉ်အတွက် ရက်ချိန်းပြည့်နေသော ၉၀% အထက် မူလက်ကျန် မတွေ့ရှိပါ။")
                else:
                    for step_key in sorted(compiled_master_buckets.keys()):
                        formulas_dict = compiled_master_buckets[step_key]
                        if not formulas_dict: continue
                        
                        with st.expander(f"⚠️ {step_key} ပွဲအတွင်း မူများ [ရက်ချိန်းပြည့်]", expanded=False):
                            for key_id, d_card in formulas_dict.items():
                                badge_class = "badge-inline-sniper" if d_card['rate'] == 100.0 else "badge-inline-hp"
                                span_tag = f"<span class='badge-inline {badge_class}'>{step_key} ပွဲအတွင်း (ပြည့်)</span>"
                                
                                st.markdown(f"""
                                <div class="card card-sniper">
                                    <span class="line-trigger">{d_card['top']} {span_tag}</span>
                                    <span class="line-formula">{d_card['formula']}</span>
                                    <span class="line-history">{d_card['bottom']}</span>
                                    <span class="line-advisor">{d_card['advisor']}</span>
                                </div>
                                """, unsafe_allow_html=True)

        with tab_custom:
            st.markdown("##### 🧠 တွက်ချက်မှုစနစ် (Mode) ရွေးချယ်ရန်")
            custom_mode = st.radio("", ["AI Trend (ရှေ့သမိုင်း ၅၀ အထိုင်)", "Calendar သီးသန့်မူများ (Fixed Pattern)"], horizontal=True, key="custom_mode")
            st.write("---")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                trigger_day = st.selectbox("📆 Trigger Day:", ["All", "Mon", "Tue", "Wed", "Thur", "Fri"], index=0)
                trigger_num = st.text_input("🔍 ရှာလိုသောဂဏန်း ရိုက်ထည့်ပါ:", value="01", max_chars=7)
            with c2:
                if trigger_day != "All":
                    st.markdown("<span style='color:#00FFCC; font-size:13px;'>ℹ️ Day စနစ်သုံးထားသဖြင့် အကြိမ်ရေပြည့်မီစေရန် R-စနစ် နှင့် AM+PM ပေါင်းချုပ် စနစ်ကို Backend က Auto Lock ချပေးထားပါသည်။</span>", unsafe_allow_html=True)
                    target_session_custom = "AM+PM ပေါင်းချုပ်"
                else:
                    target_session_custom = st.selectbox("⏱️ Target ပွဲစဉ် အခြေအနေ ရွေးရန်:", ["AM+PM ပေါင်းချုပ်", "AM သီးသန့်", "PM သီးသန့်"], index=2)
            with c3:
                custom_max_tf = st.number_input("⏳ စစ်ဆေးမည့် ပွဲစဉ်အရေအတွက်", min_value=1, max_value=25, value=16, key="custom_input_tf")

            if st.button("ရှာဖွေမည် 🚀", key="btn_custom"):
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
                    
                    master_step_res = execute_analysis(
                        target_hits, full_draws, custom_max_tf, 
                        is_custom_tab=True, sel_session=target_session_custom, 
                        custom_trigger=lbl_prefix_custom, strict_day_mode=(trigger_day != "All"),
                        mode=custom_mode
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
