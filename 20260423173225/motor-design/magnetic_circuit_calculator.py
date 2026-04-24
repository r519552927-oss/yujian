# -*- coding: utf-8 -*-
"""
永磁同步电机(PMSM)磁路计算工具 v2.0
Motor Magnetic Circuit Calculation Tool

功能:
1. 主要尺寸计算与校核
2. 气隙磁路计算 (含卡氏系数)
3. 齿部磁路计算 (分段计算)
4. 轭部磁路计算
5. 永磁体等效磁路
6. 空载气隙磁密迭代计算
7. 空载反电动势估算

Author: WorkBuddy Motor Design
Date: 2026-04-24
"""

import math
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

# ==================== 材料磁化曲线数据 ====================
# B-H曲线数据 (B in T, H in A/m)
MAGNETIC_MATERIALS = {
    # 35AW300 (新能源汽车驱动电机常用)
    '35AW300': {
        'name': '35AW300 (新能源汽车)',
        'Bs': 2.05,
        'curve': [
            (0.0, 0),
            (0.2, 80),
            (0.4, 150),
            (0.6, 220),
            (0.8, 320),
            (1.0, 450),
            (1.1, 580),
            (1.2, 800),
            (1.3, 1150),
            (1.4, 1800),
            (1.5, 3200),
            (1.6, 7000),
            (1.7, 18000),
            (1.8, 50000),
        ]
    },
    # 硅钢片 DW310
    'DW310': {
        'name': '硅钢片 DW310',
        'Bs': 1.82,
        'curve': [
            (0.0, 0),
            (0.2, 180),
            (0.4, 350),
            (0.6, 520),
            (0.8, 700),
            (1.0, 950),
            (1.1, 1200),
            (1.2, 1600),
            (1.3, 2200),
            (1.4, 3200),
            (1.5, 5000),
            (1.6, 9000),
            (1.7, 18000),
            (1.8, 40000),
        ]
    },
    # 硅钢片 DW465
    'DW465': {
        'name': '硅钢片 DW465',
        'Bs': 1.78,
        'curve': [
            (0.0, 0),
            (0.2, 120),
            (0.4, 240),
            (0.6, 380),
            (0.8, 520),
            (1.0, 700),
            (1.1, 880),
            (1.2, 1150),
            (1.3, 1600),
            (1.4, 2500),
            (1.5, 4500),
            (1.6, 10000),
            (1.7, 25000),
            (1.8, 60000),
        ]
    },
}

# 永磁体材料
PM_MATERIALS = {
    'N52': {
        'name': '钕铁硼 N52',
        'Br': 1.45,  # 剩余磁密 T (20°C)
        'Hcb': 860e3,  # 磁感应矫顽力 A/m
        'Hcj': 960e3,  # 内禀矫顽力 A/m
        'u_rec': 1.05,  # 回复磁导率
        'alpha_B': -0.12,  # Br温度系数 %/K
        'alpha_H': -0.6,  # Hcb温度系数 %/K
    },
    'N48SH': {
        'name': '钕铁硼 N48SH (耐高温)',
        'Br': 1.38,
        'Hcb': 1000e3,
        'Hcj': 1400e3,
        'u_rec': 1.05,
        'alpha_B': -0.11,
        'alpha_H': -0.5,
    },
}


@dataclass
class PMSMParams:
    """PMSM电机参数"""
    # ===== 额定参数 =====
    rated_power: float = 1.5e3       # 额定功率 W
    rated_speed: float = 3000        # 额定转速 rpm
    poles: int = 8                   # 极数
    phases: int = 3                  # 相数
    rated_voltage: float = 220        # 额定电压 V

    # ===== 定子参数 (mm) =====
    D_out: float = 90                 # 定子外径 mm
    D_in: float = 58                  # 定子内径 mm
    L_a: float = 65                   # 铁心长度 mm
    Q_s: int = 36                     # 槽数

    # ===== 槽型参数 (mm) =====
    h_s: float = 14                   # 槽高 mm
    b_s: float = 3.5                  # 槽宽 mm
    h_t: float = 12                   # 齿高 mm
    b_t: float = 5                    # 齿宽 mm
    h_j: float = 6                    # 轭高 mm

    # ===== 气隙参数 (mm) =====
    delta: float = 0.5               # 单边气隙 mm

    # ===== 永磁体参数 =====
    pm_material: str = 'N52'
    h_m: float = 3.0                 # 永磁体厚度 mm
    b_m: float = 8.0                 # 永磁体宽度 mm
    alpha_p: float = 0.9             # 极弧系数

    # ===== 材料 =====
    core_material: str = '35AW300'

    # ===== 绕组参数 =====
    N_ph: int = 50                   # 每相串联匝数
    winding_factor: float = 0.933     # 绕组系数

    # ===== 工艺系数 =====
    k_Fe: float = 0.95               # 叠压系数
    k_c: float = 1.15                # 卡氏系数
    sigma: float = 1.08              # 漏磁系数

    def to_si(self):
        """转换为国际单位"""
        return {
            'D_out': self.D_out * 1e-3,
            'D_in': self.D_in * 1e-3,
            'L_a': self.L_a * 1e-3,
            'delta': self.delta * 1e-3,
            'h_m': self.h_m * 1e-3,
            'b_m': self.b_m * 1e-3,
            'h_s': self.h_s * 1e-3,
            'b_s': self.b_s * 1e-3,
            'h_t': self.h_t * 1e-3,
            'b_t': self.b_t * 1e-3,
            'h_j': self.h_j * 1e-3,
        }


