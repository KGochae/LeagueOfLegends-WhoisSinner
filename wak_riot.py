# ----- json, dataframe ...etc ------#
import re
import json
import pandas as pd
import numpy as np
import streamlit as st
import requests
from sklearn.preprocessing import StandardScaler
import time


# ------ image matplotlib ----------- #

import matplotlib.pyplot as plt
from PIL import Image
from sklearn.preprocessing import MinMaxScaler
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from scipy.stats import gaussian_kde

# matplotlib 에러
import matplotlib
matplotlib.use('Agg')  # Use the 'agg' backend

# Create API client.
api_key  = st.secrets.RIOTAPI.api_key
version = '14.1.1'


# 매치 데이터 가져오기
def get_puuid(summoner_name, api_key):
    # Get summoner puuid
    sohwan = "https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/{}?api_key={}"
    url = sohwan.format(summoner_name, api_key)
    response = requests.get(url)
    puuid = response.json()['puuid']
    summoner_id = response.json()['id']
    iconId = response.json()['profileIconId']

    return puuid, summoner_id, iconId


def get_match_ids(puuid, api_key, start= 0, count=65):
    # Get match ids
    matchid_url = "https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{}/ids?type=ranked&start={}&count={}&api_key={}"
    url = matchid_url.format(puuid, start, count, api_key)
    response = requests.get(url)
    match_ids = response.json()
    return match_ids


def get_match_data_logs(match_ids, api_key):
    match_data_logs = []
    time_url = 'https://asia.api.riotgames.com/lol/match/v5/matches/{}/timeline?api_key={}'
    
    for i, match_id in enumerate(match_ids):
        url = time_url.format(match_id, api_key)
        response = requests.get(url)
        
        # Check if the status code is 429 (Rate Limit Exceeded)
        if response.status_code == 429:
            # Get the Retry-After header value
            retry_after = int(response.headers['Retry-After'])
            
            # Print a message or handle the delay as needed
            print(f"Rate Limit Exceeded. Waiting for {retry_after} seconds.")
            
            # Wait for the specified time before making the next API call
            time.sleep(retry_after)
            
            # Retry the API call after waiting
            response = requests.get(url)
        
        match_data_logs.append(pd.DataFrame(response.json()))

    return match_data_logs


# 유저의 랭크 , 승패
def get_rank_info (summoner_id, api_key):
    rank_info = "https://kr.api.riotgames.com/lol/league/v4/entries/by-summoner/{}?api_key={}"
    url = rank_info.format(summoner_id, api_key)
    response = requests.get(url)
    rank_data = response.json()

    return rank_data




