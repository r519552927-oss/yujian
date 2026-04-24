# -*- coding: utf-8 -*-
"""
PMSM 磁路计算工具 - 交互式界面
Motor Magnetic Circuit Calculator - Interactive UI

Author: WorkBuddy Motor Design
Date: 2026-04-24
"""

from magnetic_circuit_calculator import (
    PMSMParams, MagneticCircuitCalculator,
    MAGNETIC_MATERIALS, PM_MATERIALS, quick_calc
)
import math


def print_header():
    """打印标题"""
    print("\n" + "="*70)
    print("           PMSM 永磁同步电机 磁路计算工具")
    print("="*70)


def print_menu():
    """打印菜单"""
    print("\n功能选项:")
    print("  1. 自定义参数计算")
    print("  2. 快速计算 (1.5kW/3000rpm/8极)")
    print("  3. 小功率电机 (750W)")
    print("  4. 中功率电机 (3kW)")
    print("  5. 查看材料库")
    print("  6. 参数敏感性分析")
    print("  0. 退出")
    print("-"*70)


def input_params() -> PMSMParams:
    """交互式输入参数"""
    print("\n" + "-"*50)
    print("请输入电机参数 (直接回车使用默认值)")
    print("-"*50)

    p = PMSMParams()

    # 额定参数
    print("\n【额定参数】")
    rated_power = input(f"  额定功率 (W) [默认 {p.rated_power}]: ").strip()
    if rated_power:
        p.rated_power = float(rated_power)

    rated_speed = input(f"  额定转速 (rpm) [默认 {p.rated_speed}]: ").strip()
    if rated_speed:
        p.rated_speed = float(rated_speed)

    poles = input(f"  极数 [默认 {p.poles}]: ").strip()
    if poles:
        p.poles = int(poles)

    # 定子尺寸
    print("\n【定子尺寸 (mm)】")
    D_out = input(f"  定子外径 [默认 {p.D_out}]: ").strip()
    if D_out:
        p.D_out = float(D_out)

    D_in = input(f"  定子内径 [默认 {p.D_in}]: ").strip()
    if D_in:
        p.D_in = float(D_in)

    L_a = input(f"  铁心长度 [默认 {p.L_a}]: ").strip()
    if L_a:
        p.L_a = float(L_a)

    Q_s = input(f"  槽数 [默认 {p.Q_s}]: ").strip()
    if Q_s:
        p.Q_s = int(Q_s)

    # 槽型
    print("\n【槽型参数 (mm)】")
    h_t = input(f"  齿高 [默认 {p.h_t}]: ").strip()
    if h_t:
        p.h_t = float(h_t)

    b_t = input(f"  齿宽 [默认 {p.b_t}]: ").strip()
    if b_t:
        p.b_t = float(b_t)

    h_j = input(f"  轭高 [默认 {p.h_j}]: ").strip()
    if h_j:
        p.h_j = float(h_j)

    # 气隙
    print("\n【气隙参数】")
    delta = input(f"  单边气隙 (mm) [默认 {p.delta}]: ").strip()
    if delta:
        p.delta = float(delta)

    # 永磁体
    print("\n【永磁体参数】")
    print(f"  可选材料: {', '.join(PM_MATERIALS.keys())}")
    pm_mat = input(f"  材料 [默认 {p.pm_material}]: ").strip()
    if pm_mat and pm_mat in PM_MATERIALS:
        p.pm_material = pm_mat

    h_m = input(f"  厚度 (mm) [默认 {p.h_m}]: ").strip()
    if h_m:
        p.h_m = float(h_m)

    b_m = input(f"  宽度 (mm) [默认 {p.b_m}]: ").strip()
    if b_m:
        p.b_m = float(b_m)

    alpha_p = input(f"  极弧系数 [默认 {p.alpha_p}]: ").strip()
    if alpha_p:
        p.alpha_p = float(alpha_p)

    # 绕组
    print("\n【绕组参数】")
    N_ph = input(f"  每相串联匝数 [默认 {p.N_ph}]: ").strip()
    if N_ph:
        p.N_ph = int(N_ph)

    return p


def run_calculation(params: PMSMParams) -> MagneticCircuitCalculator:
    """执行计算并返回结果"""
    calc = MagneticCircuitCalculator(params)
    calc.calculate()
    return calc


