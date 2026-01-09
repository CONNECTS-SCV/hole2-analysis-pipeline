# HOLE Analysis with YAML Configuration

YAML 설정 파일을 사용하여 HOLE 기공 분석을 간편하게 실행할 수 있습니다.

## 빠른 시작

### 1. 설정 파일 수정

`hole_config.yml` 파일을 열어서 수정하세요:

```yaml
# 필수 설정
pdb_file: "your_protein.pdb"      # 분석할 PDB 파일
output_prefix: "my_analysis"       # 출력 파일 이름

# 선택 설정
radius_file: "simple.rad"          # 반지름 파일
endrad: 5.0                        # 채널 종료 반지름 (Å)
work_dir: "output"                 # 결과 저장 디렉토리
```

### 2. 실행

```bash
python3 run_hole_from_yaml.py
```

또는 커스텀 설정 파일 사용:

```bash
python3 run_hole_from_yaml.py my_config.yml
```

## 사용 방법

### 방법 1: YAML 파일 사용 (추천)

1. **설정 파일 준비**
   ```bash
   # hole_config.yml 파일이 있는지 확인
   ls hole_config.yml
   ```

2. **설정 수정**
   ```yaml
   pdb_file: "examples/01_gramicidin_1grm/1grm_single.pdb"
   output_prefix: "gramicidin_test"
   radius_file: "simple.rad"
   endrad: 5.0
   work_dir: "output"
   ```

3. **실행**
   ```bash
   python3 run_hole_from_yaml.py
   ```

### 방법 2: 대화형 모드

설정 파일 없이 실행하면 대화형으로 입력받습니다:

```bash
python3 run_hole_from_yaml.py
```

프롬프트에 따라 입력:
```
PDB 파일 경로: my_protein.pdb
출력 파일 접두사 [analysis]: my_analysis
반지름 파일 선택:
  1. simple.rad (추천)
  2. amberuni.rad
  ...
선택 [1]: 1
...
```

## 설정 파일 상세

### 필수 설정

```yaml
# PDB 파일 경로
pdb_file: "protein.pdb"

# 출력 파일 접두사
# 결과: {output_prefix}_out.txt, {output_prefix}.sph
output_prefix: "analysis"
```

### 기본 설정

```yaml
# 반지름 파일 선택
# - simple.rad (기본, 추천)
# - amberuni.rad
# - bondi.rad
# - hardcore.rad (작은 반지름 → 넓은 기공)
# - xplor.rad
radius_file: "simple.rad"

# 채널 종료 반지름 (Angstrom)
# - 좁은 이온 채널: 5.0
# - 넓은 채널: 10.0 ~ 15.0
endrad: 5.0

# 작업 디렉토리
work_dir: "output"
```

### 고급 설정

```yaml
# 채널 방향 벡터 수동 지정
# 자동 탐지가 실패할 때만 사용
cvect: [0.0, 0.0, 1.0]  # Z축 방향

# 채널 시작점 수동 지정
cpoint: [10.0, 20.0, 30.0]  # X, Y, Z 좌표

# 샘플링 간격 (Angstrom)
# 작을수록 정밀, 클수록 빠름
sample: 0.125

# 무시할 잔기 목록
ignore:
  - HOH    # 물 분자
  - SOL    # 용매
  - NA     # 나트륨
  - CL     # 염소

# SPH 파일 생성 여부
generate_sph: true

# 타임아웃 (초)
timeout: 120
```

## 설정 예시

### 예시 1: 기본 이온 채널 분석

```yaml
pdb_file: "channel.pdb"
output_prefix: "ion_channel"
radius_file: "simple.rad"
endrad: 5.0
work_dir: "results"
```

### 예시 2: 넓은 채널 (트랜스포터)

```yaml
pdb_file: "transporter.pdb"
output_prefix: "transporter"
radius_file: "simple.rad"
endrad: 15.0  # 큰 분자 통과 가능
work_dir: "transporter_results"
```

