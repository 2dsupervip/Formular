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
    
    /* Bro 3/4-Line Stack Display Typography (Screenshot Exact Match) */
    .line-alert { color: #FF4D4D; font-size: 16px; font-weight: bold; margin-bottom: 6px; display: block; }
    .line-trigger { font-size: 18px; font-weight: bold; color: #E0D5FA; margin-bottom: 6px; display: block; }
    .line-formula { font-size: 22px; font-weight: bold; color: #FFD700; margin-bottom: 6px; display: block; }
    .line-history { font-size: 15px; color: #A294C7; display: block; }
    
    /* Dynamic Badge Blocks (SS Style) */
    .badge-inline { padding: 2px 10px; border-radius: 6px; font-size: 14px; font-weight: bold; margin-left: 6px; margin-right: 6px; display: inline-block; vertical-align: middle; }
    .badge-inline-sniper { background-color: #9b59b6; color: white; }
    .badge-inline-hp { background-color: #2ecc71; color: #0D2216; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🤖 THE PERFECT 2D AI MASTER (V26 PRO)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Ultimate Reverse Countdown Matrix Engine | Pure Line Display Architecture</div>', unsafe_allow_html=True)

special_groups = {
    "ညီကို": {"01","10","12","21","23","32","34","43","45","54","56","65","67","76","78","87","89","98","90","09"},
    "ပါဝါ": {"05","50","16","61","27","72","38","83","49","94"},
    "နက္ခတ်": {"07","70","18","81","24","42","35","53","69","96"},
    "ထိုင်းပါဝါ": {"09","90","13","31","26","62","47","74","58","85"},
    "အပူး": {"00","11","22","33","44","55","66","77","88","99"},
    "ဆယ်ပြည့်": {"10","01","20","02","30","03","40","04","50","05","60","06","70","07","80","08","90","09"}
}

# ==========================================
# HELPER: CHECK IF VALUE ALREADY HIT IN RECENT TIMELINE
# ==========================================
def is_already_hit(mu_name, mu_val, start_idx, end_idx, full_draws_list):
    if start_idx >= len(full_draws_list): return True
    check_draws = [d['draw'] for d in full_draws_list[start_idx : min(end_idx + 1, len(full_draws_list))]]
    if not check_draws: return False
    
    clean_val = re.sub(r'[^\d,\+]', '', mu_val).strip()
    
    if "လုံးဘိုင်" in mu_name:
        return any(clean_val in d for d in check_draws)
    elif "One Change" in mu_name or "key" in mu_name or "အမာခံ" in mu_name:
        return any(any(x in d for x in clean_val) for d in check_draws)
    elif "ခွေ" in mu_name:
        return any(d[0] in clean_val and d[1] in clean_val for d in check_draws)
    elif "ထိပ်စီး" in mu_name:
        return any(d[0] in clean_val for d in check_draws)
    elif "ဘရိတ်" in mu_name:
        brk_list = [x.strip() for x in clean_val.split(',') if x.strip()]
        return any(str((int(d[0])+int(d[1]))%10) in brk_list for d in check_draws)
    elif "စုံ/မ ကပ်" in mu_name or "ကပ်" in mu_name:
        match = re.search(r'\[(\d+)\]\s*"([^"]+)"ကပ်', mu_val)
        if match:
            b1 = match.group(1)
            is_even = "စုံ" in match.group(2)
            mway_digits = [f"{b1}{i}" for i in ([0,2,4,6,8] if is_even else [1,3,5,7,9])]
            return any(d in mway_digits for d in check_draws)
    elif "အုပ်စုတွဲ" in mu_name or "+" in mu_val:
        g1 = "ညီကို" if "ညီကို" in mu_val else "ပါဝါ" if "ပါဝါ" in mu_val else "နက္ခတ်" if "နက္ခတ်" in mu_val else "ထိုင်းပါဝါ" if "ထိုင်းပါဝါ" in mu_val else "အပူး" if "အပူး" in mu_val else "ဆယ်ပြည့်"
        g2 = "အပူး" if "အပူး" in mu_val and g1 != "အပူး" else "ပါဝါ" if "ပါဝါ" in mu_val and g1 != "ပါဝါ" else ""
        return any(d in special_groups.get(g1, set()) or (g2 and d in special_groups.get(g2, set())) for d in check_draws)
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
    all_breaks = [str((int(d[0]) + int(d[1])) % 10) for d in sub_draws]

    top_single = Counter(all_singles).most_common(1)[0][0] if all_singles else ""
    top_oc = "".join([x[0] for x in Counter(all_singles).most_common(2)]) if len(Counter(all_singles)) >= 2 else top_single
    top_key3 = "".join([x[0] for x in Counter(all_singles).most_common(3)]) if len(Counter(all_singles)) >= 3 else top_oc
    top_k4 = "".join([x[0] for x in Counter(all_singles).most_common(4)]) if len(Counter(all_singles)) >= 4 else top_key3
    
    top_brk_data = Counter(all_breaks).most_common(2)
    top_brk2 = [x[0] for x in top_brk_data]
    if len(top_brk2) < 2: top_brk2.append(str((int(top_brk2[0])+1)%10 if top_brk2 else 0))
    brk_label = f"{top_brk2[0]}, {top_brk2[1]}"

    e_sc = sum(1 for d in sub_draws if top_single in d and int(d.replace(top_single,'',1) if d.replace(top_single,'',1) else top_single) % 2 == 0)
    o_sc = sum(1 for d in sub_draws if top_single in d and int(d.replace(top_single,'',1) if d.replace(top_single,'',1) else top_single) % 2 != 0)
    kap_label = f'[{top_single}] "စုံ"ကပ်' if e_sc >= o_sc else f'[{top_single}] "မ"ကပ်'

    best_gp = ""; max_gp_c = 0
    for combo in itertools.combinations(special_groups.keys(), 2):
        c = sum(1 for d in sub_draws if d in special_groups[combo[0]] or d in special_groups[combo[1]])
        if c > max_gp_c: max_gp_c = c; best_gp = f"{combo[0]}+{combo[1]}"

    kwat_kyin_label = f"{top_key3} ပါသော {brk_label} ဘရိတ်"

    act_draws = [d['draw'] for d in full_draws_list[hit_idx+1 : min(hit_idx+e_off+1, len(full_draws_list))]]
    if not act_draws: return None

    if best_gp and '+' in best_gp:
        g1_key, g2_key = best_gp.split('+')[0], best_gp.split('+')[1]
        gp_hit = any(d in special_groups.get(g1_key, set()) or d in special_groups.get(g2_key, set()) for d in act_draws)
    else:
        gp_hit = False

    return {
        "လုံးဘိုင်": {"val": f"{top_single} လုံးဘိုင်", "hit": any(top_single in d for d in act_draws), "pure": top_single},
        "One Change": {"val": f"{top_oc} One Change", "hit": any(any(x in d for x in top_oc) for d in act_draws), "pure": top_oc},
        "key": {"val": f"{top_key3} key", "hit": any(any(x in d for x in top_key3) for d in act_draws), "pure": top_key3},
        "အပူးပါခွေ": {"val": f"{top_k4} အပူးပါခွေ", "hit": any(d[0] in top_k4 and d[1] in top_k4 for d in act_draws), "pure": top_k4},
        "ဘရိတ်": {"val": f"{brk_label} ဘရိတ်", "hit": any(str((int(d[0])+int(d[1]))%10) in top_brk2 for d in act_draws), "pure": brk_label},
        "စုံ/မ ကပ်": {"val": kap_label, "hit": (any(d in [f"{top_single}{i}" for i in [0,2,4,6,8]] for d in act_draws) if e_sc >= o_sc else any(d in [f"{top_single}{i}" for i in [1,3,5,7,9]] for d in act_draws)), "pure": top_single},
        "အုပ်စုတွဲ": {"val": best_gp if best_gp else "-", "hit": gp_hit, "pure": best_gp},
        "ကွက်ကျဉ်းစနစ်": {"val": kwat_kyin_label, "hit": any(any(k in d for k in top_key3) and str((int(d[0])+int(d[1]))%10) in top_brk2 for d in act_draws), "pure": top_key3}
    }

# ==========================================
# MASTER ROUTINE: HYBRID DATA ANALYSIS ENGINE
# ==========================================
def execute_analysis(target_hits, full_draws, active_tfs, label_prefix, is_custom_tab=False, sel_session=""):
    hp_store = {}
    sniper_store = {}
    recovered_store = []
    current_latest_idx = len(full_draws) - 1

    for tf_name, s_off, e_off in active_tfs:
        sequence_tracker = {f"mu_{m}": [] for m in range(1, 9)}
        mu_latest_values = {}
        mu_pure_values = {}
        mu_keys_list = []

        # Filter target hits strictly if Tab 2 Custom specific session chosen
        filtered_hits = target_hits
        if is_custom_tab and sel_session != "AM+PM ပေါင်းချုပ်":
            req_time = "AM" if "AM" in sel_session else "PM"
            filtered_hits = [h for h in target_hits if h['time'] == req_time]

        for hit in filtered_hits:
            res = run_mu_evaluation(hit['index'], full_draws, s_off, e_off)
            if res:
                if not mu_keys_list: mu_keys_list = list(res.keys())
                for m_idx, mu_k in enumerate(mu_keys_list, 1):
                    sequence_tracker[f"mu_{m_idx}"].append(res[mu_k]['hit'])
                    mu_latest_values[mu_k] = res[mu_k]['val']
                    mu_pure_values[mu_k] = res[mu_k]['pure']

        if not mu_keys_list: continue

        for m_idx, mu_k in enumerate(mu_keys_list, 1):
            seq = sequence_tracker[f"mu_{m_idx}"]
            if len(seq) < 5: continue
            
            win_count = sum(1 for x in seq if x)
            total_count = len(seq)
            rate = (win_count / total_count) * 100

            is_deadline_flag = False
            if filtered_hits:
                last_hit_global_idx = filtered_hits[-1]['index']
                elapsed_draws = current_latest_idx - last_hit_global_idx
                if (elapsed_draws + 1) == e_off:
                    already_out = is_already_hit(mu_k, mu_latest_values[mu_k], last_hit_global_idx + 1, current_latest_idx, full_draws)
                    if not already_out:
                        is_deadline_flag = True

            display_val = mu_latest_values[mu_k]
            rate_str = "100%" if rate == 100.0 else f"{rate:.1f}%"
            badge_color_class = "badge-inline-sniper" if rate == 100.0 else "badge-inline-hp"
            
            # Bro 3/4-Line Stack Architecture Setup (SS Match)
            top_line = f"🔮 [{label_prefix}] ထွက်ပြီးလျှင် <span class='badge-inline {badge_color_class}'>{tf_name}အတွင်း</span>"
            formula_line = f"{display_val} {rate_str}"
            bottom_line = f"မှန်ကန်မှု: ({total_count} ကြိမ်မှာ {win_count} ကြိမ်မှန်)"

            card_payload = {"top": top_line, "formula": formula_line, "bottom": bottom_line, "e_off": e_off, "is_deadline": is_deadline_flag, "pure": mu_pure_values[mu_k]}

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

    return hp_store, sniper_store, recovered_store

# ==========================================
# FILE UPLOAD & DYNAMIC CHRONOLOGY
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

        # Auto Day Alignment Engine Control (Excluding Sat, Sun)
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
        # TAB 1: FIXED REVERSE COUNTDOWN SHIFT ENGINE
        # ------------------------------------------
        with tab_live:
            live_max_tf = st.number_input("ရှာလိုသော ပွဲစဉ်အရေအတွက်", min_value=1, max_value=20, value=6)
            
            if st.button("ယခုပွဲအတွက် Auto ရှာဖွေမည် ⚡", key="btn_auto"):
                current_end_idx = len(full_draws) - 1
                convergence_pool = []
                detailed_live_store = []
                
                # စနစ်မှန် နောက်ကြောင်းပြန် Row-by-Row Active Dynamic Mapping
                for step in range(1, live_max_tf + 1):
                    target_past_idx = current_end_idx - step + 1
                    if target_past_idx < 0: continue
                    
                    past_obj = full_draws[target_past_idx]
                    past_val = past_obj['draw']
                    past_time = past_obj['time']
                    
                    # ကွက်တိထိုးစစ်ရမည့် Session အခြေအနေ ၂ မျိုးတည်းသာ ဆွဲထုတ်ခြင်း Logic
                    condition_pools = [
                        {"hits": [d for d in full_draws[:target_past_idx+1] if d['draw'] == past_val and d['time'] == past_time], "lbl": f"{past_val} {past_time}"},
                        {"hits": [d for d in full_draws[:target_past_idx+1] if d['draw'] == past_val], "lbl": f"{past_val}"}
                    ]
                    
                    for pool in condition_pools:
                        if not pool['hits']: continue
                        res_live = run_mu_evaluation(pool['hits'][-1]['index'], full_draws, 1, step)
                        if res_live:
                            for m_k, m_v in res_live.items():
                                already_out = is_already_hit(m_k, m_v['val'], pool['hits'][-1]['index'] + 1, current_end_idx, full_draws)
                                if not already_out:
                                    pure_digits = "".join(re.findall(r'\d', m_v['pure']))
                                    if pure_digits:
                                        convergence_pool.extend(list(pure_digits))
                                    elif "+" in m_v['pure']:
                                        convergence_pool.append(m_v['pure'])
                                    
                                    badge_cls = "badge-inline-sniper"
                                    top_l = f"🔮 [{pool['lbl']}] ထွက်ပြီးလျှင် <span class='badge-inline {badge_cls}'>{step} ပွဲအတွင်း</span>"
                                    form_l = f"{m_v['val']} 100%"
                                    bot_l = f"မှန်ကန်မှု: ရက်ချိန်းပြည့် မူလက်ကျန်"
                                    detailed_live_store.append({"top": top_l, "form": form_l, "bot": bot_l})

                st.write("---")
                st.markdown("#### 🏆 TOP RESULTS")
                
                if convergence_pool:
                    top_averages = Counter(convergence_pool).most_common(3)
                    st.markdown('<div class="card card-live"><div style="display:flex; gap:20px; flex-wrap: wrap;">', unsafe_allow_html=True)
                    for idx, (b_val, b_score) in enumerate(top_averages, 1):
                        st.markdown(f"""
                            <div style="background:#1a273f; padding:15px 25px; border-radius:10px; border:1px solid #3498db; min-width:200px;">
                                <span style="color:#54a0ff; font-weight:bold; font-size:16px;">🏆 Top {idx} Convergence:</span> <br>
                                <span class="metric-val" style="margin-top:5px;">{b_val}</span>
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
                    for d_card in detailed_live_store:
                        st.markdown(f"""
                        <div class="card card-sniper">
                            <span class="line-trigger">{d_card['top']}</span>
                            <span class="line-formula">{d_card['form']}</span>
                            <span class="line-history">{d_card['bot']}</span>
                        </div>
                        """, unsafe_allow_html=True)

        # ------------------------------------------
        # TAB 2: CLEAN CUSTOM FORMULARS ENGINE
        # ------------------------------------------
        with tab_custom:
            c1, c2, c3 = st.columns(3)
            with c1:
                trigger_day = st.selectbox("📆 Trigger Day:", ["All", "Mon", "Tue", "Wed", "Thur", "Fri"], index=0)
                trigger_num = st.text_input("🔍 ရှာလိုသောဂဏန်း ရိုက်ထည့်ပါ:", value="60", max_chars=2)
            with c2:
                target_session_custom = st.selectbox("⏱️ အခြေအနေ ရွေးချယ်ရန်
