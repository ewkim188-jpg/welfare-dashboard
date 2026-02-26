import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
import os

# 웹 페이지 타이틀 설정
def get_file_path(default_path):
    """폴더 경로와 루트 경로 중 존재하는 파일을 반환"""
    if os.path.exists(default_path):
        return default_path
    base_name = os.path.basename(default_path)
    if os.path.exists(base_name):
        return base_name
    return default_path

try:
    img_path = get_file_path("image/sample.png")
    img = Image.open(img_path)
    st.set_page_config(
        layout="wide", page_title="복지패널 데이터분석 시각화 대시보드", page_icon=img
    )
except Exception:
    st.set_page_config(layout="wide", page_title="복지패널 데이터분석 시각화 대시보드")

# 한글 폰트 지정 (Windows 환경)
# Streamlit Cloud(Linux) 환경에서도 한글이 나오도록 폰트 설정 추가
if os.name == 'posix': # 리눅스/맥
    plt.rc("font", family="NanumGothic")
else: # 윈도우
    plt.rc("font", family="Malgun Gothic")

# 마이너스 기호 깨짐 방지
plt.rcParams["axes.unicode_minus"] = False

# 데이터 로드 함수
@st.cache_data
def load_welfare(sav_path: str):
    # 입력된 경로가 없으면 루트에서 시도
    actual_path = get_file_path(sav_path)
    
    if not os.path.exists(actual_path):
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {actual_path}")
        
    raw_welfare = pd.read_csv(actual_path)
    welfare = raw_welfare.copy()
    welfare = welfare.rename(
        columns={
            "h10_g3": "sex",  # 성별
            "h10_g4": "birth_year",  # 태어난 연도
            "h10_g10": "marital_status",  # 혼인 상태
            "h10_g11": "religion",  # 종교
            "h10_eco9": "job_code",  # 직업 코드
            "p1002_8aq1": "income",  # 월급
            "h10_reg7": "region_code", # 지역 코드
        }
    )

    # 전처리
    if "sex" in welfare.columns:
        welfare["sex"] = welfare["sex"].replace(9, np.nan)
        welfare["sex"] = welfare["sex"].map({1: "male", 2: "female"})

    if "income" in welfare.columns:
        welfare["income"] = welfare["income"].replace(9999, np.nan)
        welfare["income"] = np.where(welfare["income"] == 0, np.nan, welfare["income"])

    if "birth_year" in welfare.columns:
        welfare["birth_year"] = welfare["birth_year"].replace(9999, np.nan)
        welfare["age"] = 2015 - welfare["birth_year"] + 1

        def age_group(age):
            if pd.isnull(age):
                return np.nan
            elif age >= 60:
                return "old"
            elif age >= 30:
                return "middle"
            else:
                return "young"

        welfare["age_group"] = welfare["age"].apply(age_group)

    if "job_code" in welfare.columns:
        welfare["job_code"] = np.where(
            welfare["job_code"] == 9999, np.nan, welfare["job_code"]
        )
        try:
            codebook_path = get_file_path("data/welfare_2015_codebook.xlsx")
            job_list = pd.read_excel(
                codebook_path, sheet_name="직종코드"
            )
            # 직업 코드 데이터에 'job' 컬럼 이름 확인 (codebook에 따라 다를 수 있음)
            if 'job' not in job_list.columns and '직종' in job_list.columns:
                job_list = job_list.rename(columns={'직종': 'job'})
            elif 'job' not in job_list.columns and job_list.shape[1] > 1:
                 # 두 번째 컬럼을 job으로 가정 (보통 코드, 이름 순이므로)
                job_list.columns = [job_list.columns[0], 'job']

            welfare = welfare.merge(job_list, how="left", on="job_code")
        except Exception:
            pass

    return welfare

# 사이드바
st.sidebar.title("데이터 로드")
default_data_path = "data/welfare_2015.csv"
if not os.path.exists(default_data_path) and os.path.exists("welfare_2015.csv"):
    default_data_path = "welfare_2015.csv"
data_path = st.sidebar.text_input("데이터 파일 경로", value=default_data_path)

if st.sidebar.button("데이터 다시 로드"):
    st.rerun()

# 메인
st.title("한국복지패널 대시보드")
st.markdown("데이터 출처: 복지패널 데이터")

# 데이터 로드 시도
try:
    welfare = load_welfare(data_path)
    st.success(f"데이터 로드 완료: {welfare.shape[0]}행 {welfare.shape[1]}열")
except FileNotFoundError:
    st.error(f"데이터 파일({data_path})을 찾을 수 없습니다.")
    st.markdown("""
    ### 📥 데이터 파일이 없으신가요?
    아래 링크에서 `welfare_2015.csv` 파일을 다운로드하여 `data` 폴더에 넣어주세요.
    - [welfare_2015.csv 다운로드](https://raw.githubusercontent.com/dswoorisam/data/master/welfare_2015.csv)
    """)
    st.stop()
