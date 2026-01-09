#!/usr/bin/env python3
"""
HOLE to PyMOL Visualization (공식 HOLE sph_process 사용)

HOLE의 공식 도구인 sph_process와 qpt_conv를 사용하여
표면 점을 생성하고 PyMOL 형식으로 변환합니다.
"""

import subprocess
import re
from pathlib import Path
import pexpect


# HOLE 실행 파일 경로
HOLE_EXE_DIR = Path(__file__).parent.parent / "exe"
SPH_PROCESS = HOLE_EXE_DIR / "sph_process"
QPT_CONV = HOLE_EXE_DIR / "qpt_conv"


def run_sph_process(sph_file, qpt_file, dotden=15):
    """
    HOLE sph_process로 표면 점 생성

    Parameters
    ----------
    sph_file : str
        입력 .sph 파일
    qpt_file : str
        출력 .qpt 파일
    dotden : int
        표면 점 밀도 (5-30)

    Returns
    -------
    bool
        성공 여부
    """
    cmd = [str(SPH_PROCESS), "-dotden", str(dotden), "-color", str(sph_file), str(qpt_file)]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error: sph_process 실행 실패")
        print(result.stderr)
        return False

    print(f"✓ sph_process 완료")
    return True


def convert_qpt_to_vmd(qpt_file, vmd_file):
    """
    qpt_conv로 VMD 형식 변환 (pexpect 사용)

    Parameters
    ----------
    qpt_file : str
        입력 .qpt 파일
    vmd_file : str
        출력 .vmd_plot 파일 (원하는 경로)

    Returns
    -------
    bool
        성공 여부
    """
    qpt_path = Path(qpt_file)
    work_dir = qpt_path.parent

    # qpt_conv는 기본적으로 입력 파일명.vmd_plot으로 저장
    default_output = work_dir / f"{qpt_path.stem}.vmd_plot"

    try:
        # pexpect로 대화형 프로그램 실행
        child = pexpect.spawn(str(QPT_CONV), cwd=str(work_dir), timeout=60, encoding='utf-8')

        # 첫 번째 입력: D (VMD 형식 선택)
        child.expect('Enter conversion option character')
        child.sendline('D')

        # 두 번째 입력: qpt 파일명 입력 (엔터로 기본값 사용)
        child.expect('Please enter input binary hydra/quanta plot')
        child.sendline('')  # 기본값 사용

        # 세 번째 입력: 출력 파일명 (엔터 = 기본값)
        child.expect('vmd format file')
        child.sendline('')

        # 네 번째 입력: 파일 존재시 덮어쓰기 옵션 또는 선 두께
        index = child.expect(['Enter option', 'What width do you want lines to appear'], timeout=10)
        if index == 0:  # 파일 존재 - 덮어쓰기
            child.sendline('o')
            # 다시 선 두께 입력
            child.expect('What width do you want lines to appear')
            child.sendline('')
        else:  # 선 두께 입력
            child.sendline('')

        # 프로그램 종료 대기
        child.expect(pexpect.EOF, timeout=10)
        child.close()

    except Exception as e:
        print(f"Error: qpt_conv 실행 중 오류 발생: {e}")
        return False

    # 기본 출력 파일 확인
    if default_output.exists() and default_output.stat().st_size > 0:
        # 원하는 경로가 다르면 이동
        if str(default_output) != str(vmd_file):
            default_output.rename(vmd_file)
        print(f"✓ qpt_conv 완료")
        return True
    else:
        print(f"Error: VMD 파일 생성 실패")
        return False


def parse_sph_file(sph_file):
    """
    .sph 파일에서 채널 중심선과 반경 정보 추출

    Returns
    -------
    list of dict
        각 점: {'coords': (x, y, z), 'radius': float}
    """
    channel_points = []

    with open(sph_file, 'r') as f:
        for line in f:
            if line.startswith('ATOM'):
                # PDB 포맷은 고정 폭 컬럼 사용 (공백이 없을 수 있음)
                # ATOM     ID  NAME RES C RESID    X       Y       Z       R1      R2
                # 컬럼 위치: 30-38 (X), 38-46 (Y), 46-54 (Z), 54-60 (R1)
                try:
                    x = float(line[30:38].strip())
                    y = float(line[38:46].strip())
                    z = float(line[46:54].strip())
                    radius = float(line[54:60].strip())

                    # 유효한 반경만 포함 (양수 && 합리적인 범위)
                    if 0 < radius < 50:
                        channel_points.append({
                            'coords': (x, y, z),
                            'radius': radius
                        })
                except (ValueError, IndexError):
                    # 파싱 실패한 라인은 건너뛰기
                    continue

    return channel_points


