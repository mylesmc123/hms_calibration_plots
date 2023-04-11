from pydsstools.heclib.dss import HecDss
from pydsstools.core import TimeSeriesContainer
import pandas as pd
import numpy as np
# import plotly
from plotly.graph_objs import Scatter, Layout
from plotly.subplots import make_subplots
import plotly.graph_objects as go

parameter = 'Flow'
units = 'cfs'

eventList = ['TS_Bill', 'Hurricane_Katrina', 'Hurricane_Isaac']
for event in eventList:

    dss_file = fr'V:\projects\p00542_cpra_2020_lwi_t10\02_analysis\HEC_HMS_RE-Calibration\HMS_Model_AORC_{event}\{event}.dss'
    fid = HecDss.Open(fr"{dss_file}")
    pathname_pattern = f'//*/FLOW-OBSERVED/*/1HOUR/*/'
    path_list = fid.getPathnameList(pathname_pattern,sort=1)

    gageList = []
    DSSpaths_List = []
    DSSpaths_List_sim = []

    for path in path_list:
        
        pathSplit = path.split("/")
        gage = pathSplit[2]
        cPart = pathSplit[3]
        ePart = pathSplit[5]
        fPart = pathSplit[6]
        gageList.append(gage)
        
        # Remove d-part
        noDpartPath = f"//{gage}/{cPart}//{ePart}/{fPart}/"
        noDpartPath_sim = f"//{gage}/FLOW//{ePart}/{fPart}/"
        DSSpaths_List.append(noDpartPath)
        DSSpaths_List_sim.append(noDpartPath_sim)

    # sort the lists alphabetically, and remove dups
    gageList = sorted(list(set(gageList)))
    DSSpaths_List = sorted(list(set(DSSpaths_List)))
    DSSpaths_List_sim = sorted(list(set(DSSpaths_List_sim)))

    # Setup plotly subplot figure
    fig = make_subplots(  
        rows=len(gageList), 
        cols=1, 
        # vertical_spacing=3,
        # padding = 
        # vertical_spacing=(1 / (n - 1)),
        subplot_titles=gageList,
        
    )
    
    for i, path_obs in enumerate(DSSpaths_List):
        
        # Create sim path based on FLOW-OBSERVED path.
        path_sim = path_obs.replace("FLOW-OBSERVED", "FLOW")

        # Make plot name = bPart
        pathSplit = path_obs.split("/")
        gage = pathSplit[2]

        ts_obs = fid.read_ts(path_obs)
        ts_sim = fid.read_ts(path_sim)

        # setup dataframe of traces
        df_obs = pd.DataFrame()
        df_sim = pd.DataFrame()
        df_obs['Times_obs'] = ts_obs.pytimes
        df_obs['Values_obs'] = ts_obs.values
        df_obs['Missing_obs'] = ts_obs.nodata
        df_sim['Times_sim'] = ts_sim.pytimes
        df_sim['Values_sim'] = ts_sim.values
        df_sim['Missing_sim'] = ts_sim.nodata

        df_obs.Values_obs = np.where(df_obs.Missing_obs == True, np.NaN, df_obs.Values_obs)
        df_sim.Values_sim = np.where(df_sim.Missing_sim == True, np.NaN, df_sim.Values_sim)
        # df['sim'] = sim
        
        # concatenate dataframes for each sim to a single dataframe that will be output to a csv file
        # df_gage = pd.concat([df_gage,df])


        fig.append_trace(
            go.Scatter(
                x=df_obs.Times_obs, 
                y=df_obs.Values_obs,
                # name = sim,
                name = f'{gage} Flow Observed',
                legendgroup=f'{i}',
                # showlegend = False,
            ), 
            row=i+1,
            # row = 1, 
            col=1
        )
        fig.append_trace(
            go.Scatter(
                x=df_sim.Times_sim, 
                y=df_sim.Values_sim,
                # name = sim,
                name = f'{gage} Flow Simulated',
                legendgroup=f'{i}',
                # showlegend = False,
            ), 
            row=i+1,
            # row = 1, 
            col=1
        )

        fig_iso = make_subplots(  
            rows=1, 
            cols=1, 
            # vertical_spacing=3,
            # padding = 
            # vertical_spacing=(1 / (n - 1)),
            # subplot_titles=gage
        )

        fig_iso.append_trace(
            go.Scatter(
                x=df_obs.Times_obs, 
                y=df_obs.Values_obs,
                name = f'{gage} Flow Observed',
            ), 
            row=1,
            col=1
        )
        fig_iso.append_trace(
            go.Scatter(
                x=df_sim.Times_sim, 
                y=df_sim.Values_sim,
                name = f'{gage} Flow Simulated',
            ), 
            row=1,
            col=1
        )

        fig_iso.update_layout(
            height=1000, 
            width=2300,
            showlegend=True, 
            title_text=f"Amite HMS: {event} - {gage} {parameter} ({units})",
            font=dict(
                    family='sans-serif', size=30
            ),
            template= "seaborn",
            hoverlabel=dict(
                font=dict(
                    family='sans-serif', size=22
                ),
                namelength= -1
            )
        )

        fig_iso.update_yaxes(automargin=True)
        fig_iso.write_html(f"results/html/{gage} {event} Results.html")
        fig_iso.write_image(f"results/png/{gage} {event} Results.png")

    fid.close()

    fig.update_layout(
        height=len(gageList)*1000, 
        width=2300,
        showlegend=True,
        legend_tracegroupgap = 955,
        font=dict(
                family='sans-serif', size=30
        ),
        title_text=f"Amite HMS Calibration Points {event} - {parameter} ({units})",
        template= "seaborn",
        hoverlabel=dict(
            font=dict(
                family='sans-serif', size=22
            ),
            namelength= -1
        )
    )

    fig.update_yaxes(automargin=True)
    fig.update_annotations(font_size=30)
    fig.write_html(f"results/html/{event} Results.html")
    fig.write_image(f"results/png/{event} Results.png")
