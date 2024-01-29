# chart 
import streamlit as st
from streamlit_elements import dashboard
from streamlit_elements import nivo, elements, mui
import streamlit.components.v1 as components

# ----- jso, dataframe ...etc ------#
import pandas as pd
import numpy as np
import streamlit as st

from sklearn.preprocessing import MinMaxScaler

# ------ image , animation ----------- #

import matplotlib.pyplot as plt
from time import sleep

import matplotlib
matplotlib.use('Agg')




# RIOT.PY
from wak_riot import get_puuid, get_match_ids, get_match_data_logs, get_rank_info, get_match_v5, radar_chart
from wak_riot import gold_data, lose_match_gold_diff, get_events, duo_score ,death_spot, death_spot_sc, calculate_lane



pd.set_option('mode.chained_assignment',  None)
st.set_page_config(layout="wide"
                   , page_title = "League Of Legends dashboard"
                   , page_icon="🎮")



with open( "wak.css" ) as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)



# 사이드바
with st.sidebar:
    with st.form(key ='searchform'):
        summoner_name = st.text_input("search_summoner")
        api_key = st.text_input("api_key",
                                type = "password")     
        submit_search = st.form_submit_button()

if submit_search :
    with st.spinner('''### 최근 경기 데이터 수집중..🎮'''):
        puuid, summoner_id, iconId = get_puuid(summoner_name, api_key)
        match_ids = get_match_ids(puuid, api_key)
        match_info, champion_info = get_match_v5(match_ids, api_key)
        match_data_logs = get_match_data_logs(match_ids, api_key)  
        kill_log, wakteam_death_log,victim_by_jungle = get_events(match_data_logs,champion_info,summoner_name)
        nol_kill_log, chun_kill_log = duo_score(kill_log,champion_info,summoner_name)


        rank_data = get_rank_info(summoner_id,api_key)
        wak_radar_data, wak_vs_df = radar_chart(match_info,summoner_name,'MIDDLE')
        
        log_df = gold_data(match_data_logs, match_ids)
        gold_df = lose_match_gold_diff(log_df, summoner_name,'MIDDLE',champion_info)    


        # info, match, champion
        st.session_state.puuid = puuid
        st.session_state.match_ids = match_ids
        st.session_state.match_info = match_info
        st.session_state.match_data_logs = match_data_logs
        st.session_state.champion_info = champion_info
        st.session_state.rank_data= rank_data

        # summoner,death,kill,gold
        st.session_state.wak_radar_data = wak_radar_data
        st.session_state.wak_vs_df = wak_vs_df
        st.session_state.wakteam_death_log = wakteam_death_log
        st.session_state.victim_by_jungle = victim_by_jungle
        st.session_state.kill_log = kill_log
        st.session_state.gold_df = gold_df
        st.session_state.log_df = log_df
        # duo
        st.session_state.nol_kill_log = nol_kill_log
        st.session_state.chun_kill_log = chun_kill_log




if hasattr(st.session_state, 'puuid'):
    puuid = st.session_state.puuid

if hasattr(st.session_state, 'wak_vs_df'):
    wak_vs_df = st.session_state.wak_vs_df

    agg_columns = ['totalDamageDealtToChampions', 'totalCS10Minutes', 'soloKills', 'visionScore', 'damageDealtToBuildings']
    col= ['summonerName','챔피언딜량','10분CS','솔로킬','시야점수','타워피해량']

    wak_static = wak_vs_df.groupby(['summonerName']).agg(
        **{column: pd.NamedAgg(column=column, aggfunc='mean') for column in agg_columns}
    ).reset_index().round()
    wak_static.columns = col


# 매치 데이터
if hasattr(st.session_state, 'match_info'):
    match_info = st.session_state.match_info    
    unique_match = match_info['matchId'].nunique()
    lose_match_cnt = len(match_info[(match_info['puuid'] == puuid) & (match_info['win']==False)]) 
    wak_middle_lose = match_info[(match_info['summonerName'] == summoner_name)&(match_info['win']== False)&(match_info['teamPosition']== 'MIDDLE')]['matchId'].tolist()
    wak_middle_lose_cnt = len(wak_middle_lose)


    cs_10 = match_info.groupby(['teamPosition']).agg(
        cs = pd.NamedAgg(column='totalCS10Minutes', aggfunc='mean')
    ).reset_index()

    


if hasattr(st.session_state, 'champion_info'):
    champion_info = st.session_state.champion_info
    # len(set(lose_matchlist)) 


if hasattr(st.session_state, 'log_df'):
    log_df = st.session_state.log_df
    log_df['timestamp'] = log_df['timestamp'].astype(int)
    ld = log_df[['matchId','timestamp','minionsKilled','participantId','position','totalGold','xp','level']]
    champion_info = champion_info[['matchId','participantId','teamId','teamPosition','summonerName','championName','win']]
    df1 = pd.merge(ld, champion_info, on=['matchId', 'participantId'], how='inner')
    wak20CS= df1[(df1['summonerName'] == summoner_name)&(df1['timestamp'] < 21)]


if hasattr(st.session_state, 'match_ids'):
    match_ids = st.session_state.match_ids

if hasattr(st.session_state, 'wakteam_death_log'):
    wakteam_death_log = st.session_state.wakteam_death_log
    

    # 왁굳이 미드라인에서 패배한 경기만    
    wakteam_lose_log = wakteam_death_log[wakteam_death_log['matchId'].isin(wak_middle_lose)]

    # 왁굳이 죽은 포지션
    wakgood_death = wakteam_lose_log[(wakteam_lose_log['summonerName_x'] == summoner_name)&(wakteam_lose_log['timestamp'] > 15)]

    # 패배한경기, 포지션별 죽은 횟수 집계
    team_death_15 = wakteam_lose_log[wakteam_lose_log['timestamp'] < 16].groupby(['victimPosition']).agg(
                    count = pd.NamedAgg(column = 'victimPosition', aggfunc='count')
                    ).reset_index().sort_values(by='count',ascending=True)
    
    team_death_16 = wakteam_lose_log[wakteam_lose_log['timestamp'] > 15].groupby(['victimPosition']).agg(
                    count = pd.NamedAgg(column = 'victimPosition', aggfunc='count')
                    ).reset_index().sort_values(by='count',ascending=True)
    

    # 왁굳이 패배한 경기중에서 솔로킬을 당한 경우
    wakteam_death_solo = wakteam_lose_log[wakteam_lose_log['assistingParticipantIds'].isna()] # 다른 상대팀의 어시스트 없이 솔로킬을 당한 경우

    death_solo_16 = wakteam_death_solo[wakteam_death_solo['timestamp'] > 15].groupby(['victimPosition']).agg(
                    death = pd.NamedAgg(column = 'victimPosition', aggfunc='count')).reset_index().sort_values(by='death',ascending=True)

    death_solo_15 = wakteam_death_solo[wakteam_death_solo['timestamp'] < 15].groupby(['victimPosition']).agg(
                    death = pd.NamedAgg(column = 'victimPosition', aggfunc='count')).reset_index().sort_values(by='death',ascending=True)


    # 라인전 이후 솔로킬로 짤린 포지션은 바텀(원딜) 이었다. 그렇다면 주로 어디서 짤리는가
    bottom_solo_death = wakteam_death_solo[(wakteam_death_solo['victimPosition'] == 'BOTTOM') & (wakteam_death_solo['timestamp'] > 15)]
  
    # 라인전동안 적팀정글로 인한 데스 (+우리팀 정글은 어디서 죽었을까?)
    jungle_death = wakteam_death_log[(wakteam_death_log['victimPosition'] == 'JUNGLE') | (wakteam_death_log['assistingParticipantIds'].apply(lambda x: 'JUNGLE' in x if isinstance(x, list) else False))]
    jungle_death_15 = jungle_death[jungle_death['timestamp'] < 16]


    # to json
    @st.cache_data
    def to_json_pie(data,col1,col2):
        death_cnt = []
        for index, row in data.iterrows():
            item = {
                'id': row[col1],
                'value': row[col2]
            }
            death_cnt.append(item)
        return death_cnt 



    death_cnt = to_json_pie(team_death_15,'victimPosition','count')
    death_cnt_16 = to_json_pie(team_death_16,'victimPosition','count')    
    death_solo_16 = death_solo_16.to_dict('records')

    
if hasattr(st.session_state, 'victim_by_jungle'):
    victim_by_jungle = st.session_state.victim_by_jungle
    jungle_15 = victim_by_jungle[victim_by_jungle['timestamp'] < 15 ].groupby(['victimPosition']).agg({'cnt':'sum'}).reset_index().sort_values(by=['cnt'])
    jungle_15 = jungle_15.to_dict('records')

if hasattr(st.session_state, 'nol_kill_log'):
    nol_kill_log = st.session_state.nol_kill_log

if hasattr(st.session_state, 'chun_kill_log'):
    chun_kill_log = st.session_state.chun_kill_log

if hasattr(st.session_state, 'gold_df'):
    gold_df = st.session_state.gold_df
    t3 = gold_df[gold_df['timestamp'] == 20].nsmallest(3, 'totalGold_diff')['teamPosition'].tolist()

    # to json
    gold_15 = []
    for team in gold_df['teamPosition'].unique():
        team_data = {
            'id': team,
            'data': []
        }

        team_df = gold_df[gold_df['teamPosition'] == team]
        for index, row in team_df.iterrows():
            item = {
                'x': row["timestamp"],
                'y': row["totalGold_diff"]
            }
            team_data["data"].append(item)

        gold_15.append(team_data)


# 흑백화면, 골드 통계
@st.cache_data
def lose_static():
    # 경기가 끝나고 total 골드 차이
    wak_team = (
        match_info.groupby(['matchId', 'teamId'])
        .filter(lambda x: any(x['summonerName'] == summoner_name))
    )


    stat = wak_team[wak_team['win']== False].groupby(['teamPosition']).agg(
            death_time = pd.NamedAgg(column = 'totalTimeSpentDead' , aggfunc='mean'),
            kda_mean = pd.NamedAgg(column = 'kda', aggfunc= 'mean'),
            ).reset_index()

    stat['death_time'] = round(stat['death_time'])
    stat.columns = ['victimPosition', 'death_time','kda_mean']
    return stat      



#랭크 데이터
if hasattr(st.session_state, 'rank_data'):
    rank_data = st.session_state.rank_data
    try:
        if rank_data:
            tier = rank_data[0]['tier'].lower()
            rank = rank_data[0]['rank']
            wins = rank_data[0]['wins']
            losses = rank_data[0]['losses']

            wins = sum([entry['wins'] for entry in rank_data])
            losses = sum([entry['losses'] for entry in rank_data])
            win_lose = [
                {"id": "Wins", "label": "Wins", "value": wins},
                {"id": "Losses", "label": "Losses", "value": losses}
            ]
        else:
            win_lose = []
    except:
        win_lose = [] 


