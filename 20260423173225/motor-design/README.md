# PMSM 永磁同步电机磁路计算工具

## 简介

这是一个用于永磁同步电机(PMSM)磁路计算的Python工具，可快速估算气隙磁密、齿部磁密、轭部磁密等关键参数，并给出设计建议。

## 文件结构

```
motor-design/
├── magnetic_circuit_calculator.py   # 核心计算模块
├── motor_calc_ui.py                 # 交互式界面
├── IMA_KB_notes.md                  # IMA知识库笔记同步
└── README.md                        # 本文档
```

## 安装依赖

```bash
# 无需安装额外依赖，仅需Python 3.x
python magnetic_circuit_calculator.py
```

## 使用方法

### 方式1: 命令行快速运行

```bash
python magnetic_circuit_calculator.py
```

自动运行示例计算，输出1.5kW/3000rpm/8极电机的磁路计算报告。

### 方式2: 交互式界面

```bash
python motor_calc_ui.py
```

提供菜单式交互，可选择：
- 自定义参数计算
- 预设功率等级计算
- 参数敏感性分析
- 材料库查看

### 方式3: 代码调用

```python
from magnetic_circuit_calculator import PMSMParams, MagneticCircuitCalculator

# 创建参数
params = PMSMParams(
    rated_power=1.5e3,      # 1.5kW
    rated_speed=3000,        # 3000rpm
    poles=8,                # 8极
    D_out=90,               # 定子外径90mm
    D_in=58,                # 定子内径58mm
    L_a=65,                 # 铁心长度65mm
    Q_s=36,                 # 36槽
    delta=0.5,             # 单边气隙0.5mm
    h_m=3.0,               # 永磁体厚度3mm
    b_m=8.0,               # 永磁体宽度8mm
)

# 计算
calc = MagneticCircuitCalculator(params)
calc.calculate()

# 输出报告
print(calc.get_report())

# 获取结果字典
results = calc.results
```

## 快速计算函数

```python
from magnetic_circuit_calculator import quick_calc

# 自动根据功率估算参数并计算
result = quick_calc(power_kw=0.75, speed_rpm=3000, poles=8)
```

支持的功率等级：
- 750W: D_out=60mm, D_in=38mm, L=45mm
- 1.5kW: D_out=90mm, D_in=58mm, L=65mm
- 3.0kW: D_out=120mm, D_in=75mm, L=85mm
- 更大功率: D_out=150mm, D_in=95mm, L=100mm

## 计算功能

### 1. 基础参数计算
- 极距
- 每极每相槽数
- 槽距
- 绕组估算

### 2. 永磁体等效磁路
- 永磁体面积和体积
- 等效磁势
- 材料温度特性

### 3. 气隙磁路
- 等效气隙长度(含卡氏系数)
- 气隙磁导
- 气隙磁密(迭代求解)

### 4. 齿部磁路
- 齿部磁密
- 齿部场强
- 齿部磁势降

### 5. 轭部磁路
- 轭部磁密
- 轭部场强
- 轭部磁势降

### 6. 空载特性
- 估算反电动势
- 设计警告和建议

## 内置材料库

### 硅钢片
| 材料 | 饱和磁密 | 特点 |
|------|---------|------|
| 35AW300 | 2.05T | 新能源汽车常用 |
| DW310 | 1.82T | 通用型 |
| DW465 | 1.78T | 低损耗 |

### 永磁体
| 材料 | 剩余磁密 | 矫顽力 | 特点 |
|------|---------|--------|------|
| N52 | 1.45T | 860kA/m | 高性能 |
| N48SH | 1.38T | 1000kA/m | 耐高温 |

## 参数说明

### 额定参数
- `rated_power`: 额定功率 (W)
- `rated_speed`: 额定转速 (rpm)
- `poles`: 极数
- `phases`: 相数

### 定子参数
- `D_out`: 定子外径 (mm)
- `D_in`: 定子内径 (mm)
- `L_a`: 铁心长度 (mm)
- `Q_s`: 槽数

### 槽型参数
- `h_t`: 齿高 (mm)
- `b_t`: 齿宽 (mm)
- `h_j`: 轭高 (mm)
- `h_s`: 槽高 (mm)
- `b_s`: 槽宽 (mm)

### 气隙参数
- `delta`: 单边气隙长度 (mm)

### 永磁体参数
- `pm_material`: 材料类型 ('N52', 'N48SH')
- `h_m`: 永磁体厚度 (mm)
- `b_m`: 永磁体宽度 (mm)
- `alpha_p`: 极弧系数

### 工艺系数
- `k_c`: 卡氏系数 (默认1.15)
- `sigma`: 漏磁系数 (默认1.08)
- `k_Fe`: 叠压系数 (默认0.95)

## 设计建议解读

### 齿部磁密 B_t
| 范围 | 状态 | 建议 |
|------|------|------|
| < 1.4T | 偏低 | 可减小齿宽降低成本 |
| 1.4-1.7T | 合理 ✓ | 设计良好 |
| > 1.7T | 偏高 | 增大齿宽或降低气隙磁密 |

### 气隙磁密 B_g
| 范围 | 状态 | 建议 |
|------|------|------|
| < 0.8T | 偏低 | 增加永磁体厚度 |
| 0.8-1.1T | 合理 ✓ | 设计良好 |
| > 1.1T | 偏高 | 注意高温退磁风险 |

### 轭部磁密 B_j
| 范围 | 状态 | 建议 |
|------|------|------|
| < 1.2T | 偏低 | 材料利用率低 |
| 1.2-1.5T | 合理 ✓ | 设计良好 |
| > 1.5T | 偏高 | 增大轭高 |

## 后续扩展计划

- [ ] 添加JMAG/ANSYS Maxwell仿真对比验证
- [ ] 增加绕组设计模块(槽满率、线径选择)
- [ ] 添加效率Map计算
- [ ] 增加温度场耦合计算
- [ ] 添加损耗计算(铜损、铁损、机械损耗)

## 参考资料

1. 《现代永磁电机理论与设计》- 唐任远
2. 《电机设计》- 陈世坤
3. 《永磁同步电机实用设计及应用技术》
4. IMA知识库: 电机教程|自学知识库

---

**更新日期**: 2026-04-24
**版本**: v2.0
