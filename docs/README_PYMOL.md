# HOLE to PyMOL Visualization

HOLE 분석 결과를 PyMOL에서 3D 시각화하는 도구

## 기능

1. **기공 표면 PDB 생성**: `.sph` 파일에서 3D 표면 좌표 생성
2. **색상 기반 표현**: 기공 반경에 따른 자동 색상 지정
3. **PyMOL 스크립트**: 자동 시각화 스크립트 생성
4. **두 가지 모드**: 고밀도 표면 / 가벼운 메쉬

## 빠른 시작

### 1. 기본 사용법

```bash
# HOLE 분석 실행 (sph 파일 생성)
python3 run_hole_from_yaml.py

# PyMOL 시각화 파일 생성
python3 hole_pymol.py output/my_analysis.sph

# PyMOL에서 열기
pymol output/my_analysis_pymol.pml
```

## 출력 파일

### 1. 고밀도 표면 PDB
- `{prefix}_pore_surface.pdb` (약 750KB)
- surface 시각화용
- 9,000~10,000개 포인트

### 2. 가벼운 메쉬 PDB
- `{prefix}_pore_mesh.pdb` (약 400KB)
- mesh 시각화용
- 5,000개 포인트

### 3. PyMOL 스크립트
- `{prefix}_pymol.pml`
- 자동 시각화 스크립트

## 색상 코드

HOLE 표준 색상 규칙:

| 색상 | 반경 범위 | 의미 |
|------|-----------|------|
| **빨강** | < 1.15 Å | 물 분자 통과 불가 (너무 좁음) |
| **초록** | 1.15-2.30 Å | 물 분자 1개 (단일 파일) |
| **파랑** | > 2.30 Å | 물 분자 2개 이상 (넓음) |

## Python에서 사용

### 기본 사용

```python
from hole_pymol import create_pore_pdb, create_pymol_script

# 1. 기공 표면 PDB 생성
result = create_pore_pdb(
    sph_file="hole_out.sph",
    output_pdb="pore_surface.pdb",
    density=15,      # 표면 밀도
    subsample=1      # 1=전체, 2=절반
)

print(f"생성된 포인트: {result['n_points']}")
print(f"빨강: {result['n_red']}, 초록: {result['n_green']}, 파랑: {result['n_blue']}")

# 2. PyMOL 스크립트 생성
create_pymol_script(
    protein_pdb="protein.pdb",
    pore_pdb="pore_surface.pdb",
    output_script="visualize.pml",
    protein_style="cartoon",  # cartoon, ribbon, lines, sticks
    pore_style="surface"      # surface, mesh, dots, spheres
)
```

### 가벼운 메쉬 버전

```python
from hole_pymol import create_pore_mesh_pdb

# 메쉬 PDB 생성 (더 가벼움)
create_pore_mesh_pdb(
    sph_file="hole_out.sph",
    output_pdb="pore_mesh.pdb",
    n_segments=16    # 원형 세그먼트 수
)
```

### 밀도 조절

```python
# 고밀도 (더 부드러운 표면, 더 큰 파일)
create_pore_pdb("hole.sph", "dense.pdb", density=20, subsample=1)

# 저밀도 (빠르고 가벼움)
create_pore_pdb("hole.sph", "light.pdb", density=10, subsample=2)
```

## PyMOL 명령어

### 스크립트 실행 후 사용 가능한 명령

```python
# 투명도 조절
set transparency, 0.5, pore

# 표현 방식 변경
show mesh, pore        # 메쉬로 변경
show surface, pore     # 표면으로 변경
show dots, pore        # 점으로 변경
show spheres, pore     # 구체로 변경

# 색상 조절
color red, pore and chain R
color green, pore and chain G
color blue, pore and chain B

# 렌더링
ray                    # 고품질 렌더링
ray 1920, 1080        # 특정 해상도

# 이미지 저장
png output.png, dpi=300
```

### 수동 로드

```python
# PyMOL에서 수동으로 로드
load protein.pdb
load pore_surface.pdb

# 표현 설정
hide everything
show cartoon, protein
show surface, pore_surface

# 색상
color red, pore_surface and chain R
color green, pore_surface and chain G
color blue, pore_surface and chain B
```

## 시각화 팁

### 1. 투명도 조절