# 능력치 radar 차트
if hasattr(st.session_state, 'wak_radar_data'):
    wak_radar_data = st.session_state.wak_radar_data
    # min_value_var = min(wak_radar_data, key=lambda x: x[f'{summoner_name}'])["var"]
    


    def main():
        with st.container():
            st.header("🎮 누가 범인 인가!?")
            st.caption(''' " 아니 우리팀 뭐하냐 " 우왁굳이 패배한 이유, 도대체 누구 때문에 지는걸까, 궁금해서 데이터를 분석해보았습니다. ''')
            st.markdown(f''' 
                            <div>\n
                            * 편차를 줄이기 위해 20분이상 진행된 경기만 분석했으며 총 {unique_match}경기 입니다. 
                            * '{summoner_name}'님의 최근{unique_match}개의 경기중 <span style="color:orange">패배한 경기는 {lose_match_cnt} 경기</span>입니다. 
                            * 그 중에서 왁굳님의 주포지션인 <span style="color:orange"> MIDDLE 포지션일때</span> {wak_middle_lose_cnt}번 졌으며, 이 기준으로 데이터가 집계되었습니다.                            
                            </div> 
                            ''', unsafe_allow_html=True)


            # MAIN - WAKGOOD
            col1,col2 = st.columns([2,4])
            with col1: 
                tab1,tab2 = st.tabs(['기본지표','Most Champ'])
                with tab1:   # INFO
                    st.subheader('🎲 INFO')
                    st.caption(f''' {summoner_name}님이 그동안 만난 상대 미드라이너와의 게임지표
                            (0~1점으로 표준화)''')
                    
                    with elements("info/radar"):                
                            layout = [
                                        dashboard.Item("item_info", 0, 0, 1.2, 2, isDraggable=False, isResizable=True ),
                                        dashboard.Item("item_rank", 2, 1, 0.8, 1, isDraggable=False, isResizable=True ),
                                        dashboard.Item("item_tier", 2, 2, 0.8, 1, isDraggable=False, isResizable=True)
                                        ]
                            card_sx = {"background-color":"#0a0a0adb","borderRadius": "20px", "outline": "1px solid #31323b"} # "outline": "1px solid #31323b"
                            with dashboard.Grid(layout):

                                mui.Card( # 티어,랭크

                                        mui.Typography('TIER',body='h4',sx={'text-align':'center'}),
                                        mui.CardMedia( 
                                            mui.Divider(),
                                            sx={
                                                "height":"90px",
                                                "width":"170px",                                     
                                                "backgroundImage": f"url(https://raw.communitydragon.org/14.1/game/assets/ux/tftmobile/particles/tft_regalia_{tier}.png)",  
                                            },
                                        ),
                                        mui.Typography(f'{tier} - {rank}',body='h5',sx={'text-align':'center'})
                                    
                                        , key='item_tier',sx=card_sx)
                                
                                mui.Box( # radar charts
                                    children = [
                                        mui.CardContent(                                 
                                            sx={
                                                "display": "flex",
                                                "align-items": "center",
                                                "text-align":"center",
                                                "padding": "0 8px 0 8px",
                                                "gap" : 1                                        
                                            },                                    
                                            
                                            children = [
                                                mui.CardMedia( 
                                                    sx={
                                                        "height": 80,
                                                        "width": 80,
                                                        "borderRadius": "10%",
                                                        "backgroundImage": f"url(http://ddragon.leagueoflegends.com/cdn/14.1.1/img/profileicon/4025.png)",  
                                                    },
                                                ),
                                                mui.Divider(orientation="vertical",sx={"height": "100px"}), 
                                
                                            ]
                                        ),                                 

                                            mui.Divider(sx={"height": "1px"}), # orientation="vertical",
                                            
                                            nivo.Radar(
                                                data=wak_radar_data,
                                                keys=[f'{summoner_name}','상대라이너'],
                                                colors={'scheme': 'nivo' },
                                                indexBy="var",
                                                valueFormat=">-.2f",
                                                maxValue={1.0},
                                                margin={ "top": 50, "right": 60, "bottom": 110, "left": 80 },
                                                borderColor={ "from": "color" },
                                                gridShape="linear",
                                                gridLevels={3},
                                                gridLabelOffset=15,
                                                dotSize=5,
                                                dotColor={ "theme": "background" },
                                                dotBorderWidth=1,
                                                motionConfig="wobbly",
                                                legends=[
                                                    {
                                                        "anchor": "top-left",
                                                        "direction": "column",
                                                        "translateX": -70,
                                                        "translateY": -30,
                                                        "itemWidth": 100,
                                                        "itemHeight": 20,
                                                        "itemTextColor": "white",
                                                        "symbolSize": 15,
                                                        "symbolShape": "circle",
                                                        "effects": [
                                                            {
                                                                "on": "hover",
                                                                "style": {
                                                                    "itemTextColor": "white"
                                                                }
                                                            }
                                                        ]
                                                    }
                                                ],
                                                theme={
                                                    "textColor": "white",
                                                    "tooltip": {
                                                        "container": {
                                                            "background": "#262730",
                                                            "color": "white",
                                                        }
                                                    }
                                                }
                                            ),
                                    ]
                                    ,key="item_info",sx=card_sx)
            
                                mui.Card( # RANK 승패
                                    children=[
                                        mui.Typography(
                                                "24S RECORD",variant="body2",sx={'background-color':'#181819','text-align':'center'}),  
                                        
                                        nivo.Pie( 
                                            data=win_lose,
                                            margin={"top": 8, "right": 20, "bottom": 50, "left": 20 },
                                            innerRadius={0.5},
                                            padAngle={2},
                                            activeOuterRadiusOffset={8},
                                            colors=['#459ae5', '#ed4141'],                   
                                            borderWidth={1},
                                            borderColor={
                                                "from": 'color',
                                                "modifiers": [
                                                    [
                                                        'darker',
                                                        0.2,
                                                        'opacity',
                                                        0.6
                                                    ]
                                                ]
                                            },
                                            enableArcLinkLabels=False,
                                            arcLinkLabelsSkipAngle={10},
                                            arcLinkLabelsTextColor="white",
                                            arcLinkLabelsThickness={0},
                                            arcLinkLabelsColor={ "from": 'color', "modifiers": [] },
                                            arcLabelsSkipAngle={10},
                                            arcLabelsTextColor={ "theme": 'background' },
                                            legends=[
                                                {
                                                    "anchor": "bottom",
                                                    "direction": "row",
                                                    "translateX": 0,
                                                    "translateY": 20,
                                                    "itemWidth": 50,
                                                    "itemsSpacing" : 5,
                                                    "itemHeight": 20,
                                                    "itemTextColor": "white",
                                                    "symbolSize": 7,
                                                    "symbolShape": "circle",
                                                    "effects": [
                                                        {
                                                            "on": "hover",
                                                            "style": {
                                                                "itemTextColor": "white"
                                                            }
                                                        }
                                                    ]
                                                }
                                            ],
                                            theme={
                                                "background": "#181819",
                                                "textColor": "white",
                                                "tooltip": {
                                                    "container": {
                                                        "background": "#181819",
                                                        "color": "white",
                                                    }
                                                }
                                            },
                                        )

                                        ]
                                    
                                        ,key='item_rank',sx=card_sx)

                    st.markdown(''' #### 🔎 Wak point ''')                                

                    expander = st.expander("(평균) 데이터")
                    with expander:
                        st.write(wak_static)

                        st.markdown(f'''
                                <div> \n
   
                                * 평균적으로 한웨이브의 미니언을 놓치는 수치입니다.
 
                                </div>
                                ''',unsafe_allow_html= True)

                            #  ✔️ 왁굳님의 가장 취약한 부분은 <strong>{min_value_var}</strong> 입니다. 
                            #     * 현재 왁굳님의 평균 10분CS는 {int(wak_static[f'{min_value_var}'][0])}개 이며 
                            #     * 상대 라이너의 평균 10분CS는 {int(wak_static[f'{min_value_var}'][1])}개 입니다.


                # Most Champ
                with tab2:
                    summoner_match_info = match_info[(match_info['puuid'] == puuid)]
                    # 챔피언별 통계
                    champ_static = summoner_match_info.groupby(['championName']).agg(
                                            champion_count = pd.NamedAgg(column = 'championName', aggfunc='count'),
                                            soloKills_sum = pd.NamedAgg(column = 'soloKills', aggfunc='sum'),
                                            multiKills_sum = pd.NamedAgg(column = 'multikills', aggfunc='sum'),                                       
                                            win_sum = pd.NamedAgg(column = 'win', aggfunc='sum'),
                                            totalCS10Minutes_mean = pd.NamedAgg(column = 'totalCS10Minutes', aggfunc='mean'),
                                            damagePerMinute_mean = pd.NamedAgg(column = 'damagePerMinute', aggfunc ='mean'), 
                                            damageDealtToBuildings_mean = pd.NamedAgg(column = 'damageDealtToBuildings', aggfunc='mean'),
                                            damageDealtToObjectives_mean = pd.NamedAgg(column = 'damageDealtToObjectives', aggfunc='mean'),
                                            visionScore_mean = pd.NamedAgg(column='visionScore',aggfunc='mean'),
                                            longestTimeSpentLiving = pd.NamedAgg(column = 'longestTimeSpentLiving', aggfunc='mean'), 
                                            kda_mean = pd.NamedAgg(column='kda', aggfunc ='mean')                                          

                                            ).sort_values(by=['champion_count'], ascending=False).reset_index().round(2)
                    
                    champ_static['win_rate'] = round((champ_static['win_sum']/champ_static['champion_count']) * 100)

                    first_champ = champ_static.iloc[0]['championName']
                    second_champ = champ_static.iloc[1]['championName']


                    st.subheader('Most Champion')
                    st.caption(''' 5판이상 사용한 챔피언 기준입니다. ''')

                    with elements("most_champ"):                
                        layout = [
                                    dashboard.Item("champ1", 0, 0, 1, 3,isDraggable=True, isResizable=True ),
                                    dashboard.Item("champ2", 2, 0, 1, 3,isDraggable=True, isResizable=True ),

                                    ]
                        
                        with dashboard.Grid(layout):
                            mui.Card(
                                children=[      
                                    mui.CardMedia( # most champ 1
                                            sx={
                                                "height": 110,
                                                "backgroundImage": f"linear-gradient(rgba(0, 0, 0, 0), rgba(10,10,10,10)),url(https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{first_champ}_3.jpg)",
                                                "backgroundPosition": "bottom",
                                            }
                                        ),
                                    mui.CardContent(
                                        sx={'padding':2}, # 설명
                                        children=[  
                                            mui.Typography(
                                                f" {first_champ} ",
                                                variant="h4",
                                                component="div"
                                            ),
                                            mui.Typography(
                                                    "ㅎㅇ",
                                                variant="body2",
                                                color="text.secondary",
                                                sx={
                                                    "font-size": "12px"},
                                                
                                            )]
                                        ),


                                    mui.Box( 
                                        sx={
                                            "display": "flex",
                                            "gap": "20px",
                                            "padding": "0",
                                            "justify-content": "center",
                                        },
                                        children=[
                                            mui.Box( 
                                                sx={
                                                    "display": "flex",
                                                    "flexDirection": "column",
                                                    "alignItems": "center",
                                                },
                                                children=[
      
                                                    mui.Typography(
                                                        f'챔피언 승률, 최다 라인전 CS, 최다 솔로킬',
                                                        sx={"font-size": "12px"}
                                                    )
                                                ]
                                            ),


                                        ]
                                    ),

                                ] , key="mostchamp", elevation=1 , sx=card_sx) #  sx = {"background-color":"#0a0a0adb","borderRadius": "23px"}

                            mui.Card(
                                children=[      
                                    mui.CardMedia( # 챔피언
                                            sx={
                                                "height": 110,
                                                "backgroundImage": f"linear-gradient(rgba(0, 0, 0, 0), rgba(10,10,10,10)),url(https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{second_champ}_0.jpg)",
                                                "backgroundPosition": "bottom",
                                            }
                                        ),
                                  
                                    mui.CardContent(
                                        sx={'padding':2}, # 설명
                                        children=[  
                                            mui.Typography(
                                                f" {second_champ} ",
                                                variant="h4",
                                                component="div"
                                            ),
                                            mui.Typography(
                                                    "ㅎㅇ",
                                                variant="body2",
                                                color="text.secondary",
                                                sx={
                                                    "font-size": "12px"},
                                                
                                            )]
                                        ),


                                    mui.Box( 
                                        sx={
                                            "display": "flex",
                                            "gap": "20px",
                                            "padding": "0",
                                            "justify-content": "center",
                                        },
                                        children=[
                                            mui.Box( 
                                                sx={
                                                    "width" : "70px",
                                                    "display": "flex",
                                                    "flexDirection": "column",
                                                    "alignItems": "center",
                                                },
                                                children=[
    
                                                    mui.Typography(
                                                        f';;',
                                                        sx={"font-size": "30px"}
                                                    )
                                                ]
                                            ),


                                        ]
                                    ),

                                ] , key="champ2", elevation=0 , sx={"background-color":"black","borderRadius": "23px",'text-align':'center'}) 
            
                        
                    expander = st.expander("챔피언 데이터")
                    with expander:
                        st.dataframe(champ_static)
          

            with col2: # 패배한경기 분석 (gold)

                tab1,tab2,tab3,tab4 = st.tabs(['GOLD🪙','DEATH','DEATH II','DEATH III'])
                with tab1: # 골드
                    st.subheader(''' ✔️ (패배한 경기) 포지션별 골드차이(20분)''')
                    st.caption('첫번째 단서는 GOLD 입니다. 라인전 동안의 CS, KILL 을 통해 벌어진 상대 라이너와의 골드차이를 통해 누가 똥쌌는지 유추 할 수 있습니다.')
                    with elements("GOLD"):                
                            layout = [
                                        dashboard.Item("item1", 0, 0, 4, 1,isDraggable=True, isResizable=True ),
                                        dashboard.Item("item2", 0, 3, 5, 2,isDraggable=True, isResizable=True ),
                                        dashboard.Item("item3", 6, 0, 1, 2,isDraggable=True, isResizable=True ),

                                        ]
                            card_sx = {"background-color":"#0a0a0adb","borderRadius": "23px", "outline": "1px solid #242427"}
                            with dashboard.Grid(layout):

                                mui.Card(  # nivo_line                                       
                                    children=[                                
                                        nivo.Line(
                                            data= gold_15,
                                            margin={'top': 30, 'right': 60, 'bottom': 50, 'left': 80},
                                            xScale={'type': 'point'},
                                            yScale={
                                                'type': 'linear',
                                                'min': 'auto',
                                                'max': 'auto',
                                                # 'stacked': True,
                                                'reverse': False
                                            },
                                            curve="cardinal",

                                            axisBottom={
                                                    'tickSize': 5,
                                                    'tickPadding': 3,
                                                    'tickRotation': 0,
                                                    'legend': 'miniute',
                                                    'legendOffset': 36,
                                                    'legendPosition': 'middle'
                                                },

                                            axisLeft={
                                                'tickSize': 2,
                                                'tickPadding': 3,
                                                'tickRotation': 0,
                                                'legend': 'gold',
                                                'legendOffset': -50,
                                                'legendPosition': 'middle'
                                            },


                                            legends=[
                                                {
                                                    "anchor": "bottom-left",
                                                    "direction": "column",
                                                    "translateX": 10,
                                                    "translateY": -10,
                                                    "itemWidth": 10,
                                                    "itemHeight": 15,
                                                    "itemTextColor": "white",
                                                    "symbolSize": 10,
                                                    "symbolShape": "circle",
                                                    "effects": [
                                                        {
                                                            "on": "hover",
                                                            "style": {
                                                                "itemTextColor": "white",
                                                                'itemBackground': 'rgba(0, 0, 0, .03)',
                                                                'itemOpacity': 1
                                                            }
                                                        }
                                                    ]
                                                }
                                            ],

                                            colors=  {'scheme': 'accent'},
                                            enableGridX = False,
                                            enableGridY = False,
                                            lineWidth=2,
                                            pointSize=3,
                                            pointColor='white',
                                            pointBorderWidth=1,
                                            pointBorderColor={'from': 'serieColor'},
                                            pointLabelYOffset=-12,
                                            enableArea=True,
                                            areaOpacity='0.2',
                                            useMesh=True,                
                                            theme={
                                                    "textColor": "white",
                                                    "tooltip": {
                                                        "container": {
                                                            "background": "#3a3c4a",
                                                            "color": "white",
                                                        }
                                                    }
                                                },

                                            animate= False),

                                        ]
                                    
                                        ,key="item2",sx=card_sx) #sx=card_sx          
                            
                                mui.Card(
                                        f'none'
                                        ,key="item3") #sx=card_sx          
                    
                    

                    st.markdown(f'''
                                <div> \n
                                * 패배한 경기의 <strong> 20분</strong> 동안의 <strong> 포지션별 골드량(평균) 차이</strong>를 구해보았습니다.
                                * 라인전 이후부터 상대적으로 <span style="color:#74c476"> {t3[0]} </span>라인 에서 골드량(평균)차이가 많이 벌어지고 있는 편입니다.
                                * 놀랍게도 <span style="color:orange">왁굳님(MIDDLE)</span>의 경우 라이너중 가장 안정적인 GOLD차이를 보여주고 있었습니다. 
                                * 하지만 골드차이만 보고 단정짓기는 어렵습니다. 서포터의 경우 원래 KILL,CS 를 먹기 힘든 포지션이라 상대와 비교했을 때 큰 차이가 없기 때문입니다.
                                <span style="color:#ae8ed9"> 'DEATH☠️' </span> 관련한 변수를 확인해봅시다.
                                </div>
                                    '''
                            , unsafe_allow_html=True)                

                with tab2: # Death
                    st.subheader('✔️ (패배한 경기) 포지션별 죽은 횟수')
                    st.caption(' 15분 전후로 어떤 포지션이 가장 많이 죽었는지 확인해보았습니다. 왁굳님의 경기 시간은 평균적으로 31분입니다. ')
                    with elements("death"):                
                            layout = [
                                        dashboard.Item("item1", 0, 0, 3, 2,isDraggable=True, isResizable=True ),
                                        dashboard.Item("item2", 3, 0, 3, 2,isDraggable=True, isResizable=True ),
                                        dashboard.Item("item3", 6, 0, 1, 2,isDraggable=True, isResizable=True ),

                                        ]
                            card_sx = {"background-color":"#0a0a0adb","borderRadius": "23px", "outline": "1px solid #242427",'text-align':'center'}

                            with dashboard.Grid(layout): # death_cnt
                                                            
                                mui.Card( # 15 이전 데스 집계
                                    mui.Typography(
                                            "Before 15 Death",variant="h5",sx={'mt':2}),                                  
                                    nivo.Pie( 
                                        data=death_cnt,
                                        margin={"top": 30, "right": 50, "bottom": 100, "left": 50 },
                                        innerRadius={0.5},
                                        padAngle={2},
                                        activeOuterRadiusOffset={8},
                                        colors=  {'scheme': 'greens'}, # 
                                        borderWidth={1},
                                        borderColor={
                                            "from": 'color',
                                            "modifiers": [
                                                [
                                                    'darker',
                                                    0.2,
                                                    'opacity',
                                                    0.6
                                                ]
                                            ]
                                        },
                                        enableArcLinkLabels=True,
                                        arcLinkLabelsSkipAngle={10},
                                        arcLinkLabelsTextColor="white",
                                        arcLinkLabelsThickness={0.5},
                                        arcLinkLabelsColor="white",
                                        arcLabelsSkipAngle={10},
                                        arcLabelsTextColor= "black",

                                        legends=[
                                            {
                                                "anchor": "bottom",
                                                "direction": "row",
                                                "translateX": 0,
                                                "translateY": 30,
                                                "itemWidth": 60,
                                                "itemsSpacing" : 5,
                                                "itemHeight": 10,
                                                "itemTextColor": "white",
                                                "symbolSize": 10,
                                                "symbolShape": "circle",
                                                "effects": [
                                                    {
                                                        "on": "hover",
                                                        "style": {
                                                            "itemTextColor": "white"
                                                        }
                                                    }
                                                ]
                                            }
                                        ],
                                        theme={
                                            # "background": "#0a0a0adb",
                                            "textColor": "black",
                                            "tooltip": {
                                                "container": {
                                                    "background": "#3a3c4a",
                                                    "color": "white",
                                                }
                                            }
                                        },
                                    )                                
                                                                            
                                    ,key="item1",sx=card_sx) 
                            
                                mui.Card( # 15 이후 데스 집계
                                    mui.Typography(
                                        "After 15 Death",variant= "h5",sx={'mt':2}
                                        ),
                                    nivo.Pie( 
                                        data=death_cnt_16,
                                        margin={"top": 30, "right": 50, "bottom": 100, "left": 50 },
                                        innerRadius={0.5},
                                        padAngle={2},
                                        activeOuterRadiusOffset={8},
                                        colors=  {'scheme': 'blues'}, # 
                                        borderWidth={1},
                                        borderColor={
                                            "from": 'color',
                                            "modifiers": [
                                                [
                                                    'darker',
                                                    0.2,
                                                    'opacity',
                                                    0.6
                                                ]
                                            ]
                                        },
                                        enableArcLinkLabels=True,
                                        arcLinkLabelsSkipAngle={10},
                                        arcLinkLabelsTextColor="white",
                                        arcLinkLabelsThickness={0.5},
                                        arcLinkLabelsColor="white",
                                        arcLabelsSkipAngle={10},
                                        arcLabelsTextColor= "black",

                                        legends=[
                                            {
                                                "anchor": "bottom",
                                                "direction": "row",
                                                "translateX": 0,
                                                "translateY": 30,
                                                "itemWidth": 60,
                                                "itemsSpacing" : 5,
                                                "itemHeight": 10,
                                                "itemTextColor": "white",
                                                "symbolSize": 10,
                                                "symbolShape": "circle",
                                                "effects": [
                                                    {
                                                        "on": "hover",
                                                        "style": {
                                                            "itemTextColor": "white"
                                                        }
                                                    }
                                                ]
                                            }
                                        ],
                                        theme={
                                            # "background": "#0a0a0adb",
                                            "textColor": "black",
                                            "tooltip": {
                                                "container": {
                                                    "background": "#3a3c4a",
                                                    "color": "white",
                                                }
                                            }
                                        },
                                    )                                
                                                                                                                                                                        
                                    ,key='item2',sx=card_sx)

                    
                    expander = st.expander("(평균) 포지션별 데스, 죽은 시간")

                    with expander:
                        stat = lose_static()
                        death_15 = wakteam_death_log[wakteam_death_log['timestamp'] < 16].groupby(['matchId','victimPosition']).agg(
                                        count = pd.NamedAgg(column = 'victimPosition', aggfunc='count')
                                        ).reset_index().sort_values(by='count',ascending=True)
                        death_16 = wakteam_death_log[wakteam_death_log['timestamp'] > 15].groupby(['matchId','victimPosition']).agg(
                                        count = pd.NamedAgg(column = 'victimPosition', aggfunc='count')
                                        ).reset_index().sort_values(by='count',ascending=True)



                        death_15 = death_15.groupby('victimPosition').agg(
                            before_15 = pd.NamedAgg(column = 'count', aggfunc='mean'),
                        ).round(1)

                        death_16 = death_16.groupby('victimPosition').agg(
                            after_15 = pd.NamedAgg(column = 'count', aggfunc='mean'),
                        ).round(1)

                        death_mean = pd.concat([death_15,death_16],axis= 1).reset_index()                       
                        death_mean['차이'] = death_mean['after_15'] - death_mean['before_15']

                        death_mean = pd.merge(death_mean, stat, on=['victimPosition'], how='inner').set_index(['victimPosition'])
                        st.dataframe(death_mean)                                

                    st.markdown(f'''
                                <div> \n 
                                #### 15분 이전                               
                                * 위 차트는 <strong> 포지션별 '죽은 횟수'</strong>를 집계한 결과입니다 (전체 합계)
                                * 라인전 동안 <span style="color:#74c476"> {death_cnt[4]['id']} , {death_cnt[3]['id']}</span> 포지션에서 상대적으로 많이 죽었으며  <strong style="color:#f7fcf5">{death_cnt[0]['id']}</strong>이 가장 적었습니다.
                                * 패배한 경기에서 왁굳님의 경우 라인전때 거의 죽지 않은 편이었습니다.
                                
                                </div>

                                <div> \n
                                #### 15분 이후
                                * 하지만, 패배한 경기중 평균적으로 오랫동안 <span style="color:gray">흑백화면</span>을 본 포지션은 <span style="color:#82b1ff">MIDDLE</span> 이었습니다. 
                                * 모든 포지션이 라인전 이후에 죽는 경우가 더 많았지만, <span style="color:#82b1ff">MIDDLE</span> 의 경우 특히 라인전 이후의 컨디션 차이가 있는 편입니다.                               
                                * 현재까지의 골드차이, 죽은횟수를 고려해보면 상대적으로 <strong> 바텀(원딜)</strong>이 유력해보입니다. 하지만 이정도 지표로는 아직 억울할 수 있습니다..\n
                                > death와 관련된 변수들을 좀 더 여러가지 주제로 집계 해보았는데요🤔.
                                    
                                ''',
                                unsafe_allow_html=True)
            
                with tab3: # Death detail
                    st.subheader('✔️ (패배한 경기) 누가 자꾸 짤리는거야?')
                    st.caption('''
                               * 우리팀중 누가 자꾸 짤리는걸까요? 특히 라인전 이후 솔로킬을 당한 포지션, 라인전 동안 정글에의해 가장 많이 당한 포지션, 가장 오랫동안 죽은 포지션은?  
                               * 라인전 솔로킬(합) , 정글갱(합), 흑백화면(평균) 
                               ''')

                    death_time = death_mean.reset_index()[['victimPosition','death_time']].sort_values(by=['death_time'],ascending=True).to_dict('records')

                    with elements("death_2"):                
                        layout = [
                                    dashboard.Item("item1", 0, 0, 2, 3,isDraggable=True, isResizable=True ),
                                    dashboard.Item("item2", 2, 0, 2, 3,isDraggable=True, isResizable=True ),
                                    dashboard.Item("item3", 4, 0, 2, 3,isDraggable=True, isResizable=True ),

                                    ]
                        
                        with dashboard.Grid(layout):
                            mui.Card(
                                children=[      
                                    mui.CardMedia( #paper
                                        sx={ "height": 90,
                                            "backgroundImage": f"linear-gradient(rgba(0, 0, 0, 0), rgba(0,0,0,1)),url(https://get.wallhere.com/photo/League-of-Legends-jungle-Terrain-screenshot-atmospheric-phenomenon-computer-wallpaper-284470.jpg)",
                                            # https://i.ibb.co/ngqJc66/image.jpg # https://i.ibb.co/fdNcMQP/pngegg-8
                                            # "margin": "10px 70px 0 70px"
                                              },
                                        
                                            ),
                                    mui.CardContent(
                                        sx={'padding':1}, # 설명
                                        children=[  
                                            mui.Typography(
                                                " 나는 솔로다",
                                                variant="h5",
                                                component="div"
                                            ),
                                            mui.Typography(
                                                "라인전 이후 가장 많이 솔로킬로 짤린 포지션은? "
                                                    ,
                                                variant="body2",
                                                color="text.secondary",
                                                sx={
                                                    "font-size": "12px"},
                                                
                                            )]
                                        ),


                                    mui.Box( 
                                        sx={
                                            "display": "flex",
                                            "gap": "20px",
                                            "padding": "0",
                                            "justify-content": "center",
                                        },
                                        children=[
                                            mui.Box( 
                                                sx={
                                                    "width" : "70px",
                                                    "display": "flex",
                                                    "flexDirection": "column",
                                                    "alignItems": "center",
                                                },
                                                children=[
                                                    mui.CardMedia(
                                                        sx={
                                                            "height": 60,
                                                            "width": 60,
                                                            "borderRadius": "10%",
                                                            "backgroundImage": f"url(https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-clash/global/default/assets/images/position-selector/positions/icon-position-{death_solo_16[4]['victimPosition'].lower()}.png)"
                                                        },
                                                    ),
                                                    mui.Typography(
                                                        f'{death_solo_16[4]["victimPosition"]}',
                                                        sx={"font-size": "30px"}
                                                    )
                                                ]
                                            ),


                                        ]
                                    ),

                                    nivo.Bar(
                                        data=death_solo_16,
                                        keys=["death"],  # 막대 그래프의 그룹을 구분하는 속성
                                        indexBy="victimPosition",  # x축에 표시할 속성

                                        margin={"top": 0, "right": 30, "bottom": 300, "left": 80},
                                        padding={0.4},
                                        layout="horizontal",

                                        valueScale={ "type" : 'linear' },
                                        indexScale={ "type": 'band', "round": 'true'},
                                        borderRadius={5},
                                        colors=['#459ae5'],                   

                                        innerRadius=0.3,
                                        padAngle=0.5,
                                        activeOuterRadiusOffset=8,
                                        enableGridY= False,
        
                                        # labelSkipWidth={},
                                        # labelSkipHeight={36},
                                        axisBottom=False,
                                        theme={
                                                # "background": "black",
                                                "textColor": "white",
                                                "tooltip": {
                                                    "container": {
                                                        "background": "#3a3c4a",
                                                        "color": "white",
                                                    }
                                                }
                                            }                         
                                        ),
                            
                                ] , key="item1",elevation=0 , sx=card_sx) #  sx = {"background-color":"#0a0a0adb","borderRadius": "23px"}
        
                                                                    
                            mui.Card(
                                children=[      
                                    mui.CardMedia( # 챔피언paper
                                        sx={ "height": 90,
                                            "backgroundImage": f"linear-gradient(rgba(0, 0, 0, 0), rgba(0,0,0,1)),url(https://get.wallhere.com/photo/League-of-Legends-jungle-Terrain-screenshot-atmospheric-phenomenon-computer-wallpaper-284470.jpg)",
                                            "backgroundPosition": "top"
                                            }, # https://i.ibb.co/5jkFtWj/pngwing-com-2.png
                                        
                                            ),
                                    mui.CardContent( # 설명
                                        sx={'padding':1},
                                        children=[  
                                            mui.Typography(
                                                " 맵리딩 수준",
                                                variant="h5",
                                                component="div"
                                            ),
                                            mui.Typography(
                                                "라인전 동안 상대 정글에게 가장 많이 당한 포지션? ",
                                                variant="body2",
                                                color="text.secondary",
                                                sx={
                                                    "font-size": "12px"},
                                                
                                            )]
                                        ),


                                    mui.Box( # score
                                        sx={
                                            "display": "flex",
                                            "gap": "20px",
                                            "padding": "0",
                                            "justify-content": "center",
                                        },
                                        children=[

                                            mui.Box( 
                                                sx={
                                                    "width" : "70px",
                                                    "display": "flex",
                                                    "flexDirection": "column",
                                                    "alignItems": "center",
                                                },
                                                children=[
                                                    mui.CardMedia(
                                                        sx={
                                                            "height": 60,
                                                            "width": 60,
                                                            "borderRadius": "10%",
                                                            "backgroundImage": f"url(https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-clash/global/default/assets/images/position-selector/positions/icon-position-{jungle_15[4]['victimPosition'].lower()}.png)"
                                                        },
                                                    ),
                                                    mui.Typography(
                                                        f'{jungle_15[4]["victimPosition"]}',
                                                        sx={"font-size": "30px"}
                                                    )
                                                ]
                                            ),


                                        ]
                                    ),

                                    nivo.Bar(
                                        data=jungle_15,
                                        keys=["cnt"],  # 막대 그래프의 그룹을 구분하는 속성
                                        indexBy="victimPosition",  # x축에 표시할 속성

                                        margin={"top": 0, "right": 30, "bottom": 300, "left": 80},
                                        padding={0.4},
                                        layout="horizontal",

                                        valueScale={ "type" : 'linear' },
                                        indexScale={ "type": 'band', "round": 'true'},
                                        borderRadius={5},
                                        colors={'scheme':'accent'},                   

                                        innerRadius=0.3,
                                        padAngle=0.5,
                                        activeOuterRadiusOffset=8,
                                        enableGridY= False,
        
                                        # labelSkipWidth={},
                                        # labelSkipHeight={36},
                                        axisBottom=False,
                                        theme={
                                                # "background": "black",
                                                "textColor": "white",
                                                "tooltip": {
                                                    "container": {
                                                        "background": "#3a3c4a",
                                                        "color": "white",
                                                    }
                                                }
                                            }                         
                                        ),
                            
                                ]                                
                                
                                , key='item2', elevation=0, sx=card_sx)


                            mui.Card(
                                children=[      
                                    mui.CardMedia( # 챔피언paper
                                        sx={ "height": 90,
                                            "backgroundImage": f"linear-gradient(rgba(0, 0, 0, 0), rgba(0,0,0,1)),url(https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Nocturne_5.jpg)",
                                            "backgroundPosition": "top"
                                            },                                        
                                        ),
                                  
                                    mui.CardContent( # 설명
                                        sx={'padding':1},
                                        children=[  
                                            mui.Typography(
                                                "자체 녹턴궁",
                                                variant="h5",
                                                component="div",
                                            ),
                                            mui.Typography(
                                                '''흑백화면을 가장 오래본 포지션은? (단위:초) '''
                                                    ,
                                                variant="body2",
                                                color="text.secondary",
                                                sx={
                                                    "font-size": "12px"},
                                                
                                            )]
                                        ),

                                    mui.Box( # score
                                        sx={
                                            "display": "flex",
                                            "gap": "20px",
                                            "padding": "0",
                                            "justify-content": "center",
                                        },
                                        children=[

                                            mui.Box( 
                                                sx={
                                                    "width" : "70px",
                                                    "display": "flex",
                                                    "flexDirection": "column",
                                                    "alignItems": "center",
                                                },
                                                children=[
                                                    mui.CardMedia(
                                                        sx={
                                                            "height": 60,
                                                            "width": 60,
                                                            "borderRadius": "10%",
                                                            "backgroundImage": f"url(https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-clash/global/default/assets/images/position-selector/positions/icon-position-{death_time[4]['victimPosition'].lower()}.png)"
                                                        },
                                                    ),
                                                    mui.Typography(
                                                        f'{death_time[4]["victimPosition"]}',
                                                        sx={"font-size": "30px"}
                                                    )
                                                ]
                                            ),


                                        ]
                                    ),

                                    nivo.Bar(
                                        data=death_time,
                                        keys=["death_time"],  # 막대 그래프의 그룹을 구분하는 속성
                                        indexBy="victimPosition",  # x축에 표시할 속성

                                        margin={"top": 0, "right": 30, "bottom": 300, "left": 80},
                                        padding={0.4},
                                        layout="horizontal",

                                        valueScale={ "type" : 'linear' },
                                        indexScale={ "type": 'band', "round": 'true'},
                                        borderRadius={5},
                                        colors= ['#c98244'],
                                            #{'scheme':'accent'},                   

                                        innerRadius=0.3,
                                        padAngle=0.5,
                                        activeOuterRadiusOffset=8,
                                        enableGridY= False,
        
                                        # labelSkipWidth={},
                                        # labelSkipHeight={36},
                                        axisBottom=False,
                                        theme={
                                                # "background": "black",
                                                "textColor": "white",
                                                "tooltip": {
                                                    "container": {
                                                        "background": "#3a3c4a",
                                                        "color": "white",
                                                    }
                                                }
                                            }                         
                                        ),
                                                        


                                ] , key="item3",elevation=0 , sx=card_sx) #  sx = {"background-color":"#0a0a0adb","borderRadius": "23px"}
    


                    # expander = st.expander("주로 어디서 죽었나?")
                    # with expander:
                    #     col1,col2,col3 =st.columns([1,1,1])
                    #     with col1:
                    #         st.write('''##### ✔️ 솔로킬을 당한 위치 (원딜) ''')
                    #         death_spot(bottom_solo_death)

                    #         st.markdown('''
                    #                     <div> \n                            
                    #                      * 라인전이후 가장 많이 솔로킬로 짤린 포지션은 <span style="color:#82b1ff">BOTTOM</span>.
                    #                      *                                         
                    #                     </div>
                                        
                    #                     ''' ,unsafe_allow_html=True)

                    #     with col2:
                    #         st.write('''##### ✔️ 정글에 의한 죽음 ''' )
                    #         death_spot_sc(jungle_death_15,'Greens')
 
                    #         st.markdown(''' 
                    #                     <div> \n
                    #                     * 라인전동안 가장 많이 정글에게 당한 포지션은  <span style="color:#74c476">JUNGLE</span>. 
                    #                     * 특히, <span style="color:#74c476"> 바텀에서의 역갱, 정글링 싸움</span>으로 인한 death가 가장 많았습니다.
                    #                     </div>
                    #                     ''', unsafe_allow_html = True)
                    #     with col3:
                    #         st.write('''##### ✔️ 흑백화면을 가장 오래본 포지션 ''')

                    #         wakgood_death.loc[:, 'lane'] = wakgood_death.apply(lambda row: calculate_lane(row['position']['x'], row['position']['y']), axis=1)
                    #         groupby_lane = wakgood_death.groupby(['lane']).agg(count = pd.NamedAgg(column='lane',aggfunc ='count')).reset_index()
                    #         total_count = groupby_lane['count'].sum()
                    #         groupby_lane['ratio'] = (groupby_lane['count'] / total_count) * 100

                    #         groupby_lane = groupby_lane.sort_values(by=['ratio'],ascending=False)

                    #         death_spot_sc(wakgood_death,'Reds')
                    #         st.markdown('''
                    #                      <div> \n
                    #                     * 왁굳님의 경우 상대적으로 후반부에 짤리는 경우가 특히 많았습니다.

                    #                     </div>
                    #                     ''', unsafe_allow_html=True)

                    #         st.dataframe(groupby_lane)





                with tab4:
                    st.subheader('☠️ 합류하는데 차이가 있을까?')
                    st.write(''' 
                                * 가장 많이 일어난 정글지형에서 일어난 전투 비교 
                            ''')
                    
                    
