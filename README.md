# HOLE2 Analysis Pipeline

이온 채널 기공 분석을 위한 HOLE 프로그램 자동화 파이프라인

## 주요 기능

- **HOLE 분석**: 단백질 구조의 이온 채널 기공 반경 자동 분석
- **그래프 생성**: matplotlib 기반 기공 프로파일 시각화
- **PyMOL 시각화**: 3D 구조 자동 렌더링 (레이어별 합성)
- **파일 관리**: 최종 출력과 중간 파일 자동 정리

## 설치

### 필수 요구사항

```bash
# Conda 환경 생성 및 활성화
conda create -n hole2 python=3.9
conda activate hole2

# 의존성 설치
conda install numpy matplotlib pyyaml pillow
conda install -c conda-forge pymol-open-source
```

### HOLE 프로그램 설치

1. HOLE 실행 파일을 `exe/` 디렉토리에 배치
2. 반지름 파일을 `rad/` 디렉토리에 배치

## 사용법

### YAML 설정 파일 작성

`hole_config.yml` 파일 예시:

```yaml
# 필수 설정
pdb_file: "protein.pdb"
output_prefix: "my_analysis"

# 반지름 파일 (rad/ 디렉토리 기준)
radius_file: "simple.rad"

# 채널 종료 반지름 (Angstrom)
endrad: 10.0

# 작업 디렉토리
work_dir: "output"
```

### 파이프라인 실행

```bash
python hole_runner.py hole_config.yml
```

## 출력 파일

### 최종 출력 (`output/` 디렉토리)

1. `{prefix}.pdb` - 원본 단백질 구조
2. `{prefix}_pore_surface.pdb` - HOLE 기공 표면 PDB
3. `{prefix}_profile.png` - 기공 반경 프로파일 그래프
4. `{prefix}_pymol.pml` - PyMOL 시각화 스크립트
5. `{prefix}_visualization.png` - 최종 렌더링 이미지

### 중간 파일 (`output/intermediate_files/` 디렉토리)

- `.inp`, `_out.txt`, `.sph`, `_surface.qpt`, `_surface.vmd_plot`, `.tsv`

## PNG 렌더링

레이어별 렌더링 방식:
- **Layer 1**: Surface (회색, 60% 투명) + Pore (반경별 색상)
- **Layer 2**: Cartoon (오렌지, 40% 투명, 투명 배경)
- **합성**: PIL alpha composite로 최종 이미지 생성
- **설정**: 800x800, DPI 200, zoom 20배

### Pore 색상 코드 (HOLE 표준)

- 🔴 RED: 좁음 (< 1.15 Å)
- 🟢 GREEN: 중간 (1.15-2.30 Å)
- 🔵 BLUE: 넓음 (> 2.30 Å)
- 🟡 YELLOW: 중심선

## 프로젝트 구조

```
hole2/
├── exe/                    # HOLE 실행 파일
├── rad/                    # 반지름 파일
├── scripts/                # 분석 스크립트
│   ├── hole_plot.py       # 그래프 생성
│   └── hole_pymol.py      # PyMOL 시각화
├── hole_runner.py          # 메인 파이프라인
├── hole_config.yml         # 설정 파일
└── output/                 # 출력 디렉토리
```

## 라이선스

이 프로젝트는 HOLE 프로그램의 공식 도구를 사용합니다.
- HOLE: http://www.holeprogram.org/

## 저자

Claude Sonnet 4.5 with Human Collaboration
