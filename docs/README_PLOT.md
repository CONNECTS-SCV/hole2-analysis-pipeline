# HOLE 결과 시각화

HOLE 분석 결과를 2D 그래프로 시각화하는 도구입니다.

## 기능

1. **데이터 추출**: HOLE 출력 파일에서 기공 반경 프로파일 데이터 추출
2. **TSV 파일 생성**: 엑셀/스프레드시트에서 열 수 있는 TSV 파일 생성
3. **2D 그래프**: 채널 좌표 vs 기공 반경 그래프 생성
4. **비교 그래프**: 여러 분석 결과를 하나의 그래프로 비교

## 빠른 시작

### 1. 기본 사용법

```bash
# conda 환경 활성화
conda activate hole2

# 또는 직접 Python 경로 사용
/home/connects/miniforge3/envs/hole2/bin/python hole_plot.py <HOLE_output_file>
```

### 2. 예시

```bash
# HOLE 실행
python3 run_hole_from_yaml.py

# 결과 시각화
/home/connects/miniforge3/envs/hole2/bin/python hole_plot.py output/my_analysis_out.txt
```

자동으로 생성됨:
- `output/my_analysis.tsv` - TSV 데이터 파일
- `output/my_analysis_profile.png` - 그래프 이미지

## Python에서 사용

```python
from hole_plot import plot_hole_profile, extract_hole_data, save_tsv

# 1. 데이터만 추출
data = extract_hole_data("hole_out.txt")
print(f"최소 반경: {min(data['radius']):.2f} Å")

# 2. TSV 파일 생성
save_tsv("hole_out.txt", "pore_data.tsv")

# 3. 그래프 그리기
plot_hole_profile("hole_out.txt",
                  title="My Channel Analysis",
                  save_as="my_plot.png")

# 4. 커스텀 설정
plot_hole_profile("hole_out.txt",
                  title="Gramicidin A Channel",
                  xlabel="Channel Coordinate (Å)",
                  ylabel="Pore Radius (Å)",
                  figsize=(12, 7),
                  dpi=300,
                  save_as="high_res_plot.png",
                  highlight_minimum=True)
```

## 여러 결과 비교

```python
from hole_plot import plot_multiple_profiles

# 여러 시뮬레이션 결과 비교
output_files = [
    "frame_0/hole_out.txt",
    "frame_100/hole_out.txt",
    "frame_200/hole_out.txt"
]

labels = ["0 ns", "100 ns", "200 ns"]

plot_multiple_profiles(output_files,
                      labels=labels,
                      title="Channel Dynamics",
                      save_as="comparison.png")
```

## 출력 형식

### TSV 파일 (엑셀에서 열기)

```
channel_coord   radius  cen_line_d  sum_s_area  type
-16.01225       3.69861 -18.23637   0.00291     sampled
-15.88725       3.60907 -18.10865   0.00596     mid-point
...
```

열 설명:
- **channel_coord**: 채널 좌표 (채널 벡터 방향)
- **radius**: 기공 반경 (Å)
- **cen_line_d**: 중심선을 따라 측정한 거리
- **sum_s_area**: 전도도 예측에 사용되는 값
- **type**: sampled 또는 mid-point

### PNG 그래프

- X축: 채널 좌표 (Å)
- Y축: 기공 반경 (Å)
- 최소 반경 위치가 빨간 별표로 표시됨
- Sampled 포인트: 파란 점
- Mid-point 포인트: 연한 파란 사각형

## 엑셀/LibreOffice에서 그래프 그리기

TSV 파일을 사용하여 직접 그래프를 그릴 수 있습니다:

```bash
# TSV 파일만 생성
/home/connects/miniforge3/envs/hole2/bin/python -c "
from hole_plot import save_tsv
save_tsv('output/my_analysis_out.txt', 'pore_data.tsv')
"

# LibreOffice에서 열기
libreoffice --calc pore_data.tsv
```

또는 명령줄에서:
```bash
# egrep으로 데이터 추출 (전통적인 방법)
egrep "mid-|sampled" output/my_analysis_out.txt > hole_data.tsv
```

## API 참조

### extract_hole_data(output_file)

HOLE 출력 파일에서 데이터 추출

**반환값**:
```python
{
    'channel_coord': np.array([...]),  # 채널 좌표
    'radius': np.array([...]),          # 기공 반경
    'cen_line_d': np.array([...]),      # 중심선 거리
    'sum_s_area': np.array([...]),      # 전도도 계산용
    'type': [...],                      # 'sampled' 또는 'mid-point'
    'all_data': [...],                  # 전체 데이터
    'sampled_only': [...],              # sampled만
    'midpoint_only': [...]              # mid-point만
}
```

### plot_hole_profile(output_file, **options)

2D 그래프 생성

**파라미터**:
- `output_file` (str): HOLE 출력 파일
- `title` (str): 그래프 제목
- `xlabel`, `ylabel` (str): 축 레이블
- `figsize` (tuple): 그래프 크기, 기본 (10, 6)
- `dpi` (int): 해상도, 기본 150
- `save_as` (str): 저장 파일명
- `show_grid` (bool): 그리드 표시, 기본 True
- `show_points` (bool): 데이터 포인트 표시, 기본 True
- `highlight_minimum` (bool): 최소값 강조, 기본 True

### save_tsv(output_file, tsv_file=None)

TSV 파일 생성

**반환값**: 생성된 TSV 파일 경로

### plot_multiple_profiles(output_files, labels=None, **options)

여러 결과 비교 그래프

**파라미터**:
- `output_files` (list): HOLE 출력 파일 리스트
- `labels` (list): 각 파일의 레이블 (기본: 파일명)

## 의존성

hole2 conda 환경에 설치됨:
- Python 3.11
- matplotlib 3.10+
- numpy 2.4+
- PyYAML 6.0+

## 참고

HOLE 프로그램: https://www.holeprogram.org/

논문:
- Smart OS, Goodfellow JM, Wallace BA (1993). The pore dimensions of gramicidin A. Biophys J 65:2455-2460.
