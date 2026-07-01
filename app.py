import streamlit as st
import pandas as pd
import io
import itertools
import re
from collections import Counter

# ==========================================
# PAGE CONFIG & APP-LIKE CUSTOM CSS
# ==========================================
st.set_page_config(page_title="2D AI Master V34 Mobile", layout="wide", page_icon="📱")

if 't1_anchors' not in st.session_state:
    st.session_state.t1_anchors = set()
if 't2_grid' not in st.session_state:
    st.session_state.t2_grid = set()

st.markdown("""
<style>
    .stApp { background-color: #0B031A; color: #E0D5FA; }
    .main-title { color: #A078FF; font-size: 32px; font-weight: bold; text-align: center; margin-bottom: 5px; text-shadow: 0 0 10px rgba(160,120,255,0.5); }
    .sub-title { color: #8F72D6; font-size: 14px; text-align: center; margin-bottom: 20px; }
    
    /* Result Cards */
    .card { background-color: #170E2B; padding: 15px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); margin-bottom: 15px; border: 1px solid #2D1B4E; }
    .card-live { border-left: 5px solid #3498db; background-color: #0E1A2F; margin-bottom: 15px; }
    .card-hp { border-left: 5px solid #2ecc71; background-color: #0D2216; }
    .card-sniper { border-left: 5px solid #9b59b6; background-color: #201135; }
    .card-recovery { border-left: 5px solid #e67e22; background-color: #2D1A0E; margin-bottom: 10px; }
    .card-intersection { border: 2px dashed #FFD700; background-color: #1A180B; text-align: center; padding: 15px; border-radius: 12px; margin-top: 15px;}
    
    /* Mobile Responsive Grid Override */
    @media (max-width: 768px) {
        /* Force columns to wrap on mobile instead of stacking into 1 long column */
        div[data-testid="column"] {
            min-width: 15% !important;
            flex-basis: 15% !important;
            flex-grow: 1 !important;
        }
        /* Make Tab 1 columns 50% width on mobile */
        .tab1-col div[data-testid="column"] {
            min-width: 45% !important;
            flex-basis: 45% !important;
        }
    }

    /* Style the Primary Button (Selected State: Navy + Gold Border) */
    div[data-testid="stButton"] > button[kind="primary"] {
        background: linear-gradient(145deg, #0A1B3F, #122B5E) !important;
        color: #FFFFFF !important;
        border: 2px solid #D4AF37 !important;
        border-radius: 10px !important;
        font-weight: bold !important;
        font-size: 16px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.4) !important;
        padding: 10px 5px !important;
        width: 100% !important;
    }

    /* Style the Secondary Button (Unselected State: Light Grey) */
    div[data-testid="stButton"] > button[kind="secondary"] {
        background: linear-gradient(145deg, #E2E8F0, #F8FAFC) !important;
        color: #1E293B !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 10px !important;
        font-weight: bold !important;
        font-size: 16px !important;
        padding: 10px 5px !important;
        width: 100% !important;
    }
    
    .final-digits { font-size: 24px; font-weight: bold; color: #FFD700; display: block; margin-top: 10px; line-height: 1.5; }
    .score-badge { background-color: #333; color: #fff; font-size: 14px; padding: 4px 8px; border-radius: 6px; margin-left: 5px; margin-right: 10px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📱 2D AI MASTER (V34 Mobile)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Interactive Touch UI | Deep Scan Horizon</div>', unsafe_allow_html=True)

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
# LOGIC FUNCTIONS (Hidden for brevity, fully retained from V33)
# ==========================================
def normalize_formula(mu_k, mu_val):
    if mu_val == "-" or not mu_val: return mu_val
    try:
        if mu_k in ["One Change", "key", "အပူးပါခွေ"]:
            parts = mu_val.split()
            if len(parts) > 1: return f"{''.join(sorted(parts[0]))} {' '.join(parts[1:])}"
        elif mu_k == "ဘရိတ်":
            m = re.match(r'([0-9]+)\s*,\s*([0-9]+)\s*ဘရိတ်', mu_val)
            if m: return f"{sorted([m.group(1), m.group(2)])[0]}, {sorted([m.group(1), m.group(2)])[1]} ဘရိတ်"
        elif mu_k == "အုပ်စုတွဲ":
            gps = mu_val.split('+')
            if len(gps) == 2: return f"{sorted([g.strip() for g in gps])[0]}+{sorted([g.strip() for g in gps])[1]}"
    except: pass
    return mu_val

def check_single_draw_against_formula(d, mu_k, mu_val):
    d_break = str((int(d[0]) + int(d[1])) % 10)
    if mu_k == "လုံးဘိုင်": return mu_val.split()[0] in d
    elif mu_k in ["One Change", "key"]: return any(x in d for x in mu_val.split()[0])
    elif mu_k == "အပူးပါခွေ": return d[0] in mu_val.split()[0] and d[1] in mu_val.split()[0]
    elif mu_k == "ထိပ်စီးစနစ်သစ်":
        m = re.search(r'([0-9]+)\s*ထိပ်\s*/\s*([0-9,]+)\s*ကပ်', mu_val)
        if m: return d[0] in m.group(1) and d[1] in [t.strip() for t in m.group(2).split(',')]
    elif mu_k == "နောက်ပိတ်စနစ်သစ်":
        m = re.search(r'([0-9]+)\s*ပိတ်\s*/\s*([0-9,]+)\s*ကပ်', mu_val)
        if m: return d[1] in m.group(1) and d[0] in [h.strip() for h in m.group(2).split(',')]
    elif mu_k == "ဘရိတ်": return d_break in [b.strip() for b in mu_val.split()[0].split(',')]
    elif mu_k == "စုံ/မ ကပ်":
        m = re.search(r'\[(\d+)\]\s*"([^"]+)"ကပ်', mu_val)
        if m:
            b1 = m.group(1)
            if b1 in d:
                rem = int(d.replace(b1, '', 1) or b1)
                return ("စုံ" in m.group(2) and rem % 2 == 0) or ("စုံ" not in m.group(2) and rem % 2 != 0)
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
    all_heads, all_tails = [d[0] for d in analysis_pool], [d[1] for d in analysis_pool]
    all_breaks = [str((int(d[0]) + int(d[1])) % 10) for d in analysis_pool]
    top_single = Counter(all_singles).most_common(1)[0][0] if all_singles else ""
    top_oc = "".join([x[0] for x in Counter(all_singles).most_common(2)]) if len(Counter(all_singles)) >= 2 else top_single
    top_key3 = "".join([x[0] for x in Counter(all_singles).most_common(3)]) if len(Counter(all_singles)) >= 3 else top_oc
    top_k4 = "".join([x[0] for x in Counter(all_singles).most_common(4)]) if len(Counter(all_singles)) >= 4 else top_key3
    top_h3 = [x[0] for x in Counter(all_heads).most_common(3)]
    best_tails = [x[0] for x in Counter([d[1] for d in analysis_pool if d[0] in top_h3]).most_common(4)]
    top_t3 = [x[0] for x in Counter(all_tails).most_common(3)]
    best_heads = [x[0] for x in Counter([d[0] for d in analysis_pool if d[1] in top_t3]).most_common(4)]
    top_brk2 = [x[0] for x in Counter(all_breaks).most_common(2)]
    if len(top_brk2) < 2 and top_brk2: top_brk2.append(str((int(top_brk2[0])+1)%10))
    e_sc = sum(1 for d in analysis_pool if top_single in d and int(d.replace(top_single,'',1) or top_single) % 2 == 0)
    o_sc = sum(1 for d in analysis_pool if top_single in d and int(d.replace(top_single,'',1) or top_single) % 2 != 0)
    best_sgp = "-"
    max_sgp_c = 0
    for g_name in special_groups.keys():
        c = sum(1 for d in analysis_pool if d in special_groups[g_name])
        if c > max_sgp_c: max_sgp_c = c; best_sgp = g_name
    best_gp = "-"
    max_gp_c = 0
    for combo in itertools.combinations(special_groups.keys(), 2):
        c = sum(1 for d in analysis_pool if d in special_groups[combo[0]] or d in special_groups[combo[1]])
        if c > max_gp_c: max_gp_c = c; best_gp = f"{combo[0]}+{combo[1]}"
    res = {
        "လုံးဘိုင်": f"{top_single} လုံးဘိုင်" if top_single else "-", 
        "One Change": f"{top_oc} One Change" if top_oc else "-",
        "key": f"{top_key3} key" if top_key3 else "-", 
        "အပူးပါခွေ": f"{top_k4} အပူးပါခွေ" if top_k4 else "-",
        "ထိပ်စီးစနစ်သစ်": f"{''.join(top_h3)} ထိပ် / {','.join(best_tails)} ကပ်" if top_h3 else "-", 
        "နောက်ပိတ်စနစ်သစ်": f"{''.join(top_t3)} ပိတ် / {','.join(best_heads)} ကပ်" if top_t3 else "-",
        "ဘရိတ်": f"{top_brk2[0]}, {top_brk2[1]} ဘရိတ်" if len(top_brk2) == 2 else "-", 
        "စုံ/မ ကပ်": (f'[{top_single}] "စုံ"ကပ်' if e_sc >= o_sc else f'[{top_single}] "မ"ကပ်') if top_single else "-", 
        "အုပ်စု သီးသန့်": best_sgp, "အုပ်စုတွဲ": best_gp
    }
    return {k: normalize_formula(k, v) for k, v in res.items()}

def get_hybrid_candidates(target_hits, full_draws, max_step):
    c = {k: [] for k in mu_keys_list}
    for i in range(10): c["လုံးဘိုင်"].append(f"{i} လုံးဘိုင်")
    for b in itertools.combinations([str(x) for x in range(10)], 2): c["ဘရိတ်"].append(normalize_formula("ဘရိတ်", f"{b[0]}, {b[1]} ဘရိတ်"))
    for g in special_groups.keys(): c["အုပ်စု သီးသန့်"].append(g)
    for combo in itertools.combinations(special_groups.keys(), 2): c["အုပ်စုတွဲ"].append(normalize_formula("အုပ်စုတွဲ", f"{combo[0]}+{combo[1]}"))
    pool = [full_draws[h['index']+s]['draw'] for h in target_hits for s in range(1, max_step + 1) if h['index']+s < len(full_draws)]
    c_form = generate_formula_from_pool(pool)
    for k in ["One Change", "key", "အပူးပါခွေ", "ထိပ်စီးစနစ်သစ်", "နောက်ပိတ်စနစ်သစ်", "စုံ/မ ကပ်"]:
        if c_form[k] != "-": c[k].append(c_form[k])
    return c

def execute_analysis(target_hits, full_draws, max_s, is_custom=False, sel_session="All", custom_trigger="", mode="AI Trend", is_research=False):
    step_buckets = {s: {} for s in range(1, max_s + 1)}
    rec_pool = []
    if not target_hits: return step_buckets, rec_pool
    cal_cands = get_hybrid_candidates(target_hits, full_draws, max_s) if mode != "AI Trend" else {}
    for mu_k in mu_keys_list:
        cands = cal_cands.get(mu_k, []) if mode != "AI Trend" else ["DYNAMIC_AI"]
        for cand_val in cands:
            hit_steps = []
            actual_hits = []
            last_val = cand_val
            for hit in target_hits:
                h_idx = hit['index']
                cur_val = cand_val
                if mode == "AI Trend":
                    cur_val = generate_formula_from_pool([d['draw'] for d in full_draws[max(0, h_idx - 50):h_idx]]).get(mu_k, "-")
                    last_val = cur_val
                if cur_val == "-": hit_steps.append(999); continue
                found = None
                for s in range(1, max_s + 1):
                    if h_idx + s >= len(full_draws): break
                    is_h, m_draw = is_already_hit(mu_k, cur_val, h_idx + s, h_idx + s, full_draws)
                    if is_h:
                        if is_custom and "သီးသန့်" in sel_session and full_draws[h_idx+s]['time'] != ("AM" if "AM" in sel_session else "PM"): continue
                        found = s; actual_hits.append(m_draw); break
                hit_steps.append(found if found else 999)
            valid_s = [s for s in hit_steps if s <= max_s]
            if not valid_s or last_val == "-": continue
            req_span = max(valid_s)
            rate = (sum(1 for s in hit_steps if s <= req_span) / len(target_hits)) * 100
            if rate < 90.0 or len(target_hits) < 10: continue
            
            elapsed = (len(full_draws) - 1) - target_hits[-1]['index']
            rem = req_span - elapsed - 1
            is_dead = (rem == 0)
            
            if not is_research:
                if elapsed >= req_span: continue
                if elapsed > 0 and is_already_hit(mu_k, last_val, target_hits[-1]['index'] + 1, len(full_draws) - 1, full_draws)[0]: continue
            
            lbl_prefix = custom_trigger if is_custom else f"{target_hits[-1]['draw']} {target_hits[-1]['time']}"
            card = {
                "top": f"🔮 [{lbl_prefix}] ပြီးလျှင်", "formula": f"{last_val} {'100%' if rate==100 else f'{rate:.1f}%'}",
                "bottom": f"({len(target_hits)} ကြိမ်တွင် {sum(1 for s in hit_steps if s <= req_span)} ကြိမ်မှန်)",
                "is_deadline": is_dead, "pure": last_val, "mu_k": mu_k, "max_span": req_span, "lbl_prefix": lbl_prefix,
                "advisor": f"💡 အဖြစ်နိုင်ဆုံး ၃/၄ ကွက်: {', '.join([x[0] for x in Counter(actual_hits).most_common(4)])}" if actual_hits else ""
            }
            if is_research or is_dead: step_buckets[req_span][last_val if mode != "AI Trend" else mu_k] = card
            if not is_research and rem in [1, 2]: rec_pool.append({"key": last_val, "rem_steps": rem, "score": 80 if rem==1 else 50, "card": card})
    return step_buckets, rec_pool

# ==========================================
# FILE UPLOAD & UI
# ==========================================
uploaded_file = st.file_uploader("Bro ရဲ့ 2D CSV သို့မဟုတ် Excel ဖိုင်ကို ရွေးချယ်တင်ပေးပါ...", type=['csv', 'xlsx', 'xls'])

if uploaded_file:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip().str.lower()
    
    for col in ['year', 'am1', 'am2', 'pm1', 'pm2']: df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna(subset=['year', 'day']).reset_index(drop=True)
    df['day'] = df['day'].astype(str).str.strip().str.capitalize()
    
    full_draws = []
    for idx, row in df.iterrows():
        if pd.notna(row['am1']) and pd.notna(row['am2']): full_draws.append({'draw': f"{int(row['am1'])}{int(row['am2'])}", 'time': 'AM', 'day': row['day'], 'index': len(full_draws)})
        if pd.notna(row['pm1']) and pd.notna(row['pm2']): full_draws.append({'draw': f"{int(row['pm1'])}{int(row['pm2'])}", 'time': 'PM', 'day': row['day'], 'index': len(full_draws)})
        
    st.write("---")
    tab_live, tab_custom = st.tabs(["⚡ တွက်ချက်မည် (Live)", "🔍 သုတေသန (Grid)"])

    # ------------------------------------------
    # TAB 1: LIVE AUTO TRACKER (Mobile Optimized Buttons)
    # ------------------------------------------
    with tab_live:
        st.markdown("#### 🎯 ယခုပွဲစဉ်အတွက် အမာခံ (Anchor) ထောက်တိုင်များ ရွေးချယ်ရန်")
        st.caption("နောက်ဆုံး (၁၁) ရက်စာ မှတ်တမ်းမှ ယနေ့အတွက် လွှမ်းမိုးမှုရှိမည်ဟု ယူဆသော ဂဏန်းများကို နှိပ်၍ ရွေးချယ်ပါ။")
        
        last_11_days_df = df.tail(11).copy()
        
        # Wrapped in a custom div class for mobile targeting
        st.markdown('<div class="tab1-col">', unsafe_allow_html=True)
        col_am, col_pm = st.columns(2)
        
        with col_am:
            st.markdown("<span style='color:#E0D5FA; font-weight:bold;'>AM (မနက်ပိုင်း)</span>", unsafe_allow_html=True)
            for _, r in last_11_days_df.iterrows():
                if pd.notna(r['am1']) and pd.notna(r['am2']):
                    val = f"{int(r['am1'])}{int(r['am2'])}"
                    lbl = f"{r['day']} AM : {val}"
                    b_type = "primary" if lbl in st.session_state.t1_anchors else "secondary"
                    if st.button(lbl, key=f"btn_t1_am_{_}", type=b_type):
                        if lbl in st.session_state.t1_anchors: st.session_state.t1_anchors.remove(lbl)
                        else: st.session_state.t1_anchors.add(lbl)
                        st.rerun()
                        
        with col_pm:
            st.markdown("<span style='color:#E0D5FA; font-weight:bold;'>PM (ညနေပိုင်း)</span>", unsafe_allow_html=True)
            for _, r in last_11_days_df.iterrows():
                if pd.notna(r['pm1']) and pd.notna(r['pm2']):
                    val = f"{int(r['pm1'])}{int(r['pm2'])}"
                    lbl = f"{r['day']} PM : {val}"
                    b_type = "primary" if lbl in st.session_state.t1_anchors else "secondary"
                    if st.button(lbl, key=f"btn_t1_pm_{_}", type=b_type):
                        if lbl in st.session_state.t1_anchors: st.session_state.t1_anchors.remove(lbl)
                        else: st.session_state.t1_anchors.add(lbl)
                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.write("---")
        input_box_val = st.text_input("⏳ ရှာဖွေမည့် နယ်ကုန်ရက်ချိန်း (Max Span) ပွဲစဉ်အရေအတွက် (Default: 20):", value="20")
        live_max_tf = int(input_box_val.strip()) if input_box_val.strip().isdigit() else 20
        live_mode = st.radio("🧠 AI တွက်ချက်မှုစနစ် ရွေးချယ်ရန်:", ["AI Trend (ရှေ့သမိုင်း ၅၀ အထိုင်)", "Calendar သီးသန့်မူများ (Fixed Pattern)"], horizontal=True)

        if st.button("ရွေးချယ်ထားသော အမာခံများဖြင့် Auto ရှာဖွေမည် ⚡", key="btn_auto"):
            if not st.session_state.t1_anchors:
                st.warning("⚠️ ကျေးဇူးပြု၍ အထက်ပါဇယားမှ အမာခံ ဂဏန်း အနည်းဆုံး (၁) ခု ရွေးချယ်ပေးပါ Bro!")
            else:
                compiled_master_buckets = {step: {} for step in range(1, live_max_tf + 1)}
                scoring_pool, global_recovery = {}, {}
                
                for lbl in st.session_state.t1_anchors:
                    parts = lbl.split(":")
                    past_val = parts[1].strip()
                    past_time = "AM" if "AM" in parts[0] else "PM"
                    past_day = parts[0].split()[0]
                    
                    c_pools = [
                        {"hits": [d for d in full_draws if d['draw'] == past_val and d['time'] == past_time], "lbl": f"{past_val} {past_time} စစ်စစ်"},
                        {"hits": [d for d in full_draws if d['draw'] == past_val], "lbl": f"{past_val} ပေါင်းချုပ်"},
                        {"hits": [d for d in full_draws if d['draw'] == past_val and d['day'] == past_day], "lbl": f"{past_val} {past_day} သီးသန့်"}
                    ]
                    
                    for pool in c_pools:
                        if not pool['hits']: continue
                        s_res, r_pool = execute_analysis(pool['hits'], full_draws, live_max_tf, True, "All", pool['lbl'], live_mode, False)
                        
                        for step_dist, f_dict in s_res.items():
                            for mk, mv in f_dict.items():
                                f_key = mv['pure']
                                if f_key not in scoring_pool: scoring_pool[f_key] = {'count': 0, 'details': [], 'mu_k': mv['mu_k']}
                                if mv['top'] not in [d['top'] for d in scoring_pool[f_key]['details']]:
                                    scoring_pool[f_key]['details'].append(mv); scoring_pool[f_key]['count'] += 1

                        for rp in r_pool:
                            r_key = rp['key']
                            if r_key not in global_recovery: global_recovery[r_key] = {'score': 0, 'rem_steps': rp['rem_steps'], 'details': []}
                            if rp['card']['top'] not in [d['top'] for d in global_recovery[r_key]['details']]:
                                global_recovery[r_key]['details'].append(rp['card']); global_recovery[r_key]['score'] += rp['score']
                                if len(global_recovery[r_key]['details']) >= 2: global_recovery[r_key]['score'] *= 2

                vips = {k: v for k, v in scoring_pool.items() if v['count'] >= 2}
                
                st.write("---")
                st.markdown("#### 🏆 VIP ဆုံးဖြတ်ချက် (Super & Second Overlaps)")
                if vips:
                    for b_val, b_data in sorted(vips.items(), key=lambda x: x[1]['count'], reverse=True):
                        tier = "Super VIP" if b_data['count'] >= 3 else "Second VIP"
                        badge = "badge-super" if tier == "Super VIP" else "badge-second"
                        with st.expander(f"⭐ {tier}: {b_val} (တူညီမှု: {b_data['count']} ခု)", expanded=False):
                            st.markdown(f"<span class='{badge}'>{tier}</span><div style='color:#00FFCC; font-size:14px; margin-top:10px;'>💡 ဤမူကို အောက်ပါ ထောက်တိုင်များက ဘုံတူညီစွာ ညွှန်ပြနေပါသည်-</div>", unsafe_allow_html=True)
                            for d_detail in b_data['details']:
                                st.markdown(f"<div class='card card-live' style='padding:10px;'><span style='font-weight:bold; color:#E0D5FA;'>{d_detail['top']}</span><span class='badge-inline {'badge-inline-sniper' if d_detail['rate']==100 else 'badge-inline-hp'}'>{d_detail['max_span']} ပွဲအတွင်း (ရက်ချိန်းပြည့်)</span></div>", unsafe_allow_html=True)
                    
                    st.write("---")
                    st.markdown("#### 🎯 အတိကျဆုံး အကြံပြု Final ဂဏန်းများ (Weighted Scoring)")
                    f_scores = {f"{i:02d}": 0 for i in range(100)}
                    for b_val, b_data in vips.items():
                        for d in f_scores.keys():
                            if check_single_draw_against_formula(d, b_data['mu_k'], b_val): f_scores[d] += b_data['count']
                    
                    top_d = sorted(f_scores.items(), key=lambda x: x[1], reverse=True)[:5]
                    if top_d and top_d[0][1] > 0:
                        st.markdown(f"<div class='card card-intersection'><span style='color:#A294C7; font-size:14px;'>VIP မူများအားလုံးကို အမှတ်ပေး ချိန်ခွင်လျှာညှိပြီး ရွေးချယ်ထားသော (Top 5) အကွက်များ:</span><div class='final-digits'>{''.join([f'<span style=\"display:inline-block; margin-bottom:8px;\">{d} <span class=\"score-badge\">Score: {s}</span></span>' for d, s in top_d if s > 0])}</div></div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div style='color:#A294C7; padding:10px;'>ခိုင်မာသော VIP တူညီမှု ရလဒ်မရှိပါ (အနည်းဆုံး တိုက်ဆိုင်မှု ၂ ခု လိုအပ်ပါသည်)</div>", unsafe_allow_html=True)

                st.write("---")
                st.markdown("#### 🛡️ Recovery & စောင့်ကြည့်ရမည့် မူကျန်များ (Top 5)")
                if global_recovery:
                    for r_key, r_data in sorted(global_recovery.items(), key=lambda x: x[1]['score'], reverse=True)[:5]:
                        icon = "🔴" if r_data['score'] >= 100 else ("🟠" if r_data['score'] == 80 else "🟡")
                        st.markdown(f"<div class='card card-recovery' style='padding:12px;'><span style='font-weight:bold; color:#fff;'>{icon} Score: {r_data['score']} | [{r_data['details'][0]['lbl_prefix']}] {r_key}</span><br/><span style='font-size:14px; color:#f39c12; margin-top:5px; display:block;'>⏳ {'၁ ပွဲသာ လိုတော့သည်' if r_data['rem_steps']==1 else '၂ ပွဲ လိုသေးသည်'} {'(ထောက်တိုင် '+str(len(r_data['details']))+' ခုငြိနေသည်)' if len(r_data['details'])>1 else ''}</span></div>", unsafe_allow_html=True)
                else:
                    st.info("၁ ပွဲ သို့မဟုတ် ၂ ပွဲ အလိုရှိသော ခိုင်မာသည့် မူကျန်များ မရှိပါ။")

    # ------------------------------------------
    # TAB 2: CUSTOM FORMULAS ENGINE (10x10 Mobile Grid)
    # ------------------------------------------
    with tab_custom:
        custom_mode = st.radio("🧠 တွက်ချက်မှုစနစ် (Mode) ရွေးချယ်ရန်", ["AI Trend (ရှေ့သမိုင်း ၅၀ အထိုင်)", "Calendar သီးသန့်မူများ (Fixed Pattern)"], horizontal=True, key="custom_mode_tab2")
        st.write("---")
        
        st.markdown("##### 🎛️ ၁။ Master Grid (00 မှ 99 အထိ နှိပ်၍ရွေးချယ်ရန်)")
        use_r_checkbox = st.checkbox("✅ အရံ (R) အကွက်များကိုပါ အလိုအလျောက် ထည့်သွင်းတွက်ချက်မည်", value=False)
        
        # 10x10 Mobile App-like Grid
        for row in range(10):
            cols = st.columns(10) # CSS handles wrapping on mobile to 5 items per row perfectly
            for col_idx in range(10):
                num_val = f"{row}{col_idx}"
                b_type = "primary" if num_val in st.session_state.t2_grid else "secondary"
                with cols[col_idx]:
                    if st.button(num_val, key=f"btn_t2_{num_val}", type=b_type):
                        if num_val in st.session_state.t2_grid: st.session_state.t2_grid.remove(num_val)
                        else: st.session_state.t2_grid.add(num_val)
                        st.rerun()
                                
        st.write("---")
        st.markdown("##### ⌨️ ၂။ စာသားဖြင့် ရှာဖွေရန် (Backup Search - ဥပမာ: '683 key')")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            trigger_day = st.selectbox("📆 Trigger Day:", ["All"] + active_days_cycle, index=0)
            trigger_num = st.text_input("🔍 ရှာလိုသောစာသား ရိုက်ထည့်ပါ:", value="", max_chars=15)
        with c2:
            target_session_custom = "AM+PM ပေါင်းချုပ်" if trigger_day != "All" else st.selectbox("⏱️ Target ပွဲစဉ် အခြေအနေ ရွေးရန်:", ["AM+PM ပေါင်းချုပ်", "AM သီးသန့်", "PM သီးသန့်"], index=0)
        with c3:
            custom_max_tf = st.number_input("⏳ စစ်ဆေးမည့် ပွဲစဉ်အရေအတွက်", min_value=1, max_value=25, value=20)

        if st.button("ရွေးချယ်ထားသော မူများကို ရှာဖွေမည် 🚀", key="btn_custom"):
            target_hits = []
            lbl_prefix_custom = ""
            
            if st.session_state.t2_grid:
                grid_nums = list(st.session_state.t2_grid)
                if use_r_checkbox: grid_nums.extend([n[::-1] for n in grid_nums])
                grid_nums = list(set(grid_nums))
                
                for d_val in grid_nums:
                    if target_session_custom != "AM+PM ပေါင်းချုပ်" and "သီးသန့်" in target_session_custom:
                        target_hits.extend([d for d in full_draws if d['draw'] == d_val and d['time'] == ("AM" if "AM" in target_session_custom else "PM")])
                    else:
                        target_hits.extend([d for d in full_draws if d['draw'] == d_val])
                
                lbl_prefix_custom = f"[{','.join(grid_nums[:4])}{'...' if len(grid_nums)>4 else ''}]{' (+R)' if use_r_checkbox else ''} {'PM' if 'PM' in target_session_custom else 'AM' if 'AM' in target_session_custom else ''}".strip()
            
            elif trigger_num.strip():
                c_trig = trigger_num.strip().upper()
                d_found = re.findall(r'\d+', c_trig)
                
                if d_found and "KEY" not in c_trig:
                    p_dig = d_found[0]
                    if trigger_day == "All":
                        if "+" in c_trig or "R" in c_trig: target_hits = [d for d in full_draws if d['draw'] == p_dig or d['draw'] == (d_found[1] if len(d_found)>1 else p_dig[::-1])]
                        else: target_hits = [d for d in full_draws if d['draw'] == p_dig and (True if target_session_custom == "AM+PM ပေါင်းချုပ်" else d['time'] == ("AM" if "AM" in target_session_custom else "PM"))]
                    else:
                        m_weeks = {d['row_idx'] for d in full_draws if d['day'] == trigger_day and (d['draw'] == p_dig or d['draw'] == (d_found[1] if len(d_found)>1 else p_dig[::-1]))}
                        target_hits = [d for d in full_draws if d['row_idx'] in m_weeks]
                elif "KEY" in c_trig and d_found:
                    target_hits = [d for d in full_draws if any(k in d['draw'] for k in list(d_found[0]))]
                    
                lbl_prefix_custom = f"{trigger_num}{' R' if trigger_day != 'All' and 'R' not in trigger_num else ''} {trigger_day if trigger_day != 'All' else ''} {'PM' if target_session_custom == 'PM သီးသန့်' else 'AM' if target_session_custom == 'AM သီးသန့်' else ''}".strip()

            if not target_hits:
                st.error("⚠️ သတ်မှတ်ချက်များနှင့် ကိုက်ညီသော သမိုင်းကြောင်းမှတ်တမ်း မရှိပါ Bro! (Grid မှ ဂဏန်းများကို နှိပ်၍ရွေးချယ်ပါ)")
            else:
                st.write("---")
                st.markdown(f"#### 📋 အသေးစိတ်အချက်အလက် (Window အလိုက် ခေါက်သိမ်းစနစ်)")
                m_res, _ = execute_analysis(target_hits, full_draws, custom_max_tf, True, target_session_custom, lbl_prefix_custom, custom_mode, True)
                
                if not any(m_res[sk] for sk in m_res if sk <= custom_max_tf):
                    st.info("သတ်မှတ်ထားသော ၉၀% အထက် ရက်ချိန်းနယ်ကုန် သတ်မှတ်ချက်အတွင်း ကိုက်ညီမည့် မူရင်းမှတ်တမ်း မတွေ့ရှိပါ Bro!")
                else:
                    for step in sorted(m_res.keys()):
                        if not m_res[step]: continue 
                        with st.expander(f"⚠️ {step} ပွဲအတွင်း မူများ [ရက်ချိန်းပြည့်]" if any(v['is_deadline'] for v in m_res[step].values()) else f"🔽 {step} ပွဲအတွင်း မူများ", expanded=True):
                            for mu_name, data in m_res[step].items():
                                st.markdown(f"<div class='card {'card-sniper' if '100%' in data['formula'] else 'card-hp'}'><span class='line-trigger'>{data['top']} <span class='badge-inline {'badge-inline-sniper' if '100%' in data['formula'] else 'badge-inline-hp'}'>{step} ပွဲအတွင်း</span></span><span class='line-formula'>{data['formula']}</span><span class='line-history'>{data['bottom']}</span><span class='line-advisor'>{data['advisor']}</span></div>", unsafe_allow_html=True)
else:
    st.info("စတင်ရန်အတွက် Bro ရဲ့ 2D CSV သို့မဟုတ် Excel ဒေတာဖိုင်ကို အပေါ်တွင် အရင် တင်ပေးပါဦး။")
