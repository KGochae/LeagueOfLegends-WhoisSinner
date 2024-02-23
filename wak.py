# chart 
import streamlit as st
from streamlit_elements import dashboard
from streamlit_elements import nivo, elements, mui
import streamlit.components.v1 as components

# ----- dataframe,image ...etc ------#
import pandas as pd
import numpy as np
import streamlit as st
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import time
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

# secrets key
api_key = (
    # .stremlit/secrets.toml
    st.secrets["RIOTAPI"]
).get('api_key')
summoner_name = '메시아빠우왁굳'

# 사이드바
with st.sidebar:
    with st.form(key ='searchform'):
        # summoner_name = st.text_input("메시아빠우왁굳")
        # api_key = st.text_input("API KEY",
        #                         type = "password")     
        st.subheader("SUMMONER DASHBOARD")
        st.caption('''  
            해당 대시보드는 게임 BJ 우왁굳님의 경기데이터를 기준으로 만들어진 대시보드 입니다. 
            * RIOT API를 이용해 실시간으로 최근경기를 수집하며 80 ~ 120초 가량 소요됩니다😓.
            ''')

        st.image('https://i.ibb.co/n3vbJLS/lux.png', width = 150)
        submit_search = st.form_submit_button('우왁굳님의 데이터 불러오기')

        st.markdown(
            '''             
            * 우왁굳님의 [반응 보러가기😂](https://vod.afreecatv.com/player/116265471)
            '''
        )


# header
st.header("🎮 LEAGUE OF LEGENDS SUMMONER DASHBOARD")
st.caption(f'''  
            '메시아빠우왁굳' 소환사님의 과거의 경기와 현재의 경기를 통해 얼마나 성장했는지 확인해보았습니다.  
            ''')

# submit button 클릭시 riot api 및 전처리 함수가 실행됩니다.
if submit_search :
    puuid, summoner_id, iconId = get_puuid(summoner_name, api_key)
    match_ids = get_match_ids(puuid, api_key)
    match_info, champion_info = get_match_v5(match_ids, summoner_name, api_key)
    match_data_logs = get_match_data_logs(match_ids, api_key)  

    with st.spinner(''' 데이터 분석중.. 거의 다 왔어요🫠!'''):
        kill_and_ward, team_death_log, victim_by_jungle = get_events(match_data_logs,champion_info,summoner_name) # kill_and_ward, team_death_log
        rank_data = get_rank_info(summoner_id,api_key)
        summoner_radar_data, summoner_vs = radar_chart(match_info,summoner_name,'MIDDLE')
        
        log_df = gold_data(match_data_logs, match_ids)
        gold_df, lose_match_gold_by_team = lose_match_gold_diff(log_df, summoner_name,'MIDDLE',champion_info)    


    # info, match, champion
    st.session_state.puuid = puuid
    st.session_state.match_ids = match_ids
    st.session_state.match_info = match_info
    st.session_state.match_data_logs = match_data_logs
    st.session_state.champion_info = champion_info
    st.session_state.rank_data= rank_data

    # summoner,death,kill,gold
    st.session_state.summoner_radar_data = summoner_radar_data
    st.session_state.summoner_vs = summoner_vs
    st.session_state.team_death_log = team_death_log
    st.session_state.victim_by_jungle = victim_by_jungle
    st.session_state.kill_and_ward = kill_and_ward
    st.session_state.gold_df = gold_df
    st.session_state.log_df = log_df
    st.session_state.lose_match_gold_by_team = lose_match_gold_by_team

# session_state
if hasattr(st.session_state, 'puuid'):
    puuid = st.session_state.puuid

if hasattr(st.session_state, 'summoner_vs'):
    summoner_vs = st.session_state.summoner_vs

    agg_columns = ['totalDamageDealtToChampions', 'totalCS10Minutes', 'soloKills', 'visionScore', 'damageDealtToBuildings']
    col= ['summonerName','챔피언딜량','10분CS','솔로킬','시야점수','타워피해량']

    summoner_static = summoner_vs.groupby(['summonerName']).agg(
        **{column: pd.NamedAgg(column=column, aggfunc='mean') for column in agg_columns}
    ).reset_index().round() 
    summoner_static.columns = col

# 매치 데이터
if hasattr(st.session_state, 'match_info'):
    match_info = st.session_state.match_info    
    unique_match = match_info['matchId'].nunique()
    lose_match_cnt = len(match_info[(match_info['puuid'] == puuid) & (match_info['win']==False)]) 
 
    summoner_mid_lose = match_info[(match_info['summonerName'] == summoner_name)&(match_info['win']== False)&(match_info['teamPosition']== 'MIDDLE')]['matchId'].tolist()

    summoner_mid_lose_cnt = len(summoner_mid_lose)


    cs_10 = match_info.groupby(['teamPosition']).agg(
        cs = pd.NamedAgg(column='totalCS10Minutes', aggfunc='mean')
    ).reset_index()

if hasattr(st.session_state, 'champion_info'):
    champion_info = st.session_state.champion_info


if hasattr(st.session_state, 'match_data_logs'):
    match_data_logs = st.session_state.match_data_logs



if hasattr(st.session_state, 'log_df'):
    log_df = st.session_state.log_df
    log_df['timestamp'] = log_df['timestamp'].astype(int)


    ld = log_df[['matchId','timestamp','minionsKilled','participantId','position','totalGold','xp','level']]
    champion_info = champion_info[['matchId','participantId','teamId','teamPosition','summonerName','championName','win']]
    df1 = pd.merge(ld, champion_info, on=['matchId', 'participantId'], how='inner')
    summoner_20CS= df1[(df1['summonerName'] == summoner_name) & (df1['timestamp'] < 21) & (df1['teamPosition'] != '')]


if hasattr(st.session_state, 'match_ids'):
    match_ids = st.session_state.match_ids


