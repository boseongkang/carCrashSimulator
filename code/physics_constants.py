import math

"""
[물리 환경 상수 및 노면 데이터베이스]
Project: Autonomous Vehicle Safety Simulation
Author: User (Candidate for Research Assistant)

[Data Sources & References]
1. Gravity: ISO 80000-3 (Quantities and units — Space and time).
2. Friction (Mu): NHTSA 'The Pneumatic Tire', Gillespie 'Fundamentals of Vehicle Dynamics'.
3. Reaction Time: AASHTO 'Green Book'.
"""

# -----------------------------------------------------------
# 1. 환경 상수 (ENV) - 시뮬레이터 호환성 필수 항목
# -----------------------------------------------------------
ENV = {
    # 중력 가속도 (Standard Gravity) - ISO 80000-3
    "G_MS2": 9.80665,
    
    # 공기 밀도 (Air Density at Sea Level)
    # Gillespie Eq 2.16 공기저항 계산에 필수
    "RHO_AIR_KG_M3": 1.225
}

# -----------------------------------------------------------
# 2. 노면 마찰계수 (FRICTION)
# -----------------------------------------------------------
FRICTION = {
    "DRY_ASPHALT": 0.85,  # Gillespie Range: 0.80-0.90
    "WET_ASPHALT": 0.60,  # NHTSA Data (Conservative)
    "DRY_CONCRETE": 0.80,
    "WET_CONCRETE": 0.55,
    "SNOW": 0.25,         # Bosch Handbook
    "ICE": 0.10
}

# -----------------------------------------------------------
# 3. 운전자 반응 속도 (REACTION_TIME)
# -----------------------------------------------------------
REACTION_TIME = {
    "DESIGN_STANDARD": 2.5,  # AASHTO (95%)
    "AVERAGE": 1.5,          # Traffic Eng (Avg)
    "FAST_AI": 0.5
}

# -----------------------------------------------------------
# 4. 수식용 상수 (Constants for Formulas)
# -----------------------------------------------------------
# 토크 변환: 1 Nm = 0.737562 ft-lb
UNIT_NM_TO_FTLB = 0.737562

# [Missing Constant Fixed] 마력 계산용 분모 (33,000 ft-lb/min)
CONST_HP_DIVISOR = 33000 

# Gillespie Eq 2.1의 핵심 상수 (33,000 / 2pi)
CONST_GILLESPIE_DIVISOR = 5252

# -----------------------------------------------------------
# 5. 가속 성능 공식 (Equations)
# -----------------------------------------------------------
ACCELERATION_FORMULAS = {

    # [Conversion] 토크 변환 (Nm -> ft-lb)
    "T_ftlb": lambda T_nm: T_nm * UNIT_NM_TO_FTLB,

    # [Fundamental 1] 각속도 (Angular Velocity)
    # w = RPM * 2pi (단위: rad/min)
    "w_rad_min": lambda rpm: rpm * 2 * math.pi,

    # [Fundamental 2] Power (일률)
    # P(ft-lb/min) = T(ft-lb) * w(rad/min)
    "P_ftlb_min": lambda T_ftlb, w_rad_min: T_ftlb * w_rad_min,

    # [Eq 2.1 Derived] Horsepower (마력)
    # HP = P(ft-lb/min) / 33000
    "HP_from_P": lambda P_ftlb_min: P_ftlb_min / CONST_HP_DIVISOR,

    # [Eq 2.1 Shortcut] 책의 단축 공식 (바로 계산용)
    # HP = (T[ft-lb] * RPM) / 5252
    "HP_imperial": lambda T_ftlb, rpm: (T_ftlb * rpm) / CONST_GILLESPIE_DIVISOR,

    # [Eq 2.6] Velocity (속도, m/s)
    "V": lambda rpm, gear_ratio, r: (rpm * 2 * math.pi * r) / (60 * gear_ratio),

    # [Eq 2.16] Aerodynamic Drag (공기저항, N)
    # 시뮬레이터에서 phy.ENV["RHO_AIR_KG_M3"] 값을 rho 인자로 넘겨줌
    "Da": lambda rho, Cd, A, V: 0.5 * rho * Cd * A * (V ** 2),

    # [Eq 2.22] Rolling Resistance (구름저항, N)
    "Rx": lambda fr, mass, g: fr * mass * g,

    # [Newton Law] Acceleration (가속도, m/s^2)
    "ax": lambda Fx, Da, Rx, m: (Fx - Da - Rx) / m
}

# -----------------------------------------------------------
# 6. 문서화 (Documentation)
# -----------------------------------------------------------
FORMULA_INFO = {
    "BASIC_POWER": "P(ft-lb/min) = T(ft-lb) * w(rad/min)",
    "HP_DEF": "HP = P(ft-lb/min) / 33000",
    "GILLESPIE_HP": "HP = T(ft-lb) * RPM / 5252"
}