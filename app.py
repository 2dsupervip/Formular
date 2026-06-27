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
    .card-live { border-left: 6px solid #3498db; background-color: #0E1A2F; }
    .card-hp { border-left: 6px solid #2ecc71; background-color: #0D2216; }
    .card-sniper { border-left: 6px solid #9b59b6; background-color: #201135; }
    
    /* Bro 3/4-Line Stack Display Typography */
    .line-alert { color: #FF4D4D; font-size: 16px; font-weight: bold; margin-bottom: 6px; display: block; }
    .line-trigger { font-size: 18px; font-weight: bold; color: #E0D5FA; margin-bottom: 6px; display: block; }
    .line-formula { font-size: 22px; font-weight: bold; color: #FFD700; margin-bottom: 6px; display: block; }
    .line-history { font-size: 15px; color: #A294C7; display: block; }
    .line-advisor { font-size: 14px; color: #00FFCC; font-style: italic; margin-top: 4px; display: block; }
    
    /* Dynamic Badge Blocks */
    .badge-inline { padding: 2px 10px; border-radius: 6px; font-size: 14px; font-weight: bold; margin-left: 6px; margin-right: 6px; display: inline-block; vertical-align: middle; }
    .badge-inline-sniper { background-color: #9b59b6; color: white; }
    .badge-inline-hp { background-color: #2ecc71; color: #0D2216; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🤖 THE PERFECT 2D AI MASTER (V26 PRO)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Ultimate Verified Calendar Matrix Engine | Strict Exact Step Boundary Lock</div>', unsafe_allow_html=True)

special_groups = {
    "ညီကို": {"01","10","12","21","23","32","34","43","45","54","56","65","67","76","78","87","89","98","90","09"},
    "ပါဝါ": {"05","50","16","61","27","72","38","83","49","94"},
    "နက္ခတ်": {"07","70","18","81","24","42","35","53","69","96"},
    "ထိုင်းပါဝါ": {"09","90","13","31","26","62","47","74","58","85"},
    "အပူး": {"00","11","22","33","44","55","66","77","88","99"},
    "ဆယ်ပြည့်": {"10","01","20","02","30","03","40","04","50","05","60","06","70","07","80","08","90","09"}
}

# ==========================================
# STUCT ALREADY HIT TRACKER (STABLE INTERNAL LOOKUP)
# ==========================================
def is_already_hit(mu_name, mu_val, start_idx, end_idx, full_draws_list):
    if start_idx >= len(full_draws_list): return True
    check_draws = [d['draw'] for d in full_draws_list[start_idx : min(end_idx + 1, len(full_draws_list))]]
    if not check_draws: return False
    
    for d in check_draws:
        d_break = str((int(d[0]) + int(d[1])) % 10)
        
        if mu_name == "လုံးဘိုင်":
            pure_num = mu_val.split()[0]
            if pure_num in d: return True
        elif mu_name == "One Change":
            pure_oc = mu_val.split()[0]
            if any(x in d for x in pure_oc): return True
        elif mu_name == "key":
            pure_key = mu_val.split()[0]
            if any(x in d for x in pure_key): return True
        elif mu_name == "အပူးပါခွေ":
            pure_k4 = mu_val.split()[0]
            if d[0] in pure_k4 and d[1] in pure_k4: return True
        elif mu_name == "ထိပ်စီး":
            pure_h = mu_val.split()[0]
            if d[0] in pure_h: return True
        elif mu_name == "နောက်ပိတ်":
            pure_t = mu_val.split()[0]
            if d[1] in pure_t: return True
        elif mu_name == "ဘရိတ်":
            pure_brk = mu_val.split()[0].split(',')
            if d_break in [b.strip() for b in pure_brk]: return True
        elif mu_name == "စုံ/မ ကပ်":
            match = re.search(r'\[(\d+)\]\s*"([^"]+)"ကပ်', mu_val)
            if match:
                b1 = match.group(1)
                is_even = "စုံ" in match.group(2)
                if b1 in d:
                    rem = d.replace(b1, '', 1)
                    rem_digit = int(rem if rem else b1)
                    if is_even and rem_digit % 2 == 0: return True
                    if not is_even and rem_digit % 2 != 0: return True
        elif mu_name == "အုပ်စုတွဲ":
            if mu_val == "-" or not mu_val: return True
            gps = mu_val.split('+')
            for g in gps:
                if d in special_groups.get(g.strip(), set()): return True
        elif mu_name == "ကွက်ကျဉ်းစနစ်":
            match = re.search(r'^(\d+)\s*ပါသော\s*([\d,\s]+)\s*ဘရိတ်', mu_val)
            if match:
                pure_k = match.group(1)
                pure_b = [b.strip() for b in match.group(2).split(',')]
                if any(k in d for k in pure_k) and d_break in pure_b: return True
    return False

# ==========================================
# MASTER ROUTINE: HYBRID DATA ANALYSIS ENGINE
# ==========================================
def execute_analysis(target_hits, full_draws, active_tfs, is_custom_tab=False, sel_session="AM+PM ပေါင်းချုပ်", custom_trigger="", strict_day_mode=False):
    hp_store = {}
    sniper_store = {}
    current_latest_idx = len(full_draws) - 1

    filtered_hits = target_hits
    total_count = len(filtered_hits)
    if total_count == 0: return hp_store, sniper_store

    for tf_name, s_off, e_off in active_tfs:
        mu_keys_list = ["လုံးဘိုင်", "One Change", "key", "အပူးပါခွေ", "ထိပ်စီး", "နောက်ပိတ်", "ဘရိတ်", "စုံ/မ ကပ်", "အုပ်စုတွဲ", "ကွက်ကျဉ်းစနစ်"]
        
        for mu_k in mu_keys_list:
            win_count = 0
            latest_val = ""
            latest_pure = ""
            
            for hit in filtered_hits:
                # 🚨 Stable History Window Extraction (Backward Look Base)
                hit_idx = hit['index']
                start_history_idx = max(0, hit_idx - 50)
                end_history_idx = hit_idx - 1
                if start_history_idx >= end_history_idx: continue
                
                sub_draws = [d['draw'] for d in full_draws[start_history_idx : end_history_idx + 1]]
                all_singles = "".join(sub_draws)
                all_heads = [d[0] for d in sub_draws]
                all_tails = [d[1] for d in sub_draws]
                all_breaks = [str((int(d[0]) + int(d[1])) % 10) for d in sub_draws]

                top_single = Counter(all_singles).most_common(1)[0][0] if all_singles else ""
                top_oc = "".join([x[0] for x in Counter(all_singles).most_common(2)]) if len(Counter(all_singles)) >= 2 else top_single
                top_key3 = "".join([x[0] for x in Counter(all_singles).most_common(3)]) if len(Counter(all_singles)) >= 3 else top_oc
                top_k4 = "".join([x[0] for x in Counter(all_singles).most_common(4)]) if len(Counter(all_singles)) >= 4 else top_key3
                top_h3 = "".join([x[0] for x in Counter(all_heads).most_common(3)]) if all_heads else ""
                top_t3 = "".join([x[0] for x in Counter(all_tails).most_common(3)]) if all_tails else ""
                top_brk2 = [x[0] for x in Counter(all_breaks).most_common(2)]
                if len(top_brk2) < 2: top_brk2.append(str((int(top_brk2[0])+1)%10 if top_brk2 else 0))
                brk_label = f"{top_brk2[0]}, {top_brk2[1]}"
                
                e_sc = sum(1 for d in sub_draws if top_single in d and int(d.replace(top_single,'',1) if d.replace(top_single,'',1) else top_single) % 2 == 0)
                o_sc = sum(1 for d in sub_draws if top_single in d and int(d.replace(top_single,'',1) if d.replace(top_single,'',1) else top_single) % 2 != 0)
                kap_label = f'[{top_single}] "စုံ"ကပ်' if e_sc >= o_sc else f'[{top_single}] "မ"ကပ်'
                
                best_gp = ""
                max_gp_c = 0
                for combo in itertools.combinations(special_groups.keys(), 2):
                    c = sum(1 for d in sub_draws if d in special_groups[combo[0]] or d in special_groups[combo[1]])
                    if c > max_gp_c: max_gp_c = c; best_gp = f"{combo[0]}+{combo[1]}"
                kwat_kyin_label = f"{top_key3} ပါသော {brk_label} ဘရိတ်"

                mapping = {
                    "လုံးဘိုင်": f"{top_single} လုံးဘိုင်", "One Change": f"{top_oc} One Change",
                    "key": f"{top_key3} key", "အပူးပါခွေ": f"{top_k4} အပူးပါခွေ",
                    "ထိပ်စီး": f"{top_h3} ထိပ်စီး", "နောက်ပိတ်": f"{top_t3} နောက်ပိတ်",
                    "ဘရိတ်": f"{brk_label} ဘရိတ်", "စုံ/မ ကပ်": kap_label, "အုပ်စုတွဲ": best_gp if best_gp else "-",
                    "ကွက်ကျဉ်းစနစ်": kwat_kyin_label
                }
                
                latest_val = mapping[mu_k]
                latest_pure = mapping[mu_k]
                
                # 🚨 Bro's Core Rule: Strict Exact Step Target Boundary Validation
                exact_target_idx = hit_idx + e_off
                if exact_target_idx < len(full_draws):
                    d_target = full_draws[exact_target_idx]
                    
                    if is_custom_tab and sel_session != "AM+PM ပေါင်းချုပ်" and "သီးသန့်" in sel_session:
                        req_t = "AM" if "AM" in sel_session else "PM"
                        if d_target['time'] != req_t: continue
                    
                    # 1. ရှေ့ပွဲစဉ် (1 to step-1) အတွင်း ကြိုထွက်ဖူးခြင်း ရှိ/မရှိ စစ်ဆေးသည်
                    if e_off > 1:
                        was_early_leak = is_already_hit(mu_k, latest_val, hit_idx + 1, hit_idx + e_off - 1, full_draws)
                    else:
                        was_early_leak = False
                        
                    # 2. ရှေ့မှာ လုံးဝမထွက်ခဲ့ဘဲ ယခု သတ်မှတ်ရက်ချိန်းပွဲတွင်မှ ကွက်တိထွက်ခြင်း ဟုတ်/မဟုတ် စစ်ဆေးသည်
                    if not was_early_leak:
                        if is_already_hit(mu_k, latest_val, exact_target_idx, exact_target_idx, full_draws):
                            win_count += 1

            if not latest_val: continue
            rate = (win_count / total_count) * 100

            # 🚨 Bro's Strict Cut-off Guard: Rate >= 90% and Total Sample >= 10
            if rate < 90.0 or total_count < 10:
                continue

            # Tab 1 Anti-Overlap Purge Logic
            if not is_custom_tab and filtered_hits:
                if is_already_hit(mu_k, latest_val, filtered_hits[-1]['index'] + 1, current_latest_idx, full_draws):
                    continue

            is_deadline_flag = False
            if filtered_hits:
                last_hit_global_idx = filtered_hits[-1]['index']
                elapsed_draws = current_latest_idx - last_hit_global_idx
                if (elapsed_draws + 1) == e_off:
                    is_deadline_flag = True

            lbl_prefix = custom_trigger if is_custom_tab else (f"{filtered_hits[-1]['draw']} {filtered_hits[-1]['time']}" if filtered_hits else "")
            rate_str = "100%" if rate == 100.0 else f"{rate:.1f}%"
            badge_color_class = "badge-inline-sniper" if rate == 100.0 else "badge-inline-hp"
            
            top_line = f"🔮 [{lbl_prefix}] ထွက်ပြီးလျှင် <span class='badge-inline {badge_color_class}'>{tf_name}အတွင်း</span>"
            formula_line = f"{latest_val} {rate_str}"
            bottom_line = f"မှန်ကန်မှု: ({total_count} ကြိမ်မှာ {win_count} ကြိမ်မှန်)"

            advisor_text = ""
            if is_custom_tab:
                if rate == 100.0 and total_count >= 10:
                    advisor_text = "💡 သမိုင်းကြောင်းအရ ကစားရန်သင့်လျော်သောမူဖြစ်သည် - ခန့်မှန်းချက်သာဖြစ်၍ အပိုင်မဟုတ်ပါ"
                else:
                    advisor_text = "⚠️ သမိုင်းကြောင်း အားနည်းသည် - အရန်အဖြစ်သာ စဉ်းစားပါ"

            card_payload = {
                "top": top_line, "formula": formula_line, "bottom": bottom_line, 
                "e_off": e_off, "is_deadline": is_deadline_flag, "pure": latest_pure, "advisor": advisor_text
            }

            if is_deadline_flag:
                if rate == 100.0 and total_count >= 10:
                    sniper_store[mu_k] = card_payload
                else:
                    hp_store[mu_k] = card_payload
                continue

            if total_count >= 10 and rate == 100.0:
                sniper_store[mu_k] = card_payload
            else:
                hp_store[mu_k] = card_payload

    return hp_store, sniper_store

# ==========================================
# FILE UPLOAD & PRE-PROCESSING
# ==========================================
uploaded_file = st.file_uploader("Bro ရဲ့ 2D CSV သို့မဟုတ် Excel ဖိုင်ကို ရွေးချယ်တင်ပေးပါ...", type=['csv', 'xlsx', 'xls'])

if uploaded_file:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip().str.lower()
    
    if not all(col in df.columns for col in ['year', 'day', 'am1', 'am2', 'pm1', 'pm2']):
        st.error("⚠️ ဖိုင်ထဲတွင် လိုအပ်သော ကော်လံများ (year, day, am1, am2, pm1, pm2) မပြည့်စုံပါ!")
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

        tab_live, tab_custom = st.tabs(["⚡ တွက်ချက်မည်", "🔍 2D Formulas"])

        # ------------------------------------------
        # TAB 1: AUTOMATED ENGINE TRACKER
        # ------------------------------------------
        with tab_live:
            slider_val = st.slider("ရှာလိုသော ပွဲစဉ်အရေအတွက် ရွေးရန်", min_value=1, max_value=10, value=6)
            input_box_val = st.text_input("10 ပွဲထက်ကျော်ပါက ဤနေရာတွင် ရိုက်ထည့်ပါ (ဥပမာ- 12):", value="")
            
            live_max_tf = int(input_box_val.strip()) if (input_box_val.strip() and input_box_val.strip().isdigit()) else slider_val
            live_session_target = f"{target_time_name} သီးသန့်"

            if st.button("ယခုပွဲအတွက် Auto ရှာဖွေမည် ⚡", key="btn_auto"):
                current_end_idx = len(full_draws) - 1
                convergence_pool = []
                detailed_live_store = []
                
                actual_scan_limit = max(live_max_tf, 20)
                
                for step in range(1, actual_scan_limit + 1):
                    target_past_idx = current_end_idx - step + 1
                    if target_past_idx < 0: continue
                    
                    past_obj = full_draws[target_past_idx]
                    past_val = past_obj['draw']
                    past_time = past_obj['time']
                    
                    condition_pools = [
                        {"hits": [d for d in full_draws[:target_past_idx+1] if d['draw'] == past_val and d['time'] == past_time], "lbl": f"{past_val} {past_time}"},
                        {"hits": [d for d in full_draws[:target_past_idx+1] if d['draw'] == past_val], "lbl": f"{past_val}"}
                    ]
                    
                    for pool in condition_pools:
                        if not pool['hits']: continue
                        hp_s, sniper_s = execute_analysis(pool['hits'], full_draws, [(f"{step} ပွဲ", 1, step)], is_custom_tab=False, sel_session=live_session_target)
                        
                        combined_res = {**hp_s, **sniper_s}
                        for mk, mv in combined_res.items():
                            if step <= live_max_tf or not detailed_live_store:
                                convergence_pool.append(mv['pure'])
                                prefix = "🚨 [ရက်ချိန်းပြည့်] " if mv['is_deadline'] else ""
                                detailed_live_store.append({"top": f"{prefix}{mv['top']}", "form": mv['formula'], "bot": mv['bottom'], "step": step, "deadline": mv['is_deadline']})

                st.write("---")
                st.markdown("#### 🏆 TOP RESULTS")
                
                if convergence_pool:
                    top_averages = Counter(convergence_pool).most_common(3)
                    st.markdown('<div class="card card-live"><div style="display:flex; gap:20px; flex-wrap: wrap;">', unsafe_allow_html=True)
                    for idx, (b_val, b_score) in enumerate(top_averages, 1):
                        st.markdown(f"""
                            <div style="background:#1a273f; padding:15px 25px; border-radius:10px; border:1px solid #3498db; min-width:200px;">
                                <span style="color:#54a0ff; font-weight:bold; font-size:16px;">🏆 Top {idx} Convergence:</span> <br>
                                <span class="metric-val" style="margin-top:5px; font-size:16px;">{b_val}</span>
                                <div style="font-size:13px; color:#8cc5ff; margin-top:5px;">ဘုံတူညီမှုအမှတ်: {b_score} ကြိမ်</div>
                            </div>
                        """, unsafe_allow_html=True)
                    st.markdown("</div></div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div style='font-size:15px; font-weight:bold; color:#A294C7; padding:10px;'>အကောင်းဆုံးရလဒ်မရှိပါ</div>", unsafe_allow_html=True)

                st.write("---")
                st.markdown("#### 📋 အသေးစိတ်အချက်အလက်")
                if not detailed_live_store:
                    st.info("မထွက်သေးဘဲ ကျန်ရှိနေသော ရက်ချိန်းပြည့် မူလက်ကျန် လက္ခဏာ မတွေ့ရှိပါ။")
                else:
                    grouped_by_step = {}
                    for item in detailed_live_store:
                        grouped_by_step.setdefault(item['step'], []).append(item)
                    
                    for step_key in sorted(grouped_by_step.keys()):
                        card_list = grouped_by_step[step_key]
                        is_any_deadline = any(c['deadline'] for c in card_list)
                        header_title = f"⚠️ {step_key} ပွဲအတွင်း မူများ [ရက်ချိန်းပြည့်]" if is_any_deadline else f"🔽 {step_key} ပွဲအတွင်း မူများ"
                            
                        with st.expander(header_title, expanded=True):
                            for d_card in card_list:
                                fallback_label = ""
                                if d_card['step'] > live_max_tf:
                                    fallback_label = f" <span style='color:#FF4D4D; font-size:12px;'>[Auto Backstep ခြေရာခံမှု: ပွဲစဉ် {d_card['step']}]</span>"
                                
                                st.markdown(f"""
                                <div class="card card-sniper">
                                    <span class="line-trigger">{d_card['top']}{fallback_label}</span>
                                    <span class="line-formula">{d_card['form']}</span>
                                    <span class="line-history">{d_card['bot']}</span>
                                </div>
                                """, unsafe_allow_html=True)

        # ------------------------------------------
        # TAB 2: CLEAN CUSTOM FORMULARS ENGINE (Exact Bounds Main Frame)
        # ------------------------------------------
        with tab_custom:
            c1, c2, c3 = st.columns(3)
            with c1:
                trigger_day = st.selectbox("📆 Trigger Day:", ["All", "Mon", "Tue", "Wed", "Thur", "Fri"], index=0)
                trigger_num = st.text_input("🔍 ရှာလိုသောဂဏန်း ရိုက်ထည့်ပါ:", value="48", max_chars=7)
            with c2:
                if trigger_day != "All":
                    st.markdown("<span style='color:#00FFCC; font-size:13px;'>ℹ️ Day စနစ်သုံးထားသဖြင့် အကြိမ်ရေပြည့်မီစေရန် R-စနစ် နှင့် AM+PM ပေါင်းချုပ် စနစ်ကို Backend က Auto Lock ချပေးထားပါသည်။</span>", unsafe_allow_html=True)
                    target_session_custom = "AM+PM ပေါင်းချုပ်"
                else:
                    target_session_custom = st.selectbox("⏱️ Target ပွဲစဉ် အခြေအနေ ရွေးရန်:", ["AM+PM ပေါင်းချုပ်", "AM သီးသန့်", "PM သီးသန့်"], index=2)
            with c3:
                custom_max_tf = st.number_input("⏳ စစ်ဆေးမည့် ပွဲစဉ်အရေအတွက်", min_value=1, max
