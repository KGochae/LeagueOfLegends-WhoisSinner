### issue..
> 이전 시즌의 데이터가 날라가.. 대시보드에 문제가 생겼습니다.

# 🖥️ LeagueOfLegends-WhoisSinner?
* ### 실제 [대시보드](https://wakgood-dashbaord.streamlit.app/)를 위 링크를 통해 구경하실 수 있으며! 정리된 내용은 pdf/ 파일안에 요약되어 있습니다! 😁 

## 디렉토리 

```bash
├── 📁.streamlit
| └── config.toml 
├── 📁 img
│ ├── death.png
| └── minimap.jpg 
├── 📁 pdf ------------------ #프로젝트를 정리한 발표자료 입니다. 
│ └── 소환사지표(ppt정리본).pdf 
├── .gitignore
├── .README.md
├── requirements.txt
├── wak.css
├── wak.py ---------- # streamlit main
└── wak_riot.py ----- # 데이터 수집 및 전처리 
```


### 🔎 들어가기전..
* 본 컨텐츠는 종합 게임 스트리머 '우왁굳'님의 롤 방송을 보던 도중 영감을 받아 재미로 만들어본 대시보드입니다..🙇🏻‍♂️
* 우왁굳님의 롤 아이디인 '메시아빠우왁굳' 소환사의 데이터를 기준으로 대시보드를 만들었습니다.
* 실제 **우왁굳님의 반응**은 위 [링크](https://vod.afreecatv.com/player/116265471)에서 보실 수 있습니다.😂

# Chapter.1 Who is sinner? 

우왁굳님이 패배한 경기.. 도대체 어떤 포지션에 의해 지는걸까요? 과연 내가 못해서 졌을까요 ?😂 \
패배한 경기 데이터를 기준으로 게임내 대표 지표들을 통해 팀운이 좋은지 나쁜지 확인해보았습니다.


## 🖥️ 대시보드 미리보기

### 👾 소환사의 기본 지표
> 그동안 만난 미드라이너 (주포지션)와의 게임지표를 비교해 보았습니다.

![image](https://github.com/KGochae/LeagueOfLegends-WhoisSinner/assets/86241587/7abad176-224f-437c-8558-3910528470d5)

## 🖥️ main info, 패배한 경기 eda

![image](https://github.com/KGochae/LeagueOfLegends-WhoisSinner/assets/86241587/67316088-83a7-4fc8-ba24-4d76c3128733)

### 💰누가 범인인가 ? - GOLD
> 범인을 찾는데 대표적인 지표는 포지션별 골드차이 입니다! 리그 오브 레전드 에서 GOLD는 챔피언/타워 킬, CS/몬스터 등을 통해 수급하며 상대적인 실력차이를 나타내는 가장 대표적인 지표입니다!
> 20분동안의 GOLD 차이를 포지션별로 시각화 해보았습니다.

![image](https://github.com/KGochae/LeagueOfLegends-WhoisSinner/assets/86241587/983b4886-45f5-4b48-b219-d7f007676d32)

### ☠️누가 범인인가 ? - DEATH 1
> 라인전후로 DEATH를 가장 많이한 포지션은 누구일까요?

![image](https://github.com/KGochae/LeagueOfLegends-WhoisSinner/assets/86241587/6de0f1a6-37b9-4bae-9f4a-d6168556824c)

### ☠️누가 범인인가 ? - DEATH 2
> 게임 후반부에 짤리는 포지션, 라인전 동안 적정글에게 가장 많이 죽은 포지션, 그리고 흑백화면을 가장 많이 본 포지션은 누구일까요?

![image](https://github.com/KGochae/LeagueOfLegends-WhoisSinner/assets/86241587/e5ab0588-2c8e-4578-8b6b-940efffb7b78)

> *  범인일 확률이 높은 포지션들.. 어디서 죽었을까요? 좌표들을 EDA 해보았습니다.  

![image](https://github.com/KGochae/LeagueOfLegends-WhoisSinner/assets/86241587/5f88d48a-1d50-4abe-875a-72faa62bca95)

# 📊 Chapter 2. 소환사 성장 지표

> 과거경기와 최근 경기의 비교를 통해 얼마나 과거의 비해 얼마나 성장했는지 대시보드로 구성해보았습니다. (그리고 언젠가 만날 'FAKER'님과 대표적인 게임 지표들과 함께 말이죠😂!)
> 그리고 부족한 부분은 무엇인지 우왁굳님의 데이터를 통해 게임 내 대표 지표들을 분석하고 피드백 해보았습니다.

#### ① 공격지표
![image](https://github.com/KGochae/LeagueOfLegends-WhoisSinner/assets/86241587/dd379dbe-faf7-48e2-9272-b5288fd0f259)

#### ② 시야점수
![image](https://github.com/KGochae/LeagueOfLegends-WhoisSinner/assets/86241587/1924d8ba-ea23-42e9-bf4d-e88f9ebcd842)

#### ③ GOLD
![image](https://github.com/KGochae/LeagueOfLegends-WhoisSinner/assets/86241587/cd40d5cc-4abb-4176-a484-6bc9a934d1b7)





## 시야에 특히 약하다
해당 유저의 시야지표가 특히 낮기 때문에 이와 관련해서 데이터를 좀 더 분석해보고 싶었던 주제가 있었습니다. 바로 **정글 포지션에게 갱을 당한 경우** 입니다
* 리그 오브 레전드에서 시야점수가 부족해서 일어날 수 있는 상황이 있는데요! 대표적으로 적이 어디있는지 파악이 되지 않아 갱에 당하는 경우라고 할 수 있습니다.
* 이처럼 와드를 박지 않아서 죽은 경우도 있는지 궁금했습니다!

그렇다면 "와드를 박지 않아서 죽었다"고 판단하는 기준은 다음과 같습니다.
* 라인전 중에서 다른 라이너들에게 CHAMPION_KILL 을 당하기 전에 WARDING의 여부 (즉, WARD가 살아 있는지 Check 하여 집계하였습니다)

> 결과를 보면 4~6분 이후에 정글갱에 당한 죽음이 특히 많은 것을 볼 수 있었습니다.
![image](https://github.com/user-attachments/assets/ab0eee0e-b56d-4eab-bdd0-03115187c4a5)







# 그럼에도 불구하고..!!

![image](https://github.com/user-attachments/assets/b0507260-3118-4d0c-982e-0a2556147ba0)


특히, 6분 이후, 정글갱에의해 죽은 경우가 많으신 우왁굳님에게 정글동선에 관한 피드백을 한번 드려보았습니다. (30경기 기준) 아래는 RED, BLUE 팀 정글러의 위치를 TIMESTAMP (분) 대로 집계한 결과 인데요! 실제로 4분 이후 바위게 싸움 그리고 6분대 공허 유충 킬로그가 많은것을 볼 수 있었습니다. 아무래도 해당 시간대에는 정글러의 위치가 상대적으로 미드,탑에 가까운 위치이므로 조심해야합니다!

> 또한, 리그 오브 레전드의 기본 와드 지속 시간은 초반 2분대라고 알고 있는데요! 해당 정글러의 위치를 생각 하고 4~6분 구간에 와드를 박는것이 좋아 보입니다. (물론 정글의 동선은 유동적이므로 항상 맵리딩을 합시다!)