# match_v5 (경기가 끝나고 나오는 통계요약)
def get_match_v5(match_ids,summoner_name, api_key):
    url = 'https://asia.api.riotgames.com/lol/match/v5/matches/{}?api_key={}'
    match_info_list = []
    champion_info_list = []

    for match_id in match_ids:
        response = requests.get(url.format(match_id, api_key))
        match_df = pd.DataFrame(response.json())

        try:
            df = pd.DataFrame(match_df['info']['participants'])
        except KeyError:
            print(f"KeyError: 'info' key not found in match_df for matchId {match_id}. Skipping...")
            continue

        sample = df[['teamId', 'puuid', 'summonerName', 'participantId', 'teamPosition', 'challenges', 'summoner1Id', 'summoner2Id',
            'championName', 'lane', 'kills', 'deaths', 'assists', 'totalMinionsKilled', 'neutralMinionsKilled', 'goldEarned', 'goldSpent',
            'champExperience', 'item0', 'item1', 'item2','item3', 'item4', 'item5', 'item6', 'totalDamageDealt', 'totalDamageDealtToChampions',
            'totalDamageTaken', 'damageDealtToTurrets', 'damageDealtToBuildings','totalTimeSpentDead', 'longestTimeSpentLiving', 'visionScore', 
            'win', 'timePlayed', 'damageSelfMitigated', 'totalDamageShieldedOnTeammates','totalHealsOnTeammates', 'damageDealtToObjectives']]


        challenge = pd.DataFrame(sample['challenges'].tolist())

        col = challenge[['soloKills', 'multikills', 'abilityUses', 'skillshotsDodged', 'skillshotsHit', 'enemyChampionImmobilizations', 'laneMinionsFirst10Minutes','controlWardsPlaced'
                        , 'wardTakedowns', 'effectiveHealAndShielding', 'dragonTakedowns', 'baronTakedowns', 'teamBaronKills']]
        jungle_and_etc_col = challenge.filter(regex='^jungle|Jungle|kda|Per')

        match_info = pd.concat([sample, col, jungle_and_etc_col], axis=1)
        match_info['summonerName'] = match_info.apply(lambda row: row['puuid'][:10] if row['summonerName'].strip() == '' else row['summonerName'], axis=1)

        # CS 집계
        match_info['totalCS'] = match_info['totalMinionsKilled'] + match_info['neutralMinionsKilled']
        match_info['totalCS10Minutes'] = match_info['laneMinionsFirst10Minutes'] + match_info['jungleCsBefore10Minutes']

        # match_info 에 matchid 정보추가
        match_info['matchId'] = match_df['metadata']['matchId']
        match_info['championName'] = match_info['championName'].apply(lambda x: 'Fiddlesticks' if x == 'FiddleSticks' else x)  # 피들스틱 에러
        match_info.loc[match_info['summonerName'] == '우왁굳', 'summonerName'] = '돈까스'
        match_info['win_kr'] = match_info['win'].apply(lambda x: '승리' if x == 1 else '패배')
        match_info = match_info[match_info['matchId'] != 'KR_6900203193']


        champion_info = match_info[['win','matchId', 'participantId', 'teamId', 'teamPosition', 'summonerName', 'puuid', 'championName']]
        
        # 각각의 데이터를 리스트에 추가
        match_info_list.append(match_info)
        champion_info_list.append(champion_info)

        match_info = pd.concat(match_info_list)
        champion_info = pd.concat(champion_info_list)        
        match_info = match_info[(match_info['timePlayed'] >= 1200) & (match_info['timePlayed'] < 2500)]

        # 해당 소환사의 팀을 우리팀, 나머지를 상대팀으로
        team_info = (
            champion_info.groupby(['matchId', 'teamId'])
            .filter(lambda x: any(x['summonerName'] == summoner_name))
        )[['matchId','teamId','participantId','summonerName','championName','teamPosition','win']]

        team_info['teamId'] = '우리팀'

        opponent_info = (
            champion_info.groupby(['matchId', 'teamId'])
                .filter(lambda x: not any(x['summonerName'] == summoner_name))
        )[['matchId','teamId','participantId','summonerName','championName','teamPosition','win']]

        opponent_info['teamId'] = '상대팀'

        champion_info = pd.concat([team_info, opponent_info])


    return match_info, champion_info



# 라인전 GOLD량 차이
def gold_data(match_data_logs,match_ids):
    match_data_logs = pd.concat(match_data_logs)
    frames_data = match_data_logs['info']['frames']
    matchId_data= match_data_logs['metadata']['matchId']

    all_data = pd.DataFrame()

    # 'frames'의 각 데이터에 대해 반복
    for i, frame in enumerate(frames_data):
        # 현재 프레임의 데이터 추출
        frame_data = pd.DataFrame(frame)

        # 현재 프레임의 데이터에 matchId 추가
        frame_data['matchId'] = matchId_data[i]

        # 현재 프레임의 데이터를 기존 데이터프레임에 추가
        all_data = pd.concat([all_data, frame_data])
    
    frames_list = pd.DataFrame(all_data['participantFrames'])['participantFrames'].tolist()


    # 모든 결과를 저장할 리스트 생성
    final_result = []

    for match_Id in match_ids:
        # match_Id에 해당하는 데이터만 추출
        match_data = all_data[all_data['matchId'] == match_Id]
        timestamp = match_data['timestamp']

        # participantFrames 데이터 처리
        frames_list = pd.DataFrame(match_data['participantFrames'])['participantFrames'].tolist()
        participant_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        moving_data = [[] for _ in range(len(participant_ids))]

        for frame in frames_list:
            for i, participant_id in enumerate(participant_ids):
                if str(participant_id) in frame:
                    moving_data[i].append(frame[str(participant_id)])

        moving_dfs = [pd.DataFrame(md) for md in moving_data]

        # 시간 정보 , match_Id 열 추가
        for i, moving_df in enumerate(moving_dfs):
            moving_df['timestamp'] = timestamp / 60000
            moving_df['matchId'] = match_Id

        # 결과를 리스트에 추가
        final_result.extend(moving_dfs)

    log_df = pd.concat(final_result, ignore_index=True)


    return log_df