def create_uniform_cylinder_points(channel_points, num_points_per_slice=20):
    """
    채널 중심선을 따라 중간 반경으로 균일한 원통 표면 점 생성

    Parameters
    ----------
    channel_points : list of dict
        채널 중심선 정보
    num_points_per_slice : int
        각 단면당 생성할 점의 개수

    Returns
    -------
    list of dict
        원통 표면 점: {'coords': (x, y, z), 'color': 'blue'}
    """
    if not channel_points:
        return []

    # 중간 반경 계산 (최소, 최대의 평균)
    radii = [p['radius'] for p in channel_points]
    min_radius = min(radii)
    max_radius = max(radii)
    mid_radius = (min_radius + max_radius) / 2

    print(f"   최소 반경: {min_radius:.2f} Å")
    print(f"   최대 반경: {max_radius:.2f} Å")
    print(f"   중간 반경: {mid_radius:.2f} Å (사용)")

    # 색상 결정
    if mid_radius < 1.15:
        color = 'red'
    elif mid_radius < 2.30:
        color = 'green'
    else:
        color = 'blue'

    # 각 채널 중심점에 대해 원통 표면 점 생성
    cylinder_points = []
    import math

    for point in channel_points:
        cx, cy, cz = point['coords']

        # 원 둘레에 점들 생성
        for i in range(num_points_per_slice):
            angle = 2 * math.pi * i / num_points_per_slice

            # Z축 수직 방향으로 원 생성 (XY 평면)
            x = cx + mid_radius * math.cos(angle)
            y = cy + mid_radius * math.sin(angle)
            z = cz

            cylinder_points.append({
                'coords': (x, y, z),
                'color': color
            })

    return cylinder_points


def parse_vmd_plot(vmd_file):
    """
    VMD plot 파일에서 좌표와 색상 추출

    Returns
    -------
    list of dict
        각 점: {'coords': (x, y, z), 'color': 'red'/'green'/'blue'/'yellow'}
    """
    points = []
    current_color = None

    with open(vmd_file, 'r') as f:
        for line in f:
            # 색상 변경 감지
            if 'draw color' in line:
                if 'red' in line:
                    current_color = 'red'
                elif 'green' in line:
                    current_color = 'green'
                elif 'blue' in line:
                    current_color = 'blue'
                elif 'yellow' in line:
                    current_color = 'yellow'

            # draw point {x y z} 형식 파싱
            if 'draw point' in line:
                match = re.search(r'\{([\s\d.-]+)\}', line)
                if match:
                    coords_str = match.group(1).split()
                    if len(coords_str) == 3:
                        x, y, z = map(float, coords_str)
                        points.append({
                            'coords': (x, y, z),
                            'color': current_color
                        })

    return points


def create_pdb_from_points(points, output_pdb):
    """
    추출한 점들을 PDB 파일로 저장

    Parameters
    ----------
    points : list of dict
        점 정보
    output_pdb : str
        출력 PDB 파일
    """
    with open(output_pdb, 'w') as f:
        # 헤더
        f.write("REMARK   Generated by hole_pymol.py\n")
        f.write("REMARK   Using HOLE sph_process (official tool)\n")
        f.write("REMARK   All atoms are independent (no CONECT records)\n")
        f.write("REMARK   Color scheme (HOLE standard):\n")
        f.write("REMARK     RED    - radius < 1.15 A (too narrow)\n")
        f.write("REMARK     GREEN  - radius 1.15-2.30 A (single water)\n")
        f.write("REMARK     BLUE   - radius > 2.30 A (multiple waters)\n")
        f.write("REMARK     YELLOW - channel center line\n")

        atom_num = 1
        for point in points:
            x, y, z = point['coords']
            color = point['color']

            # 색상별 residue 이름만 사용 (chain은 P로 통일)
            if color == 'red':
                resname = 'POR'
            elif color == 'green':
                resname = 'POG'
            elif color == 'blue':
                resname = 'POB'
            elif color == 'yellow':
                resname = 'CEN'
            else:
                resname = 'UNK'

            # ATOM 레코드 - 각 원자마다 다른 residue 번호 사용
            # chain P, residue 번호 = atom 번호 (각각 독립적)
            f.write(f"ATOM  {atom_num:5d} 10PS {resname} P{atom_num:4d}    "
                   f"{x:8.3f}{y:8.3f}{z:8.3f}  0.00  0.00      PSDOPS  \n")

            atom_num += 1

        f.write("END\n")

    # 통계
    colors_count = {}
    for point in points:
        color = point['color']
        colors_count[color] = colors_count.get(color, 0) + 1

    print(f"✓ PDB 파일 생성: {output_pdb}")
    print(f"   총 {atom_num-1}개 원자")
    print(f"\n색상 분포:")
    for color in ['red', 'green', 'blue', 'yellow']:
        if color in colors_count:
            count = colors_count[color]
            pct = count / len(points) * 100
            print(f"  {color:8s}: {count:5d} ({pct:5.1f}%)")


