# HOLE2 설치 및 설정 가이드

## 가상환경 설정 (완료됨)

HOLE2 작업을 위한 독립적인 Python 가상환경이 생성되어 있습니다.

### 가상환경 활성화

```bash
cd ~/MODEL/hole2
source activate_hole2.sh
```

또는 직접:

```bash
cd ~/MODEL/hole2
source hole2_env/bin/activate
```

### 가상환경 종료

```bash
deactivate
```

## 설치된 구성 요소

### 1. HOLE 프로그램 (바이너리)
```
exe/hole                    # HOLE 실행 파일
rad/simple.rad              # 반지름 파일들
```

### 2. Python 스크립트
```
hole_runner.py              # Python API
run_hole_from_yaml.py       # YAML 기반 실행
```

### 3. Python 패키지 (가상환경 내)
```
PyYAML 6.0.3               # YAML 파일 파싱
```

## 빠른 시작

### 1. 가상환경 활성화

```bash
source activate_hole2.sh
```

### 2. 설정 파일 수정

`hole_config.yml` 파일 열기:

```yaml
pdb_file: "your_protein.pdb"
output_prefix: "my_analysis"
radius_file: "simple.rad"
endrad: 5.0
work_dir: "output"
```

### 3. 실행

```bash
python3 run_hole_from_yaml.py
```

## 디렉토리 구조

```
~/MODEL/hole2/
├── hole2_env/                 # 가상환경 (자동 생성됨)
│   ├── bin/
│   │   ├── python3
│   │   ├── pip
│   │   └── activate
│   └── lib/
│       └── python3.*/
│           └── site-packages/
│               └── yaml/      # PyYAML
│
├── exe/                       # HOLE 바이너리
│   └── hole
│
├── rad/                       # 반지름 파일들
│   ├── simple.rad
│   ├── amberuni.rad
│   └── ...
│
├── examples/                  # 예제 파일들
│   └── 01_gramicidin_1grm/
│       └── 1grm_single.pdb
│
├── activate_hole2.sh          # 가상환경 활성화 스크립트
├── hole_config.yml            # YAML 설정 파일
├── run_hole_from_yaml.py      # YAML 실행 스크립트
├── hole_runner.py             # Python API
├── README_YAML.md             # 사용 설명서
├── SETUP.md                   # 이 파일
│
└── output/                    # 결과 저장 (자동 생성)
    ├── *.inp
    ├── *_out.txt
    └── *.sph
```

## 사용 예시

### 예시 1: 기본 사용

```bash
# 1. 가상환경 활성화
source activate_hole2.sh

# 2. HOLE 실행
python3 run_hole_from_yaml.py

# 3. 가상환경 종료
deactivate
```

### 예시 2: 커스텀 설정

```bash
# 1. 활성화
source activate_hole2.sh

# 2. 커스텀 YAML 파일 생성
cat > my_protein.yml << EOF
pdb_file: "path/to/my_protein.pdb"
output_prefix: "my_protein"
radius_file: "simple.rad"
endrad: 5.0
work_dir: "my_results"
EOF

# 3. 실행
python3 run_hole_from_yaml.py my_protein.yml

# 4. 종료
deactivate
```

### 예시 3: Python API 사용

```bash
# 1. 활성화
source activate_hole2.sh

# 2. Python에서 직접 사용
python3 << EOF
from hole_runner import run_hole

result = run_hole(
    pdb_file="protein.pdb",
    output_prefix="api_test",
    endrad=5.0
)

if result['success']:
    print(f"최소 반지름: {result['min_radius']} Å")
EOF

# 3. 종료
deactivate
```

## 문제 해결

### 가상환경이 활성화되지 않음

```bash
# 수동으로 활성화
cd ~/MODEL/hole2
source hole2_env/bin/activate
```

### PyYAML이 없다는 오류

```bash
# 가상환경 활성화 후
pip install pyyaml
```

### 가상환경 재생성

기존 가상환경 삭제 후 재생성:

```bash
cd ~/MODEL/hole2
rm -rf hole2_env
python3 -m venv hole2_env
source hole2_env/bin/activate
pip install pyyaml
```

## 가상환경 장점

1. **독립성**: 시스템 Python과 분리된 환경
2. **깔끔함**: 필요한 패키지만 설치
3. **재현성**: 동일한 환경 쉽게 재생성
4. **충돌 방지**: 다른 프로젝트와 패키지 충돌 없음

## 추가 패키지 설치 (필요시)

```bash
# 가상환경 활성화 후
source activate_hole2.sh

# 패키지 설치
pip install numpy pandas matplotlib

# 설치된 패키지 확인
pip list
```

## 체크리스트

설치가 제대로 되었는지 확인:

- [ ] 가상환경 생성됨: `ls hole2_env/`
- [ ] 활성화 스크립트 작동: `source activate_hole2.sh`
- [ ] PyYAML 설치됨: `pip list | grep PyYAML`
- [ ] HOLE 실행 파일 존재: `ls exe/hole`
- [ ] Python 스크립트 존재: `ls *.py`
- [ ] 예제 실행 성공: `python3 run_hole_from_yaml.py`

모두 체크되면 준비 완료!

## 참고

- HOLE 공식 사이트: https://www.holeprogram.org/
- 가상환경 문서: https://docs.python.org/3/library/venv.html
