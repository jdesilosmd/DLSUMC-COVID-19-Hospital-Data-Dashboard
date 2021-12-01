import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import date

today = date.today()

st.set_page_config(page_title="DLSUMC COVID-19 Dashboard", layout="wide")

with st.container():
    st.title("DLSUMC COVID-19 Surveillance Dashboard")
    st.markdown("#### (As of {})".format(today))
    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")

gsheet_id = "1KGC21M3r32veUwlJNADAlHxZAubdWpw4wAxjbZzeIuY"
sheet_main = "DLSUMC_2021_COVID_DATABASE"
sheet_confirmed = "DLSUMC_DATABASE_COVID_CONFIRMED"
sheet_hcw_confirmed = "HCW_CONFIRMED"


main_url = "https://docs.google.com/spreadsheets/d/{0}/gviz/tq?tqx=out:csv&sheet={1}".format(gsheet_id, sheet_main)
confirmed_url = "https://docs.google.com/spreadsheets/d/{0}/gviz/tq?tqx=out:csv&sheet={1}".format(gsheet_id, sheet_confirmed)
hcw_confirmed_url = "https://docs.google.com/spreadsheets/d/{0}/gviz/tq?tqx=out:csv&sheet={1}".format(gsheet_id, sheet_hcw_confirmed)


df_main = pd.read_csv(main_url)
df_confirmed = pd.read_csv(confirmed_url)
df_hcw = pd.read_csv(hcw_confirmed_url)
df_hcw["VACCINATION STATUS"] = df_hcw["VACCINATION STATUS"].fillna("UNVACCINATED")

with st.container():
    st.header("COVID-19 Confirmed Cases Summary:")
    st.markdown(" ")
    st.markdown(" ")

    with st.container():
        # Confirmed data:
        ## Admit Status:
        admit_count = df_confirmed["ADMIT CLASS"].value_counts().rename_axis("Admit Class").reset_index(name='Total')
        admitted_total = admit_count['Total'].values[0]
        hcw_hq_total = admit_count['Total'].values[1]
        er_total = admit_count['Total'].values[2]
        admitted_hcw_total = admit_count['Total'].values[3]
        opd_watcher_total = admit_count['Total'].values[4]


        # st.write(admit_count)

        ## Reinfection
        reinfect_count = df_confirmed.loc[df_confirmed["HCW #"]=='REINFECTION', ["HCW #"]].count()
        reinfect_total = reinfect_count.iloc[0]
        hcw_total = (admitted_hcw_total + hcw_hq_total)-reinfect_total


        ## ER Status:
        df_er_disposition = df_confirmed.loc[df_confirmed["ADMIT CLASS"]=="ER", ["DISPOSITION"]]
        disposition_count = df_er_disposition["DISPOSITION"].value_counts().rename_axis("Disposition").reset_index(name="Total")
        er_expired_total = disposition_count['Total'].values[0]
        er_discharged_total = disposition_count['Total'].values[1]
        er_hama_total = disposition_count['Total'].values[2]
        er_transferred_total = disposition_count['Total'].values[3]
        # st.write(disposition_count)


        ## Total:
        dlsumc_confirmed = (admitted_total + admitted_hcw_total + er_total + hcw_hq_total) - reinfect_total


        ## data breakdown for In-patient:
        status_disposition = df_confirmed.loc[df_confirmed["STATUS"]=="ADMITTED", ["DISPOSITION"]]
        status_count = status_disposition["DISPOSITION"].value_counts().rename_axis("Disposition").reset_index(name="Total")
        # st.write(status_count)

        admit_disposition = df_confirmed.loc[df_confirmed["ADMIT CLASS"] == "ADMITTED", ["DISPOSITION"]]
        admit_disposition_count = admit_disposition["DISPOSITION"].value_counts().rename_axis("Disposition").reset_index(name="Total")
        # st.write(admit_disposition_count)

        in_pt_discharged = admit_disposition_count["Total"].values[0]
        in_pt_expired = admit_disposition_count["Total"].values[1]
        in_pt_hama = admit_disposition_count["Total"].values[2]
        in_pt_curr_admitted = status_count["Total"].values[3]
        in_pt_non_covid = status_count["Total"].values[4]
        #in_pt_transf = admit_disposition_count["Total"].values[5]

        hcw_home_hosp_q = hcw_hq_total - reinfect_total
        hcw_hq_discharged = df_confirmed.loc[(df_confirmed["ADMIT CLASS"]=="HCW-HQ")&
                                             (df_confirmed["DISPOSITION"]=="DISCHARGED"), ["ADMIT CLASS"]]
        hcw_hq_discharged = hcw_hq_discharged.value_counts().values[0]

        hcw_admit_discharged = df_confirmed.loc[(df_confirmed["ADMIT CLASS"]=="ADMITTED-HCW")&
                                                (df_confirmed["DISPOSITION"]=="DISCHARGED"), ["ADMIT CLASS"]]
        hcw_admit_discharged = hcw_admit_discharged.value_counts().values[0]

        hcw_discharged_all = (hcw_hq_discharged + hcw_admit_discharged) - reinfect_total



        hcw_hq_expired = df_confirmed.loc[(df_confirmed["ADMIT CLASS"] == "HCW-HQ") &
                                          (df_confirmed["DISPOSITION"] == "EXPIRED"), ["ADMIT CLASS"]]
        hcw_hq_expired = hcw_hq_expired.value_counts().values[0]

        hcw_admit_expired = df_confirmed.loc[(df_confirmed["ADMIT CLASS"] == "ADMITTED-HCW") &
                                             (df_confirmed["DISPOSITION"] == "EXPIRED"), ["ADMIT CLASS"]]
        hcw_admit_expired = hcw_admit_expired.value_counts().values[0]

        hcw_expired_all = hcw_hq_expired + hcw_admit_expired




        # COVID-19 Summary
        col_summary1, col_summary2, col_summary3, col_summary4 = st.columns(4)
        with col_summary1:
            st.metric(label="COVID-19 Confirmed Cases", value=dlsumc_confirmed.astype(str))

        with col_summary2:
            st.metric(label="In-Patient", value=admitted_total.astype(str))
            with st.expander(label="See data breakdown"):
                st.metric(label="Currently Admitted", value=in_pt_curr_admitted.astype(str))
                st.metric(label="Discharged", value=in_pt_discharged.astype(str))
              #  st.metric(label="Transferred", value=in_pt_transf.astype(str))
                st.metric(label="Transferred to Non-COVID", value=in_pt_non_covid.astype(str))
                st.metric(label="HAMA", value=in_pt_hama.astype(str))
                st.metric(label="Expired", value=in_pt_expired.astype(str))

        with col_summary3:
            st.metric(label="Emergency Room", value=er_total.astype(str))
            with st.expander(label="See data breakdown"):
                st.metric(label="Discharged", value=er_discharged_total.astype(str))
                st.metric(label="HAMA", value=er_hama_total.astype(str))
                st.metric(label="Transferred", value=er_transferred_total.astype(str))
                st.metric(label="Expired", value=er_expired_total.astype(str))

        with col_summary4:
            st.metric(label="Healthcare Workers with COVID-19", value=hcw_total.astype(str))
            with st.expander(label="See data breakdown"):
                st.metric(label="Admitted", value=admitted_hcw_total.astype(str))
                st.metric(label="Home/Hospital Quarantined", value=hcw_home_hosp_q.astype(str))
                st.metric(label="Discharged", value=hcw_discharged_all.astype(str))
                st.metric(label="Expired", value=hcw_expired_all.astype(str))

    st.markdown("   ")
    st.markdown("   ")

