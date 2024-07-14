#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@lwoodblake
"""
import streamlit as st
import pandas as pd
from statsbombpy import sb
from mplsoccer import Pitch
from matplotlib.colors import LinearSegmentedColormap

#get all competitions available for free from StatsBomb API
allcomps=sb.competitions()
allcomps['display_name']=allcomps['competition_name'] + ' (' + allcomps['season_name'] + ')'

#page title
st.set_page_config(
    page_title="endless-heatmaps",
    page_icon=":fire:",
)
st.title('endless-heatmaps')

#add competition filter
with st.sidebar:
    st.title(':fire: endless-heatmaps')
    
    comp = st.selectbox(
    'Competition',
     allcomps['display_name'])
    
#choose relevant competitions
selected_df=allcomps[(allcomps.display_name==comp)]

#get comp and season id
comp_id=selected_df.competition_id.iloc[0]
szn_id=selected_df.season_id.iloc[0]

#get matches within comp/season
matches_df=sb.matches(competition_id=comp_id,season_id=szn_id)

#create column to be displayed in dropdown
matches_df['display_name']=matches_df['home_team'] + ' vs ' + matches_df['away_team'] + ' (' + matches_df['match_date'] + ')'

#add match filter
with st.sidebar:
    
    match_choice = st.selectbox(
    'Match',
     matches_df['display_name'])
    
#select event data for chosen match
chosen_match_df=matches_df[(matches_df.display_name==match_choice)]
final_id=chosen_match_df.match_id.iloc[0]
events_df=sb.events(match_id=final_id)

#parse start and end location of events
events_df[['x', 'y']] = events_df['location'].apply(pd.Series)
events_df[['pass_end_x', 'pass_end_y']] = events_df['pass_end_location'].apply(pd.Series)
events_df[['carry_end_x', 'carry_end_y']] = events_df['carry_end_location'].apply(pd.Series)

#get a list of all players that appear in event data for the game
events_df=events_df[~(events_df.player.isna())]
player_list=events_df.player.unique().tolist()

#create filter for event type and player
type_list=['Pass', 'Carry', 'Ball Receipt*', 'Shot', 'Duel', 'Interception', 'Clearance', 'Foul Won', 'Block',
'Ball Recovery', 'Dribble', 'Miscontrol']
with st.sidebar:
    
    player_name = st.selectbox(
    'Player',
     player_list)
    
    selected_type = st.selectbox(
    'Action Type',
     type_list)

#add option to choose between start and end location if event type selected is a pass or carry
if selected_type == "Pass" or selected_type == "Carry":
    with st.sidebar:
        coordinate_choice = st.radio(
            "Location",
            ["Start", "End"]
            )
else:
    with st.sidebar:
        coordinate_choice = st.radio(
            "Location",
            ["Start"]
            )
    
#add colour options, used to create the colour map
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    background_colour = st.color_picker("Background", "#313639")

with col2:
    line_colour = st.color_picker("Line", "#c3c3c3")

with col3:
    colour1 = st.color_picker("Heatmap 1", "#8ace00")
    
with col4:
    colour2 = st.color_picker("Heatmap 2", "#d7ff85")

with col5:
    colour3 = st.color_picker("Heatmap 3", "#ffffff")

cmaplist = [background_colour, colour1, colour2, colour3]
cmap = LinearSegmentedColormap.from_list("", cmaplist)

#filter event data based on event type and player name
selected_events_df=events_df[(events_df.type==selected_type)&(events_df.player==player_name)]
#set your pitch and figure details
pitch = Pitch(pitch_type='statsbomb', pitch_color=background_colour, line_color=line_colour, line_zorder=2, linewidth=3)

#visualise data as a heatmap on the pitch
fig, ax = pitch.draw(figsize=(16, 11), constrained_layout=True, tight_layout=False)
fig.set_facecolor('white')

if coordinate_choice=="End" and selected_type=="Pass":
    
    #plot the heatmap for end point of passes
    pitch.kdeplot(selected_events_df.pass_end_x, selected_events_df.pass_end_y, 
                  shade=True, levels=100,
                  shade_lowest=False, ax=ax,
                  cmap=cmap)
    
elif coordinate_choice=="End" and selected_type=="Carry":
    
    #plot the heatmap for end point of carries
    pitch.kdeplot(selected_events_df.carry_end_x, selected_events_df.carry_end_y, 
                  fill=True, levels=100,
                  shade_lowest=False, ax=ax,
                  cmap=cmap)
    
else:
    
    #plot the start coordinates
    pitch.kdeplot(selected_events_df.x, selected_events_df.y, 
                  fill=True, levels=100,
                  shade_lowest=False, ax=ax,
                  cmap=cmap)
    

st.pyplot(ax.get_figure())

#add credits
st.text('Data via statsbombpy. Visual created using mplsoccer.')