### 예시 3: 물 분자 제외

```yaml
pdb_file: "protein.pdb"
output_prefix: "no_water"
radius_file: "simple.rad"
endrad: 5.0
ignore:
  - HOH
  - WAT
work_dir: "output"
```

### 예시 4: 방향 수동 지정

```yaml
pdb_file: "membrane_protein.pdb"
output_prefix: "membrane"
radius_file: "simple.rad"
cvect: [1.0, 0.0, 0.0]  # X축 방향
cpoint: [50.0, 30.0, 20.0]  # 시작점
endrad: 7.0
work_dir: "membrane_results"
```

### 예시 5: 고정밀 분석

```yaml
pdb_file: "precise_analysis.pdb"
output_prefix: "high_precision"
radius_file: "simple.rad"
sample: 0.05  # 정밀한 샘플링
endrad: 5.0
timeout: 300  # 더 긴 타임아웃
work_dir: "precise_output"
```

## 출력 파일

실행 후 생성되는 파일들:

```
work_dir/
├── {output_prefix}.inp         # HOLE 입력 파일
├── {output_prefix}_out.txt     # 주 결과 파일
└── {output_prefix}.sph         # 시각화용 구 중심 파일 (선택)
```

### 결과 파일 내용

**{output_prefix}_out.txt**
- 각 위치별 기공 반지름 데이터
- 최소 기공 반지름
- 예측 전도도
- 상세 분석 로그

**{output_prefix}.sph**
- 기공 중심선 좌표 (PDB 형식)
- VMD, PyMOL에서 시각화 가능

## 결과 해석

프로그램 실행 후 출력:

```
============================================================
✓ HOLE 분석 완료!
============================================================
출력 파일: output/my_analysis_out.txt
SPH 파일:  output/my_analysis.sph

최소 기공 반지름: 1.199 Å
예측 전도도:      270.0 pS
============================================================
```

- **최소 기공 반지름**: 채널의 가장 좁은 지점
  - < 2 Å: 매우 좁음 (작은 이온만 통과)
  - 2-5 Å: 좁음 (일반적인 이온 채널)
  - > 5 Å: 넓음 (큰 분자 통과 가능)

- **예측 전도도**: 1M KCl 기준 전기 전도도 (pS)

## 문제 해결

### "PDB 파일을 찾을 수 없습니다"

설정 파일의 `pdb_file` 경로 확인:
```yaml
# 절대 경로
pdb_file: "/home/user/data/protein.pdb"

# 상대 경로 (현재 디렉토리 기준)
pdb_file: "protein.pdb"

# ~ 사용 가능
pdb_file: "~/data/protein.pdb"
```

### "반지름 파일을 찾을 수 없습니다"

반지름 파일명 확인:
```yaml
# 올바른 예시
radius_file: "simple.rad"      # ✓
radius_file: "amberuni.rad"    # ✓

# 잘못된 예시
radius_file: "simple"          # ✗ (.rad 확장자 필요)
```

### "채널 방향 탐지 실패"

수동으로 방향 지정:
```yaml
cvect: [0.0, 0.0, 1.0]  # Z축
cpoint: [x, y, z]        # 채널 내부의 한 점
```

### 타임아웃 발생

큰 단백질의 경우 타임아웃 증가:
```yaml
timeout: 300  # 5분
```

## 추가 도구

### 기존 hole_runner.py 사용

Python 코드에서 직접 호출:

```python
from hole_runner import run_hole

result = run_hole(
    pdb_file="protein.pdb",
    output_prefix="my_analysis",
    endrad=5.0
)

if result['success']:
    print(f"최소 반지름: {result['min_radius']}")
```

## 참고 자료

- HOLE 공식 문서: https://www.holeprogram.org/
- 논문: Smart OS, Goodfellow JM, Wallace BA (1993) Biophys J 65:2455-2460

## 라이센스

HOLE 프로그램: Apache License 2.0