class MagneticCircuitCalculator:
    """电机磁路计算器"""

    def __init__(self, params: PMSMParams):
        self.p = params
        self.u0 = 4 * math.pi * 1e-7
        self.results = {}

    def calculate(self) -> Dict:
        """执行完整磁路计算"""
        p = self.p
        si = p.to_si()

        results = {
            'basic': {},
            'air_gap': {},
            'tooth': {},
            'yoke': {},
            'pm': {},
            'mmf_balance': {},
        }

        # ===== 1. 基础参数 =====
        tau_p = math.pi * si['D_in'] / p.poles  # 极距
        q = p.Q_s / (2 * p.phases * (p.poles / 2))  # 每极每相槽数
        tau_s = math.pi * si['D_in'] / p.Q_s  # 槽距

        results['basic'] = {
            'tau_p': tau_p * 1000,  # mm
            'q': q,
            'tau_s': tau_s * 1000,  # mm
            'rated_torque': p.rated_power / (p.rated_speed * 2 * math.pi / 60),
            'rated_frequency': p.rated_speed * p.poles / 120,
        }

        # ===== 2. 永磁体等效 =====
        # 永磁体面积
        A_m = si['b_m'] * si['L_a']

        # 永磁体磁动势
        F_m = p.pm_material in PM_MATERIALS and PM_MATERIALS[p.pm_material]['Hcb'] * si['h_m'] or 860e3 * si['h_m']

        results['pm'] = {
            'A_m': A_m * 1e6,  # mm²
            'F_m': F_m,  # A
            'material': PM_MATERIALS.get(p.pm_material, PM_MATERIALS['N52'])['name'],
        }

        # ===== 3. 气隙磁路 =====
        # 气隙长度 (考虑卡氏系数)
        delta_e = p.k_c * si['delta']

        # 气隙面积
        tau_p = results['basic']['tau_p'] * 1e-3
        A_g = p.alpha_p * tau_p * si['L_a'] * p.k_Fe

        # 气隙磁导
        G_g = self.u0 * A_g / (2 * delta_e)  # 两段气隙

        # 气隙磁阻
        R_g = 1 / G_g

        results['air_gap'] = {
            'delta_e': delta_e * 1000,  # mm
            'A_g': A_g * 1e6,  # mm²
            'G_g': G_g * 1e6,  # H
            'R_g': R_g * 1e-6,  # A/Wb
        }

        # ===== 4. 齿部磁路 =====
        # 齿部面积 (取1/3高度处)
        A_t = si['b_t'] * si['L_a'] * p.k_Fe

        # 齿部磁路长度
        L_t = si['h_t']

        results['tooth'] = {
            'A_t': A_t * 1e6,  # mm²
            'L_t': L_t * 1000,  # mm
            'b_t': si['b_t'] * 1000,  # mm
        }

        # ===== 5. 轭部磁路 =====
        # 轭部面积
        D_j = si['D_in'] - 2 * si['h_t'] - 2 * si['h_s']  # 轭部中径
        A_j = si['h_j'] * si['L_a'] * p.k_Fe

        # 轭部磁路长度 (半极距)
        L_j = math.pi * D_j / p.poles

        results['yoke'] = {
            'A_j': A_j * 1e6,  # mm²
            'L_j': L_j * 1000,  # mm
            'D_j': D_j * 1000,  # mm
            'h_j': si['h_j'] * 1000,  # mm
        }

        # ===== 6. 迭代计算气隙磁密 =====
        B_g = self._iterate_air_gap_flux(F_m, R_g, results)

        # 计算各部分磁密
        results['mmf_balance'] = self._calculate_flux_densities(B_g, results)

        # ===== 7. 反电动势估算 =====
        results['emf'] = self._estimate_back_emf(B_g, results)

        self.results = results
        return results

    def _iterate_air_gap_flux(self, F_m: float, R_g: float, results: Dict) -> float:
        """迭代求解气隙磁密 (使用牛顿-拉夫森法)"""
        p = self.p
        si = p.to_si()
        tau_p = results['basic']['tau_p'] * 1e-3

        # 初始猜测
        B_g = 0.9  # T

        for iteration in range(50):
            # 气隙磁势
            F_g = B_g * si['delta'] * 1e3 / self.u0 * 2  # 两段气隙

            # 齿部磁密
            B_t = B_g * tau_p / si['b_t'] * p.alpha_p
            B_t = max(0.1, min(2.0, B_t))
            H_t = self._interpolate_bh(p.core_material, B_t)
            F_t = H_t * si['h_t']

            # 轭部磁密 (转子轭部)
            B_j = B_g * tau_p / (2 * si['h_j']) * p.alpha_p
            B_j = max(0.1, min(2.0, B_j))
            H_j = self._interpolate_bh(p.core_material, B_j)
            # 轭部磁路长度 = 极距
            F_j = H_j * tau_p

            # 总磁势需求
            F_total = F_g + F_t + F_j

            # 误差
            error = F_total - F_m

            # 检查收敛
            if abs(error) < 5:  # 5A精度
                break

            # 梯度 (简化)
            gradient = (F_g + F_t + F_j) / B_g if B_g > 0.01 else 1000

            # 更新
            delta_B = error / gradient
            B_g = B_g - delta_B

            # 限制范围
            B_g = max(0.5, min(1.3, B_g))

        return B_g

    def _calculate_flux_densities(self, B_g: float, results: Dict) -> Dict:
        """计算各部分磁密"""
        p = self.p
        si = p.to_si()

        tau_p = results['basic']['tau_p'] * 1e-3

        # 齿部磁密
        B_t = B_g * tau_p / si['b_t'] * p.alpha_p
        H_t = self._interpolate_bh(p.core_material, B_t)

        # 轭部磁密
        B_j = B_g * tau_p / (2 * si['h_j']) * p.alpha_p
        H_j = self._interpolate_bh(p.core_material, B_j)

        # 气隙磁通
        A_g = results['air_gap']['A_g'] * 1e-6
        Phi_g = B_g * A_g

        return {
            'B_g': B_g,
            'B_t': B_t,
            'B_j': B_j,
            'H_t': H_t,
            'H_j': H_j,
            'Phi_g': Phi_g * 1e3,  # mWb
        }

    def _interpolate_bh(self, material: str, B: float) -> float:
        """查表获取H (B-H插值)"""
        if material not in MAGNETIC_MATERIALS:
            material = '35AW300'

        curve = MAGNETIC_MATERIALS[material]['curve']

        # 边界处理
        if B <= curve[0][0]:
            return curve[0][1]
        if B >= curve[-1][0]:
            return curve[-1][1] + (B - curve[-1][0]) * 5000

        # 线性插值
        for i in range(len(curve) - 1):
            B1, H1 = curve[i]
            B2, H2 = curve[i + 1]
            if B1 <= B <= B2:
                ratio = (B - B1) / (B2 - B1) if B2 != B1 else 0
                return H1 + ratio * (H2 - H1)

        return 500 * B * 1e4

    def _estimate_back_emf(self, B_g: float, results: Dict) -> Dict:
        """估算反电动势"""
        p = self.p

        # 气隙磁通
        Phi_g = results['mmf_balance']['Phi_g'] * 1e-3  # Wb

        # 电势常数
        f = results['basic']['rated_frequency']
        E_0 = 4.44 * f * p.N_ph * p.winding_factor * Phi_g * p.sigma

        return {
            'E_0': E_0,  # V
            'frequency': f,  # Hz
        }

    def get_report(self) -> str:
        """生成计算报告"""
        if not self.results:
            return "请先执行 calculate()"

        p = self.p
        r = self.results
        mb = r['mmf_balance']

        # 检查磁密是否合理
        warnings = []
        if mb['B_t'] > 1.8:
            warnings.append(f"齿部磁密过高 ({mb['B_t']:.2f}T > 1.8T)")
        if mb['B_j'] > 1.5:
            warnings.append(f"轭部磁密过高 ({mb['B_j']:.2f}T > 1.5T)")
        if mb['B_g'] > 1.2:
            warnings.append(f"气隙磁密偏高 ({mb['B_g']:.2f}T)")

        report = f"""
{'='*65}
永磁同步电机 磁路计算报告
{'='*65}

【电机规格】
  额定功率:     {p.rated_power/1000:.1f} kW
  额定转速:     {p.rated_speed} rpm
  极数:         {p.poles}
  相数:         {p.phases}
  定子外径:     {p.D_out} mm
  定子内径:     {p.D_in} mm
  铁心长度:     {p.L_a} mm
  槽数:         {p.Q_s}

【绕组参数】
  每相串联匝数: {p.N_ph}
  绕组系数:     {p.winding_factor}
  极距:         {r['basic']['tau_p']:.2f} mm
  每极每相槽数: {r['basic']['q']:.1f}

【永磁体】
  材料:         {r['pm']['material']}
  厚度:         {p.h_m} mm
  宽度:         {p.b_m} mm
  等效磁势:     {r['pm']['F_m']:.0f} A

【气隙】
  单边气隙:     {p.delta} mm
  等效气隙:     {r['air_gap']['delta_e']:.3f} mm
  卡氏系数:     {p.k_c}
  漏磁系数:     {p.sigma}

【定子齿部】
  齿宽:         {r['tooth']['b_t']:.2f} mm
  齿高:         {r['tooth']['L_t']:.1f} mm
  齿部面积:     {r['tooth']['A_t']:.2f} mm²
  ★齿部磁密:   {mb['B_t']:.4f} T
  齿部场强:     {mb['H_t']:.0f} A/m

【定子轭部】
  轭高:         {r['yoke']['h_j']:.1f} mm
  轭部面积:     {r['yoke']['A_j']:.2f} mm²
  ★轭部磁密:   {mb['B_j']:.4f} T
  轭部场强:     {mb['H_j']:.0f} A/m

【气隙】
  ★气隙磁密:   {mb['B_g']:.4f} T
  气隙磁通:     {mb['Phi_g']:.4f} mWb

【空载特性】
  频率:         {r['emf']['frequency']:.1f} Hz
  估算反电动势: {r['emf']['E_0']:.1f} V

{'='*65}
"""
        if warnings:
            report += "【⚠️ 设计警告】\n"
            for w in warnings:
                report += f"  • {w}\n"
            report += "\n"

        report += "【设计建议】\n"
        if mb['B_t'] < 1.4:
            report += "  • 齿部磁密偏低，可考虑减小齿宽以降低成本\n"
        elif mb['B_t'] < 1.7:
            report += "  • 齿部磁密设计合理 ✓\n"
        else:
            report += "  • 齿部磁密偏高，建议增大齿宽或降低气隙磁密\n"

        if mb['B_g'] < 0.9:
            report += "  • 气隙磁密偏低，可增加永磁体厚度\n"
        elif mb['B_g'] < 1.1:
            report += "  • 气隙磁密设计合理 ✓\n"
        else:
            report += "  • 气隙磁密偏高，需注意高温退磁风险\n"

        report += "=" * 65 + "\n"

        return report