# ------------------------------------------------------------------ DUO CARD ----------------------------------------------------------------------------------#                                                      

        # st.divider()
        # with st.container():
        # # 듀오 승률 계산
        #     @st.cache_data
        #     def duo_win(match_info,summoner_name):

        #         win = match_info[match_info['summonerName'] == summoner_name]['win_kr'].value_counts() #['championName']
        #         c_win = win[0].astype(str)
        #         c_lose = win[1].astype(str)

        #         duo_ratio = [
        #             {"id": "Wins", "label": "Wins", "value": c_win},
        #             {"id": "Losses", "label": "Losses", "value": c_lose}
        #         ]
        #         return duo_ratio

        #     chun_win_lose = duo_win(match_info,'돈까스')
        #     chun_radar,chun_vs_df = radar_chart(match_info, '돈까스', 'JUNGLE') # 508

        #     nor_win_lose = duo_win(match_info,'The Nollan')
        #     nol_radar,nor_vs_df = radar_chart(match_info,'The Nollan','JUNGLE') # 6473


        #     # 듀오 인포
        #     chun_id = 'MP9q12SlMt7EFmMxbd1IoqJsOPGp9lMA6KTjWBuzPYnn7Q' 
        #     noll_id = '4f9H3ie0k-21eW1RiocOqzN_YQNn5kTL-wIhrHb_-GIxKQ'

        #     chun = get_rank_info (chun_id, api_key)
        #     noll = get_rank_info (noll_id, api_key)

        #     chun_tier = chun[0]['tier']
        #     noll_tier = noll[0]['tier']
            

        #     # 듀오경기id (정글인 경우만)
        #     n = champion_info[(champion_info['summonerName'] == 'The Nollan')&(champion_info['teamPosition'] =='JUNGLE')]['matchId'].tolist()
        #     c = champion_info[(champion_info['summonerName'] =='돈까스') & (champion_info['teamPosition'] =='JUNGLE')]['matchId'].tolist()



        #     # 듀오의 어시스트 정보
        #     nol_assist = nol_kill_log[nol_kill_log['assistingParticipantIds'].apply(lambda ids: 'The Nollan' in ids if isinstance(ids, list) else False)]

        #     chun_assist = chun_kill_log[chun_kill_log['assistingParticipantIds'].apply(lambda ids: '돈까스' in ids if isinstance(ids, list) else False)]


        #     # 놀란과 함께한 경기의 전체킬
        #     nol_wak_kill = match_info[(match_info['matchId'].isin(n)) & (match_info['summonerName']== summoner_name)]['kills'].sum()
        #     chun_wak_kill = match_info[(match_info['matchId'].isin(c)) & (match_info['summonerName']== summoner_name)]['kills'].sum()

        #     # 킬관여율
        #     nol_kill_rate = round(((len(nol_assist))/(nol_wak_kill))*100,1)
        #     chun_kill_rate = round(((len(chun_assist))/(chun_wak_kill))*100,1)


        #     # 어떻게 표현?
        #     # 승률, 듀오경기 횟수, 놀란킬 기여 n개, (ex) n개의 킬 중에서 x개의 킬이 놀란님과 함께 만들었습니다.



        # with st.container():
        #     st.subheader('🤡 DUO SCORE - 누가 충신인가')
        #     st.write(''' 우왁굳님의 최근 50경기중 듀오를 진행한 경기를 바탕으로 듀오점수를 매겨보았습니다. 10경기 이상 진행한 듀오의 기준입니다.                  

        #               ''')
        #     st.caption(''' 
        #                * 천양님의 경우 우왁굳+돈까스 합산한 결과입니다.
        #                * 천양, 놀란님 모두 JUNGLE 포지션이었던 경기를 기준으로 집계 되었습니다. 
        #                * 정글링 점수? 오브젝트, 드래곤, 바론, 상대정글을 카정한 횟수에 관한 지표입니다. 
        #                ''')




        #     with elements("DUO"):                
        #         layout = [
        #                     dashboard.Item("item1", 0, 0, 3, 3,isDraggable=True, isResizable=True ),
        #                     dashboard.Item("item2", 3, 0, 2, 1,isDraggable=True, isResizable=True ),
        #                     dashboard.Item("item2_1", 3, 3, 2, 2,isDraggable=True, isResizable=True ),
                                                        
        #                     dashboard.Item("item3", 6, 0, 3, 3,isDraggable=True, isResizable=True ),
        #                     dashboard.Item("item4", 9, 0, 2, 1,isDraggable=True, isResizable=True ),
        #                     dashboard.Item("item5", 9, 3, 2, 1,isDraggable=True, isResizable=True ),

        #                     ]
                
        #         with dashboard.Grid(layout):
        #                 mui.Card( # 천양
        #                     children = [
        #                         mui.CardContent(                                 
        #                             sx={
        #                                 "display": "flex",
        #                                 "align-items": "center",
        #                                 "text-align":"center",
        #                                 "padding": "0 8px 0 8px",
        #                                 "gap" : 1                                        
        #                             },                                    
                                    
        #                             children = [
        #                                 mui.CardMedia( 
        #                                     sx={
        #                                         "height": 70,
        #                                         "width": 70,
        #                                         "borderRadius": "10%",
        #                                         "backgroundImage": f"url(http://ddragon.leagueoflegends.com/cdn/14.1.1/img/profileicon/508.png)",  
        #                                     },
        #                                 ),
                                     
        #                                 mui.Divider(orientation="vertical",sx={"height": "100px"}), 
                                        
        #                                 mui.CardContent(
        #                                     children=[
        #                                         mui.Typography(
        #                                                 "Most Lane", variant="body2",sx={'text-align':'center','mt':0}),                                                                                           
        #                                         mui.CardMedia( 
        #                                             sx={
        #                                                 "height": 70,
        #                                                 "width": 70,
        #                                                 "backgroundImage": f"url(https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-clash/global/default/assets/images/position-selector/positions/icon-position-jungle.png)",
        #                                                 "position":'center'
        #                                             },
        #                                         )], sx={'paddig':'0'}            
        #                                 ),


        #                                 mui.Divider(orientation="vertical",sx={"height": "100px"}), 

        #                                 mui.CardContent(
        #                                     children=[
        #                                     mui.Typography(
        #                                             "TIER", variant="body2",sx={'text-align':'center'}),                                                                                           

        #                                     mui.CardMedia( 
        #                                         sx={
        #                                             "height":70,
        #                                             "width":100,                                     
        #                                             "backgroundImage": f"url(https://i.ibb.co/WD5p2cF/Rank-Bronze.png)",  
        #                                             },
        #                                         )
        #                                     ] ,sx={'padding':0},
        #                                     )
        #                                 ]
        #                             ),                                 

        #                             mui.Divider(sx={"height": "1px"}), # orientation="vertical",
                                    
        #                             nivo.Radar(
        #                                 data=chun_radar,
        #                                 keys=['돈까스','상대라이너'],
        #                                 colors={'scheme': 'accent' },
        #                                 indexBy="var",
        #                                 valueFormat=">-.2f",
        #                                 maxValue={1.0},
        #                                 margin={ "top": 50, "right": 60, "bottom": 110, "left": 80 },
        #                                 borderColor={ "from": "color" },
        #                                 gridShape="linear",
        #                                 gridLevels={3},
        #                                 gridLabelOffset=15,
        #                                 dotSize=5,
        #                                 dotColor={ "theme": "background" },
        #                                 dotBorderWidth=1,
        #                                 motionConfig="wobbly",
        #                                 legends=[
        #                                     {
        #                                         "anchor": "top-left",
        #                                         "direction": "column",
        #                                         "translateX": -70,
        #                                         "translateY": -30,
        #                                         "itemWidth": 100,
        #                                         "itemHeight": 20,
        #                                         "itemTextColor": "white",
        #                                         "symbolSize": 15,
        #                                         "symbolShape": "circle",
        #                                         "effects": [
        #                                             {
        #                                                 "on": "hover",
        #                                                 "style": {
        #                                                     "itemTextColor": "white"
        #                                                 }
        #                                             }
        #                                         ]
        #                                     }
        #                                 ],
        #                                 theme={
        #                                     "textColor": "white",
        #                                     "tooltip": {
        #                                         "container": {
        #                                             "background": "#262730",
        #                                             "color": "white",
        #                                         }
        #                                     }
        #                                 }
        #                             ),
        #                     ]
        #                     ,key="item1",sx=card_sx)

        #                 mui.Card( # 천양 승률
        #                     children=[
        #                         mui.Typography(
        #                                 "DUO WIN",variant="body2",sx={'background-color':'#181819','text-align':'center'}),  
                                
        #                         nivo.Pie( 
        #                             data=chun_win_lose,
        #                             margin={"top":10, "right": 20, "bottom": 50, "left": 20 },
        #                             innerRadius={0.5},
        #                             padAngle={2},
        #                             activeOuterRadiusOffset={8},
        #                             colors=['#459ae5', '#ed4141'],                   
        #                             borderWidth={1},
        #                             borderColor={
        #                                 "from": 'color',
        #                                 "modifiers": [
        #                                     [
        #                                         'darker',
        #                                         0.2,
        #                                         'opacity',
        #                                         0.6
        #                                     ]
        #                                 ]
        #                             },
        #                             enableArcLinkLabels=False,
        #                             arcLinkLabelsSkipAngle={10},
        #                             arcLinkLabelsTextColor="white",
        #                             arcLinkLabelsThickness={0},
        #                             arcLinkLabelsColor={ "from": 'color', "modifiers": [] },
        #                             arcLabelsSkipAngle={10},
        #                             arcLabelsTextColor={ "theme": 'background' },
        #                             legends=[
        #                                 {
        #                                     "anchor": "bottom",
        #                                     "direction": "row",
        #                                     "translateX": 0,
        #                                     "translateY": 20,
        #                                     "itemWidth": 50,
        #                                     "itemsSpacing" : 5,
        #                                     "itemHeight": 20,
        #                                     "itemTextColor": "white",
        #                                     "symbolSize": 7,
        #                                     "symbolShape": "circle",
        #                                     "effects": [
        #                                         {
        #                                             "on": "hover",
        #                                             "style": {
        #                                                 "itemTextColor": "white"
        #                                             }
        #                                         }
        #                                     ]
        #                                 }
        #                             ],
        #                             theme={
        #                                 "background": "#181819",
        #                                 "textColor": "white",
        #                                 "tooltip": {
        #                                     "container": {
        #                                         "background": "#181819",
        #                                         "color": "white",
        #                                     }
        #                                 }
        #                             },
        #                         ),
                                                    
        #                         mui.Typography(
        #                             "기여도",
        #                             variant="h4",
        #                             ),                                
        #                         ]
                                 
                                 
        #                         ,key="item2", sx=card_sx)

        #                 mui.Card(
                            
        #                         mui.CardContent( # 설명
        #                             children=[  
        #                                 mui.Typography(
        #                                     " 킬 관여율 ",
        #                                     variant="h5",
        #                                     component="div"
        #                                 ),
        #                                 mui.Typography(
        #                                     f''' 우왁굳님의 kill {chun_wak_kill}개 중에서,
        #                                         {len(chun_assist)}번의 천양 어시스트를 받았어요!''',
        #                                     variant="body2",
        #                                     color="text.secondary",
        #                                     sx={"mb":2,
        #                                         "font-size": "12px"},
        #                                 ),

        #                                 mui.Typography(
        #                                     f'{chun_kill_rate}',
        #                                     variant='h3',
        #                                     # sx={"font-size": "30px"}
                                                                                    
        #                                 )]
        #                             )
                                                            
                            
        #                     ,key='item2_1',sx=card_sx)

                        

        #                 mui.Card( # 놀란
        #                     children = [
        #                         mui.CardContent(                                 
        #                             sx={
        #                                 "display": "flex",
        #                                 "align-items": "center",
        #                                 "text-align":"center",
        #                                 "padding": "0 8px 0 8px",
        #                                 "gap" : 1                                        
        #                             },                                    
                                    
        #                             children = [
        #                                 mui.CardMedia( 
        #                                     sx={
        #                                         "height": 80,
        #                                         "width": 80,
        #                                         "borderRadius": "10%",
        #                                         "backgroundImage": f"url(http://ddragon.leagueoflegends.com/cdn/14.1.1/img/profileicon/6473.png)",  
        #                                     },
        #                                 ),
        #                                 mui.Divider(orientation="vertical",sx={"height": "100px"}), 

        #                                 mui.CardMedia( 
        #                                     sx={
        #                                         "height": 80,
        #                                         "width": 80,
        #                                         "backgroundImage": f"url(https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-clash/global/default/assets/images/position-selector/positions/icon-position-jungle.png)"
        #                                     },
        #                                 ),               

        #                                 mui.Divider(orientation="vertical",sx={"height": "100px"}), 

        #                                 mui.CardMedia( 
        #                                         sx={
        #                                             "height":"90px",
        #                                             "width":"170px",                                     
        #                                             "backgroundImage": f"url(https://i.ibb.co/cCdBMhk/Rank-Silver.png)",  
        #                                             },
        #                                         ),
        #                                     ]
        #                                 ),                                 

        #                             mui.Divider(sx={"height": "1px"}), # orientation="vertical",
                                    
        #                             nivo.Radar(
        #                                 data=nol_radar,
        #                                 keys=['The Nollan','상대라이너'],
        #                                 colors={'scheme': 'accent' },
        #                                 indexBy="var",
        #                                 valueFormat=">-.2f",
        #                                 maxValue={1.0},
        #                                 margin={ "top": 50, "right": 60, "bottom": 110, "left": 80 },
        #                                 borderColor={ "from": "color" },
        #                                 gridShape="linear",
        #                                 gridLevels={3},
        #                                 gridLabelOffset=15,
        #                                 dotSize=5,
        #                                 dotColor={ "theme": "background" },
        #                                 dotBorderWidth=1,
        #                                 motionConfig="wobbly",
        #                                 legends=[
        #                                     {
        #                                         "anchor": "top-left",
        #                                         "direction": "column",
        #                                         "translateX": -70,
        #                                         "translateY": -30,
        #                                         "itemWidth": 100,
        #                                         "itemHeight": 20,
        #                                         "itemTextColor": "white",
        #                                         "symbolSize": 15,
        #                                         "symbolShape": "circle",
        #                                         "effects": [
        #                                             {
        #                                                 "on": "hover",
        #                                                 "style": {
        #                                                     "itemTextColor": "white"
        #                                                 }
        #                                             }
        #                                         ]
        #                                     }
        #                                 ],
        #                                 theme={
        #                                     "textColor": "white",
        #                                     "tooltip": {
        #                                         "container": {
        #                                             "background": "#262730",
        #                                             "color": "white",
        #                                         }
        #                                     }
        #                                 }
        #                             ),
        #                     ]
        #                     ,key="item3",sx=card_sx)

        #                 mui.Card( # 놀란 승률
        #                     children=[
        #                         mui.Typography(
        #                                 "DUO WIN",variant="body2",sx={'background-color':'#181819','text-align':'center'}),  
                                
        #                         nivo.Pie( 
        #                             data=nor_win_lose,
        #                             margin={"top":10, "right": 20, "bottom": 50, "left": 20 },
        #                             innerRadius={0.5},
        #                             padAngle={2},
        #                             activeOuterRadiusOffset={8},
        #                             colors=['#459ae5', '#ed4141'],                   
        #                             borderWidth={1},
        #                             borderColor={
        #                                 "from": 'color',
        #                                 "modifiers": [
        #                                     [
        #                                         'darker',
        #                                         0.2,
        #                                         'opacity',
        #                                         0.6
        #                                     ]
        #                                 ]
        #                             },
        #                             enableArcLinkLabels=False,
        #                             arcLinkLabelsSkipAngle={10},
        #                             arcLinkLabelsTextColor="white",
        #                             arcLinkLabelsThickness={0},
        #                             arcLinkLabelsColor={ "from": 'color', "modifiers": [] },
        #                             arcLabelsSkipAngle={10},
        #                             arcLabelsTextColor={ "theme": 'background' },
        #                             legends=[
        #                                 {
        #                                     "anchor": "bottom",
        #                                     "direction": "row",
        #                                     "translateX": 0,
        #                                     "translateY": 20,
        #                                     "itemWidth": 50,
        #                                     "itemsSpacing" : 5,
        #                                     "itemHeight": 20,
        #                                     "itemTextColor": "white",
        #                                     "symbolSize": 7,
        #                                     "symbolShape": "circle",
        #                                     "effects": [
        #                                         {
        #                                             "on": "hover",
        #                                             "style": {
        #                                                 "itemTextColor": "white"
        #                                             }
        #                                         }
        #                                     ]
        #                                 }
        #                             ],
        #                             theme={
        #                                 "background": "#181819",
        #                                 "textColor": "white",
        #                                 "tooltip": {
        #                                     "container": {
        #                                         "background": "#181819",
        #                                         "color": "white",
        #                                     }
        #                                 }
        #                             },
        #                         ),
                                                    
        #                         mui.Typography(
        #                             "기여도",
        #                             variant="h4",
        #                             ),                                
        #                         ]
                                 
                                 
        #                         ,key="item4", sx=card_sx)

        #                 mui.Card(
                            
        #                         mui.CardContent( # 설명
        #                             children=[  
        #                                 mui.Typography(
        #                                     " 킬 관여율 ",
        #                                     variant="h5",
        #                                     component="div"
        #                                 ),
        #                                 mui.Typography(
        #                                     f''' 우왁굳님의 KILL {nol_wak_kill}번중에서
        #                                         {len(nol_assist)}번의 놀란 어시스트를 받았어요!''',
        #                                     variant="body2",
        #                                     color="text.secondary",
        #                                     sx={"mb":2,
        #                                         "font-size": "12px"},
        #                                 ),

        #                                 mui.Typography(
        #                                     f'{chun_kill_rate}',
        #                                     variant='h3',
        #                                     # sx={"font-size": "30px"}
                                                                                    
        #                                 )]
        #                             )
                                                            
                            
        #                     ,key='item5',sx=card_sx)




