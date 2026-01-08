#!/usr/bin/env python3
"""
HOLE 결과 시각화 스크립트
========================
HOLE 출력 파일에서 기공 반경 데이터를 추출하여 2D 그래프로 그리기

사용 예시:
---------
from hole_plot import plot_hole_profile, extract_hole_data

# 데이터 추출
data = extract_hole_data("hole_out.txt")

# 그래프 그리기
plot_hole_profile("hole_out.txt", save_as="pore_profile.png")

# 또는 커스텀 설정
plot_hole_profile("hole_out.txt",
                  title="Gramicidin A Channel",
                  xlabel="Channel Coordinate (Å)",
                  ylabel="Pore Radius (Å)",
                  save_as="gramicidin.png")
"""

import re
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


def extract_hole_data(output_file):
    """
    HOLE 출력 파일에서 기공 반경 프로파일 데이터 추출

    Parameters
    ----------
    output_file : str
        HOLE 출력 텍스트 파일 경로

    Returns
    -------
    dict
        데이터 딕셔너리:
        - 'channel_coord': 채널 좌표 (cvec과 내적)
        - 'radius': 기공 반경
        - 'x', 'y', 'z': 3D 좌표
        - 'type': 'sampled' 또는 'mid-point'
        - 'all_data': 전체 데이터 리스트

    Examples
    --------
    >>> data = extract_hole_data("hole_out.txt")
    >>> print(f"Points: {len(data['all_data'])}")
    >>> print(f"Min radius: {min(data['radius']):.2f} Å")
    """

    sampled_data = []
    midpoint_data = []

    with open(output_file, 'r') as f:
        content = f.read()

    # 데이터 섹션 시작 찾기
    # "cenxyz.cvec" 이후부터 데이터 시작
    if 'cenxyz.cvec' not in content:
        print("Warning: 'cenxyz.cvec' 헤더를 찾을 수 없습니다.")
        print("전체 파일에서 (sampled)/(mid-point) 패턴을 검색합니다.")

    # sampled와 mid-point 데이터 추출
    # 형식: channel_coord   cen_x   cen_y   radius   (sampled/mid-point)
    # 실제 HOLE 출력: cenxyz.cvec(채널좌표)  radius  cen_line_D  sum{s/area}
    pattern = r'^\s*(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+\((sampled|mid-point)\)'

    for match in re.finditer(pattern, content, re.MULTILINE):
        channel_coord = float(match.group(1))
        radius = float(match.group(2))
        cen_line_d = float(match.group(3))
        sum_s_area = float(match.group(4))
        point_type = match.group(5)

        data_point = {
            'channel_coord': channel_coord,
            'radius': radius,
            'cen_line_d': cen_line_d,
            'sum_s_area': sum_s_area,
            'type': point_type
        }

        if point_type == 'sampled':
            sampled_data.append(data_point)
        else:  # mid-point
            midpoint_data.append(data_point)

    # 전체 데이터 (sampled + mid-point) 채널 좌표로 정렬
    all_data = sampled_data + midpoint_data
    all_data.sort(key=lambda x: x['channel_coord'])

    if not all_data:
        raise ValueError(f"데이터를 찾을 수 없습니다: {output_file}")

    # 배열로 변환
    result = {
        'channel_coord': np.array([d['channel_coord'] for d in all_data]),
        'radius': np.array([d['radius'] for d in all_data]),
        'cen_line_d': np.array([d['cen_line_d'] for d in all_data]),
        'sum_s_area': np.array([d['sum_s_area'] for d in all_data]),
        'type': [d['type'] for d in all_data],
        'all_data': all_data,
        'sampled_only': sampled_data,
        'midpoint_only': midpoint_data
    }

    return result


