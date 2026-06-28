import streamlit as st
import pandas as pd
import io
import itertools
import re
from collections import Counter

# ==========================================
# PAGE CONFIG & PREMIUM DARK-THEME STYLE
# ==========================================
st.set_page_config(page_title="2D AI Master V26 Pro", layout="wide", page_icon="🤖")

st.markdown("""
<style>
    .stApp { background-color: #0B031A; color: #E0D5FA; }
    .main-title { color: #A078FF; font-size: 40px; font-weight: bold; text-align: center; margin-bottom: 5px; text-shadow: 0 0 10px rgba(160,120,255,0.5); }
    .sub-title { color: #8F72D6; font-size: 16px; text-align: center; margin-bottom: 30px; }
    
    /* Card Styles */
    .card { background-color: #170E2B; padding: 20px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); margin-bottom: 15px; border: 1px solid #2D1B4E; }
    .card-live { border-left: 6px solid #3498db; background-color: #0E1A2F; margin-bottom: 15px; }
    .card-hp { border-left: 6px solid #2ecc71; background-color: #0D2216; }
    .card-sniper { border-left: 6px solid #9b59b6; background-color: #201135; }
    
    /* Typography Styles */
    .line-trigger { font-size: 18px; font-weight: bold; color: #E0D5FA; margin-bottom: 6px; display: block; }
    .line-formula { font-size: 22px; font-weight: bold; color: #FFD700; margin-bottom: 6px; display: block; }
    .line-history { font-size: 15px; color: #A294C7; display: block; }
    .line-advisor { font-size: 16px; color: #00FFCC; font-style: italic; margin-top: 10px; display: block; border-top: 1px dashed #3D2B5E; padding-top: 8px; }
    
    /* Dynamic Badge Blocks */
    .badge-inline { padding: 2px 10px; border-radius: 6px; font-size: 14px; font-weight: bold; margin-left: 6px; margin-right: 6px; display: inline-block; vertical-align: middle; }
    .badge-inline-sniper { background-color: #9b59b6; color: white; }
    .badge-inline-hp { background-color: #2ecc71; color: #0D2216; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🤖 THE PERFECT 2D AI MASTER (V26 PRO)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Ultimate Verified Calendar Matrix Engine | Sniper & Cover System</div>', unsafe_allow_html=True)

special_groups = {
    "ညီကို": {"01","10","12","21","23","32","34","43","45","54","56","65","67","76","78","87","89","98","90","09"},
    "ပါဝါ": {"05","50","16","61","27","72","38","83","49","94"},
    "နက္ခတ်": {"07","70","18","81","24","42","35","53","69","96"},
    "ထိုင်းပါဝါ": {"09","90","13","31","26","62","47","74","58","85"},
    "အပူး": {"00","11","22","33","44","55","66","77","88","99"},
    "ဆယ်ပြည့်": {"10","01","20","02","30","03","40","04","50","05","60","06","70","07","80","08","90","09"}
}

def is_already_hit(mu_name, mu_val, start_idx, end_idx, full_draws_list):
    if start_idx >= len(full_draws_list): return False, ""
    check_draws = [d['draw'] for d in full_draws_list[start_idx : min(end_idx + 1, len(full_draws_list))]]
    if not check_draws: return False, ""
    
    for d in check_draws:
        d_break = str((int(d[0]) + int(d[1])) % 10)
        hit_val = ""
        
        if mu_name == "လုံးဘိုင်":
            pure_num = mu_val.split()[0]
            if pure_num in d: return True, d
        elif mu_name == "One Change":
            pure_oc = mu_val.split()[0]
            if any(x in d for x in pure_oc): return True, d
        elif mu_name == "key":
            pure_key = mu_val.split()[0]
            if any(x in d for x in pure_key): return True, d
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
            if mu_val == "-" or not mu_val: return True, d
            gps = mu_val.split('+')
            for g in gps:
                if d in special_groups.get(g.strip(), set()): return True, d
        elif mu_name == "ကွက်ကျဉ်းစနစ်":
            match = re.search(r'^(\d+)\s*ပါသော\s*([\d,\s]+)\s*ဘရိတ်', mu_val)
            if match:
                pure_k = match.group(1)
                pure_b = [b.strip() for b in match.group(2).split(',')]
                if any(k in d for k in pure_k) and d_break in pure_b: return True, d
    return False, ""

# ==========================================
# MASTER ROUTINE: DUAL MODE ENGINE
# ==========================================
def execute_analysis(target_hits, full_draws, requested_max_step, is_custom_tab=False, sel_session="AM+PM ပေါင်းချုပ်", custom_trigger="", strict_day_mode=False, mode="AI Trend"):
    step_buckets = {step: {} for step in range(1, requested_max_step + 1)}
    current_latest_idx = len(full_draws) - 1

    filtered_hits = target_hits
    total_count = len(filtered_hits)
    if total_count == 0: return step_buckets

    mu_keys_list = ["လုံးဘိုင်", "One Change", "key", "အပူးပါခွေ", "ထိပ်စီးစနစ်သစ်", "နောက်ပိတ်စနစ်သစ်", "ဘရိတ်", "စုံ/မ ကပ်", "အုပ်စုတွဲ", "ကွက်ကျဉ်းစနစ်"]

    for mu_k in mu_keys_list:
        hit_steps_across_history = []
        actual_hit_combinations = []
        is_valid_formula = True

        latest_val = ""
        latest_pure = ""

        # DUAL MODE LOGIC: Global Fixed Pattern Extraction vs AI Trend Extraction
        if mode == "Calendar သီးသန့်မူများ":
            # Extract common post-hit patterns globally (The 100% Fixed Rules approach)
            all_sub_draws = []
            for hit in filtered_hits:
                start_post = hit['index'] + 1
                end_post = min(hit['index'] + requested_max_step, len(full_draws) - 1)
                all_sub_draws.extend([d['draw'] for d in full_draws[start_post:end_post + 1]])
            if not all_sub_draws: continue
            analysis_pool = all_sub_draws
        else:
            # AI Trend Mode: Base formula on the pre-history of the most recent hit
            recent_hit_idx = filtered_hits[-1]['index']
            start_history_idx = max(0, recent_hit_idx - 50)
            analysis_pool = [d['draw'] for d in full_draws[start_history_idx : recent_hit_idx]]
            if not analysis_pool: continue

        all_singles = "".join(analysis_pool)
        all_heads = [d[0] for d in analysis_pool]
        all_tails = [d[1] for d in analysis_pool]
        all_breaks = [str((int(d[0]) + int(d[1])) % 10) for d in analysis_pool]

        top_single = Counter(all_singles).most_common(1)[0][0] if all_singles else ""
        top_oc = "".join([x[0] for x in Counter(all_singles).most_common(2)]) if len(Counter(all_singles)) >= 2 else top_single
        top_key3 = "".join([x[0] for x in Counter(all_singles).most_common(3)]) if len(Counter(all_singles)) >= 3 else top_oc
        top_k4 = "".join([x[0] for x in Counter(all_singles).most_common(4)]) if len(Counter(all_singles)) >= 4 else top_key3
        
        # Rule 5 & 6 Upgrade: 3 Heads/Tails + 3 to 5 Dynamic Attached Digits
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
        if len(top_brk2) < 2: top_brk2.append(str((int(top_brk2[0])+1)%10 if top_brk2 else 0))
        brk_label = f"{top_brk2[0]}, {top_brk2[1]}"
        
        e_sc = sum(1 for d in analysis_pool if top_single in d and int(d.replace(top_single,'',1) if d.replace(top_single,'',1) else top_single) % 2 == 0)
        o_sc = sum(1 for d in analysis_pool if top_single in d and int(d.replace(top_single,'',1) if d.replace(top_single,'',1) else top_single) % 2 != 0)
        kap_label = f'[{top_single}] "စုံ"ကပ်' if e_sc >= o_sc else f'[{top_single}] "မ"ကပ်'
        
        best_gp = ""
        max_gp_c = 0
        for combo in itertools.combinations(special_groups.keys(), 2):
            c = sum(1 for d in analysis_pool if d in special_groups[combo[0]] or d in special_groups[combo[1]])
            if c > max_gp_c: max_gp_c = c; best_gp = f"{combo[0]}+{combo[1]}"
        kwat_kyin_label = f"{top_key3} ပါသော {brk_label} ဘရိတ်"

        mapping = {
            "လုံးဘိုင်": f"{top_single} လုံးဘိုင်", "One Change": f"{top_oc} One Change",
            "key": f"{top_key3} key", "အပူးပါခွေ": f"{top_k4} အပူးပါခွေ",
            "ထိပ်စီးစနစ်သစ်": head_formula_str, "နောက်ပိတ်စနစ်သစ်": tail_formula_str,
            "ဘရိတ်": f"{brk_label} ဘရိတ်", "စုံ/မ ကပ်": kap_label, "အုပ်စုတွဲ": best_gp if best_gp else "-",
            "ကွက်ကျဉ်းစနစ်": kwat_kyin_label
        }
        
        latest_val = mapping[mu_k]
        latest_pure = mapping[mu_k]

        # Scan exactly up to user's absolute max step limit.
        for hit in filtered_hits:
            hit_idx = hit['index']
            found_hit_step = None
            for step_check in range(1, requested_max_step + 1):
                t_idx = hit_idx + step_check
                if t_idx >= len(full_draws): break
                
                is_hit, matched_draw = is_already_hit(mu_k, latest_val, t_idx, t_idx, full_draws)
                if is_hit:
                    if is_custom_tab and sel_session != "AM+PM ပေါင်းချုပ်" and "သီးသန့်" in sel_session:
                        req_time_str = "AM" if "AM" in sel_session else "PM"
                        if full_draws[t_idx]['time'] != req_time_str:
                            continue 
                    found_hit_step = step_check
                    actual_hit_combinations.append(matched_draw)
                    break
            
            if found_hit_step is not None:
                hit_steps_across_history.append(found_hit_step)
            else:
                hit_steps_across_history.append(999) 

        valid_spans = [s for s in hit_steps_across_history if s <= requested_max_step]
        if not valid_spans: continue
        
        max_required_span = max(valid_spans)
        successful_hits_within_max_span = sum(1 for s in hit_steps_across_history if s <= max_required_span)
        rate = (successful_hits_within_max_span / total_count) * 100

        # Strict precision guards 
        if rate < 90.0 or total_count < 10: continue

        if max_required_span <= requested_max_step:
            # Check Deadline Status
            is_deadline_flag = False
            if filtered_hits:
                last_hit_global_idx = filtered_hits[-1]['index']
                elapsed_draws = current_latest_idx - last_hit_global_idx
                if (elapsed_draws + 1) == max_required_span:
                    is_deadline_flag = True
                
                # Check if already dropped for global
                if not is_custom_tab:
                    is_hit, _ = is_already_hit(mu_k, latest_val, last_hit_global_idx + 1, current_latest_idx, full_draws)
                    if is_hit: continue

            # Sniper Notes Generation
            sniper_note = ""
            if actual_hit_combinations:
                top_combos = [x[0] for x in Counter(actual_hit_combinations).most_common(4)]
                sniper_note = f"💡 အဖြစ်နိုင်ဆုံး ၃/၄ ကွက်: {', '.join(top_combos)}"

            lbl_prefix = custom_trigger if is_custom_tab else (f"{filtered_hits[-1]['draw']} {filtered_hits[-1]['time']}" if filtered_hits else "")
            rate_str = "100%" if rate == 100.0 else f"{rate:.1f}%"
            
            card_payload = {
                "top": f"🔮 [{lbl_prefix}] ထွက်ပြီးလျှင်", 
                "formula": f"{latest_val} {rate_str}", 
                "bottom": f"မှန်ကန်မှု: ({total_count} ကြိမ်မှာ {successful_hits_within_max_span} ကြိမ်မှန်)", 
                "is_deadline": is_deadline_flag, 
                "pure": latest_pure, 
                "advisor": sniper_note, 
                "rate": rate,
                "max_span": max_required_span
            }
            
            step_buckets[max_required_span][mu_k] = card_payload

    return step_buckets

# ==========================================
# FILE UPLOAD & PRE-PROCESSING
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

        # ------------------------------------------
        # TAB 1: AUTOMATED ENGINE TRACKER
        # ------------------------------------------
        with tab_live:
            # Replaced Slider with Input Box (Default 10)
            input_box_val = st.text_input("⏳ စစ်ဆေးမည့် ပွဲစဉ်အရေအတွက် အတိအကျ (Default: 10):", value="10", key="live_input")
            live_max_tf = int(input_box_val.strip()) if input_box_val.strip().isdigit() else 10
            
            c1_mode, _ = st.columns([1, 1])
            with c1_mode:
                live_mode = st.radio("🧠 AI တွက်ချက်မှုစနစ် ရွေးချယ်ရန်:", ["AI Trend (ရှေ့သမိုင်း ၅၀ အထိုင်)", "Calendar သီးသန့်မူများ (Fixed Pattern)"], horizontal=True, key="live_mode")
            live_session_target = f"{target_time_name} သီးသန့်"

            if st.button("ယခုပွဲအတွက် Auto ရှာဖွေမည် ⚡", key="btn_auto"):
                current_end_idx = len(full_draws) - 1
                compiled_master_buckets = {step: {} for step in range(1, live_max_tf + 1)}
                scoring_pool = {} # Anchor & Cover Scoring Dict
                
                for step in range(1, live_max_tf + 1):
                    target_past_idx = current_end_idx - step + 1
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
                        
                        for step_key, formulas in step_res.items():
                            if step_key > live_max_tf: continue # Strict lock bound constraint
                            
                            for mk, mv in formulas.items():
                                f_key = mv['pure']
                                compiled_master_buckets[step_key][f"{pool['lbl']}_{mk}"] = mv
                                
                                # Scoring Logic (Sniper Anchor & Cover System)
                                if f_key not in scoring_pool:
                                    scoring_pool[f_key] = {'score': 0, 'details': [], 'is_anchor': False}
                                
                                scoring_pool[f_key]['details'].append(mv)
                                
                                if mv['is_deadline']:
                                    scoring_pool[f_key]['is_anchor'] = True
                                    scoring_pool[f_key]['score'] += 100 # High priority for Deadlines
                                else:
                                    # Urgency Weighting (fewer steps remaining = higher points)
                                    rem_steps = live_max_tf - step_key + 1
                                    scoring_pool[f_key]['score'] += rem_steps

                st.write("---")
                st.markdown("#### 🏆 TOP RESULTS (Sniper & Cover Anchors)")
                
                # Filter Top Results (Minimum 2 convergences or contains an Anchor)
                valid_top = {k: v for k, v in scoring_pool.items() if len(v['details']) >= 2 or v['is_anchor']}
                top_averages = sorted(valid_top.items(), key=lambda item: item[1]['score'], reverse=True)[:3]
                
                if top_averages:
                    for idx, (b_val, b_data) in enumerate(top_averages, 1):
                        icon = "🔥 Sniper Anchor" if b_data['is_anchor'] else "🛡️ Top Cover"
                        with st.expander(f"🏆 Top {idx} Convergence: {b_val} [{icon}] (အမှတ်: {b_data['score']})", expanded=(idx==1)):
                            st.markdown(f"<div style='color:#00FFCC; font-size:14px; margin-bottom:10px;'>💡 ဤမူကို အောက်ပါ ထောက်တိုင်များက ဘုံတူညီစွာ ညွှန်ပြနေပါသည်-</div>", unsafe_allow_html=True)
                            for d_detail in b_data['details']:
                                badge_class = "badge-inline-sniper" if d_detail['rate'] == 100.0 else "badge-inline-hp"
                                st.markdown(f"""
                                <div class="card card-live" style="padding:10px; margin-bottom:10px;">
                                    <span style="font-size:16px; font-weight:bold; color:#E0D5FA;">{d_detail['top']}</span>
                                    <span class='badge-inline {badge_class}'>{d_detail['max_span']} ပွဲအတွင်း</span>
                                    <span style="font-size:13px; color:#A294C7; display:block; margin-top:5px;">{d_detail['advisor']}</span>
                                </div>
                                """, unsafe_allow_html=True)
                else:
                    st.markdown("<div style='font-size:15px; font-weight:bold; color:#A294C7; padding:10px;'>ခိုင်မာသော ဘုံတူညီမှု ရလဒ်မရှိပါ (အနည်းဆုံး တိုက်ဆိုင်မှု ၂ ခု လိုအပ်ပါသည်)</div>", unsafe_allow_html=True)

                st.write("---")
                st.markdown("#### 📋 အသေးစိတ်အချက်အလက်")
                
                has_any_output_cards = any(compiled_master_buckets[sk] for sk in compiled_master_buckets if sk <= live_max_tf)
                
                if not has_any_output_cards:
                    st.info("မထွက်သေးဘဲ ကျန်ရှိနေသော ၉၀% အထက် ရက်ချိန်းနယ်ကုန် မူလက်ကျန် လက္ခဏာ မတွေ့ရှိပါ။")
                else:
                    for step_key in sorted(compiled_master_buckets.keys()):
                        if step_key > live_max_tf: continue
                        formulas_dict = compiled_master_buckets[step_key]
                        if not formulas_dict: continue
                        
                        is_any_deadline = any(c['is_deadline'] for c in formulas_dict.values())
                        header_title = f"⚠️ {step_key} ပွဲအတွင်း မူများ [ရက်ချိန်းပြည့်]" if is_any_deadline else f"🔽 {step_key} ပွဲအတွင်း မူများ"
                            
                        with st.expander(header_title, expanded=False):
                            for key_id, d_card in formulas_dict.items():
                                badge_class = "badge-inline-sniper" if d_card['rate'] == 100.0 else "badge-inline-hp"
                                span_tag = f"<span class='badge-inline {badge_class}'>{step_key} ပွဲအတွင်း</span>"
                                
                                st.markdown(f"""
                                <div class="card card-sniper">
                                    <span class="line-trigger">{d_card['top']} {span_tag}</span>
                                    <span class="line-formula">{d_card['formula']}</span>
                                    <span class="line-history">{d_card['bottom']}</span>
                                    <span class="line-advisor">{d_card['advisor']}</span>
                                </div>
                                """, unsafe_allow_html=True)

        # ------------------------------------------
        # TAB 2: CLEAN CUSTOM FORMULARS ENGINE 
        # ------------------------------------------
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

                # Safe prefix building to avoid SyntaxError with missing brackets
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
                            if step > custom_max_tf: continue # Strict Absolute Cap
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