def create_pymol_script_individual(points, protein_pdb, output_script, sphere_radius=0.3):
    """PyMOL 스크립트 생성 (각 점을 개별 객체로)"""

    script = f"""# PyMOL Visualization Script (Individual Spheres)
# Generated by hole_pymol.py (using official HOLE sph_process)

from pymol import cmd

# 1. 단백질 로드
cmd.load("{protein_pdb}", "protein")

# 2. 단백질 표현
cmd.hide("everything", "protein")
cmd.show("cartoon", "protein")
cmd.color("grey70", "protein")
cmd.set("cartoon_transparency", 0.3, "protein")

# 3. 개별 sphere 생성
"""

    # 색상 매핑
    color_map = {
        'red': 'red',
        'green': 'green',
        'blue': 'blue',
        'yellow': 'yellow'
    }

    # 각 점을 개별 pseudoatom으로 생성
    for i, point in enumerate(points, 1):
        x, y, z = point['coords']
        color = point['color']
        pymol_color = color_map.get(color, 'gray')

        obj_name = f"pore_sphere_{i}"
        script += f'cmd.pseudoatom("{obj_name}", pos=({x:.3f}, {y:.3f}, {z:.3f}))\n'
        script += f'cmd.show("spheres", "{obj_name}")\n'
        script += f'cmd.set("sphere_scale", {sphere_radius}, "{obj_name}")\n'
        script += f'cmd.color("{pymol_color}", "{obj_name}")\n\n'

    # 그룹화 및 추가 설정
    script += f"""
# 4. 모든 sphere를 하나의 그룹으로
cmd.group("pore_spheres", "pore_sphere_*")

# 5. 시각화 설정
cmd.bg_color("white")
cmd.set("ray_shadows", 1)
cmd.set("antialias", 2)

# 6. 뷰 조정
cmd.zoom("protein")
cmd.center("protein")

print("=== HOLE Visualization (Individual Spheres) ===")
print("Protein: {protein_pdb}")
print("Total spheres: {len(points)}")
print("")
print("Color scheme:")
print("  RED    - Too narrow for water (< 1.15 Å)")
print("  GREEN  - Single water molecule (1.15-2.30 Å)")
print("  BLUE   - Multiple water molecules (> 2.30 Å)")
print("  YELLOW - Channel center line")
print("")
print("Commands:")
print("  cmd.hide('spheres', 'pore_spheres')  # 모든 sphere 숨기기")
print("  cmd.show('spheres', 'pore_spheres')  # 모든 sphere 표시")
print("  cmd.set('sphere_scale', 0.5, 'pore_spheres')  # 크기 조절")
"""

    with open(output_script, 'w') as f:
        f.write(script)

    print(f"✓ PyMOL 스크립트 (개별 객체): {output_script}")
    print(f"   총 {len(points)}개 개별 sphere 생성")