# 진경기의 포지션별 골드차이를 가져오는 함수
def lose_match_gold_diff(log_df,summoner_name,teamPosition,champion_info):

    log_df['timestamp'] = log_df['timestamp'].astype(int)

    # GOLD 와 관련된 컬럼
    gold = log_df[['matchId','timestamp','participantId','position','totalGold','xp','level']]
    champion_info = champion_info[['matchId','participantId','teamId','teamPosition','summonerName','championName','win']]
    gold_df = pd.merge(gold, champion_info, on=['matchId', 'participantId'], how='inner')
    lose_match_list = champion_info[(champion_info['summonerName'] == summoner_name) & (champion_info['teamPosition']== teamPosition) & (champion_info['win']== False)]['matchId'].tolist()

    # 진경기 
    lose_match_gold = gold_df[gold_df['matchId'].isin(lose_match_list)].groupby(['matchId','timestamp','win','teamPosition']).agg({'totalGold':'sum'}).reset_index()

    # 팀별 골드차이
    lose_match_gold_by_team = gold_df[gold_df['matchId'].isin(lose_match_list)].groupby(['matchId','timestamp','teamId']).agg({'totalGold':'sum'}).reset_index()


    # (15분, 라인전 동안) 포지션별 골드차이
    line_lose_15 = lose_match_gold[lose_match_gold['timestamp'] < 21].sort_values(by=['matchId','timestamp','win'], ascending=[True,True,False])
    line_lose_15['totalGold_diff'] = line_lose_15.groupby(['matchId','timestamp','teamPosition'])['totalGold'].diff()
    gold_by_position = line_lose_15.groupby(['teamPosition','timestamp'])['totalGold_diff'].mean().reset_index()

    gold_df = gold_by_position[gold_by_position['teamPosition'] != '']
    gold_df['totalGold_diff'] = gold_df['totalGold_diff'].astype(int)

    
    return gold_df , lose_match_gold_by_team


