import numpy as np
import physics_constants as phy
import vehicle_data as v_data

class AccidentSimulator:
    def __init__(self, car_key='waymo_jaguar_ipace'):
        """
        [Waymo Jaguar I-PACE 물리 엔진 초기화]
        - 차량 스펙 로드
        - 최대 제동 한계(Max Braking G) 계산
        """
        # 1. 차량 정보 로드
        self.specs = v_data.get_car_specs(car_key)
        if not self.specs:
            raise ValueError(f"❌ 오류: 차량 ID '{car_key}'를 찾을 수 없습니다.")
        
        # 2. 차량의 '최대 제동 성능(Max Braking G)' 역산
        # 공식: a = v^2 / 2d (등가속도 운동)
        # 데이터: 60mph(26.8m/s)에서 34m 제동 (사용자 확정 데이터)
        v_test_mph = 60
        v_test_ms = v_test_mph * 0.44704  # mph -> m/s 변환
        d_test_m = self.specs['braking_dist_at_60mph_m']
        
        # 최대 감속도 (m/s^2) 및 G-Force 계산
        self.max_decel_ms2 = (v_test_ms ** 2) / (2 * d_test_m)
        self.max_braking_g = self.max_decel_ms2 / phy.ENV["G_MS2"]  # G 단위 변환
        
        print("="*60)
        print(f"🚘 [Simulation Engine Loaded] : {self.specs['year']} {self.specs['model']}")
        print(f"📏 Spec: Length {self.specs['length_m']}m / Weight {self.specs['mass_kg']}kg")
        print(f"🛑 Max Braking Performance: {self.max_braking_g:.3f} G (Derived from {d_test_m}m @ 60mph)")
        print("="*60)

    def calculate_road_loads(self, current_speed_kmh):
        """
        [Gillespie Chapter 2 수식 적용 구간]
        현재 속도에서 차량이 받는 '주행 저항(Road Load)'을 계산
        1. 공기 저항 (Aerodynamic Drag, Da)
        2. 구름 저항 (Rolling Resistance, Rx)
        """
        # 단위 변환
        v_ms = current_speed_kmh / 3.6
        
        # 물리 상수 호출
        rho = phy.ENV["RHO_AIR_KG_M3"]  # 공기밀도 (1.225)
        g = phy.ENV["G_MS2"]            # 중력가속도 (9.80665)
        
        # 차량 스펙 호출
        Cd = self.specs['drag_coeff']       # 공기저항계수 (0.29)
        # 전면 면적(A) 추정: 폭 x 높이 x 0.85 (일반적인 자동차 공학 추정치)
        Area = self.specs['width_body_m'] * self.specs['height_m'] * 0.85
        Mass = self.specs['mass_kg']
        
        # 1. 공기 저항 계산 (Da) using physics_constants formulas
        # 식: Da = 0.5 * rho * Cd * A * V^2
        drag_force_n = phy.ACCELERATION_FORMULAS["Da"](rho, Cd, Area, v_ms)
        
        # 2. 구름 저항 계산 (Rx) using physics_constants formulas
        # 식: Rx = fr * W (W = mg)
        # fr(구름저항계수)은 아스팔트 기준 약 0.015 (Gillespie 값 참조)
        rolling_res_n = phy.ACCELERATION_FORMULAS["Rx"](0.015, Mass, g)
        
        return drag_force_n, rolling_res_n

    def run_simulation(self, current_speed_kmh, obstacle_dist_m, road_type='WET_ASPHALT', reaction_time=1.5):
        """
        [메인 시뮬레이션 루프]
        입력: 속도, 거리, 노면, 반응시간
        출력: 충돌 여부, 제동 거리, 물리적 힘 분석 결과
        """
        # 1. 단위 변환 (km/h -> m/s)
        v0 = current_speed_kmh / 3.6
        
        # 2. 주행 저항 계산 (Chapter 2 공식 활용!)
        # 이 힘들은 차가 멈추는 것을 도와주는 자연 감속력입니다.
        drag_n, roll_n = self.calculate_road_loads(current_speed_kmh)
        total_resistance_n = drag_n + roll_n
        
        # 3. 제동력 결정 (Friction Circle Theory)
        road_mu = phy.FRICTION.get(road_type, 0.6)
        
        # 실제 제동 감속도 (G) = min(차량성능, 노면마찰)
        real_braking_g = min(self.max_braking_g, road_mu)
        real_braking_ms2 = real_braking_g * phy.ENV["G_MS2"]
        
        # 4. 공주 거리 (Reaction Distance)
        dist_reaction = v0 * reaction_time
        
        # 5. 제동 거리 (Braking Distance)
        # d = v^2 / 2a
        dist_braking = (v0 ** 2) / (2 * real_braking_ms2)
        
        # 6. 최종 정지 거리
        total_stopping_dist = dist_reaction + dist_braking
        
        # 7. 충돌 판정
        is_crash = total_stopping_dist > obstacle_dist_m
        
        # 8. 충돌 속도 계산 (에너지 보존)
        impact_speed_kmh = 0.0
        if is_crash:
            dist_available = obstacle_dist_m - dist_reaction
            if dist_available <= 0:
                impact_speed_ms = v0
            else:
                v_impact_sq = (v0**2) - (2 * real_braking_ms2 * dist_available)
                impact_speed_ms = np.sqrt(v_impact_sq) if v_impact_sq > 0 else 0
            impact_speed_kmh = impact_speed_ms * 3.6

        # 결과 리포트 생성
        return {
            "scenario": f"{road_type} / {current_speed_kmh}km/h",
            "is_crash": is_crash,
            "impact_speed_kmh": round(impact_speed_kmh, 1),
            "distances": {
                "reaction_m": round(dist_reaction, 2),
                "braking_m": round(dist_braking, 2),
                "total_m": round(total_stopping_dist, 2),
                "obstacle_m": obstacle_dist_m
            },
            "physics_analysis": {
                "friction_mu": road_mu,
                "braking_g": round(real_braking_g, 2),
                # 여기서 우리가 추가한 Chapter 2 수식의 결과를 보여줍니다.
                "aero_drag_N": round(drag_n, 1),      # 공기저항(뉴턴)
                "rolling_res_N": round(roll_n, 1)     # 구름저항(뉴턴)
            },
            "limit_factor": "ROAD_FRICTION" if road_mu < self.max_braking_g else "CAR_BRAKE"
        }

if __name__ == "__main__":
    # 시뮬레이터 테스트 실행
    sim = AccidentSimulator()
    
    # 테스트 케이스: 80km/h로 빗길 주행 중 40m 앞 장애물
    result = sim.run_simulation(80, 40, 'WET_ASPHALT', 1.0)
    
    print(f"\n[📊 Simulation Result]")
    print(f"Scenario: {result['scenario']}")
    print(f"Crash: {'💥 YES (충돌)' if result['is_crash'] else '✅ NO (회피)'}")
    print(f"Impact Speed: {result['impact_speed_kmh']} km/h")
    print(f"Stopping Dist: {result['distances']['total_m']} m")
    
    print("\n[🧪 Physics Analysis (Gillespie Formulas)]")
    print(f"Applied Friction (mu): {result['physics_analysis']['friction_mu']}")
    print(f"Aerodynamic Drag (Da): {result['physics_analysis']['aero_drag_N']} N (Helping Decel)")
    print(f"Rolling Resistance (Rx): {result['physics_analysis']['rolling_res_N']} N")