def create_pymol_script(protein_pdb, pore_pdb, output_script, sph_file=None):
    """PyMOL 시각화 스크립트 생성 (PDB 파일 사용 + .sph 반경 기반 색상)"""

    # Path 객체를 절대 경로 문자열로 변환
    from pathlib import Path
    protein_pdb_abs = str(Path(protein_pdb).resolve())
    pore_pdb_abs = str(Path(pore_pdb).resolve())

    script = f"""# PyMOL Visualization Script
# Generated by hole_pymol.py (using official HOLE sph_process)

# 색상 공간: CMYK
set color_space, cmyk

# 커스텀 색상 정의 (CMYK)
set_color grey70, [0.0, 0.0, 0.0, 0.3]  # CMYK: K=30%
set_color orange, [0.0, 0.5, 1.0, 0.0]  # CMYK: M=50%, Y=100%

# 배경: 흰색
bg_color white

# 1. 단백질 로드 (Cartoon) - 먼저 로드
load {protein_pdb_abs}, protein_cartoon
hide everything, protein_cartoon
show cartoon, protein_cartoon
set transparency, 0.6, protein_cartoon
color orange, protein_cartoon

# 2. 단백질 로드 (Surface) - 나중에 로드 (위에 렌더링)
load {protein_pdb_abs}, protein_surface
hide everything, protein_surface
show surface, protein_surface
set transparency, 0.8, protein_surface
color grey70, protein_surface

# 3. 기공 표면 로드
load {pore_pdb_abs}, pore
hide everything, pore
show surface, pore
set surface_quality, 1, pore

"""

    # .sph 파일이 제공되면 반경별 색상 적용
    if sph_file and Path(sph_file).exists():
        channel_points = parse_sph_file(sph_file)

        if channel_points:
            radii = [p['radius'] for p in channel_points]
            min_radius = min(radii)
            max_radius = max(radii)

            # PDB 파일의 residue 이름별 색상 지정
            script += f"""# 4. 기공 반경별 색상 (HOLE 표준)
# 반경 범위: {min_radius:.2f} - {max_radius:.2f} Å
color red, resn POR      # 좁음 (< 1.15 Å)
color green, resn POG    # 중간 (1.15-2.30 Å)
color blue, resn POB     # 넓음 (> 2.30 Å)
color yellow, resn CEN   # 중심선

"""
        else:
            script += "# 4. 기공 색상 (기본)\ncolor cyan, pore\n\n"
    else:
        script += "# 4. 기공 색상 (기본)\ncolor cyan, pore\n\n"

    script += """# 5. 시각화 설정
set ray_shadows, 1
set antialias, 2
set cartoon_transparency, 0.6, protein_cartoon
set surface_quality, 1

# 6. 렌더링 순서 명시 (아래부터: Cartoon -> Surface -> Pore)
order protein_cartoon protein_surface pore

# 7. 뷰 조정
zoom all
center pore

print("=== HOLE Visualization ===")
print("Color space: CMYK")
print("Protein (Surface): grey70 (K=30%), 80% transparent")
print("Protein (Cartoon): orange (M=50%, Y=100%), 60% transparent")
"""

    if sph_file and Path(sph_file).exists():
        script += """print("Pore surface: colored by radius (HOLE standard)")
print("  RED    - Too narrow (< 1.15 Å)")
print("  GREEN  - Single water (1.15-2.30 Å)")
print("  BLUE   - Wide pore (> 2.30 Å)")
print("  YELLOW - Center line")
"""
    else:
        script += 'print("Pore surface: cyan spheres (scale 0.25)")\n'

    with open(output_script, 'w') as f:
        f.write(script)

    print(f"✓ PyMOL 스크립트: {output_script}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python hole_pymol.py <sph_file>")
        sys.exit(1)

    sph_file = Path(sys.argv[1])

    if not sph_file.exists():
        print(f"Error: {sph_file} not found")
        sys.exit(1)

    print("=" * 60)
    print("HOLE to PyMOL (Official sph_process)")
    print("=" * 60)
    print(f"\n입력 파일: {sph_file}")

    # 출력 파일 경로
    work_dir = sph_file.parent
    base_name = sph_file.stem

    qpt_file = work_dir / f"{base_name}_surface.qpt"
    vmd_file = work_dir / f"{base_name}_surface.vmd_plot"
    pore_pdb = work_dir / f"{base_name}_pore_surface.pdb"
    pymol_script = work_dir / f"{base_name}_pymol.pml"

    # 단백질 PDB 파일 찾기
    # 1. 같은 이름의 PDB 파일
    protein_pdb = work_dir / f"{base_name}.pdb"

    # 2. _analysis, _test 등의 접미사 제거
    if not protein_pdb.exists():
        for suffix in ['_analysis', '_test', '_out']:
            candidate = work_dir / f"{base_name.replace(suffix, '')}.pdb"
            if candidate.exists():
                protein_pdb = candidate
                break

    # 3. work_dir에서 PDB 파일 검색
    if not protein_pdb.exists():
        pdb_files = list(work_dir.glob("*.pdb"))
        # pore_surface.pdb 제외
        pdb_files = [f for f in pdb_files if 'pore_surface' not in f.name]
        if pdb_files:
            protein_pdb = pdb_files[0]  # 첫 번째 PDB 사용

    print("\n1. sph_process 실행 (표면 점 생성)")
    if not run_sph_process(sph_file, qpt_file, dotden=15):
        sys.exit(1)

    print("\n2. qpt to VMD 변환")
    if not convert_qpt_to_vmd(qpt_file, vmd_file):
        sys.exit(1)

    print("\n3. VMD 파일 파싱 (좌표 추출)")
    points = parse_vmd_plot(vmd_file)
    print(f"✓ {len(points)}개 표면 점 추출")

    print("\n4. PDB 파일 생성")
    create_pdb_from_points(points, pore_pdb)

    print("\n5. PyMOL 스크립트 생성")

    if protein_pdb.exists():
        # .sph 파일 반경 정보를 사용한 스크립트 생성
        create_pymol_script(protein_pdb, pore_pdb, pymol_script, sph_file=sph_file)
    else:
        print(f"Warning: 단백질 PDB를 찾을 수 없습니다: {protein_pdb}")

    print("\n" + "=" * 60)
    print("완료!")
    print("=" * 60)
    print(f"생성된 파일:")
    print(f"  1. {pore_pdb}")
    if protein_pdb.exists():
        print(f"  2. {pymol_script}")
        print(f"\nPyMOL 실행:")
        print(f"  pymol {pymol_script}")