## Data Figures:

with st.container():
    st.header("Data Visualization:")
    st.markdown(" ")
    st.markdown(" ")


    with st.expander(label="Epi Curve: Confirmed Positive HCWs"):
        hcw_epicurve = px.histogram(df_hcw, x="DATE RESULT RELEASED",
                                    title="Epi Curve: Confirmed Positive Health Care Workers (HCWs)")

        hcw_epicurve_vax = px.histogram(df_hcw, x="DATE RESULT RELEASED", color="VACCINATION STATUS",
                                    title="Epi Curve: Confirmed Positive Health Care Workers (HCWs), as to Vaccination Status")

        st.plotly_chart(hcw_epicurve, use_container_width= True)
        st.plotly_chart(hcw_epicurve_vax, use_container_width=True)

    with st.expander(label="Health Care Workers Infected with COVID-19"):

        severity_hcw = df_hcw["SEVERITY"].value_counts().rename_axis("Severity").reset_index(name='Total')
        severity_hcw.iloc[0, 1] = severity_hcw.iloc[0, 1] + severity_hcw.iloc[7, 1]
        severity_hcw.iloc[2, 1] = severity_hcw.iloc[2, 1] + severity_hcw.iloc[5, 1]
        severity_hcw.iloc[4, 1] = severity_hcw.iloc[4, 1] + severity_hcw.iloc[9, 1]
        severity_hcw = severity_hcw.iloc[[0, 1, 2, 3, 4, 6]]

        classification_hcw = df_hcw["CLASSIFICATION"].value_counts().rename_axis("HCW Classification").reset_index(name='Total')
        classification_hcw.iloc[0,1] = classification_hcw.iloc[0, 1] + classification_hcw.iloc[5, 1] + classification_hcw.iloc[6, 1] +\
                                       classification_hcw.iloc[8, 1] + classification_hcw.iloc[9, 1] + classification_hcw.iloc[10, 1]
        classification_hcw.iloc[1, 1] = classification_hcw.iloc[1, 1] + classification_hcw.iloc[4, 1]
        classification_hcw.iloc[2, 1] = classification_hcw.iloc[2, 1] + classification_hcw.iloc[7, 1]
        classification_hcw = classification_hcw.iloc[[0, 1, 2, 3]]


        severity_hcw_bar = px.bar(severity_hcw, x="Severity", y="Total", color="Severity",
                                  title="COVID-19 Positive HCWs by Severity")
        severity_hcw_bar.update_layout(showlegend=False)

        classification_hcw_bar = px.bar(classification_hcw, x="HCW Classification", y="Total",
                                        color="HCW Classification", title="COVID-19 Positive HCWs by Profession")
        classification_hcw_bar.update_layout(showlegend=False)

        st.plotly_chart(severity_hcw_bar, use_container_width= True)
        st.plotly_chart(classification_hcw_bar, use_container_width=True)

    with st.expander(label="Positivity Rate"):
        st.write("Coming soon")