```python
# 기공만 보기
set transparency, 0.0, pore
set cartoon_transparency, 0.8, protein

# 단백질만 보기
set transparency, 0.9, pore
set cartoon_transparency, 0.0, protein
```

### 2. 특정 색상만 보기

```python
# 좁은 부분만 보기 (빨강)
hide everything, pore
show surface, pore and chain R
color red, pore and chain R

# 넓은 부분만 보기 (파랑)
hide everything, pore
show surface, pore and chain B
color blue, pore and chain B
```

### 3. 메쉬 + 표면 조합

```python
# 표면은 투명하게, 메쉬는 선명하게
load pore_surface.pdb
load pore_mesh.pdb

show surface, pore_surface
set transparency, 0.7, pore_surface

show mesh, pore_mesh
set transparency, 0.0, pore_mesh
```

### 4. 고품질 이미지 생성

```python
# 설정
bg_color white
set ray_shadows, 1
set ray_trace_mode, 1
set antialias, 2
set depth_cue, 0

# 렌더링
ray 3000, 3000
png figure.png, dpi=300
```

## 워크플로우 예시

### 완전한 시각화 파이프라인

```bash
# 1. HOLE 분석
python3 run_hole_from_yaml.py

# 2. 그래프 생성
/home/connects/miniforge3/envs/hole2/bin/python hole_plot.py output/my_analysis_out.txt

# 3. PyMOL 시각화 파일 생성
python3 hole_pymol.py output/my_analysis.sph

# 4. PyMOL에서 열기
pymol output/my_analysis_pymol.pml
```

### Python 스크립트로 전체 자동화

```python
from hole_runner import run_hole
from hole_plot import plot_hole_profile
from hole_pymol import create_pore_pdb, create_pymol_script

# 1. HOLE 실행
result = run_hole("protein.pdb", output_prefix="channel", work_dir="results")

if result['success']:
    # 2. 그래프
    plot_hole_profile(result['output_file'], save_as="results/profile.png")

    # 3. PyMOL 시각화
    create_pore_pdb(result['sph_file'], "results/pore.pdb")
    create_pymol_script(result['pdb_file'], "results/pore.pdb",
                       "results/view.pml")

    print("완료! PyMOL 실행:")
    print("  pymol results/view.pml")
```

## 문제 해결

### "No spheres found in sph file"

`.sph` 파일이 비어있거나 형식이 잘못됨:

```bash
# sph 파일 확인
grep ATOM my_analysis.sph | head

# HOLE 재실행 (sphpdb 옵션 확인)
```

### 표면이 너무 거칠거나 부드럽지 않음

```python
# 밀도 조절
create_pore_pdb("hole.sph", "pore.pdb", density=20)  # 더 부드럽게

# 또는 PyMOL에서
set surface_quality, 2
```

### 파일이 너무 큼

```python
# 서브샘플링
create_pore_pdb("hole.sph", "pore.pdb", subsample=2)  # 절반만

# 또는 메쉬 버전 사용
create_pore_mesh_pdb("hole.sph", "pore.pdb")
```

### 색상이 안 보임

```python
# PyMOL에서 확인
select red_pore, pore and chain R
select green_pore, pore and chain G
select blue_pore, pore and chain B

# 각각 확인
show surface, red_pore
color red, red_pore
```

## 알고리즘

### Fibonacci Sphere

표면 포인트는 Fibonacci sphere 알고리즘으로 생성되어 균일한 분포를 보장합니다:

```python
# 각 구체에서
n_points = density × radius²
# Golden angle을 사용한 균일 분포
phi = π × (3 - √5)
```

## 성능

### 파일 크기 비교

| 모드 | 포인트 수 | 파일 크기 | 용도 |
|------|-----------|-----------|------|
| 고밀도 표면 | ~10,000 | ~750KB | Surface |
| 가벼운 메쉬 | ~5,000 | ~400KB | Mesh |
| 저밀도 표면 | ~3,000 | ~250KB | 빠른 프리뷰 |

### 처리 시간

- 320개 구체 처리: ~1초
- 고밀도 표면 생성: ~2초
- PyMOL 로딩: ~1초

## 참고

- HOLE: https://www.holeprogram.org/
- PyMOL: https://pymol.org/
- Fibonacci Sphere: https://stackoverflow.com/q/9600801