def quick_calc(power_kw: float, speed_rpm: int, poles: int = 8) -> Dict:
    """快速计算 (基于经验公式估算参数)"""
    # 根据功率估算主要尺寸
    if power_kw <= 0.75:
        D_out, D_in, L = 60, 38, 45
        Q_s, delta = 18, 0.35
        h_m, b_m = 2.5, 5
    elif power_kw <= 1.5:
        D_out, D_in, L = 90, 58, 65
        Q_s, delta = 36, 0.5
        h_m, b_m = 3.0, 6
    elif power_kw <= 3.0:
        D_out, D_in, L = 120, 75, 85
        Q_s, delta = 36, 0.6
        h_m, b_m = 3.5, 7
    else:
        D_out, D_in, L = 150, 95, 100
        Q_s, delta = 48, 0.7
        h_m, b_m = 4.0, 8

    # 创建参数
    params = PMSMParams(
        rated_power=power_kw * 1000,
        rated_speed=speed_rpm,
        poles=poles,
        D_out=D_out,
        D_in=D_in,
        L_a=L,
        Q_s=Q_s,
        delta=delta,
        h_m=h_m,
        b_m=b_m,
    )

    # 计算
    calc = MagneticCircuitCalculator(params)
    return calc.calculate()


def run_example():
    """运行示例"""
    print("\n" + "="*65)
    print("PMSM 磁路计算工具 v2.0")
    print("="*65)

    # 示例1: 标准参数
    print("\n--- 示例1: 1.5kW, 3000rpm, 8极 ---\n")

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
        h_s=14,
        b_s=3.5,
        h_m=3.0,
        b_m=8.0,
        alpha_p=0.9,
    )

    calc = MagneticCircuitCalculator(params)
    calc.calculate()
    print(calc.get_report())

    # 示例2: 快速计算
    print("\n--- 示例2: 快速计算 750W 电机 ---\n")
    result = quick_calc(0.75, 3000, 8)
    calc2 = MagneticCircuitCalculator(PMSMParams())
    calc2.results = result
    print(calc2.get_report())


if __name__ == "__main__":
    run_example()