if hasattr(st.session_state, 'team_death_log'):
    team_death_log = st.session_state.team_death_log    
    team_death_log.loc[:, 'lane'] = team_death_log.apply(lambda row: calculate_lane(row['position']['x'], row['position']['y']), axis=1)

    # 왁굳이 미드라인에서 패배한 경기만    
    summoner_lose_log = team_death_log[team_death_log['matchId'].isin(summoner_mid_lose)]

    # 미드라인에서 패배한 경기중, 후반부에 왁굳이 죽은 좌표
    summoner_death_16 = summoner_lose_log[(summoner_lose_log['summonerName_x'] == summoner_name)&(summoner_lose_log['timestamp'] > 15)]

    # 패배한경기, 포지션별 죽은 횟수 집계
    team_death_15 = summoner_lose_log[summoner_lose_log['timestamp'] < 16].groupby(['victimPosition']).agg(
                    count = pd.NamedAgg(column = 'victimPosition', aggfunc='count')
                    ).reset_index().sort_values(by='count',ascending=True)
    
    team_death_16 = summoner_lose_log[summoner_lose_log['timestamp'] > 15].groupby(['victimPosition']).agg(
                    count = pd.NamedAgg(column = 'victimPosition', aggfunc='count')
                    ).reset_index().sort_values(by='count',ascending=True)
    

    # 왁굳이 패배한 경기중에서 솔로킬을 당한 경우
    summoner_death_solo = summoner_lose_log[summoner_lose_log['assistingParticipantIds'].isna()] # 다른 상대팀의 어시스트 없이 솔로킬을 당한 경우

    # 15분 전후로 포지션별 집계
    death_solo_16 = summoner_death_solo[summoner_death_solo['timestamp'] > 15].groupby(['victimPosition']).agg(
                    death = pd.NamedAgg(column = 'victimPosition', aggfunc='count')).reset_index().sort_values(by='death',ascending=True)

    death_solo_15 = summoner_death_solo[summoner_death_solo['timestamp'] < 15].groupby(['victimPosition']).agg(
                    death = pd.NamedAgg(column = 'victimPosition', aggfunc='count')).reset_index().sort_values(by='death',ascending=True)


    # 라인전 이후 솔로킬로 짤린 포지션은 바텀(원딜) 이었다. 그렇다면 주로 어디서 짤리는가
    bottom_solo_death = summoner_death_solo[(summoner_death_solo['victimPosition'] == 'BOTTOM') & (summoner_death_solo['timestamp'] > 15)]
  
    # 라인전동안 적팀정글로 인한 데스 (+우리팀 정글은 어디서 죽었을까?)
    jungle_death = team_death_log[(team_death_log['victimPosition'] == 'JUNGLE') | (team_death_log['assistingParticipantIds'].apply(lambda x: 'JUNGLE' in x if isinstance(x, list) else False))]
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
    # 패배한 경기중 정글에게 당한 로그 (라인전)
    summoner_mid_match = match_info[(match_info['summonerName'] == summoner_name)&(match_info['teamPosition']== 'MIDDLE')]['matchId'].tolist()

    jungle_15_death = victim_by_jungle[(victim_by_jungle['timestamp'] <= 20) & (victim_by_jungle['matchId'].isin(summoner_mid_match))] 
    jungle_15_group = jungle_15_death.groupby(['victimPosition']).agg({'cnt':'sum'}).reset_index().sort_values(by=['cnt'])
    jungle_15 = jungle_15_group.to_dict('records')

    jungle_15_sum = jungle_15_death.groupby(['matchId','victimPosition']).agg(
                    death_sum = pd.NamedAgg(column='cnt', aggfunc='sum')).reset_index()
    
    jungle_15_mean_df = jungle_15_sum.groupby(['victimPosition']).agg(
                    mean = pd.NamedAgg(column='death_sum', aggfunc='mean'),
                    ).reset_index().round(2).sort_values(by=['mean'])
    
    jungle_15_mean = jungle_15_mean_df.to_dict('records')
    




# if hasattr(st.session_state, 'nol_kill_log'):
#     nol_kill_log = st.session_state.nol_kill_log

# if hasattr(st.session_state, 'chun_kill_log'):
#     chun_kill_log = st.session_state.chun_kill_log

if hasattr(st.session_state, 'gold_df'):
    gold_df = st.session_state.gold_df
    t3 = gold_df[gold_df['timestamp'] == 20].nsmallest(3, 'totalGold_diff')['teamPosition'].tolist()

    # to json
    @st.cache_data
    def to_nivo_line(df,group,x_col,y_col):
        nivo_line_data = []
        for team in df[group].unique():
            team_data = {
                'id': team,
                'data': []
            }

            team_df = df[df[group] == team]
            for index, row in team_df.iterrows():
                item = {
                    'x': row[x_col],
                    'y': row[y_col]
                }
                team_data["data"].append(item)

            nivo_line_data.append(team_data)
        return nivo_line_data
    
    gold_15 = to_nivo_line(gold_df,'teamPosition','timestamp','totalGold_diff')


# if hasattr(st.session_state, 'lose_match_gold_by_team'):
#     lose_match_gold_by_team = st.session_state.lose_match_gold_by_team
    # team_by_gold = lose_match_gold_by_team[lose_match_gold_by_team['timestamp'] < 21]


    # team_by_gold = team_by_gold.groupby(['timestamp','teamId']).agg({'totalGold':'mean'}).round().reset_index() #.sort_values(by=['timestamp','teamId'], ascending=[True,True])
    # team_by_gold['gold_diff'] = team_by_gold.groupby('timestamp')['totalGold'].diff() # .fillna(0).astype(int)
    # team_by_gold['gold_diff'] = team_by_gold['gold_diff'].fillna(-team_by_gold['gold_diff'].shift(-1))
    # team_by_gold = to_nivo_line(team_by_gold[team_by_gold['teamId'] == '우리팀'],'teamId','timestamp','gold_diff')


