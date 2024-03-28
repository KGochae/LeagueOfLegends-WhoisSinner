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