def sensitivity_analysis(base_params: PMSMParams):
    """参数敏感性分析"""
    print("\n" + "="*70)
    print("              参数敏感性分析")
    print("="*70)

    # 分析气隙厚度的影响
    print("\n【气隙厚度影响分析】")
    print(f"{'气隙(mm)':<12}{'气隙磁密(T)':<15}{'齿部磁密(T)':<15}{'轭部磁密(T)':<15}")
    print("-"*57)

    calc_ref = MagneticCircuitCalculator(base_params)
    calc_ref.calculate()

    for delta in [0.3, 0.4, 0.5, 0.6, 0.7, 0.8]:
        base_params.delta = delta
        calc = MagneticCircuitCalculator(base_params)
        calc.calculate()
        r = calc.results['mmf_balance']
        print(f"{delta:<12.1f}{r['B_g']:<15.4f}{r['B_t']:<15.4f}{r['B_j']:<15.4f}")

    # 恢复原始值
    base_params.delta = 0.5

    # 分析永磁体厚度的影响
    print("\n【永磁体厚度影响分析】")
    print(f"{'PM厚度(mm)':<12}{'气隙磁密(T)':<15}{'齿部磁密(T)':<15}{'反电动势(V)':<15}")
    print("-"*57)

    for h_m in [2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]:
        base_params.h_m = h_m
        calc = MagneticCircuitCalculator(base_params)
        calc.calculate()
        r = calc.results['mmf_balance']
        E_0 = calc.results['emf']['E_0']
        print(f"{h_m:<12.1f}{r['B_g']:<15.4f}{r['B_t']:<15.4f}{E_0:<15.1f}")

    # 恢复原始值
    base_params.h_m = 3.0


def show_materials():
    """显示材料库"""
    print("\n" + "="*70)
    print("                    材料库")
    print("="*70)

    print("\n【硅钢片材料】")
    print("-"*50)
    for key, mat in MAGNETIC_MATERIALS.items():
        print(f"  {key}: {mat['name']}")
        print(f"    饱和磁密: {mat['Bs']} T")
        print(f"    典型曲线点: {len(mat['curve'])} 个")
        print()

    print("\n【永磁体材料】")
    print("-"*50)
    for key, mat in PM_MATERIALS.items():
        print(f"  {key}: {mat['name']}")
        print(f"    剩余磁密 Br: {mat['Br']} T")
        print(f"    矫顽力 Hcb: {mat['Hcb']/1000:.0f} kA/m")
        print(f"    内禀矫顽力 Hcj: {mat['Hcj']/1000:.0f} kA/m")
        print(f"    回复磁导率: {mat['u_rec']}")
        print()


def interactive_mode():
    """交互式模式"""
    while True:
        print_header()
        print_menu()

        choice = input("\n请选择功能 [0-6]: ").strip()

        if choice == '1':
            # 自定义参数
            params = input_params()
            print("\n正在计算...")
            calc = run_calculation(params)
            print(calc.get_report())

        elif choice == '2':
            # 1.5kW默认
            params = PMSMParams(
                rated_power=1.5e3,
                rated_speed=3000,
                poles=8,
                D_out=90,
                D_in=58,
                L_a=65,
                Q_s=36,
                delta=0.5,
                h_t=12,
                b_t=5,
                h_j=6,
            )
            print("\n正在计算 1.5kW/3000rpm/8极 电机...")
            calc = run_calculation(params)
            print(calc.get_report())

        elif choice == '3':
            # 750W
            result = quick_calc(0.75, 3000, 8)
            calc = MagneticCircuitCalculator(PMSMParams())
            calc.results = result
            print(calc.get_report())

        elif choice == '4':
            # 3kW
            params = PMSMParams(
                rated_power=3.0e3,
                rated_speed=3000,
                poles=8,
                D_out=120,
                D_in=78,
                L_a=85,
                Q_s=36,
                delta=0.6,
                h_t=14,
                b_t=6,
                h_j=8,
                h_m=3.5,
                b_m=8,
            )
            print("\n正在计算 3kW/3000rpm/8极 电机...")
            calc = run_calculation(params)
            print(calc.get_report())

        elif choice == '5':
            show_materials()

        elif choice == '6':
            # 敏感性分析
            base_params = PMSMParams(
                rated_power=1.5e3,
                rated_speed=3000,
                poles=8,
                D_out=90,
                D_in=58,
                L_a=65,
                Q_s=36,
                delta=0.5,
                h_t=12,
                b_t=5,
                h_j=6,
                h_m=3.0,
            )
            sensitivity_analysis(base_params)

        elif choice == '0':
            print("\n感谢使用！再见。\n")
            break

        else:
            print("\n无效选择，请重新输入。")

        input("\n按回车继续...")


if __name__ == "__main__":
    interactive_mode()