# ------------------------------------------------------------- 소환사 성장 지표 ---------------------------------------------------------------------------#
        st.divider()

        # wak_df = match_info[match_info['puuid'] == puuid]['matchId'].unique()
        # st.write(len(wak_df))

        with st.container():
            st.header('📈 오늘의 나는.. 어제의 나와 다르다.')
            st.caption('''
                       * 최근 25경기와 과거 25경기, 그리고 언젠가 매치에서 만날 페이커님과 비교해보았어요
                       * 페이커님의 경우 최근 34경기의 (미드포지션) 기준이기 때문에 비교가 무의미할 수 있습니다. (*2024-01-26 기준 데이터)
                       ''')

            col1,col2 = st.columns([2,1])
            with col1:
                @st.cache_data
                def wak_indicator(match_info,summoner_name):
                    wak = match_info[match_info['summonerName'] == summoner_name]
                    wak['totalTimeSpentDead'] = wak['totalTimeSpentDead'] / 60 
                    
                    wak_recent = wak.head(25) # 최근 25경기
                    wak_befor = wak.tail(25)

                    recent_matchid= wak_recent['matchId'].tolist()
                    befor_matchid= wak_befor['matchId'].tolist()

                    # 기본지표
                    indicators = ['totalCS10Minutes','totalTimeSpentDead','visionScore','wardTakedowns','controlWardsPlaced','soloKills','kda','totalDamageDealtToChampions','damageDealtToObjectives','multikills']
                    kr_col = ['10분CS','죽은시간','시야점수','와드제거','제어와드설치','솔로킬','kda','챔피언딜량','오브젝트','멀티킬']

                    wak_recent_static = wak_recent[indicators]
                    wak_recent_static.columns = kr_col            
                    wak_recent_static = wak_recent_static.mean().rename('현재의 나')


                    wak_befor_static = wak_befor[indicators]
                    wak_befor_static.columns = kr_col            
                    wak_befor_static = wak_befor_static.mean().rename('과거의 나')

                                
                    result = pd.concat([wak_recent_static, wak_befor_static], keys=['현재의 나', '과거의 나'], axis=1).reset_index().rename(columns={'index': 'col'})
                    result['현재의 나'] = result['현재의 나'].round(2)
                    result['과거의 나'] = result['과거의 나'].round(2)

                    return result,recent_matchid,befor_matchid

                result,recent_matchid,befor_matchid = wak_indicator(match_info,summoner_name)


                @st.cache_data
                def get_death_stats(data, match_ids, summoner_name, timestamp_threshold=16, solo_death=False, jungle_death=False):
                    filters = (data['matchId'].isin(match_ids)) & (data['summonerName_x'] == summoner_name) & (data['timestamp'] < timestamp_threshold)

                    if solo_death:
                        filters &= data['assistingParticipantIds'].isna()

                    if jungle_death:
                        filters &= ((data['killerPosition'] == 'JUNGLE') | (data['assistingParticipantIds'].apply(lambda x: 'JUNGLE' in x if isinstance(x, list) else False)))

                    return len(data[filters])



                # 솔로데스
                wak_solo_death_before = get_death_stats(wakteam_death_log, befor_matchid, '메시아빠우왁굳', solo_death=True)
                wak_solo_death_recent = get_death_stats(wakteam_death_log, recent_matchid, '메시아빠우왁굳', solo_death=True)
                

                # 15분 이전 킬을 당하는 횟수 집계
                wak_death_before = get_death_stats(wakteam_death_log, befor_matchid, '메시아빠우왁굳')
                wak_death_recent = get_death_stats(wakteam_death_log, recent_matchid, '메시아빠우왁굳')

                # 15분 이전 정글갱에 의한 데스
                wak_jungle_death_before = get_death_stats(wakteam_death_log, befor_matchid, '메시아빠우왁굳', jungle_death=True)
                wak_jungle_death_recent = get_death_stats(wakteam_death_log, recent_matchid, '메시아빠우왁굳', jungle_death=True)

                new_row = pd.DataFrame({'col': ['death_15'], '과거의 나': [wak_death_before], '현재의 나': [wak_death_recent],
                                        })

                # faker 데이터
                data_values = [81.82, 2.1, 28.65, 5.65, 3.44, 1.68, 4.39, 29217.24, 11825.41, 0.85]
                # DataFrame 생성
                faker_df = pd.DataFrame({'faker': data_values})
                wak_data = pd.concat([result, faker_df],axis = 1)
                # wak_data = pd.concat([wak_data, new_row])



                vision_value = ["제어와드설치", "와드제거","시야점수"]    
                attack_value = ["솔로킬","멀티킬" ,"kda","죽은시간"] 
                deatl_value = ["챔피언딜량","오브젝트"]
                gold_value = ["10분CS"]

                vision = wak_data[wak_data['col'].isin(vision_value)]
                attack = wak_data[wak_data['col'].isin(attack_value)]
                dealt = wak_data[wak_data['col'].isin(deatl_value)]
                gold = wak_data[wak_data['col'].isin(gold_value)]

                # to json
                nivo_bar_vision = vision.to_dict('records')
                nivo_bar_attack = attack.to_dict('records')
                nivo_bar_dealt = dealt.to_dict('records')
                nivo_bar_gold = gold.to_dict('records')


                # 
                iron_vision = round(match_info['controlWardsPlaced'].mean(),1)


                with elements("wak_indicator_attack"):                
                    layout = [
                                dashboard.Item("item1", 0, 0, 6, 2,isDraggable=True, isResizable=True ),
                                ]
                    
                    with dashboard.Grid(layout):
                        st.subheader('''📊 공격지표''')
                        st.markdown(''' ##### " 날카롭게 성장중인 슬로우 스타터 " ''')
                        mui.Card(
                            nivo.Bar(
                                data=nivo_bar_attack,
                                keys=["faker","현재의 나","과거의 나"],  # 막대 그래프의 그룹을 구분하는 속성
                                indexBy="col",  # x축에 표시할 속성

                                margin={"top": 10, "right": 50, "bottom": 10, "left": 90},
                                padding={0.2},
                                layout="horizontal",
                                groupMode="grouped",

                                valueScale={ "type" : 'linear' },
                                indexScale={ "type": 'band', "round": 'true'},
                                borderRadius={5},
                                colors=['#459ae5','#a1d99b', '#ada9a9eb'],                   
                                # colors=[], # {'scheme': 'nivo' }

                                innerRadius=0.3,
                                padAngle=0.5,
                                activeOuterRadiusOffset=8,
                                enableGridY= False,

                                labelSkipWidth={20},
                                axisBottom=False,
                                theme={
                                        # "background": "black",
                                        "textColor": "white",
                                        "tooltip": {
                                            "container": {
                                                "background": "#3a3c4a",
                                                "color": "white",
                                            }
                                        }
                                    },                         
                                ) ,

                            mui.Divider(orientation="vertical"),
                            
                            nivo.Bar(
                            data=nivo_bar_dealt,
                            keys=["faker","현재의 나","과거의 나"],  # 막대 그래프의 그룹을 구분하는 속성
                            indexBy="col",  # x축에 표시할 속성

                            margin={"top": 10, "right": 50, "bottom": 10, "left": 90},
                            padding={0.4},
                            layout="horizontal",
                            groupMode="grouped",

                            valueScale={ "type" : 'linear' },
                            indexScale={ "type": 'band', "round": 'true'},
                            borderRadius={5},
                            colors=['#459ae5','#a1d99b', '#ada9a9eb'],                   
                            # colors=[], # {'scheme': 'nivo' }

                            innerRadius=0.3,
                            padAngle=0.5,
                            activeOuterRadiusOffset=8,
                            enableGridY= False,
                            legends=[
                                    {
                                        'dataFrom': 'keys',
                                        'anchor': 'top-right',
                                        'direction': 'column',
                                        'translateX': 40,
                                        'translateY': 30,
                                        'itemsSpacing': 0,
                                        'itemWidth': 80,
                                        'itemHeight': 20,
                                        'itemDirection': 'left-to-right',
                                        'itemOpacity': 0.8,
                                        'symbolSize': 15,
                                        'effects': [
                                            {
                                                'on': 'hover',
                                                'style': {
                                                    'itemOpacity': 1
                                                }
                                            }
                                        ]
                                    }
                                ],
                            labelSkipWidth={20},
                            # labelSkipHeight={36},
                            axisBottom=False,
                            theme={
                                    # "background": "black",
                                    "textColor": "white",
                                    "tooltip": {
                                        "container": {
                                            "background": "#3a3c4a",
                                            "color": "white",
                                        }
                                    }
                                },                         
                            ) 
 

                        ,key='item1',sx={'display':'flex',"background-color":"#0a0a0adb","borderRadius": "20px", "outline": "1px solid #31323b"})


                st.markdown('''                                
                                * 가끔 답답한 모습들이 보여지긴 하지만, :orange[놀랍게도 거의 모든 지표가 성장하고 있는] 슬로우 스타터 "Fe이커" 우왁굳의 모습을 볼 수 있었습니다. 
                                * 준수한 'KDA' + 의외로 자주 등장하는 '멀티킬(더블킬 이상)'
                                * 특히, 흑백화면을 보는 시간(death)이 줄어들고, 우왁굳의 안정적인 공격 모먼트가 과거에 비해 자주 나오는것을 볼 수 있습니다.                                                                       
                            ''')


            with col2:
                st.subheader('🤡 요즘 폼이 좋은 챔피언 (3판이상)')
                st.caption('''
                           * 공격지표, 시간대비 챔피언 딜량, CS, 타워피해량 등을 표준화해서 점수 산출.
                           ''')
                
                # 3판이상 진행한 챔피언... 
                df = champ_static[champ_static['champion_count']>2][['championName','soloKills_sum','multiKills_sum','visionScore_mean', 'longestTimeSpentLiving',
                                                                     'totalCS10Minutes_mean','damagePerMinute_mean','damageDealtToBuildings_mean',
                                                                     'damageDealtToObjectives_mean','kda_mean','win_rate']]

                scaler = MinMaxScaler()
                scaled_values = scaler.fit_transform(df.iloc[:, 1:])
                scaled_df = pd.DataFrame(scaled_values, columns=df.columns[1:])
                scaled_df['sum_scaled'] = round(scaled_df.sum(axis=1),2)
                scaled_df.insert(0, 'championName', df['championName'])  # 'name' 열 추가

                hot_champ = scaled_df[scaled_df['sum_scaled'] == scaled_df['sum_scaled'].max()]['championName'].iloc[0]
                hot_champ_score = scaled_df[scaled_df['championName'] == hot_champ ]['sum_scaled'].iloc[0]

                with elements("hot_champ"):                
                    layout = [
                                dashboard.Item("champ1", 0, 0, 1, 3,isDraggable=True, isResizable=True ),

                                ]
                    
                    with dashboard.Grid(layout):
                        mui.Card(
                            children=[      
                                mui.CardMedia( # most champ 1
                                        sx={
                                            "height": 110,
                                            "backgroundImage": f"linear-gradient(rgba(0, 0, 0, 0), rgba(10,10,10,10)),url(https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{hot_champ}_1.jpg)",
                                            "backgroundPosition": "bottom",
                                        }
                                    ),
                                mui.CardContent(
                                    sx={'padding':2}, # 설명
                                    children=[  
                                        mui.Typography(
                                            f" {hot_champ} ",
                                            variant="h5",
                                            component="div"
                                        ),
                                        mui.Typography(
                                                "",
                                            variant="body2",
                                            color="text.secondary",
                                            sx={
                                                "font-size": "12px"},
                                            
                                        )]
                                    ),


                                mui.Box( 
                                    sx={
                                        "display": "flex",
                                        "gap": "20px",
                                        "padding": "0",
                                        "justify-content": "center",
                                    },
                                    children=[
                                        mui.Box( 
                                            sx={
                                                "display": "flex",
                                                "flexDirection": "column",
                                                "alignItems": "center",
                                            },
                                            children=[
    
                                                mui.Typography(
                                                    f'SCORE',
                                                    variant='h5',
                                                ), 
                                                
                                                mui.Typography(
                                                    f'{hot_champ_score}/10',
                                                    variant='h3',
                                                )
                                            ]
                                        ),

                                    ]
                                ),

                            ] , key="mostchamp", elevation=1 , sx=card_sx) 
            


                # st.dataframe(scaled_df)



        st.divider()
        with st.container() :
            col1,col2 = st.columns([2,1])
            with col1:
                with elements("wak_indicator_vision"):                
                    layout = [
                                dashboard.Item("item1", 0, 0, 6, 2,isDraggable=True, isResizable=True ),

                                ]
                    
                    with dashboard.Grid(layout):
                        st.subheader('''📊 시야점수''')
                        st.markdown('''
                                    ##### " 남은돈으로 핑크와드를 사보자 "
                                    ''')

                        mui.Card(
                            nivo.Bar(
                                data=nivo_bar_vision,
                                keys=["faker","현재의 나","과거의 나"],  # 막대 그래프의 그룹을 구분하는 속성
                                indexBy="col",  # x축에 표시할 속성

                                margin={"top": 10, "right": 50, "bottom": 10, "left": 90},
                                padding={0.3},
                                layout="horizontal",
                                groupMode="grouped",

                                valueScale={ "type" : 'linear' },
                                indexScale={ "type": 'band', "round": 'true'},
                                borderRadius={5},
                                colors=['#459ae5','#a1d99b', '#ada9a9eb'],                   
                                # colors=[], # {'scheme': 'nivo' }

                                innerRadius=0.3,
                                padAngle=0.5,
                                activeOuterRadiusOffset=8,
                                enableGridY= False,

                                labelSkipWidth={20},
                                # labelSkipHeight={10},
                                # legends=[
                                #     {
                                #         'dataFrom': 'keys',
                                #         'anchor': 'top-right',
                                #         'direction': 'column',
                                #         'translateX': 0,
                                #         'translateY': 30,
                                #         'itemsSpacing': 0,
                                #         'itemWidth': 80,
                                #         'itemHeight': 20,
                                #         'itemDirection': 'left-to-right',
                                #         'itemOpacity': 0.8,
                                #         'symbolSize': 15,
                                #         'effects': [
                                #             {
                                #                 'on': 'hover',
                                #                 'style': {
                                #                     'itemOpacity': 1
                                #                 }
                                #             }
                                #         ]
                                #     }
                                # ],
                                axisBottom=False,
                                theme={
                                        # "background": "black",
                                        "textColor": "white",
                                        "tooltip": {
                                            "container": {
                                                "background": "#3a3c4a",
                                                "color": "white",
                                            }
                                        }
                                    },                         
                                ) 

                        ,key='item1',sx=card_sx)


                st.markdown(f'''
                            * 과거의 형님과 비교 했을 때, 유일하게 상대적으로 감소하고 있는 지표입니다.
                            * 와드는 그래도 지우지만 :orange[제어와드(핑크와드)를 거의 박지 않는 수준]입니다. 페이커가 되기 위해서 최소 3번은 박아야해요 
                            * 왁굳님이 여태 만난 소환사들의 평균 핑크와드 설치개수는 {iron_vision}개 입니다.

                            ''', unsafe_allow_html=False)

            with col2:
                st.subheader('🤡 시야')
                st.caption('시야가 부족한곳에서 죽은 경우 좌표')



        with st.container(): # CS지표
            col1,col2 = st.columns([2,1])
            with col1: 
                with elements("wak_indicator_GOLD"):                
                    layout = [
                                dashboard.Item("item1", 0, 0, 6, 2,isDraggable=True, isResizable=True ),

                                ]
                    
                    with dashboard.Grid(layout):
                        st.markdown('''#### 📊 GOLD''')
                        st.markdown('''
                                    ##### " 비건에서 육식으로.. "
                                    ''')

                        mui.Card(
                            nivo.Bar(
                                data=nivo_bar_gold,
                                keys=["faker","현재의 나","과거의 나"],  # 막대 그래프의 그룹을 구분하는 속성
                                indexBy="col",  # x축에 표시할 속성

                                margin={"top": 10, "right": 50, "bottom": 10, "left": 90},
                                padding={0.4},
                                layout="horizontal",
                                groupMode="grouped",

                                valueScale={ "type" : 'linear' },
                                indexScale={ "type": 'band', "round": 'true'},
                                borderRadius={5},
                                colors=['#459ae5','#a1d99b', '#ada9a9eb'],                   
                                # colors=[], # {'scheme': 'nivo' }

                                innerRadius=0.3,
                                padAngle=0.5,
                                activeOuterRadiusOffset=8,
                                enableGridY= False,

                                labelSkipWidth={20},
                                # labelSkipHeight={10},
                                # legends=[
                                #     {
                                #         'dataFrom': 'keys',
                                #         'anchor': 'top-right',
                                #         'direction': 'column',
                                #         'translateX': 0,
                                #         'translateY': 30,
                                #         'itemsSpacing': 0,
                                #         'itemWidth': 80,
                                #         'itemHeight': 20,
                                #         'itemDirection': 'left-to-right',
                                #         'itemOpacity': 0.8,
                                #         'symbolSize': 15,
                                #         'effects': [
                                #             {
                                #                 'on': 'hover',
                                #                 'style': {
                                #                     'itemOpacity': 1
                                #                 }
                                #             }
                                #         ]
                                #     }
                                # ],
                                axisBottom=False,
                                theme={
                                        # "background": "black",
                                        "textColor": "white",
                                        "tooltip": {
                                            "container": {
                                                "background": "#3a3c4a",
                                                "color": "white",
                                            }
                                        }
                                    },                         
                                ) 

                        ,key='item1',sx=card_sx)


                csper= round((nivo_bar_gold[0]['현재의 나'] - nivo_bar_gold[0]['과거의 나']) / nivo_bar_gold[0]['과거의 나'] * 100)
                st.markdown(f'''
                                * 상대라이너와 비교했을 때 아직 부족하지만  :orange[중요한건 과거의 나 자신보다 {csper}% 상승]했다는점 입니다.                              
                                * 과거의 나보다 한웨이브를 더 먹는 수준입니다. (대략6개)
                            ''')


            with col2:  # 포지션별 20분간 CS              
                st.subheader('📊포지션별 20분간 CS')
                st.caption(f'{summoner_name}님은 바텀 포지션을 갔을 때 CS를 상대적으로 잘먹는 편입니다.')
                CSbyPosition= wak20CS.groupby(['timestamp','teamPosition']).agg(
                    CS = pd.NamedAgg(column='minionsKilled', aggfunc='mean')
                ).reset_index()

                CSbyPosition['CS'] = CSbyPosition['CS'].astype(int)
                pivot_type = pd.pivot_table(CSbyPosition, values='CS', index='timestamp', columns='teamPosition')
                st.line_chart(pivot_type, use_container_width=True)


            #     st.subheader(''' ✔️ 15분 이후 솔로킬을 당한 좌표 ''')
                # wak_total_death = wakteam_death_log[wakteam_death_log['summonerName_x']==summoner_name]             
                # wak_total_death = wak_total_death[(wak_total_death['assistingParticipantIds'].isna()) & (wak_total_death['timestamp'] > 15)] 
                # st.write(wak_total_death)
                # death_spot(wak_total_death)
                # st.write(match_ids)



    if __name__ == '__main__' :
        main()