def save_tsv(output_file, tsv_file=None):
    """
    HOLE 출력에서 TSV 파일 생성 (엑셀/스프레드시트용)

    Parameters
    ----------
    output_file : str
        HOLE 출력 파일
    tsv_file : str, optional
        TSV 파일 저장 경로 (기본: output_file에서 _out.txt를 .tsv로 변경)

    Returns
    -------
    str
        생성된 TSV 파일 경로
    """

    data = extract_hole_data(output_file)

    if tsv_file is None:
        tsv_file = str(output_file).replace('_out.txt', '.tsv').replace('.txt', '.tsv')

    with open(tsv_file, 'w') as f:
        # 헤더
        f.write("channel_coord\tradius\tcen_line_d\tsum_s_area\ttype\n")

        # 데이터
        for point in data['all_data']:
            f.write(f"{point['channel_coord']:.5f}\t")
            f.write(f"{point['radius']:.5f}\t")
            f.write(f"{point['cen_line_d']:.5f}\t")
            f.write(f"{point['sum_s_area']:.5f}\t")
            f.write(f"{point['type']}\n")

    print(f"TSV 파일 생성: {tsv_file}")
    return tsv_file


def plot_hole_profile(output_file,
                      title=None,
                      xlabel="Channel Coordinate (Å)",
                      ylabel="Pore Radius (Å)",
                      figsize=(10, 6),
                      dpi=150,
                      save_as=None,
                      show_grid=True,
                      show_points=False,
                      highlight_minimum=True):
    """
    HOLE 기공 반경 프로파일 그래프 그리기

    Parameters
    ----------
    output_file : str
        HOLE 출력 파일 경로
    title : str, optional
        그래프 제목 (기본: "HOLE Pore Radius Profile")
    xlabel : str, optional
        X축 레이블 (기본: "Channel Coordinate (Å)")
    ylabel : str, optional
        Y축 레이블 (기본: "Pore Radius (Å)")
    figsize : tuple, optional
        그래프 크기 (기본: (10, 6))
    dpi : int, optional
        해상도 (기본: 150)
    save_as : str, optional
        저장할 파일 이름 (기본: None - 화면에만 표시)
    show_grid : bool, optional
        그리드 표시 여부 (기본: True)
    show_points : bool, optional
        데이터 포인트 표시 여부 (기본: True)
    highlight_minimum : bool, optional
        최소 반경 위치 강조 표시 (기본: True)

    Returns
    -------
    matplotlib.figure.Figure
        생성된 그래프 객체

    Examples
    --------
    >>> plot_hole_profile("hole_out.txt",
    ...                   title="Gramicidin A",
    ...                   save_as="gramicidin.png")
    """

    # 데이터 추출
    data = extract_hole_data(output_file)

    # 그래프 생성
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    # 매끄러운 선 그래프
    ax.plot(data['channel_coord'], data['radius'],
            'b-', linewidth=2.5, label='Pore radius', alpha=0.8)

    # 데이터 포인트 표시 (선택 사항)
    if show_points:
        ax.plot(data['channel_coord'], data['radius'],
               'o', color='blue', markersize=2, alpha=0.3)

    # 최소 반경 강조 표시
    if highlight_minimum:
        min_idx = np.argmin(data['radius'])
        min_coord = data['channel_coord'][min_idx]
        min_radius = data['radius'][min_idx]

        ax.plot(min_coord, min_radius, 'r*', markersize=15,
                label=f'Minimum: {min_radius:.2f} Å')
        ax.axhline(y=min_radius, color='r', linestyle='--',
                  alpha=0.3, linewidth=1)

    # 축 레이블
    ax.set_xlabel(xlabel, fontsize=12, fontweight='bold')
    ax.set_ylabel(ylabel, fontsize=12, fontweight='bold')

    # 제목
    if title is None:
        title = f"HOLE Pore Radius Profile\n{Path(output_file).stem}"
    ax.set_title(title, fontsize=14, fontweight='bold')

    # 그리드
    if show_grid:
        ax.grid(True, alpha=0.3, linestyle='--')

    # 범례
    ax.legend(loc='best', fontsize=10)

    # 레이아웃 조정
    plt.tight_layout()

    # 저장
    if save_as:
        plt.savefig(save_as, dpi=dpi, bbox_inches='tight')
        print(f"그래프 저장: {save_as}")

    return fig


