from pathlib import Path
import pickle
import numpy as np
import pandas as pd
import xgboost as xgb
import matplotlib.pyplot as plt
from shiny import App, Inputs, Outputs, Session, reactive, render, ui

HERE = Path(__file__).resolve().parent
with open(HERE / "model_bundle.pkl", "rb") as f:
    BUNDLE = pickle.load(f)
RACE_COL = "Race.recode..W..B..AI..API."

def derive_stage(t, n, m):
    if m == "M1": return "IV"
    if m != "M0" or t == "TX" or n == "NX": return "Unknown"
    if n == "N2" or t == "T4": return "IV"
    if t in {"T1a", "T1b", "T1NOS"} and n == "N0": return "I"
    if t == "T2" and n == "N0": return "II"
    if (t == "T3" and n == "N0") or (t in {"T1a", "T1b", "T1NOS", "T2", "T3"} and n == "N1"): return "III"
    return "Unknown"

def predict(age, sex, race, grade, t, n, m):
    stage = derive_stage(t, n, m)
    row = pd.DataFrame([{"stage_red2":stage,"age_years":float(age),"Sex":sex,RACE_COL:race,"grade_cat":grade}])
    z = BUNDLE["preprocessor"].transform(row)
    risk = float(BUNDLE["model"].get_booster().predict(xgb.DMatrix(z), output_margin=True)[0])
    grid = np.arange(0., BUNDLE["max_followup"] + 1.)
    h = np.interp(grid, BUNDLE["baseline_times"], BUNDLE["baseline_hazard"], left=0, right=BUNDLE["baseline_hazard"][-1])
    surv = np.exp(-np.exp(BUNDLE["calibration_beta"] * risk) * h)
    hit = np.where(surv <= .5)[0]
    median = int(grid[hit[0]]) if len(hit) else None
    return {"stage":stage,"risk":risk,"median":median,"survival":{12:float(surv[12]),36:float(surv[36]),60:float(surv[60])}}

CSS = """
:root{--ink:#15332f;--teal:#0d766c;--mint:#dbeee9;--paper:#f5f3ed;--line:#d7ded9}
body{background:var(--paper);color:var(--ink);font-family:Inter,system-ui,sans-serif}.container-fluid{max-width:1240px}
.hero{padding:38px 0 26px;border-bottom:1px solid var(--line);margin-bottom:24px}.kicker{font-size:11px;font-weight:800;letter-spacing:.17em;color:var(--teal)}
.hero h1{font:500 46px/1.08 Georgia,serif;margin:10px 0;color:var(--ink)}.hero p{color:#657a76;max-width:760px}
.card{border:1px solid var(--line);box-shadow:0 10px 30px #173d3310;border-radius:4px}.card-header{background:white;font:500 21px Georgia,serif;border-bottom:1px solid var(--line)}
.btn-primary{background:var(--ink);border-color:var(--ink);width:100%;font-weight:700}.btn-primary:hover{background:var(--teal);border-color:var(--teal)}
.metric{background:white;border:1px solid var(--line);padding:18px;height:100%}.metric small{color:#657a76;font-size:10px;letter-spacing:.1em}.metric strong{display:block;font:500 28px Georgia;margin-top:6px}
.median{background:var(--ink);color:white;padding:24px;margin:18px 0}.median small{color:#abd0c6}.median strong{display:block;font:500 42px Georgia;margin-top:6px}
.disclaimer{border-top:1px solid var(--line);margin-top:25px;padding:20px 0;color:#657a76;font-size:12px}.nav-tabs .nav-link.active{color:var(--teal);font-weight:700}.nav-tabs .nav-link{color:#657a76}
"""

