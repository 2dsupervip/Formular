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
    .card { background-color: #170E2B; padding: 22px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); margin-bottom: 20px; border: 1px solid #2D1B4E; }
    .card-live { border-left: 6px solid #3498db; background-color: #0E1A2F; }
    .card-hp { border-left: 6px solid #2ecc71; background-color: #0D2216; }
    .card-sniper { border-left: 6px solid #9b59b6; background-color: #201135; }
    .card-recovered { border-left: 6px solid #e74c3c; background-color: #291118; }
    .card-header { font-size: 19px; font-weight: bold; color: #FFF; margin-bottom: 8px; }
    .metric-val { font-size: 26px; font-weight: bold; color: #FFD700; background: #2D1B4E; padding: 2px 12px; border-radius: 8px; border: 1px solid #442975; display: inline-block; }
    .badge { padding: 3px 8px; border-radius: 5px; font-size: 12px; font-weight: bold; margin-left: 10px; }
    .badge-sniper { background-color: #9b59b6; color: white; }
    .badge-hp { background-color: #2ecc71; color: white; }
    .badge-recovered { background-color: #e74c3c; color: white; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🤖 THE PERFECT 2D AI MASTER (V26 PRO)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Hybrid Convergence Engine | "ရက်ချိန်းပြည့်မူ" Tracking & Live Session Automation</div>', unsafe_allow_html=True)

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
# HELPER: CHECK IF VALUE ALREADY HIT IN ACTUAL RECENT DRAWS
# ==========================================
def is_already_hit(mu_name, mu_val, start_idx, end_idx, full_draws_list):
    """လက်ရှိ အပြင်ပွဲစဉ် Timeline တွင် ၎င်းမူသည် ကြားထဲ၌ ထွက်သွားပြီးပြီလား စစ်ဆေးခြင်း"""
    if start_idx >= len(full_draws_list): return True
    check_draws = [d['draw'] for d in full_draws_list[start_idx : min(end_idx + 1, len(full_draws_list))]]
    
    if not check_draws: return False
    
    if "လုံးဘိုင်" in mu_name:
        return any(mu_val in d for d in check_draws)
    elif "One Change" in mu_name or "အမာခံ ၃ လုံး" in mu_name:
        return any(any(x in d for x in mu_val) for d in check_draws)
    elif "၄ လုံးခွေ" in mu_name:
        return any(d[0] in mu_val and d[1] in mu_val for d in check_draws)
    elif "ထိပ်စီး ၃ လုံး" in mu_name:
        return any(d[0] in mu_val for d in check_draws)
    elif "ဘရိတ် ၂ လုံး" in mu_name:
        brk_list = [x.strip() for x in mu_val.split(',')]
        return any(str((int(d[0])+int(d[1]))%10) in brk_list for d in check_draws)
    elif "စုံ/မ ကပ်" in mu_name:
        b1 = mu_val.split('[')[1].split(']')[0] if '[' in mu_val else ""
        is_even = "အစုံကပ်" in mu_val
        mway_digits = [f"{b1}{i}" for i in ([0,2,4,6,8] if is_even else [1,3,5,7,9])] if b1 else []
        return any(d in mway_digits for d in check_draws)
    elif "အုပ်စု (၁) ခုတည်း" in mu_name:
        return any(d in special_groups.get(mu_val, set()) for d in check_draws)
    elif "အုပ်စုတွဲ (၂) ခု" in mu_name:
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

    best_sg = max(special_groups.keys(), key=lambda g: sum(1 for d in sub_draws if d in special_groups[g]), default="")
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
        "1. လုံးဘိုင်": {"val": top_single, "hit": any(top_single in d for d in act_draws)},
        "2. One Change": {"val": top_oc, "hit": any(any(x in d for x in top_oc) for d in act_draws)},
        "3. အမာခံ ၃ လုံး": {"val": top_key3, "hit": any(any(x in d for x in top_key3) for d in act_draws)},
        "4. ၄ လုံးခွေ": {"val": top_k4, "hit": any(d[0] in top_k4 and d[1] in top_k4 for d in act_draws)},
        "5. ထိပ်စီး ၃ လုံး": {"val": top_h3, "hit": any(d[0] in top_h3 for d in act_draws)},
        "6. ဘရိတ် ၂ လုံး": {"val": ", ".join(top_brk2), "hit": any(str((int(d[0])+int(d[1]))%10) in top_brk2 for d in act_draws)},
        "7. စုံ/မ ကပ် (၅ ကွက်)": {"val": f"{mway_label}", "hit": any(d in mway_digits for d in act_draws)},
        "8. အုပ်စု (၁) ခုတည်း": {"val": best_sg, "hit": any(d in special_groups.get(best_sg, set()) for d in act_draws)},
        "9. အုပ်စုတွဲ (၂) ခု": {"val": best_gp if best_gp else "-", "hit": gp_hit},
        "10. အမာခံအပါ ဘရိတ် (၂လုံး)": {"val": "ကွက်ကျဉ်းတွဲစနစ်", "hit": any(d in valid_pairs for d in act_draws)}
    }

# ==========================================
# MAIN EXECUTION ROUTINE
# ==========================================
def execute_analysis(target_hits, full_draws, active_tfs):
    hp_store = {}
    sniper_store = {}
    recovered_store = []
    current_latest_idx = len(full_draws) - 1

    for tf_name, s_off, e_off in active_tfs:
        sequence_tracker = {f"mu_{m}": [] for m in range(1, 11)}
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
            rate = (sum(1 for x in seq if x) / len(seq)) * 100

            # 🚨 ရက်ချိန်းပြည့်မူ စစ်ဆေးချက် Logic (လက်ရှိအပြင်Timeline ၌ မလာသေးမှသာ ပြသရန်)
            if target_hits:
                last_hit_global_idx = target_hits[-1]['index']
                # ကြားထဲတွင် ကုန်ဆုံးသွားသော ပွဲစဉ်အရေအတွက် တွက်ချက်ခြင်း
                elapsed_draws = current_latest_idx - last_hit_global_idx
                
                # လက်ရှိပွဲသည် ရက်ချိန်းပြည့်ပွဲ (e_off မြောက်) ကွက်တိဖြစ်နေပြီး ကြားထဲတွင် မထွက်သေးပါက ရက်ချိန်းပြည့်မူအဖြစ် သတ်မှတ်
                if (elapsed_draws + 1) == e_off:
                    already_out = is_already_hit(mu_k, mu_latest_values[mu_k], last_hit_global_idx + 1, current_latest_idx, full_draws)
                    if not already_out:
                        if rate == 100.0 and len(seq) >= 10:
                            sniper_store[mu_k] = {"tf": tf_name, "val": mu_latest_values[mu_k], "rate": rate, "hits": len(seq), "e_off": e_off, "is_deadline": True}
                        elif rate >= 95.0:
                            hp_store[mu_k] = {"tf": tf_name, "val": mu_latest_values[mu_k], "rate": rate, "hits": len(seq), "e_off": e_off, "is_deadline": True}
                        continue

            # ပုံမှန် ရက်ချိန်းမစေ့သေးသော မူများအတွက် Max Bound (နယ်ကုန်စနစ်)
            if len(seq) >= 10 and rate == 100.0:
                if mu_k not in sniper_store or e_off > sniper_store[mu_k]['e_off']:
                    sniper_store[mu_k] = {"tf": tf_name, "val": mu_latest_values[mu_k], "rate": rate, "hits": len(seq), "e_off": e_off, "is_deadline": False}
            elif rate >= 95.0:
                if mu_k not in hp_store or e_off > hp_store[mu_k]['e_off']:
                    hp_store[mu_k] = {"tf": tf_name, "val": mu_latest_values[mu_k], "rate": rate, "hits": len(seq), "e_off": e_off, "is_deadline": False}

            # ၃ ကြိမ်ဆက်မှား၊ ၂ ကြိမ်ဆက်ပြန်မှန် (Recovered Sniper)
            if len(seq) >= 19:
                baseline_seq = seq[:-5]
                baseline_rate = (sum(1 for x in baseline_seq if x) / len(baseline_seq)) * 100 if baseline_seq else 0
                if baseline_rate >= 95.0 and seq[-5:] == [False, False, False, True, True]:
                    recovered_store.append({"mu": mu_k, "tf": tf_name, "val": mu_latest_values[mu_k]})

    return hp_store, sniper_store, recovered_store


# ==========================================
# FILE UPLOAD & AUTOMATED DETECTION
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

        # Build Chronological List
        full_draws = []
        for idx, row in df.iterrows():
            if pd.notna(row['am1']) and pd.notna(row['am2']):
                full_draws.append({'draw': f"{int(row['am1'])}{int(row['am2'])}", 'time': 'AM', 'day': row['day'], 'year': int(row['year']), 'row_idx': idx})
            if pd.notna(row['pm1']) and pd.notna(row['pm2']):
                full_draws.append({'draw': f"{int(row['pm1'])}{int(row['pm2'])}", 'time': 'PM', 'day': row['day'], 'year': int(row['year']), 'row_idx': idx})

        for i, d in enumerate(full_draws): d['index'] = i

        # 🚨 AUTO SESSION DETECTION LOGIC
        last_recorded_draw = full_draws[-1]
        if last_recorded_draw['time'] == 'AM':
            auto_next_session = 'PM သီးသန့်'
            auto_display_text = f"ဖိုင်ထဲက အောက်ဆုံးပွဲသည် [{last_recorded_draw['day']} AM] ဖြစ်သောကြောင့် ယခုတွက်ရမည့်အချိန်မှာ Auto ➡️ [{last_recorded_draw['day']} PM] ဖြစ်ပါသည်။"
        else:
            auto_next_session = 'AM သီးသန့်'
            auto_display_text = f"ဖိုင်ထဲက အောက်ဆုံးပွဲသည် [{last_recorded_draw['day']} PM] ဖြစ်သောကြောင့် ယခုတွက်ရမည့်အချိန်မှာ Auto ➡️ [နောက်ရက်မနက် AM] ဖြစ်ပါသည်။"

        st.success(f"🔮 ဒေတာပွဲစဉ်ပေါင်း {len(full_draws)} ခု ဖတ်ပြီးပါပြီ။ {auto_display_text}")
        st.write("---")

        # ==========================================
        # WORKSPACE SEPARATION TABS (စနစ်နှစ်ခုကို ရှင်းလင်းစွာ ခွဲခြားပေးခြင်း)
        # ==========================================
        tab_live, tab_custom = st.tabs(["⚡ (၁) ယခုအချိန်အတွက် အလိုအလျောက်တွက်ချက်မှု", "🔍 (၂) မိမိစိတ်ကြိုက် ဂဏန်းတစ်လုံးချင်းစီ ရှာဖွေမှု"])

        # ------------------------------------------
        # TAB 1: AUTOMATED LIVE MATRIX WORKSPACE
        # ------------------------------------------
        with tab_live:
            st.markdown("### ယခုအချိန်အတွက် အလိုအလျောက် Convergence & ရက်ချိန်းပြည့်မူ Dashboard")
            col1, col2 = st.columns(2)
            with col1:
                live_max_tf = st.selectbox("🎯 Live Tracker Countdown Bound (အထက်ဂဏန်းပမာဏ):", [5, 10, 12, 16, 20], index=1, key="live_max")
            with col2:
                st.info(f"ယခု Session အလိုအလျောက် စစ်ဆေးမှုစနစ်ကို ဖွင့်ထားသည်။ ပစ်မှတ်: {auto_next_session}")

            if st.button("ယခုပွဲအတွက် Auto ရှာဖွေမည် ⚡", key="btn_auto"):
                current_end_idx = len(full_draws) - 1
                convergence_pool = []

                # Live Tracker Countdown Mapping
                for step in range(live_max_tf, 0, -1):
                    target_past_idx = current_end_idx - step + 1
                    if target_past_idx < 0: continue
                    past_draw_val = full_draws[target_past_idx]['draw']
                    
                    p_hits = [d for d in full_draws[:target_past_idx+1] if d['draw'] == past_draw_val]
                    if p_hits:
                        res_live = run_mu_evaluation(p_hits[-1]['index'], full_draws, 1, step)
                        if res_live:
                            for m_k, m_v in res_live.items():
                                if not m_v['hit']: convergence_pool.append(m_v['val'])

                # Render Live Convergence Summary Card
                if convergence_pool:
                    flat_values = []
                    for val in convergence_pool:
                        extracted = re.findall(r'\d+', val)
                        flat_values.extend(extracted) if extracted else flat_values.append(val)
                    top_averages = Counter(flat_values).most_common(3)

                    st.markdown(f"""
                    <div class="card card-live">
                        <div class="card-header">🔵 LIVE CONVERGENCE SUMMARY (ရက်ချိန်းစေ့ လက်ကျန်ပွဲစဉ် ပေါင်းစပ်မှုအဖြေ)</div>
                        <div style="margin-bottom:10px;">အထက်ဂဏန်း {live_max_tf} လုံး၏ မထွက်သေးသော မူလက်ကျန်များအား ဘုံတူညီရာ ပျှမ်းမျှရှာဖွေချက်အရ အားအကောင်းဆုံးရလဒ်များ-</div>
                        <div style="display:flex; gap:20px;">
                    """)
                    for idx, (b_val, b_score) in enumerate(top_averages, 1):
                        st.markdown(f"""
                            <div style="background:#1a273f; padding:10px 20px; border-radius:10px; border:1px solid #3498db;">
                                <span style="color:#54a0ff; font-weight:bold;">🏆 Top {idx}:</span> <span class="metric-val">{b_val}</span>
                                <div style="font-size:12px; color:#8cc5ff; margin-top:5px;">ဘုံတူညီမှုအမှတ်: {b_score} ပွဲ</div>
                            </div>
                        """, unsafe_allow_html=True)
                    st.markdown("</div></div>", unsafe_allow_html=True)
                else:
                    st.info("ယခုပွဲအတွက် ရက်ချိန်းစေ့ မူလက်ကျန် ဘုံတူညီမှု မရှိသေးပါ။")

        # ------------------------------------------
        # TAB 2: CUSTOM PATTERN SEARCH WORKSPACE
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

            active_tfs = [x for x in GLOBAL_TFS if x[0] in selected_tfs]

            if st.button("သီးသန့် Pattern ရှာဖွေမည် 🚀", key="btn_custom"):
                target_hits = []
                rev_num = trigger_num[::-1]

                if trigger_day == "All":
                    target_hits = [d for d in full_draws if d['draw'] == trigger_num or d['draw'] == rev_num]
                else:
                    matched_weeks = {d['row_idx'] for d in full_draws if d['day'] == trigger_day and (d['draw'] == trigger_num or d['draw'] == rev_num)}
                    for d in full_draws:
                        if d['row_idx'] in matched_weeks:
                            if target_session_custom == "AM+PM ပေါင်းချုပ်":
                                target_hits.append(d)
                            else:
                                t_sess = 'AM' if "AM" in target_session_custom else 'PM'
                                if d['time'] == t_sess: target_hits.append(d)

                if not target_hits:
                    st.error("⚠️ သတ်မှတ်ချက်များနှင့် ကိုက်ညီသော သမိုင်းကြောင်းမှတ်တမ်း မရှိပါ Bro!")
                else:
                    hp_store, sniper_store, recovered_store = execute_analysis(target_hits, full_draws, active_tfs)

                    # ==========================================
                    # RENDER HISTORICAL CARDS
                    # ==========================================
                    st.write("---")
                    
                    # 1. RECOVERED TREND SNIPER ZONE
                    if recovered_store:
                        st.markdown("#### 🚨 RECOVERED TREND SNIPER ZONE (၃ကြိမ်မှား၊ ၂ကြိမ်မှန် ပြီး ပြန်နိုးထလာသောမူ)")
                        for r in recovered_store:
                            st.markdown(f"""
                            <div class="card card-recovered">
                                <div class="card-header">⚠️ RECOVERED SNIPER TARGET <span class="badge badge-recovered">20 ကြိမ်မြောက် ဒုန်းတင်ရန်</span></div>
                                <div style="font-size:14px; margin-bottom:10px; color:#ff8888;">{r['mu']} ({r['tf']} Window) သည် သမိုင်းကြောင်းအရ ခါထွက်သွားပြီးနောက်ပိုင်း ၂ ကြိမ်ဆက်တိုက် လတ်တလောတွင် အတိအကျ ပြန်ဝင်လာပါသဖြင့် ဤပွဲစဉ်တွင် ရာခိုင်နှုန်းအသေချာဆုံး ဖြစ်သည်။</div>
                                <div>ယခုပွဲအတွက် ပစ်မှတ်ကွက်: <span class="metric-val">{r['val']}</span></div>
                            </div>
                            """, unsafe_allow_html=True)

                    col_tab1, col_tab2 = st.tabs(["🦅 100% Super VIP Sniper Zone", "🔮 95%+ High-Probability Zone"])

                    with col_tab1:
                        if not sniper_store: st.info("၁၀၀% ကွက်တိ မူများ မတွေ့ရှိပါ။")
                        else:
                            for mu_name, data in sniper_store.items():
                                card_title = f"🚨 ရက်ချိန်းပြည့်မူ: {mu_name}" if data['is_deadline'] else f"💎 {mu_name}"
                                badge_text = f"{data['tf']} ရက်ချိန်းပြည့် ကွက်တိ" if data['is_deadline'] else f"{data['tf']} နယ်ကုန် Window"
                                st.markdown(f"""
                                <div class="card card-sniper">
                                    <div class="card-header">{card_title} <span class="badge badge-sniper">{badge_text}</span></div>
                                    <div>အမှားမခံသော Target ကွက်: <span class="metric-val">{data['val']}</span></div>
                                    <div style="color: #9b59b6; font-weight: bold; margin-top:8px;">AI Confidence: 100% အပြည့် (သမိုင်း {data['hits']}/{data['hits']} ကြိမ်စလုံး ကွက်တိ!)</div>
                                </div>
                                """, unsafe_allow_html=True)

                    with col_tab2:
                        if not hp_store: st.info("၉၅% အထက် Probability ရှိသော မူများ မတွေ့ရှိပါ။")
                        else:
                            for mu_name, data in hp_store.items():
                                card_title = f"🚨 ရက်ချိန်းပြည့်မူ: {mu_name}" if data['is_deadline'] else f"🔮 {mu_name}"
                                badge_text = f"{data['tf']} ရက်ချိန်းပြည့် ကွက်တိ" if data['is_deadline'] else f"{data['tf']} နယ်ကုန် Window"
                                st.markdown(f"""
                                <div class="card card-hp">
                                    <div class="card-header">{card_title} <span class="badge badge-hp">{badge_text}</span></div>
                                    <div>ထွက်လေ့ရှိသော ရလဒ်ပုံစံ: <span class="metric-val">{data['val']}</span></div>
                                    <div style="color: #2ecc71; font-weight: bold; margin-top:8px;">🎯 သမိုင်းကြောင်းမှန်ကန်မှု: {data['rate']:.1f}% ({data['hits']} ကြိမ်အနက်)</div>
                                </div>
                                """, unsafe_allow_html=True)
else:
    st.info("စတင်ရန်အတွက် Bro ရဲ့ 2D CSV သို့မဟုတ် Excel ဒေတာဖိုင်ကို အပေါ်တွင် အရင် တင်ပေးပါဦး။")