def plot_multiple_profiles(output_files, labels=None,
                          title="HOLE Pore Radius Comparison",
                          xlabel="Channel Coordinate (Å)",
                          ylabel="Pore Radius (Å)",
                          figsize=(12, 7),
                          dpi=150,
                          save_as=None):
    """
    여러 HOLE 결과를 한 그래프에 비교

    Parameters
    ----------
    output_files : list of str
        HOLE 출력 파일 경로 리스트
    labels : list of str, optional
        각 파일의 레이블 (기본: 파일명)
    title : str, optional
        그래프 제목
    xlabel, ylabel : str, optional
        축 레이블
    figsize : tuple, optional
        그래프 크기
    dpi : int, optional
        해상도
    save_as : str, optional
        저장할 파일 이름

    Returns
    -------
    matplotlib.figure.Figure
        생성된 그래프 객체
    """

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    colors = plt.cm.tab10(np.linspace(0, 1, len(output_files)))

    if labels is None:
        labels = [Path(f).stem for f in output_files]

    for i, (output_file, label) in enumerate(zip(output_files, labels)):
        data = extract_hole_data(output_file)
        ax.plot(data['channel_coord'], data['radius'],
               color=colors[i], linewidth=2, label=label)

        # 최소값 표시
        min_idx = np.argmin(data['radius'])
        min_coord = data['channel_coord'][min_idx]
        min_radius = data['radius'][min_idx]
        ax.plot(min_coord, min_radius, '*',
               color=colors[i], markersize=12)

    ax.set_xlabel(xlabel, fontsize=12, fontweight='bold')
    ax.set_ylabel(ylabel, fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='best', fontsize=10)

    plt.tight_layout()

    if save_as:
        plt.savefig(save_as, dpi=dpi, bbox_inches='tight')
        print(f"비교 그래프 저장: {save_as}")

    return fig


if __name__ == "__main__":
    """테스트 및 사용 예시"""

    import sys

    print("=" * 60)
    print("HOLE 결과 시각화 스크립트")
    print("=" * 60)

    # 테스트 파일 확인
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    else:
        # 기본 테스트 파일
        output_file = "test_output/gramicidin_test_out.txt"

        if not Path(output_file).exists():
            output_file = "output/my_analysis_out.txt"

    if not Path(output_file).exists():
        print(f"파일을 찾을 수 없습니다: {output_file}")
        print("\n사용법:")
        print("  python hole_plot.py <hole_output_file>")
        print("\n또는 Python에서 직접:")
        print("  from hole_plot import plot_hole_profile")
        print("  plot_hole_profile('hole_out.txt', save_as='profile.png')")
        sys.exit(1)

    print(f"\n분석 파일: {output_file}\n")

    # 1. 데이터 추출
    print("1. 데이터 추출 중...")
    data = extract_hole_data(output_file)
    print(f"   ✓ {len(data['all_data'])}개 데이터 포인트 추출")
    print(f"   - Sampled: {len(data['sampled_only'])}개")
    print(f"   - Mid-point: {len(data['midpoint_only'])}개")
    print(f"   - 최소 반경: {np.min(data['radius']):.3f} Å")
    print(f"   - 최대 반경: {np.max(data['radius']):.3f} Å")
    print(f"   - 평균 반경: {np.mean(data['radius']):.3f} Å")

    # 2. TSV 파일 저장
    print("\n2. TSV 파일 생성 중...")
    tsv_file = save_tsv(output_file)

    # 3. 그래프 생성
    print("\n3. 그래프 생성 중...")
    output_png = str(output_file).replace('_out.txt', '_profile.png').replace('.txt', '_profile.png')

    fig = plot_hole_profile(
        output_file,
        title=f"HOLE Pore Radius Profile\n{Path(output_file).stem}",
        save_as=output_png,
        highlight_minimum=True
    )

    print(f"\n{'='*60}")
    print("완료!")
    print(f"{'='*60}")
    print(f"TSV 파일:  {tsv_file}")
    print(f"그래프:    {output_png}")
    print(f"{'='*60}\n")

    # 그래프 표시 (선택 사항)
    try:
        plt.show()
    except:
        print("(그래프 화면 표시 불가 - 파일로 저장됨)")