# match_
def get_events(match_data_logs,champion_info,summoner_name):

    all_events_list = []  # 첫번째 매치부터 n번째 매치까지
    position_logs_list = []

    for match_data_log in match_data_logs:
        try:
            matchId = match_data_log['metadata']['matchId']
        except KeyError:
            print(f"Metadata not found for match. Skip.")
            continue  # metadata 키가 없는 경우 해당 매치 무시

        frame_df = pd.DataFrame(match_data_log['info']['frames'])
        events_df = pd.DataFrame(frame_df['events'])
        events = events_df['events'].tolist()

        events_all_participant_ids = []

        for event in events:
            for event_dict in event:
                event_dict['matchId'] = matchId  # matchId를 각 이벤트에 추가
                events_all_participant_ids.append(event_dict)

        all_events = pd.DataFrame(events_all_participant_ids)


        # 게임이 취소된 경우 컬럼이 없음
        required_columns = ['timestamp', 'type','wardType' ,'position', 'teamId','creatorId' ,'killerId', 'victimId', 'assistingParticipantIds','victimDamageDealt','victimDamageReceived', 'matchId']
        if all(column in all_events.columns for column in required_columns):
            df = all_events[(all_events['type'] == 'CHAMPION_KILL') | (all_events['type'].str.contains('WARD')|(all_events['type'] == 'ELITE_MONSTER_KILL'))]
            position_logs = df[['timestamp', 'type', 'wardType' ,'position', 'teamId', 'creatorId' ,'killerId', 'victimId', 'assistingParticipantIds','victimDamageDealt','victimDamageReceived', 'matchId']]
            position_logs_list.append(position_logs)
        else:
            print(f"취소된 매치아이디 {matchId}. Skip.")

        all_events_list.append(all_events)


        # 챔피언킬, 와드와 관련된 로그
        position_logs = pd.concat(position_logs_list)
        kill_and_ward = position_logs[(position_logs['type'] == 'CHAMPION_KILL')|(position_logs['type'].str.contains('WARD'))]
        kill_and_ward = kill_and_ward[kill_and_ward['wardType'] != 'UNDEFINED']
        kill_and_ward['timestamp'] = kill_and_ward['timestamp']/60000


        # 소환사와 같은팀 정보(vicitmId) - 죽은입장
        team_info = (
            champion_info.groupby(['matchId', 'teamId'])
            .filter(lambda x: any(x['summonerName'] == summoner_name))
        )[['matchId','teamId','participantId','summonerName','teamPosition','win']] 

        team_info.columns = ['matchId','teamId','victimId','summonerName','victimPosition','win']

        # 반대팀 정보(killerId) - 죽인입장
        opponent_info = (
            champion_info.groupby(['matchId', 'teamId'])
                .filter(lambda x: not any(x['summonerName'] == summoner_name))
        )[['matchId','teamId','participantId','summonerName','teamPosition','win']]

        opponent_info.columns = ['matchId','teamId','killerId','summonerName','killerPosition','win']


        # 전체경기(왁굳팀이 당한 기준)
        champ_kill_log = kill_and_ward[kill_and_ward['type'] == 'CHAMPION_KILL']
        team_death_log = pd.merge(champ_kill_log, team_info, on =['matchId','victimId'], how = 'inner')
        team_death_log = pd.merge(team_death_log,opponent_info, on=['matchId','killerId'], how ='inner' )

        # 소환사가 죽은 death 로그에서 어시스트 정보를 participantId 에서 teamposition 으로 변경
        def replace_ids_with_names(assistIds ,match_id):

            if isinstance(assistIds, list):
                return [opponent_info.loc[(opponent_info['killerId'] == id) & (opponent_info['matchId'] == match_id), 'killerPosition'].values[0] if pd.notna(id) else None for id in assistIds]
            else:
                return None


        team_death_log['assistingParticipantIds'] = team_death_log.apply(lambda row: replace_ids_with_names(row['assistingParticipantIds'], row['matchId']), axis=1)
        
        # 소환사의 전체 death 중에서 정글에 의해서, 혹은 정글에게 죽은 death log
        jungle_death = team_death_log[(team_death_log['killerPosition'] == 'JUNGLE') | (team_death_log['assistingParticipantIds'].apply(lambda x: 'JUNGLE' in x if isinstance(x, list) else False))]
       
        # 그 중 가장 많이 당한 포지션은?
        victim_by_jungle = jungle_death.groupby(['matchId','timestamp','victimPosition']).size().reset_index(name='cnt')


    return kill_and_ward, team_death_log, victim_by_jungle



