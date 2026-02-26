이 프로젝트는 한국복지패널 데이터를 활용하여 성별, 연령, 직업 등 다양한 변수에 따른 경제 수준(월급) 차이를 분석하고 시각화하는 **Streamlit** 기반의 웹 대시보드입니다.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/)

## 🚀 주요 기능
- **성별 월급 분석**: 성별에 따른 평균 월급 차이를 시각화합니다.
- **연령별 월급 분석**: 나이의 변화에 따른 월급의 추이를 선 그래프로 보여줍니다.
- **상위 10개 직업 분석**: 평균 월급이 가장 높은 상위 10개 직업을 막대 그래프로 시각화합니다.
- **다양한 필터링**: 성별, 연령대, 특정 직업군을 선택하여 데이터를 심층 분석할 수 있습니다.
- **데이터 자동 로드**: 로컬 환경과 클라우드 환경 모두에서 데이터를 유연하게 불러옵니다.

## 🛠 설치 및 로컬 실행 방법

1.  **저장소 복제 또는 다운로드**:
    ```bash
    git clone https://github.com/ewkim188-jpg/welfare-dashboard.git
    cd welfare-dashboard
    ```
2.  **필수 라이브러리 설치**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **앱 실행**:
    ```bash
    streamlit run app.py
    ```

## 📂 프로젝트 구조
```text
.
├── app.py              # 메인 애플리케이션 코드
├── requirements.txt    # 설치 필요 라이브러리 목록
├── welfare_2015.csv    # 분석 데이터셋
├── welfare_2015_codebook.xlsx # 직업 코드북 데이터
├── sample.png          # 앱 아이콘 및 이미지
└── README.md           # 프로젝트 안내 문서
```

## 🌏 배포 안내
본 앱은 **Streamlit Community Cloud**를 통해 배포되었습니다. GitHub 저장소와 연결하여 누구나 웹 브라우저에서 접근할 수 있습니다.

## 📝 데이터 출처
- **한국복지패널(Koweps)** 데이터 (2015년 기준)
