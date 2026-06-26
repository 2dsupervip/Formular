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
    .card-recovered { border-left: 6px solid #e74c3c; background-color: #291118; }
    
    /* Layout Inner Elements */
    .card-top-line { font-size: 18px; font-weight: bold; color: #E0D5FA; line-height: 1.8; margin-bottom: 8px; }
    .card-bottom-line { font-size: 15px; color: #A294C7; margin-top: 5px; }
    
    /* Dynamic Badge Blocks (SS2 Layout Style) */
    .badge-inline { padding: 2px 10px; border-radius: 6px; font-size: 14px; font-weight: bold; margin-left: 6px; margin-right: 6px; display: inline-block; vertical-align: middle; }
    .badge-inline-sniper { background-color: #9b59b6; color: white; }
    .badge-inline-hp { background-color: #2ecc71; color: #0D2216; }
    
    .target-output-text { color: #FFD700; font-size: 24px; font-weight: bold; margin-left: 4px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🤖 THE PERFECT 2D AI MASTER (V26 PRO)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Ultimate 4-Pool Convergence Engine | "ရက်ချိန်းပြည့်မူ" & Top-Down Display Architecture</div>', unsafe_allow_html=True)

special_groups = {
    "ညီကို": {"01","10","12","21","23","32","34","43","45","54","56","65","67","76","78","87","89","98","90","09"},
    "ပါဝါ": {"05","50","16","61","27","72","38","83","49","94"},
    "နက္ခတ်": {"07","70","18","81","24","42","35","53","69","96"},
    "ထိုင်းပါဝါ": {"09","90","13","31","26","62","47","74","58","85"},
    "အပူး": {"00","11","22","33","44","55","66","77","88","99"},
    "ဆယ်ပြည့်": {"10","01","20","02","30","03","40","04","50","05","60","06","70","07","80","08","90","09"}
}

GLOBAL_TFS = [("၁ ပွဲ", 1, 1), ("၂ ပွဲ", 1, 2), ("၃ ပွဲ", 1, 3), ("၄ ပွဲ", 1, 4), ("၅ ပွဲ", 1, 5),
              ("၆ ပွဲ", 1, 6), ("၈ ပွဲ", 1, 8), ("၁၀ ပွဲ", 1, 10), ("၁၂ ပွဲ", 1, 12), ("၁၆ ပွဲ", 1, 16), ("၂၀ ပွဲ", 1, 20)]

# ==========================================
# HELPER: CHECK IF VALUE ALREADY HIT IN RECENT TIMELINE
# ==========================================
def is_already_hit(mu_name, mu_val, start_idx, end_idx, full_draws_list):
    if start_idx >= len(full_draws_list): return True
    check_draws = [d['draw'] for d in full_draws_list[start_idx : min(end_idx + 1, len(full_draws_list))]]
    if not check_draws: return False
    
    if "လုံးဘိုင်" in mu_name:
        return any(mu_val in d for d in check_draws)
    elif "One Change" in mu_name or "key" in mu_name or "အမာခံ" in mu_name:
        return any(any(x in d for x in mu_val) for d in check_draws)
    elif "ခွေ" in mu_name:
        return any(d[0] in mu_val and d[1] in mu_val for d in check_draws)
    elif "ထိပ်စီး" in mu_name:
        return any(d[0] in mu_val for d in check_draws)
    elif "ဘရိတ်" in mu_name:
        brk_list = [x.strip() for x in mu_val.split(',')]
        return any(str((int(d[0])+int(d[1]))%10) in brk_list for d in check_draws)
    elif "စုံ/မ ကပ်" in mu_name:
        b1 = mu_val.split('[')[1].split(']')[0] if '[' in mu_val else ""
        is_even = "အစုံကပ်" in mu_val
        mway_digits = [f"{b1}{i}" for i in ([0,2,4,6,8] if is_even else [1,3,5,7,9])] if b1 else []
        return any(d in mway_digits for d in check_draws)
    elif "အုပ်စုတွဲ" in mu_name or "group" in mu_name:
        if mu_val == "-": return True
        g1, g2 = mu_val.split('+')[0], mu_val.split('+')[1] if '+' in mu_val else (mu_val, "")
        return any(d in special_groups.get(g1, set()) or d in special_groups.get(g2, set()) for d in check_draws)
    return False

# ==========================================
# CORE ENGINE: SINGLE EVENT EVALUATOR
# ==========================================
def run_mu_evaluation(hit_idx, full_draws_list, s_off, e_off):
    s_idx = hit_idx + s_off
    e_idx = min(hit_idx + e_off + 1, len(full_draws_list))
    if s_idx >= len(full_draws_list): return None
    
    sub_draws = [d['draw'] for d in full_draws_list[s_idx : e_idx]]
    if not sub_draws: return None

    all_singles = "".join(sub_draws)
    all_heads = [d[0] for d in sub_draws]
    all_breaks = [str((int(d[0]) + int(d[1])) % 10) for d in sub_draws]

    top_single = Counter(all_singles).most_common(1)[0][0] if all_singles else ""
    top_oc = "".join([x[0] for x in Counter(all_singles).most_common(2)]) if len(Counter(all_singles)) >= 2 else top_single
    top_key3 = "".join([x[0] for x in Counter(all_singles).most_common(3)]) if len(Counter(all_singles)) >= 3 else top_oc
    top_k4 = "".join([x[0] for x in Counter(all_singles).most_common(4)]) if len(Counter(all_singles)) >= 4 else top_key3
    top_h3 = "".join([x[0] for x in Counter(all_heads).most_common(3)]) if all_heads else ""
    top_brk2 = [x[0] for x in Counter(all_breaks).most_common(2)]

    e_sc = sum(1 for d in sub_draws if top_single in d and int(d.replace(top_single,'',1) if d.replace(top_single,'',1) else top_single) % 2 == 0)
    o_sc = sum(1 for d in sub_draws if top_single in d and int(d.replace(top_single,'',1) if d.replace(top_single,'',1) else top_single) % 2 != 0)
    mway_label = f"[{top_single}] အစုံကပ်" if e_sc >= o_sc else f"[{top_single}] အမကပ်"
    mway_digits = [f"{top_single}{i}" for i in ([0,2,4,6,8] if e_sc >= o_sc else [1,3,5,7,9])]

    best_gp = ""; max_gp_c = 0
    for combo in itertools.combinations(special_groups.keys(), 2):
        c = sum(1 for d in sub_draws if d in special_groups[combo[0]] or d in special_groups[combo[1]])
        if c > max_gp_c: max_gp_c = c; best_gp = f"{combo[0]}+{combo[1]}"

    valid_pairs = [f"{i:02d}" for i in range(100) if any(k in f"{i:02d}" for k in top_key3) and str((i//10 + i%10)%10) in top_brk2]

    act_draws = [d['draw'] for d in full_draws_list[hit_idx+1 : min(hit_idx+e_off+1, len(full_draws_list))]]
    if not act_draws: return None

    if best_gp and '+' in best_gp:
        g1_key, g2_key = best_gp.split('+')[0], best_gp.split('+')[1]
        gp_hit = any(d in special_groups.get(g1_key, set()) or d in special_groups.get(g2_key, set()) for d in act_draws)
    else:
        gp_hit = False

    return {
        "လုံးဘိုင်": {"val": top_single, "hit": any(top_single in d for d in act_draws)},
        "One Change": {"val": top_oc, "hit": any(any(x in d for x in top_oc) for d in act_draws)},
        "key": {"val": top_key3, "hit": any(any(x in d for x in top_key3) for d in act_draws)},
        "အပူးပါခွေ": {"val": top_k4, "hit": any(d[0] in top_k4 and d[1] in top_k4 for d in act_draws)},
        "ထိပ်စီး": {"val": top_h3, "hit": any(d[0] in top_h3 for d in act_draws)},
        "ဘရိတ်": {"val": ", ".join(top_brk2), "hit": any(str((int(d[0])+int(d[1]))%10) in top_brk2 for d in act_draws)},
        "စုံ/မ ကပ်": {"val": f"{mway_label}", "hit": any(d in mway_digits for d in act_draws)},
        "group_two": {"val": best_gp if best_gp else "-", "hit": gp_hit},
        "ကွက်ကျဉ်းတွဲစနစ်": {"val": "ကွက်ကျဉ်းတွဲစနစ်", "hit": any(d in valid_pairs for d in act_draws)}
    }

# ==========================================
# MASTER ROUTINE: HYBRID DATA ANALYSIS ENGINE
# ==========================================
def execute_analysis(target_hits, full_draws, active_tfs, label_prefix):
    hp_store = {}
    sniper_store = {}
    recovered_store = []
    current_latest_idx = len(full_draws) - 1

    for tf_name, s_off, e_off in active_tfs:
        sequence_tracker = {f"mu_{m}": [] for m in range(1, 10)}
        mu_latest_values = {}
        mu_keys_list = []

        for hit in target_hits:
            res = run_mu_evaluation(hit['index'], full_draws, s_off, e_off)
            if res:
                if not mu_keys_list: mu_keys_list = list(res.keys())
                for m_idx, mu_k in enumerate(mu_keys_list, 1):
                    sequence_tracker[f"mu_{m_idx}"].append(res[mu_k]['hit'])
                    mu_latest_values[mu_k] = res[mu_k]['val']

        if not mu_keys_list: continue

        for m_idx, mu_k in enumerate(mu_keys_list, 1):
            seq = sequence_tracker[f"mu_{m_idx}"]
            if len(seq) < 5: continue
            
            win_count = sum(1 for x in seq if x)
            total_count = len(seq)
            rate = (win_count / total_count) * 100

            is_deadline_flag = False
            if target_hits:
                last_hit_global_idx = target_hits[-1]['index']
                elapsed_draws = current_latest_idx - last_hit_global_idx
                
                if (elapsed_draws + 1) == e_off:
                    already_out = is_already_hit(mu_k, mu_latest_values[mu_k], last_hit_global_idx + 1, current_latest_idx, full_draws)
                    if not already_out:
                        is_deadline_flag = True

            display_val = mu_latest_values[mu_k]
            display_suffix = f" {mu_k}" if mu_k != "group_two" else ""
            rate_str = "100%" if rate == 100.0 else f"{rate:.1f}%"
            
            # SS2 Style HTML Engine Construction (၂ လိုင်းစနစ်ခွဲထုတ်မှု)
            badge_color_class = "badge-inline-sniper" if rate == 100.0 else "badge-inline-hp"
            
            top_line_html = f"🔮 [{label_prefix}] ထွက်ပြီးလျှင် <span class='badge-inline {badge_color_class}'>{tf_name}အတွင်း</span> <span class='target-output-text'>{display_val}</span>{display_suffix} {rate_str}"
            bottom_line_html = f"မှန်ကန်မှု: ({total_count} ကြိမ်မှာ {win_count} ကြိမ်မှန်)"

            card_payload = {"top": top_line_html, "bottom": bottom_line_html, "e_off": e_off, "is_deadline": is_deadline_flag}

            if is_deadline_flag:
                if rate == 100.0 and total_count >= 10:
                    sniper_store[mu_k] = card_payload
                elif rate >= 95.0:
                    hp_store[mu_k] = card_payload
                continue

            if total_count >= 10 and rate == 100.0:
                if mu_k not in sniper_store or e_off > sniper_store[mu_k]['e_off']:
                    sniper_store[mu_k] = card_payload
            elif rate >= 95.0:
                if mu_k not in hp_store or e_off > hp_store[mu_k]['e_off']:
                    hp_store[mu_k] = card_payload

            # ၃ ကြိမ်ဆက်မှား၊ ၂ ကြိမ်ဆက်ပြန်မှန် (Recovered Sniper)
            if total_count >= 19:
                baseline_seq = seq[:-5]
                baseline_rate = (sum(1 for x in baseline_seq if x) / total_count) * 100 if baseline_seq else 0
                if baseline_rate >= 95.0 and seq[-5:] == [False, False, False, True, True]:
                    rec_top = f"🚨 [ရက်ချိန်းပြည့်] [{label_prefix}] ထွက်ပြီးလျှင် <span class='badge-inline badge-inline-hp'>{tf_name}အတွင်း</span> <span class='target-output-text'>{display_val}</span>{display_suffix}"
                    recovered_store.append({"mu": mu_k, "top": rec_top, "bottom": bottom_line_html})

    return hp_store, sniper_store, recovered_store


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
        auto_next_session = 'PM သီးသန့်' if last_recorded_draw['time'] == 'AM' else 'AM သီးသန့်'
        auto_display_text = f"ဖိုင်ထဲက နောက်ဆုံးပွဲသည် [{last_recorded_draw['day']} {last_recorded_draw['time']}] ဖြစ်သဖြင့် ယခုတွက်ရမည့်အချိန်မှာ Auto ➡️ [{auto_next_session}] ဖြစ်ပါသည်။"

        st.success(f"🔮 ဒေတာပွဲစဉ်ပေါင်း {len(full_draws)} ခု ဖတ်ပြီးပါပြီ။ {auto_display_text}")
        st.write("---")

        tab_live, tab_custom = st.tabs(["⚡ (၁) ယခုအချိန်အတွက် အလိုအလျောက်တွက်ချက်မှု", "🔍 (၂) မိမိစိတ်ကြိုက် ဂဏန်းအလိုက် ရှာဖွေမှု"])

        # ------------------------------------------
        # TAB 1: AUTOMATED ENGINE TRACKER
        # ------------------------------------------
        with tab_live:
            st.markdown("### ယခုအချိန်အတွက် အလိုအလျောက် 4-Pool Scan & Convergence Engine")
            col1, col2 = st.columns(2)
            with col1:
                live_max_tf = st.selectbox("🎯 Live Tracker Countdown Bound (အထက်ဂဏန်းပမာဏ):", [5, 10, 12, 16, 20], index=1, key="live_max")
            with col2:
                st.info(f"ယခုပွဲစဉ်အတွက် [AM, PM, AM+PM, Day Alignment] ၄ လိုင်းစနစ်လုံးကို Auto သိမ်းကျုံးတွက်ချက်ပါမည်။")

            if st.button("ယခုပွဲအတွက် Auto ရှာဖွေမည် ⚡", key="btn_auto"):
                current_end_idx = len(full_draws) - 1
                convergence_pool = []
                
                for step in range(live_max_tf, 0, -1):
                    target_past_idx = current_end_idx - step + 1
                    if target_past_idx < 0: continue
                    
                    past_obj = full_draws[target_past_idx]
                    past_val = past_obj['draw']
                    rev_past_val = past_val[::-1]
                    past_day = past_obj['day']

                    all_hits = [d for d in full_draws[:target_past_idx+1] if d['draw'] == past_val]
                    day_hits = [d for d in full_draws[:target_past_idx+1] if d['day'] == past_day and (d['draw'] == past_val or d['draw'] == rev_past_val)]

                    combined_hits = all_hits + day_hits
                    seen_indices = set()
                    
                    for hit in combined_hits:
                        if hit['index'] in seen_indices: continue
                        seen_indices.add(hit['index'])
                        
                        res_live = run_mu_evaluation(hit['index'], full_draws, 1, step)
                        if res_live:
                            for m_k, m_v in res_live.items():
                                already_out = is_already_hit(m_k, m_v['val'], hit['index'] + 1, current_end_idx, full_draws)
                                if not already_out:
                                    convergence_pool.append(m_v['val'])

                # ==========================================
                # TOP-DOWN RENDERING SYSTEM
                # ==========================================
                st.write("---")
                st.markdown("#### 🏆 [အဆင့် ၁] TOP PICK CONVERGENCE (ဘုံတူညီမှု အားအကောင်းဆုံးရလဒ်)")
                
                if convergence_pool:
                    flat_values = []
                    for val in convergence_pool:
                        extracted = re.findall(r'\d+', val)
                        flat_values.extend(extracted) if extracted else flat_values.append(val)
                    top_averages = Counter(flat_values).most_common(3)

                    st.markdown('<div class="card card-live"><div style="display:flex; gap:20px; flex-wrap: wrap;">', unsafe_allow_html=True)
                    for idx, (b_val, b_score) in enumerate(top_averages, 1):
                        st.markdown(f"""
                            <div style="background:#1a273f; padding:15px 25px; border-radius:10px; border:1px solid #3498db; min-width:200px;">
                                <span style="color:#54a0ff; font-weight:bold; font-size:16px;">🏆 Top {idx} Convergence:</span> <br>
                                <span class="metric-val" style="margin-top:5px;">{b_val}</span>
                                <div style="font-size:13px; color:#8cc5ff; margin-top:5px;">၄ လိုင်းပေါင်းချုပ် ဘုံတူညီမှုအမှတ်: {b_score} ကြိမ်</div>
                            </div>
                        """, unsafe_allow_html=True)
                    st.markdown("</div></div>", unsafe_allow_html=True)
                else:
                    st.info("ယခုပွဲအတွက် ရက်ချိန်းစေ့ မူလက်ကျန် ဘုံတူညီမှု မရှိသေးပါ။")

                st.write("---")
                st.markdown("#### 📋 [အဆင့် ၂] DETAILED BREAKDOWN (မူတစ်ခုချင်းစီအလိုက် အသေးစိတ်ဆန်းစစ်ချက်)")
                
                auto_target_hits = [d for d in full_draws if d['draw'] == last_recorded_draw['draw']]
                lbl_p = f"{last_recorded_draw['draw']}"
                hp_s, sniper_s, recovered_s = execute_analysis(auto_target_hits, full_draws, GLOBAL_TFS, lbl_p)

                if recovered_s:
                    st.markdown("##### 🚨 ပျက်ပြီးပြန်နိုးထလာသော မူသေစနစ် (Recovered Sniper)")
                    for r in recovered_s:
                        st.markdown(f"""
                        <div class="card card-recovered">
                            <div class="card-top-line">{r['top']}</div>
                            <div class="card-bottom-line">{r['bottom']}</div>
                        </div>
                        """, unsafe_allow_html=True)

                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown("##### 🦅 100% Super VIP Sniper Zone")
                    if not sniper_s: st.info("၁၀၀% ကွက်တိ မူများ မတွေ့ရှိပါ။")
                    for mu_name, data in sniper_s.items():
                        prefix = "🚨 [ရက်ချိန်းပြည့်] " if data['is_deadline'] else ""
                        st.markdown(f"""
                        <div class="card card-sniper">
                            <div class="card-top-line">{prefix}{data['top']}</div>
                            <div class="card-bottom-line">{data['bottom']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                with col_b:
                    st.markdown("##### 🔮 95%+ High-Probability Zone")
                    if not hp_s: st.info("၉၅% အထက် Probability ရှိသော မူများ မတွေ့ရှိပါ။")
                    for mu_name, data in hp_s.items():
                        prefix = "🚨 [ရက်ချိန်းပြည့်] " if data['is_deadline'] else ""
                        st.markdown(f"""
                        <div class="card card-hp">
                            <div class="card-top-line">{prefix}{data['top']}</div>
                            <div class="card-bottom-line">{data['bottom']}</div>
                        </div>
                        """, unsafe_allow_html=True)

        # ------------------------------------------
        # TAB 2: CUSTOM MANUAL SEARCH TRACKER
        # ------------------------------------------
        with tab_custom:
            st.markdown("### မိမိစိတ်ကြိုက် ပြက္ခဒိန်နှင့် ဂဏန်းအလိုက် မူရှာဖွေခြင်း")
            c1, c2, c3 = st.columns(3)
            with c1:
                trigger_day = st.selectbox("📆 Trigger အစပျိုးရက် (All သည် Single Trigger အလုပ်လုပ်ပါမည်):", ["All", "Mon", "Tue", "Wed", "Thur", "Fri"], index=0, key="cust_day")
                trigger_num = st.text_input("🔍 ထွက်ဂဏန်း ရိုက်ထည့်ပါ:", value="60", max_chars=2, key="cust_num")
            with c2:
                target_session_custom = st.selectbox("⏱️ ပစ်မှတ် Session စစ်ဆေးရန်:", ["AM+PM ပေါင်းချုပ်", "AM သီးသန့်", "PM သီးသန့်"], key="cust_sess")
            with c3:
                tf_labels = [x[0] for x in GLOBAL_TFS]
                selected_tfs = st.multiselect("⏳ စစ်ဆေးမည့် ပွဲစဉ်အရေအတွက် Box:", tf_labels, default=tf_labels, key="cust_tf")

            active_tfs_custom = [x for x in GLOBAL_TFS if x[0] in selected_tfs]

            if st.button("သီးသန့် Pattern ရှာဖွေမည် 🚀", key="btn_custom"):
                target_hits = []
                rev_num = trigger_num[::-1]

                if trigger_day == "All":
                    target_hits = [d for d in full_draws if d['draw'] == trigger_num or d['draw'] == rev_num]
                    lbl_prefix = f"{trigger_num}"
                else:
                    matched_weeks = {d['row_idx'] for d in full_draws if d['day'] == trigger_day and (d['draw'] == trigger_num or d['draw'] == rev_num)}
                    for d in full_draws:
                        if d['row_idx'] in matched_weeks:
                            if target_session_custom == "AM+PM ပေါင်းချုပ်":
                                target_hits.append(d)
                            else:
                                t_sess = 'AM' if "AM" in target_session_custom else 'PM'
                                if d['time'] == t_sess: target_hits.append(d)
                    
                    t_time_label = "PM" if "PM" in target_session_custom else "AM" if "AM" in target_session_custom else ""
                    lbl_prefix = f"{trigger_num} {t_time_label}".strip()

                if not target_hits:
                    st.error("⚠️ သတ်မှတ်ချက်များနှင့် ကိုက်ညီသော သမိုင်းကြောင်းမှတ်တမ်း မရှိပါ Bro!")
                else:
                    hp_store, sniper_store, recovered_store = execute_analysis(target_hits, full_draws, active_tfs_custom, lbl_prefix)

                    st.write("---")
                    st.markdown("#### 🏆 [အဆင့် ၁] TOP PICK CONVERGENCE (ဘုံတူညီမှု အားအကောင်းဆုံးရလဒ်)")
                    
                    custom_pool = []
                    for h_obj in target_hits:
                        for t_lbl, s_o, e_o in active_tfs_custom:
                            res_c = run_mu_evaluation(h_obj['index'], full_draws, s_o, e_o)
                            if res_c:
                                for mk, mv in res_c.items():
                                    if not is_already_hit(mk, mv['val'], h_obj['index'] + 1, len(full_draws) - 1, full_draws):
                                        custom_pool.append(mv['val'])

                    if custom_pool:
                        flat_vals_c = []
                        for val in custom_pool:
                            extracted = re.findall(r'\d+', val)
                            flat_vals_c.extend(extracted) if extracted else flat_vals_c.append(val)
                        top_averages_c = Counter(flat_vals_c).most_common(3)

                        st.markdown('<div class="card card-live"><div style="display:flex; gap:20px; flex-wrap:wrap;">', unsafe_allow_html=True)
                        for idx, (b_val, b_score) in enumerate(top_averages_c, 1):
                            st.markdown(f"""
                                <div style="background:#1a273f; padding:15px 25px; border-radius:10px; border:1px solid #3498db; min-width:200px;">
                                    <span style="color:#54a0ff; font-weight:bold; font-size:16px;">🏆 Top {idx} Convergence:</span> <br>
                                    <span class="metric-val" style="margin-top:5px;">{b_val}</span>
                                    <div style="font-size:13px; color:#8cc5ff; margin-top:5px;">ဘုံတူညီမှုအမှတ်: {b_score} ကြိမ်</div>
                                </div>
                            """, unsafe_allow_html=True)
                        st.markdown("</div></div>", unsafe_allow_html=True)

                    st.write("---")
                    st.markdown("#### 📋 [အဆင့် ၂] DETAILED BREAKDOWN (မူတစ်ခုချင်းစီအလိုက် အသေးစိတ်ဆန်းစစ်ချက်)")

                    if recovered_store:
                        st.markdown("##### 🚨 ပျက်ပြီးပြန်နိုးထလာသော မူသေစနစ် (Recovered Sniper)")
                        for r in recovered_store:
                            st.markdown(f"""
                            <div class="card card-recovered">
                                <div class="card-top-line">{r['top']}</div>
                                <div class="card-bottom-line">{r['bottom']}</div>
                            </div>
                            """, unsafe_allow_html=True)

                    col_tab1, col_tab2 = st.tabs(["🦅 100% Super VIP Sniper Zone", "🔮 95%+ High-Probability Zone"])

                    with col_tab1:
                        if not sniper_store: st.info("၁၀၀% ကွက်တိ မူများ မတွေ့ရှိပါ။")
                        else:
                            for mu_name, data in sniper_store.items():
                                prefix = "🚨 [ရက်ချိန်းပြည့်] " if data['is_deadline'] else ""
                                st.markdown(f"""
                                <div class="card card-sniper">
                                    <div class="card-top-line">{prefix}{data['top']}</div>
                                    <div class="card-bottom-line">{data['bottom']}</div>
                                </div>
                                """, unsafe_allow_html=True)

                    with col_tab2:
                        if not hp_store: st.info("၉၅% အထက် Probability ရှိသော မူများ မတွေ့ရှိပါ။")
                        else:
                            for mu_name, data in hp_store.items():
                                prefix = "🚨 [ရက်ချိန်းပြည့်] " if data['is_deadline'] else ""
                                st.markdown(f"""
                                <div class="card card-hp">
                                    <div class="card-top-line">{prefix}{data['top']}</div>
                                    <div class="card-bottom-line">{data['bottom']}</div>
                                </div>
                                """, unsafe_allow_html=True)
else:
    st.info("စတင်ရန်အတွက် Bro ရဲ့ 2D CSV သို့မဟုတ် Excel ဒေတာဖိုင်ကို အပေါ်တွင် အရင် တင်ပေးပါဦး။")