def duo_score(kill_and_ward,champion_info,summoner_name):    
    champion_info = champion_info[['matchId','participantId','teamId','teamPosition','summonerName','championName']]
    champion_info.columns = ['matchId','killerId','teamId','killerPosition','summonerName','championName']

    nollan_match = champion_info[(champion_info['summonerName'] == 'The Nollan')&(champion_info['killerPosition'] =='JUNGLE')]['matchId'].tolist()
    chun_match = champion_info[(champion_info['summonerName'] =='돈까스') & (champion_info['killerPosition'] =='JUNGLE')]['matchId'].tolist()

    def replace_ids_with_names(ids, match_id):
        if isinstance(ids, list):
            return [champion_info.loc[(champion_info['killerId'] == id) & (champion_info['matchId'] == match_id), 'summonerName'].values[0] if pd.notna(id) else None for id in ids]
        else:
            return None

    kill_assist = pd.merge(kill_and_ward, champion_info, on=['matchId','killerId'], how='inner')
    kill_assist['assistingParticipantIds'] = kill_assist.apply(lambda row: replace_ids_with_names(row['assistingParticipantIds'], row['matchId']), axis=1)

    # 놀란과 상호작용하여 킬한 로그 (우왁굳, 놀란 킬)
    nol_kill_log = kill_assist[(kill_assist['matchId'].isin(nollan_match)) & (kill_assist['summonerName'] == summoner_name) | (kill_assist['summonerName'] == 'The Nollan')]

    # 천양과 상호작용하여 킬한 로그 (우왁굳, 천양 킬)
    chun_kill_log = kill_assist[(kill_assist['matchId'].isin(chun_match)) & (kill_assist['summonerName'] == summoner_name) | (kill_assist['summonerName'] == '돈까스')]


    return nol_kill_log, chun_kill_log




# 포지션별 전체적인 참여도 Radar chart
def radar_chart(match_info, summoner_name, position):

    match_info['jungling'] = match_info['dragonTakedowns'] + match_info['baronTakedowns'] + match_info['enemyJungleMonsterKills']
    summoner_match_info = match_info[(match_info['summonerName'] == summoner_name) & (match_info['teamPosition'] == position)] 
    matchids = summoner_match_info['matchId'].tolist() # 해당 포지션에 해당하는 경기만 가져와야함
    other_line_info = match_info[(match_info['summonerName'] != summoner_name) & (match_info['matchId'].isin(matchids)) & (match_info['teamPosition'] == position)]

    if position == 'MIDDLE':
        # 미드 지표 (평균)
        score = summoner_match_info[['summonerName', 'visionScore', 'soloKills', 'totalCS10Minutes',
                                    'totalDamageDealtToChampions', 'damageDealtToBuildings']]
        opponent_score = other_line_info[['summonerName', 'visionScore', 'soloKills', 'totalCS10Minutes',
                                        'totalDamageDealtToChampions', 'damageDealtToBuildings']]
    elif position == 'JUNGLE':
        # 정글 지표 (평균)
        score = summoner_match_info[['summonerName', 'visionScore', 'jungling', 'jungleCsBefore10Minutes',
                                    'totalDamageDealtToChampions', 'damageDealtToBuildings']]
        opponent_score = other_line_info[['summonerName', 'visionScore', 'jungling', 'jungleCsBefore10Minutes',
                                        'totalDamageDealtToChampions', 'damageDealtToBuildings']]
    else:
        # 예외 처리 혹은 다른 position에 대한 처리를 추가해야 할 수 있습니다.
        print("Unsupported position:", position)
        return None


    wak_vs_df = pd.concat([score,opponent_score])
    wak_vs_df.loc[wak_vs_df['summonerName']!= summoner_name, 'summonerName'] = '상대라이너'


    normalization_df = (wak_vs_df - wak_vs_df.min(numeric_only=True))/(wak_vs_df.max(numeric_only=True) - wak_vs_df.min(numeric_only=True))
    normalization_df['summonerName'] = wak_vs_df['summonerName']

    # position에 따라 지표 컬럼 동적으로 설정
    if position == 'MIDDLE':
        agg_columns = ['totalDamageDealtToChampions', 'totalCS10Minutes', 'soloKills', 'visionScore', 'damageDealtToBuildings']
        zcol= ['summonerName','시야점수','솔로킬','10분CS','챔피언딜량','타워피해량']
    
    elif position == 'JUNGLE':
        agg_columns = ['totalDamageDealtToChampions', 'jungleCsBefore10Minutes', 'jungling', 'visionScore', 'damageDealtToBuildings']
        zcol =['summonerName','챔피언딜량','10분CS','정글링','시야점수','타워피해량']
    else:
        agg_columns = []  # 예외 처리 혹은 다른 position에 대한 처리를 추가해야 할 수 있습니다.

    z = normalization_df.groupby(['summonerName']).agg(
        **{column: pd.NamedAgg(column=column, aggfunc='mean') for column in agg_columns}
    ).reset_index()

    z.columns = zcol

    melted_df = pd.melt(z, id_vars=["summonerName"], var_name="var", value_name="value")
    pivoted_df = melted_df.pivot(index="var", columns="summonerName", values="value").reset_index()
    radar_data = pivoted_df.to_dict("records")


    return radar_data, wak_vs_df