app_ui = ui.page_fluid(
    ui.tags.head(ui.tags.link(rel="icon", href="/favicon.ico")),
    ui.tags.style(CSS),
    ui.div(ui.div("CLINICAL RESEARCH MODEL", class_="kicker"), ui.h1("Gallbladder cancer dynamic survival nomogram"),
           ui.p("Redefined 2 stage plus XGBoost-Cox | Individualized overall-survival estimates from SEER data"), class_="hero"),
    ui.layout_columns(
        ui.card(ui.card_header("Patient characteristics"),
            ui.input_numeric("age","Age at diagnosis (years)",65,min=18,max=100),
            ui.input_select("sex","Sex",["Female","Male"]),
            ui.input_select("race","Race",["White","Black","Asian or Pacific Islander","American Indian/Alaska Native"]),
            ui.input_select("grade","Histological grade",{"1":"Grade I - well differentiated","2":"Grade II - moderately differentiated","3":"Grade III/IV - poorly or undifferentiated","Unknown":"Unknown"},selected="2"),
            ui.layout_columns(ui.input_select("t","T category",["T1a","T1b","T1NOS","T2","T3","T4","TX"],selected="T2"),
                              ui.input_select("n","Redefined N",{"N0":"N0","N1":"N1 (1-3 positive nodes)","N2":"N2 (>=4 positive nodes)","NX":"NX"},selected="N1"),
                              ui.input_select("m","M category",["M0","M1"]),col_widths=[4,4,4]),
            ui.input_action_button("calculate","Calculate survival estimates",class_="btn-primary")),
        ui.card(ui.card_header("Individualized prediction"),
            ui.layout_columns(ui.div(ui.tags.small("DERIVED STAGE"),ui.tags.strong(ui.output_text("stage")),class_="metric"),
                              ui.div(ui.tags.small("XGBOOST-COX RISK SCORE"),ui.tags.strong(ui.output_text("risk")),class_="metric"),col_widths=[6,6]),
            ui.div(ui.tags.small("PREDICTED MEDIAN SURVIVAL"),ui.tags.strong(ui.output_text("median")),class_="median"),
            ui.navset_tab(
                ui.nav_panel("1/3/5-year nomogram",ui.output_plot("nomogram",height="300px")),
                ui.nav_panel("Exact estimates",ui.output_table("estimates"))
            )), col_widths=[5,7]
    ),
    ui.div(ui.tags.b("Important: "),"This retrospective research model has not undergone external or prospective validation. Estimates must not replace multidisciplinary clinical judgment.",class_="disclaimer")
)

def server(input: Inputs, output: Outputs, session: Session):
    @reactive.calc
    @reactive.event(input.calculate, ignore_none=False)
    def result():
        return predict(input.age(),input.sex(),input.race(),input.grade(),input.t(),input.n(),input.m())
    @output
    @render.text
    def stage(): return "Stage " + result()["stage"]
    @output
    @render.text
    def risk(): return f'{result()["risk"]:.3f}'
    @output
    @render.text
    def median(): return f'{result()["median"]} months' if result()["median"] is not None else "Not reached"
    @output
    @render.table
    def estimates():
        r=result(); return pd.DataFrame({"Prediction horizon":["1 year","3 years","5 years"],"Survival probability":[f'{100*r["survival"][m]:.1f}%' for m in (12,36,60)]})
    @output
    @render.plot
    def nomogram():
        r=result(); vals=np.array([r["survival"][m] for m in (12,36,60)])*100
        fig,ax=plt.subplots(figsize=(7,3)); colors=["#0d766c"]*3
        bars=ax.barh(["1-year survival","3-year survival","5-year survival"],vals,color=colors,height=.52)
        ax.set_xlim(0,100);ax.set_xlabel("Predicted survival probability (%)");ax.invert_yaxis();ax.grid(axis="x",color="#d7ded9",linewidth=.7);ax.set_axisbelow(True)
        for b,v in zip(bars,vals): ax.text(min(v+1.5,94),b.get_y()+b.get_height()/2,f"{v:.1f}%",va="center",fontweight="bold",color="#15332f")
        for s in ["top","right","left"]: ax.spines[s].set_visible(False)
        fig.suptitle(f'Redefined 2 Stage {r["stage"]} | Risk score {r["risk"]:.3f}',x=.01,ha="left",fontsize=11,fontweight="bold",color="#15332f")
        fig.tight_layout(); return fig

app = App(app_ui, server, static_assets={"/favicon.ico": HERE / "www" / "favicon.svg"})