except Exception as e:
    st.error(f"데이터를 불러오는 데 실패했습니다.\n에러: {e}")
    st.stop()

# 대시보드 레이아웃 & 필터
st.sidebar.header("필터")

# 연령대 필터
if "age_group" in welfare.columns:
    age_group_list = ["All"] + sorted(welfare["age_group"].dropna().unique().tolist())
    select_multi_age_group = st.sidebar.multiselect(
        "연령대 선택 (복수 선택 가능)",
        age_group_list,
        default="All"
    )
else:
    select_multi_age_group = "All"

# 직업 필터
if "job" in welfare.columns:
    job_list = ["All"] + sorted(welfare["job"].dropna().unique().tolist())
    select_multi_job = st.sidebar.multiselect(
        "직업 선택 (복수 선택 가능)",
        job_list,
        default="All"
    )
else:
    select_multi_job = "All"

# 시각화 1: 성별에 따른 월급 차이
st.subheader("1. 성별에 따른 월급 차이")
col1, col2 = st.columns([2, 1])

with col1:
    if "sex" in welfare.columns and "income" in welfare.columns:
        # 필터 적용
        curr_welfare = welfare.copy()
        if select_sex != "All":
            curr_welfare = curr_welfare[curr_welfare["sex"] == select_sex]
        
        sex_income = (
            curr_welfare.dropna(subset=["sex", "income"])
            .groupby("sex", as_index=False)
            .agg(mean_income=("income", "mean"))
        )
        
        if not sex_income.empty:
            fig1, ax1 = plt.subplots()
            sns.barplot(x="sex", y="mean_income", data=sex_income, ax=ax1)
            plt.title("성별에 따른 평균 월급")
            plt.xlabel("성별")
            plt.ylabel("평균 월급 (만원)")
            for i, j in enumerate(sex_income["mean_income"]):
                ax1.annotate(round(j), (i, j), xytext=(0, 2), textcoords="offset points", ha="center")
            st.pyplot(fig1)
        else:
            st.info("필터 조건에 맞는 데이터가 없습니다.")
    else:
        st.info("성별/월급 데이터가 부족합니다.")

with col2:
    if "sex" in welfare.columns and "income" in welfare.columns and not sex_income.empty:
        st.dataframe(sex_income)

# 시각화 2: 나이와 월급의 관계
st.subheader("2. 나이와 월급의 관계")
col3, col4 = st.columns([2, 1])

with col3:
    if "age" in welfare.columns and "income" in welfare.columns:
        age_income = (
            welfare.dropna(subset=["age", "income"])
            .groupby("age", as_index=False)
            .agg(mean_income=("income", "mean"))
        )
        fig2, ax2 = plt.subplots()
        sns.lineplot(x="age", y="mean_income", data=age_income, ax=ax2)
        plt.title("나이에 따른 평균 월급")
        plt.xlabel("나이")
        plt.ylabel("평균 월급 (만원)")
        st.pyplot(fig2)

with col4:
    if "age" in welfare.columns and "income" in welfare.columns:
        st.dataframe(age_income.head(10))

# 시각화 3: 직업별 월급 차이
st.subheader("3. 직업별 월급 차이 (상위 10개)")
col5, col6 = st.columns([2, 1])

with col5:
    if "job" in welfare.columns and "income" in welfare.columns:
        # 필터 적용
        curr_welfare_job = welfare.copy()
        if "All" not in select_multi_job and select_multi_job:
            curr_welfare_job = curr_welfare_job[curr_welfare_job["job"].isin(select_multi_job)]
            
        job_income = (
            curr_welfare_job.dropna(subset=["job", "income"])
            .groupby("job", as_index=False)
            .agg(mean_income=("income", "mean"))
        )
        
        if not job_income.empty:
            top10 = job_income.sort_values("mean_income", ascending=False).head(10)
            fig3, ax3 = plt.subplots(figsize=(10, 6))
            sns.barplot(x="mean_income", y="job", data=top10, ax=ax3)
            plt.title("평균 월급 상위 10개 직업")
            plt.xlabel("평균 월급 (만원)")
            plt.ylabel("직업")
            st.pyplot(fig3)
        else:
            st.info("필터 조건에 맞는 데이터가 없습니다.")
    else:
        st.info("직업/월급 데이터가 부족하여 분석을 진행할 수 없습니다.")

with col6:
    if "job" in welfare.columns and "income" in welfare.columns and not job_income.empty:
        st.dataframe(top10)

# 추가 분석 가이드
with st.expander("💡 추가 분석 팁"):
    st.write("""
    - **연령대별 분석**: `age_group` 변수를 활용하여 청년, 중년, 노년층의 특성을 비교해 보세요.
    - **지역별 분석**: `region_code`를 활용하여 거주 지역에 따른 생활 수준 차이를 분석할 수 있습니다.
    - **상세 데이터 확인**: 사이드바 필터를 조정하여 특정 그룹의 데이터를 심층적으로 확인해 보세요.
    """)