# 라인을 머문 점수 계산
def calculate_lane(x, y):
    top_ranges = [(500, 2000, 6000, 14000),(600, 9000, 13000, 14500), (1900,4500,11100,13100)]

    bottom_ranges = [(6000, 14000, 500, 2000),(13000,14500, 500,9000),(10500,13000,2000,3800)]

    mid_ranges = [(4500, 6000, 4500, 6000),(5200,6700,5200,6700),(5900,7400,5900,7400),(6000,8500,6000,8500),
                  (7300,8800,7300,8800),(8000,9500,8000,9500),(8700,10200,8700,10200),(9200,10500,9200,10500)]

    blue_zone = [(0,4500,0,4500)]
    red_zone = [(10500,15000,10500,15000)]

    for range_ in top_ranges:
        if range_[0] <= x <= range_[1] and range_[2] <= y <= range_[3]:
            return 'TOP'
    for range_ in mid_ranges:
        if range_[0] <= x <= range_[1] and range_[2] <= y <= range_[3]:
            return 'MIDDLE'
    for range_ in bottom_ranges:
        if range_[0] <= x <= range_[1] and range_[2] <= y <= range_[3]:
            return 'BOTTOM'
    for range_ in blue_zone:
        if range_[0] <= x <= range_[1] and range_[2] <= y <= range_[3]:
            return 'blue_zone'
    for range_ in red_zone:
        if range_[0] <= x <= range_[1] and range_[2] <= y <= range_[3]:
            return 'red_zone'
    return 'JUNGLE' # 나머지는 jungle



# 좌표데이터 데스 이미지로
def death_spot(df):

    x_data = df['position'].apply(lambda pos: pos['x'])
    y_data = df['position'].apply(lambda pos: pos['y'])


    # 그래프 그리기
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.set_xlim(0, 15000)
    ax.set_ylim(0, 15000)
    plt.axis('off')

    # 지도 이미지 추가
    map_path = 'C:/test/black_map.jpg'
    img = Image.open(map_path)
    ax.imshow(img, extent=[0, 15000, 0, 15000])


    # 이미지로 스캐터 플롯 생성
    for x, y in zip(x_data, y_data):
        url = 'img/death.png'
        img = Image.open(url)

        # 원형 이미지로 스캐터 플롯 생성
        imagebox = OffsetImage(img, zoom=0.015)  # zoom 매개변수를 조절하여 이미지 크기 조절 가능
        ab = AnnotationBbox(imagebox, (x, y), frameon=False, pad=0)
        ax.add_artist(ab)

    st.pyplot(fig)    

# 좌표데이터 밀도플롯으로
def death_spot_sc(df,color):

    x_data = df['position'].apply(lambda pos: pos['x'])
    y_data = df['position'].apply(lambda pos: pos['y'])

    # 밀도 플롯을 위한 데이터 생성
    xy = np.vstack([x_data, y_data])
    z = gaussian_kde(xy)(xy)

    # 그래프 그리기
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlim(0, 15000)
    ax.set_ylim(0, 15000)
    plt.axis('off')

    # 지도 이미지 추가
    map_path = 'img/black_map.jpg'
    img = Image.open(map_path)
    ax.imshow(img, extent=[0, 15000, 0, 15000])

    # 밀도 플롯으로 표시
    sc = ax.scatter(x_data, y_data, c=z, cmap=color, s=50)

    # colorbar 추가
    cbar = plt.colorbar(sc)
    cbar.set_label('Density')
    cbar.remove()

    # Display the Matplotlib plot in Streamlit
    st.pyplot(fig)