if hasattr(st.session_state, 'kill_and_ward'): # ward_log
    kill_and_ward = st.session_state.kill_and_ward 
    
    ward_log = kill_and_ward[(kill_and_ward['type'].str.contains('WARD')) & (kill_and_ward['wardType'] != 'UNDEFINED')]    
    ward_info = champion_info[['matchId','teamId','teamPosition','participantId','summonerName','win']]
    ward_info.columns = ['matchId','teamId','teamPosition','creatorId','summonerName','win']
    ward_log = pd.merge(ward_log, ward_info, on=['matchId','creatorId'],how='inner')
    
  # 해당 소환사의 와드
    summoner_ward_log = ward_log[ward_log['summonerName'] == summoner_name]
    summoner_ward_log['timestamp'] = summoner_ward_log['timestamp'].astype(int)
    summoner_ward_log_static = summoner_ward_log.groupby(['matchId','win']).agg(
        ward_cnt = pd.NamedAgg(column='matchId', aggfunc='count')
    )

    summoner_ward_log_15 = summoner_ward_log[summoner_ward_log['timestamp'] < 16]



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
if hasattr(st.session_state, 'summoner_radar_data'):
    summoner_radar_data = st.session_state.summoner_radar_data
    # min_value_var = min(summoner_radar_data, key=lambda x: x[f'{summoner_name}'])["var"]
    

    def main():
        with st.container():

            # MAIN - WAKGOOD
            col1,col2 = st.columns([2,4])
            with col1: 
                tab1,tab2 = st.tabs(['기본지표','Champion Table'])
                with tab1:   # INFO
                    st.subheader('🎲 INFO')
                    st.caption(f''' {summoner_name}님이 그동안 만난 상대 미드라이너와의 게임지표를 비교했어요.  
                            (0~1점으로 표준화)''')
                    
                    with elements("info/radar"):                
                            layout = [
                                        dashboard.Item("item_info", 0, 0, 1.2, 2, isDraggable=True, isResizable=True ),
                                        dashboard.Item("item_rank", 2, 1, 0.8, 1, isDraggable=True, isResizable=True ),
                                        dashboard.Item("item_tier", 2, 2, 0.8, 1, isDraggable=True, isResizable=True)
                                        ]
                            card_sx = {"background-color":"#181819","borderRadius": "10px"} # "outline": "1px solid #31323b"
                            with dashboard.Grid(layout):
                                
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
                                                        "height": 60,
                                                        "width": 60,
                                                        "borderRadius": "10%",
                                                        "backgroundImage": f"url(http://ddragon.leagueoflegends.com/cdn/14.1.1/img/profileicon/4025.png)",  
                                                    },
                                                    title='icon'
                                                ),
                                             
                                                mui.Divider(orientation="vertical",sx={"height": "70px"}), 

                                                mui.Box(
                                                    mui.Typography(
                                                        "Position",
                                                        color="text.secondary",
                                                        sx={'font-size':'10px'}
                                                    ), 
                                                    # mui.Divider(sx={"width":50}),
                                                    mui.CardMedia(
                                                            sx={
                                                                "height": 50,
                                                                "width": 50,
                                                                "borderRadius": "10%",
                                                                "backgroundImage": f"url(https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-clash/global/default/assets/images/position-selector/positions/icon-position-middle.png)"
                                                            },
                                                            title='MIDDLE'
                                                        ),                                                    
                                                    ), 
                                                mui.Divider(orientation="vertical",sx={"height": "70px"}),                                                
                                           
                                                mui.Box(
                                                    mui.Typography(
                                                        "TIER",
                                                        color="text.secondary",
                                                        sx={'font-size':'10px'}
                                                    ), 
                                                    # mui.Divider(sx={"width":100,"padding"}),

                                                    mui.CardMedia( 
                                                        sx={
                                                            "height":50,
                                                            "width":100,                                     
                                                            "backgroundImage": f"url(https://i.ibb.co/2ZrRXqP/tft-regalia-{tier}.png)",  
                                                        },               
                                                        title='티어'                         
                                                    )                                        
                                                )
                                            ]
                                        ),                                 

                                            mui.Divider(sx={"height": "1px"}), # orientation="vertical",
                                            
                                            nivo.Radar(
                                                data=summoner_radar_data,
                                                keys=[f'{summoner_name}','상대라이너'],
                                                colors={'scheme': 'nivo' },
                                                indexBy="var",
                                                valueFormat=">-.2f",
                                                maxValue={1.0},
                                                margin={ "top": 50, "right": 60, "bottom": 50, "left": 80 },
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
                                    ,key="item_info",sx=card_sx )  # sx=card_sx
            
                                mui.Card( # RANK 승패
                                    children=[
                                        mui.Typography(
                                                "24S RECORD",
                                                color="text.secondary",
                                                variant="body2",
                                                sx={'background-color':'#181819','text-align':'center'}),  
                                        
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

                    expander = st.expander("데이터")
                    with expander:
                        st.write(summoner_static)
                        st.markdown(f'''
                                <div> \n

                                * 상대 라이너와 비교했을 때, 평균적으로 한웨이브의 미니언을 놓치는 수치입니다.
 
                                </div>
                                ''',unsafe_allow_html= True)

                                # ✔️ 상대 라이너와 비교했을 때 가장 차이가 나는 부분은 <strong>{min_value_var}</strong> 입니다. 
                                # * 현재 왁굳님의 평균 10분CS는 {int(summoner_static[f'{min_value_var}'][0])}개 이며 
                                # * 상대 라이너의 평균 10분CS는 {int(summoner_static[f'{min_value_var}'][1])}개 입니다.

                # Most Champ
                with tab2:
                    summoner_match_info = match_info[(match_info['puuid'] == puuid)]
                    # 챔피언별 통계
                    @st.cache_data
                    def champ_static_func(df):
                        champ_static = df.groupby(['championName']).agg(
                                                champion_count = pd.NamedAgg(column = 'championName', aggfunc='count'),
                                                soloKills_mean = pd.NamedAgg(column = 'soloKills', aggfunc='mean'),
                                                multiKills_mean = pd.NamedAgg(column = 'multikills', aggfunc='mean'),                                       
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
                        
                        return champ_static
                    champ_static = champ_static_func(summoner_match_info)

                    first_champ = champ_static.iloc[0]['championName']
                    second_champ = champ_static.iloc[1]['championName']


                    st.subheader('Champion Data')
                    expander = st.expander("챔피언 데이터")
                    with expander:
                        st.dataframe(champ_static)
          

            with col2: # 패배한경기 분석 (gold)

                tab0, tab1,tab2,tab3 = st.tabs(['패배한 경기','GOLD🪙','DEATH','DEATH II'])
                with tab0:

                    st.markdown(f''' 
                                    ### 패배한 경기 집계 기준
                                ''')


                    st.caption(f''' 
                                    <div>\n
                                    50 경기중 편차를 줄이기 위해 <span style="color:orange">20분~35분동안 진행된 경기</span>만 집계 되었으며 총 {unique_match}경기 입니다.
                                    '{summoner_name}'님의 최근{unique_match}개의 경기중 <span style="color:orange">패배한 경기는 {lose_match_cnt}경기</span>입니다.   
                                    그 중에서 왁굳님의 주포지션인 <span style="color:orange"> MIDDLE 포지션일때 {summoner_mid_lose_cnt}번 졌으며, 이 기준으로 데이터가 집계</span>되었습니다.                            
                                    </div> 
                                    ''', unsafe_allow_html=True)

                    # st.image('https://i.ibb.co/Y3TRmsM/image.png', width = 300)
                    st.image('https://get.wallhere.com/photo/League-of-Legends-jungle-Terrain-screenshot-atmospheric-phenomenon-computer-wallpaper-284470.jpg', width = 800)


                with tab1: # 골드
                    st.subheader(''' ✔️ (패배한 경기) 포지션별 골드차이(20분)''')
                    st.caption('첫번째 단서는 GOLD 입니다. 라인전 동안의 CS, KILL 을 통해 벌어진 상대 라이너와의 골드차이를 통해 누가 똥쌌는지 유추 할 수 있습니다.')
      
                    with elements("GOLD"):                
                            layout = [
                                        dashboard.Item("item1", 0, 0, 6, 2,isDraggable=True, isResizable=True ),
                                        dashboard.Item("item2", 0, 3, 5, 1,isDraggable=True, isResizable=True ),

                                        ]
                            # card_sx = {"background-color":"#0a0a0adb","borderRadius": "23px", "outline": "1px solid #242427"}
                            with dashboard.Grid(layout):

                                mui.Box(  # nivo_line                                       
                                    # children=[                                
                                        nivo.Line(
                                            data= gold_15,
                                            margin={'top': 30, 'right': 60, 'bottom': 50, 'left': 60},
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

                                        # ]
                                    
                                        key="item1",sx=card_sx) #sx=card_sx          
                            
                                # mui.Box(
                                #     children=[                                
                                #         nivo.Line(
                                #             data= team_by_gold,
                                #             margin={'top': 5, 'right': 60, 'bottom': 30, 'left': 0},
                                #             xScale={'type': 'point'},
                                #             yScale={
                                #                 'type': 'linear',
                                #                 'min': 'auto',
                                #                 'max': 'auto',
                                #                 # 'stacked': True,
                                #                 # 'reverse': False
                                #             },
                                #             curve="cardinal",

                                #             axisBottom= None,

                                #             axisLeft=None,


                                #             legends=[
                                #                 {
                                #                     "anchor": "bottom-left",
                                #                     "direction": "column",
                                #                     "translateX": 10,
                                #                     "translateY": -10,
                                #                     "itemWidth": 10,
                                #                     "itemHeight": 15,
                                #                     "itemTextColor": "white",
                                #                     "symbolSize": 10,
                                #                     "symbolShape": "circle",
                                #                     "effects": [
                                #                         {
                                #                             "on": "hover",
                                #                             "style": {
                                #                                 "itemTextColor": "white",
                                #                                 'itemBackground': 'rgba(0, 0, 0, .03)',
                                #                                 'itemOpacity': 1
                                #                             }
                                #                         }
                                #                     ]
                                #                 }
                                #             ],

                                #             colors= {'scheme': 'red_yellow_blue'},
                                #             enableGridX = False,
                                #             enableGridY = False,
                                #             lineWidth=3,
                                #             pointSize=0,
                                #             pointColor='white',
                                #             pointBorderWidth=1,
                                #             pointBorderColor={'from': 'serieColor'},
                                #             pointLabelYOffset=-12,
                                #             enableArea=True,
                                #             areaOpacity='0.2',
                                #             useMesh=True,                
                                #             theme={
                                #                     "textColor": "white",
                                #                     "tooltip": {
                                #                         "container": {
                                #                             "background": "#3a3c4a",
                                #                             "color": "white",
                                #                         }
                                #                     }
                                #                 },

                                #             animate= False),

                                #         ]
                                #           ,key="item2",sx=card_sx ) #sx=card_sx          
                    
                    

                    st.markdown(f'''
                                <div> \n
                                * 패배한 경기의 <strong> 20분</strong> 동안의 <strong> 포지션별 골드량(평균) 차이</strong>를 구해보았습니다.
                                * 전체적으로 모든 라인이 골드차이가 나고 있었습니다.
                                * 20분 이후부터는 상대적으로 <span style="color:#74c476"> {t3[0]} </span>라인 에서 골드량(평균)차이가 크게 나고 있었습니다.
                                > 하지만 골드차이만 보고 단정짓기는 어렵습니다. 서포터의 경우 원래 KILL,CS 를 먹기 힘든 포지션이라 상대와 비교했을 때 큰 차이가 없기 때문입니다.
                                <span style="color:#ae8ed9"> 'DEATH☠️' </span> 관련한 변수를 확인해봅시다.
                                </div>
                                    '''
                            , unsafe_allow_html=True)  
                     # 놀랍게도 <span style="color:orange">왁굳님(MIDDLE)</span> 의 경우 라이너중 가장 안정적인 GOLD차이를 보여주고 있었습니다. 


                with tab2: # Death
                    st.subheader('✔️ (패배한 경기) 포지션별 죽은 횟수')
                    st.caption(' 15분 전후로 어떤 포지션이 가장 많이 죽었는지 확인해보았습니다. 왁굳님의 경기 시간은 평균적으로 31분입니다. ')
                    with elements("death"):                
                            layout = [
                                        dashboard.Item("item1", 0, 0, 3, 2,isDraggable=True, isResizable=True ),
                                        dashboard.Item("item2", 3, 0, 3, 2,isDraggable=True, isResizable=True ),
                                        dashboard.Item("item3", 6, 0, 1, 2,isDraggable=True, isResizable=True ),

                                        ]
                            card_sx = {"background-color":"#0a0a0adb","borderRadius": "23px",'text-align':'center'} # "outline": "1px solid #242427"

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
                        death_15 = team_death_log[team_death_log['timestamp'] < 16].groupby(['matchId','victimPosition']).agg(
                                        count = pd.NamedAgg(column = 'victimPosition', aggfunc='count')
                                        ).reset_index().sort_values(by='count',ascending=True)
                        death_16 = team_death_log[team_death_log['timestamp'] > 15].groupby(['matchId','victimPosition']).agg(
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
                                * 모든 포지션이 라인전 이후에 죽는 경우가 더 많습니다. <span style="color:#82b1ff">MIDDLE</span> 의 경우도 라인전 이후의 컨디션 차이가 있는 편입니다.                               
                                * 다시 말하지만! 패배한 경기 기준입니다.
                                * 현재까지의 골드차이, 죽은횟수를 고려해보면 상대적으로 <strong> 바텀(원딜)</strong>이 유력해보입니다. 하지만 이정도 지표로는 아직 억울할 수 있습니다..\n
                                > death와 관련된 변수들을 좀 더 여러가지 주제로 집계 해보았습니다.🤔.
                                    
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
                                    dashboard.Item("item1", 0, 0, 2, 3,isDraggable=True, isResizable=False ),
                                    dashboard.Item("item2", 2, 0, 2, 3,isDraggable=True, isResizable=False ),
                                    dashboard.Item("item3", 4, 0, 2, 3,isDraggable=True, isResizable=False ),

                                    ]
                        
                        with dashboard.Grid(layout):
                            mui.Card( # 짤린 포지션
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
        
                                                                    
                            mui.Card( # 정글갱
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
                                                "20분 동안 상대 정글에게 가장 많이 당한 포지션? ",
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
                                        # colors=['grey'],                   
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


                            mui.Card( # 흑백화면
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
    


                    expander = st.expander("주로 어디서 죽었나?")
                    with expander:
                        col1,col2,col3 =st.columns([1,1,1])
                        with col1:
                            st.write('''##### ✔️ 솔로킬을 당한 위치 (원딜) ''')
                            death_spot(bottom_solo_death)

                            st.markdown('''
                                        <div> \n                            
                                         * 라인전이후 가장 많이 솔로킬로 짤린 포지션은 <span style="color:#82b1ff">BOTTOM</span>.
                                         *                                         
                                        </div>
                                        
                                        ''' ,unsafe_allow_html=True)

                        with col2:
                            st.write('''##### ✔️ 정글에 의한 죽음 ''' )
                            death_spot_sc(jungle_death_15,'Greens')
 
                            st.markdown(''' 
                                        <div> \n
                                        * 라인전동안 가장 많이 정글에게 당한 포지션은  <span style="color:#74c476">JUNGLE</span>. 
                                        * 특히, <span style="color:#74c476"> 바텀에서의 역갱, 정글링 싸움</span>으로 인한 death가 가장 많았습니다.
                                        </div>
                                        ''', unsafe_allow_html = True)
                        with col3:
                            st.write('''##### ✔️ 흑백화면을 가장 오래본 포지션 ''')

                            
                            groupby_lane = summoner_death_16.groupby(['lane']).agg(count = pd.NamedAgg(column='lane',aggfunc ='count')).reset_index()
                            total_count = groupby_lane['count'].sum()
                            groupby_lane['ratio'] = (groupby_lane['count'] / total_count) * 100

                            groupby_lane = groupby_lane.sort_values(by=['ratio'],ascending=False)

                            death_spot_sc(summoner_death_16,'Reds')
                            st.markdown('''
                                         <div> \n
                                        * 패배한 경기에서 왁굳님의 경우 상대적으로 <span style="color:orange"> 후반부에 짤리는 경우</span> 가 특히 많았습니다.
                                        * 한타가 많이 일어나고 시야확보가 중요한  <span style="color:orange"> 정글지역, 그리고 사이드(TOP,BOTTOM)를 밀다가 죽는 경우가 약 83% </span> 입니다.
                                        </div>
                                        ''', unsafe_allow_html=True)

                            st.dataframe(groupby_lane)


                    




# ------------------------------------------------------------- 소환사 성장 지표 ---------------------------------------------------------------------------#
        st.divider()


        with st.container():
            
            st.header('📈 오늘의 나는.. 어제의 나와 다르다.')
            st.caption('''
                       * 최근 25경기와 과거 25경기, 그리고 언젠가 매치에서 만날 페이커님과 비교해보았어요
                       * 페이커님의 경우 이번 시즌 34경기의 (미드포지션) 기준이기 때문에 비교가 무의미할 수 있습니다. (*2024-01-26 기준 데이터)
                       ''')

            col1,col2 = st.columns([2,1])
            with col1:
                @st.cache_data
                def summoner_indicator(summoner_match_info, ward_log, summoner_name):
                    
                    summoner_match_info['totalTimeSpentDead'] = summoner_match_info['totalTimeSpentDead']/60
                    summoner_recent = summoner_match_info.head(20) # 최근 20경기
                    summoner_befor = summoner_match_info.tail(20)

                    recent_matchid= summoner_recent['matchId'].tolist()
                    befor_matchid= summoner_befor['matchId'].tolist()

                    # ward 데이터의 경우 최근 27개의 경기의 데이터만 남아있다.. 아무래도 이전 시즌 데이터는 날라건둣함

                    ids = summoner_ward_log['matchId'].unique().tolist()
                    middle_index = len(ids) // 2

                    ward_recent = ward_log[(ward_log['matchId'].isin(match_ids[:middle_index])) & (ward_log['summonerName']==summoner_name)].groupby('matchId').size().mean().round(1)
                    ward_befor  = ward_log[ward_log['matchId'].isin(match_ids[middle_index:]) & (ward_log['summonerName']==summoner_name)].groupby('matchId').size().mean().round(1)


                    # 기본지표
                    indicators = ['totalCS10Minutes','totalTimeSpentDead','visionScore','wardTakedowns','controlWardsPlaced','soloKills','kda','totalDamageDealtToChampions','damageDealtToObjectives','multikills']
                    kr_col = ['10분CS','죽은시간','시야점수','와드제거','제어와드설치','솔로킬','kda','챔피언딜량','오브젝트','멀티킬']

                    summoner_recent_static = summoner_recent[indicators]
                    summoner_recent_static.columns = kr_col            
                    summoner_recent_static = summoner_recent_static.mean().rename('현재의 나')


                    summoner_befor_static = summoner_befor[indicators]
                    summoner_befor_static.columns = kr_col            
                    summoner_befor_static = summoner_befor_static.mean().rename('과거의 나')

                                
                    result = pd.concat([summoner_recent_static, summoner_befor_static], keys=['현재의 나', '과거의 나'], axis=1).reset_index().rename(columns={'index': 'col'})
                    result['현재의 나'] = result['현재의 나'].round(2)
                    result['과거의 나'] = result['과거의 나'].round(2)

                    # Create a new DataFrame for the additional row
                    additional_row = pd.DataFrame({'col': ['와드 설치'], '과거의 나': [ward_befor], '현재의 나': [ward_recent]})

                    # Concatenate existing DataFrame with the additional row
                    result = pd.concat([result, additional_row], ignore_index=True)

                    return result,recent_matchid,befor_matchid

                result,recent_matchid,befor_matchid = summoner_indicator(summoner_match_info,ward_log,summoner_name)

                

                @st.cache_data
                def get_death_stats(data, match_ids, summoner_name, timestamp_threshold=20, solo_death=False, jungle_death=False):
                    filters = (data['matchId'].isin(match_ids)) & (data['summonerName_x'] == summoner_name) & (data['timestamp'] < timestamp_threshold)

                    if solo_death:
                        filters &= data['assistingParticipantIds'].isna()

                    if jungle_death:
                        filters &= ((data['killerPosition'] == 'JUNGLE') | (data['assistingParticipantIds'].apply(lambda x: 'JUNGLE' in x if isinstance(x, list) else False)))

                    return len(data[filters])



                # 솔로데스
                # wak_solo_death_before = get_death_stats(team_death_log, befor_matchid, '메시아빠우왁굳', solo_death=True)
                # wak_solo_death_recent = get_death_stats(team_death_log, recent_matchid, '메시아빠우왁굳', solo_death=True)
                

                # 15분 이전 킬을 당하는 횟수 집계
                # wak_death_before = get_death_stats(team_death_log, befor_matchid, '메시아빠우왁굳')
                # wak_death_recent = get_death_stats(team_death_log, recent_matchid, '메시아빠우왁굳')

                # 15분 이전 정글갱에 의한 데스
                # wak_jungle_death_before = get_death_stats(team_death_log, befor_matchid, '메시아빠우왁굳', jungle_death=True)
                # wak_jungle_death_recent = get_death_stats(team_death_log, recent_matchid, '메시아빠우왁굳', jungle_death=True)

                # new_row = pd.DataFrame({'col': ['death_15'], '과거의 나': [wak_jungle_death_before], '현재의 나': [wak_jungle_death_recent],
                                        # })

                # faker 데이터
                data_values = [81.82, 2.1, 28.65, 5.65, 3.44, 1.68, 4.39, 29217.24, 11825.41, 0.85]
                # DataFrame 생성
                faker_df = pd.DataFrame({'faker': data_values})
                wak_data = pd.concat([result, faker_df],axis = 1)
                # wak_data = pd.concat([wak_data, new_row])
                


                vision_value = ["제어와드설치", "와드 설치", "와드제거","시야점수"]    
                attack_value = ["솔로킬","멀티킬" ,"kda","죽은시간"] 
                deatl_value = ["챔피언딜량","오브젝트"]
                gold_value = ["10분CS"]

                # to json
                nivo_bar_vision = wak_data[wak_data['col'].isin(vision_value)].to_dict('records')
                nivo_bar_attack = wak_data[wak_data['col'].isin(attack_value)].to_dict('records')
                nivo_bar_dealt = wak_data[wak_data['col'].isin(deatl_value)].to_dict('records')
                nivo_bar_gold = wak_data[wak_data['col'].isin(gold_value)].to_dict('records')




                # 최근 경기의 시야점수 
                iron_vision = round(match_info['controlWardsPlaced'].mean(),1)

                # 공격지표에 관하여
                with elements("wak_indicator_attack"):                
                    layout = [
                                dashboard.Item("item1", 0, 0, 6, 2,isDraggable=True, isResizable=True ),
                                ]
                    
                    with dashboard.Grid(layout):
                        st.subheader('''📊 공격지표''')
                        st.markdown(''' ##### " 날카롭게 성장중인 슬로우 스타터 " ''')
                      
                        mui.Card( #공격지표 chart
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
                            keys=["faker","현재의 나","과거의 나"],  # 막대 그래프의 그룹을 구분
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
 

                        ,key='item1',sx={'display':'flex',"background-color":"#0a0a0adb","borderRadius": "20px"}) #"outline": "1px solid #31323b"


                death_per = round((nivo_bar_attack[0]['과거의 나'] - nivo_bar_attack[0]['현재의 나']))
            
                st.markdown(f'''                                
                                * 가끔 답답한 모습들이 보여지긴 하지만, :orange[놀랍게도 거의 모든 지표가 성장하고 있는] 슬로우 스타터 "Fe이커" 우왁굳의 모습을 볼 수 있었습니다. 
                                * 준수한 'KDA' + 의외로 자주 등장하는 '멀티킬(더블킬 이상)'
                                * 특히, 흑백화면을 보는 시간(death)이 :orange[{death_per}분 감소]함으로서, 우왁굳의 안정적인 공격 모먼트가 과거에 비해 자주 나오는것을 볼 수 있습니다.                                                                       
                            ''')


            with col2: # hot champion
                st.subheader('🤡 폼이 안정적인 챔피언 (3판이상)')
                st.caption('''
                           * 공격지표, 시간대비 챔피언 딜량, CS, 타워피해량 등을 표준화해서 점수 산출.
                           ''')
                
                # 3판이상 진행한 챔피언
                # recent_champ = champ_static_func(summoner_match_info.head(30))
                df = champ_static[champ_static['champion_count']>2][['championName','soloKills_mean','multiKills_mean','visionScore_mean', 'longestTimeSpentLiving',
                                                                     'totalCS10Minutes_mean','damagePerMinute_mean','damageDealtToBuildings_mean',
                                                                     'damageDealtToObjectives_mean','kda_mean','win_rate']]
                # 점수 표준화 
                scaler = MinMaxScaler()
                scaled_values = scaler.fit_transform(df.iloc[:, 1:])
                scaled_df = pd.DataFrame(scaled_values, columns=df.columns[1:])
                scaled_df['sum_scaled'] = round(scaled_df.sum(axis=1),2)
                scaled_df.insert(0, 'championName', df['championName'])  # 'name' 열 추가
        
                # 소환사의 hot champ
                hot_champ = scaled_df.sort_values(by='sum_scaled',ascending=False)['championName'].iloc[0]
                hot_champ_score = scaled_df[scaled_df['championName'] == hot_champ ]['sum_scaled'].iloc[0]


                # hot champ vs most champ 비교
                radar_df = scaled_df[['championName','totalCS10Minutes_mean','damagePerMinute_mean','longestTimeSpentLiving','damageDealtToObjectives_mean','kda_mean','visionScore_mean']]
                radar_df.columns=['championName','10분CS','분당데미지','생존시간','오브젝트','KDA','시야점수']

                # radar 차트를 위한 데이터 형식
                melted_df = pd.melt(radar_df, id_vars=["championName"], var_name="var", value_name="value")
                pivoted_df = melted_df.pivot(index="var", columns="championName", values="value").reset_index()
                radar_champ = pivoted_df.to_dict("records")


                # HOT CHAMPION
                with elements("hot_champ"):                
                    layout = [
                                dashboard.Item("hot_champ1", 0, 0, 0.8, 2,isDraggable=True, isResizable=True ),
                                dashboard.Item("hot_champ2", 2, 0, 1.2, 2,isDraggable=True, isResizable=True ),
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
                                            variant="h4",
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
                                                    variant='h6',
                                                ), 
                                                
                                                mui.Typography(
                                                    f'{hot_champ_score}/10',
                                                    variant='h4',
                                                )
                                            ]
                                        ),

                                    ]
                                ),

                            ]  
                            , key="hot_champ1", elevation=0 , sx=card_sx) 

                        mui.Box(# hot_champ_info
                                mui.CardContent(
                                        sx={'padding':2}, # 설명
                                        children=[  
                                            mui.Typography(
                                                f" {hot_champ} VS ",
                                                variant="h6",
                                            ),
                                            mui.Typography(
                                                    "MOST 챔피언과 비교 ",
                                                variant="body2",
                                                color="text.secondary",
                                                sx={ "font-size": "12px"},
                                                
                                            )]
                                        ),  
                                        
                                nivo.Radar(
                                        data=radar_champ,
                                        keys=[f'{hot_champ}','Diana','Azir'],
                                        colors={'scheme': 'accent' },
                                        indexBy="var",
                                        valueFormat=">-.2f",
                                        maxValue={1.1},
                                        margin={ "top": 50, "right": 60, "bottom": 110, "left": 60 },
                                        borderColor={ "from": "color" },
                                        gridShape="linear",
                                        gridLevels={3},
                                        gridLabelOffset=15,
                                        dotSize=4,
                                        dotColor={ "theme": "background" },
                                        dotBorderWidth=1,
                                        motionConfig="wobbly",
                                        legends=[
                                            {
                                                "anchor": "top-right",
                                                "direction": "column",
                                                "translateX": -20,
                                                "translateY": -50,
                                                "itemWidth": 100,
                                                "itemHeight": 20,
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
                                            "textColor": "white",
                                            "tooltip": {
                                                "container": {
                                                    "background": "#262730",
                                                    "color": "white",
                                                }
                                            }
                                        }
                                    )                                
                                        ,key='hot_champ2',sx=card_sx)

                expander = st.expander("(3판 이상)챔피언 데이터")
                with expander:
                    st.dataframe(scaled_df)



        st.divider()

        with st.container() : # 사야점수에 관하여
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
                        # st.image('https://ddragon.leagueoflegends.com/cdn/14.1.1/img/item/2055.png')

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
                st.subheader('🤡 와드를 잘 박자')

                wak_all_death = team_death_log[team_death_log['summonerName_x'] == summoner_name]
                wak_15_death = wak_all_death[wak_all_death['timestamp'] <= 15]             
                wak_15_death['timestamp'] = wak_15_death['timestamp'].astype('int')

                wak_death_gang = wak_15_death[(wak_15_death['killerId'] == 'JUNGLE') | (wak_15_death['assistingParticipantIds'].apply(lambda x: ('JUNGLE' in x) or ('TOP' in x) or('MIDDLE' in x) if isinstance(x, list) else False))]
                wak_death_gang = wak_death_gang[['matchId','timestamp','type','wardType','position','assistingParticipantIds','summonerName_x','victimPosition','killerPosition','lane']]

                # 소환사가 갱에 의해 죽은것으로 추정되는 좌표 (라인전)
                ids = wak_death_gang['matchId'].unique().tolist()
                result = ward_log[(ward_log['summonerName'] == summoner_name) & (ward_log['matchId'].isin(ids)) & (ward_log['timestamp'] <= 15)]                
                ward_gang = pd.concat([wak_death_gang,result], axis = 0).sort_values(by=['matchId','timestamp'],ascending=[True,True])

                # mid_gang_cnt = len(wak_death_gang[wak_death_gang['lane'] == 'MIDDLE'])

                @st.cache_data
                def death_before_ward(ward_gang):
                    results = []
                    # 각 matchId에 대해 처리
                    for match_id, group in ward_gang.groupby('matchId'):
                        # "CHAMPION_KILL"을 당한 행 찾기
                        champion_kill_rows = group[group['type'] == 'CHAMPION_KILL']

                        for _, row in champion_kill_rows.iterrows():
                            # 현재 행의 150초 전 timestamp 계산
                            timestamp_before_champion_kill = row['timestamp'] - 2.5

                            # 150초 전부터 현재까지의 행 중 "WARD_PLACED" 찾기
                            relevant_rows = group[(group['timestamp'] >= timestamp_before_champion_kill) & (group['timestamp'] <= row['timestamp'])]
                            
                            # "WARD_PLACED" 여부 확인
                            ward_placed = any(relevant_rows['type'] == 'WARD_PLACED')

                            lane = row['lane']
                            # 결과를 리스트에 추가
                            results.append({
                                'matchId': match_id,
                                'timestamp': row['timestamp'],
                                'ward_placed': ward_placed,
                                'lane': lane
                            })

                    result_df = pd.DataFrame(results)

                    return result_df

                
                warding_death = death_before_ward(ward_gang)
                no_warding = warding_death[warding_death['ward_placed']== False]
                # st.write(wak_death_gang)

                # 소환사가 라인전때 갱에의해 잘죽는 시간대

                # 시간대 별로 groupby하여 빈도 계산
                time_grouped_1 = wak_15_death.groupby(['timestamp']).size().rename('TOTAL DEATH(라인전)')
                time_grouped_2 = wak_death_gang.groupby(['timestamp']).size().rename('GANG')
                time_grouped_3 = no_warding.groupby(no_warding['timestamp'].astype(int)).size().rename('NO WADING DEATH')
                # time_grouped_4 = wak_death_gang.groupby(['timestamp','victimPosition']).size().unstack()




                gang_line_chart = pd.concat([time_grouped_3,time_grouped_2,time_grouped_1], axis= 1).fillna(0)

                tab1,tab2 = st.tabs(['GANG','GANG DEATH 좌표'])
                with tab1:
                    st.bar_chart(gang_line_chart,color=['#fdc086','#459ae5','#ada9a9eb']) #fdc086  #colors=['#459ae5','#a1d99b', '#ada9a9eb'],     

                    st.write(f'''
                             <div> \n
                            * 라인전 동안 전체 데스는? {len(wak_15_death)}번
                            * 그 중 <span style="color:#fdc086"> "GANG"에 의해 죽은것</span>으로 판단되는 데스는? {len(wak_death_gang)}번
                            * 그 중 <span style="color:#459ae5">와드가 사라지거나, 와드를 설치하지 않아 </span> 죽은 경우는? {len(no_warding)}번                                                      
                            > 8분 이후에 와드를 박아보는 것을 어떨까요!?

                            </div>
                            ''',unsafe_allow_html= True)

                with tab2:
                    # st.write(warding_death[warding_death['ward_placed']== False])
                    death_spot(wak_death_gang)        




                    # st.write(wak_death_gang[['timestamp','type']])
                    # st.dataframe(wak_15_death)
                    # death_spot(wak_death_jungle)

        st.divider()
        with st.container(): # CS지표
            col1,col2 = st.columns([2,1])
            with col1: 
                with elements("wak_indicator_GOLD"):                
                    layout = [
                                dashboard.Item("item1", 0, 0, 6, 2,isDraggable=True, isResizable=True ),

                                ]
                    
                    with dashboard.Grid(layout):
                        st.subheader(''' 📊 GOLD''')
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
                st.caption(f'큰 차이는 없지만 바텀 포지션을 갔을 때 CS를 상대적으로 잘먹는 편입니다.')
                CSbyPosition= summoner_20CS.groupby(['timestamp','teamPosition']).agg(
                    CS = pd.NamedAgg(column='minionsKilled', aggfunc='mean')
                ).reset_index()

                CSbyPosition['CS'] = CSbyPosition['CS'].astype(int)
                pivot_type = pd.pivot_table(CSbyPosition, values='CS', index='timestamp', columns='teamPosition')
                st.line_chart(pivot_type, use_container_width=True)
                
                
                # df['cs_rnk'] = df['totalCS10Minutes_mean'].rank(ascending=False)
                # st.write(df)
                # st.write(f'''* 10분CS가 가장 좋은 챔피언은 {df[df['cs_rnk']==1]['championName'].iloc[0]}  ''')
                
                

            #     st.subheader(''' ✔️ 15분 이후 솔로킬을 당한 좌표 ''')
                # wak_total_death = team_death_log[team_death_log['summonerName_x']==summoner_name]             
                # wak_total_death = wak_total_death[(wak_total_death['assistingParticipantIds'].isna()) & (wak_total_death['timestamp'] > 15)] 
                # st.write(wak_total_death)
                # death_spot(wak_total_death)
                # st.write(match_ids)



    if __name__ == '__main__' :
        main()

