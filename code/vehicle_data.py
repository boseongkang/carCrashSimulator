"""
[차량 제원 데이터베이스]
작성자: User
출처: Jaguar Official Homepage & Wikipedia (Official Specs)
적용 모델: Jaguar I-PACE EV400 (Waymo Base Vehicle)
"""

CAR_DB = {
    # 📌 메인 차량: Jaguar I-PACE EV400
    "waymo_jaguar_ipace": {
        "brand": "Jaguar",
        "model": "I-PACE EV400",
        "year": 2019, 
        
        # 1. 중량 (Weight)
        "mass_kg": 2170,        # 공식 공차중량
        
        # 2. 치수 (Dimensions) - 사용자 보정값 완벽 반영
        "length_m": 4.681,      # 전장
        "width_m": 2.139,       # 전폭 (미러 포함)
        "width_folded_m": 2.012,# 전폭 (미러 접음)
        "width_body_m": 1.895,  # 전폭 (차체만)
        "height_m": 1.557,      # 전고
        "wheelbase_m": 2.990,   # 휠베이스
        
        # 3. 섀시 (Chassis)
        "track_front_m": 1.643, 
        "track_rear_m": 1.661,  
        "turning_circle_curb_m": 12.350,
        "turning_circle_wall_m": 12.7500, 
        "drag_coeff": 0.29,     

        # 4. 타이어 (Tires) - 사용자 확인 공기압 반영
        "tire_spec_main": "245/50R20", 
        "tire_pressure_psi_front": 37, 
        "tire_pressure_psi_rear": 40, 
        # (참고: 뒤쪽 공기압이 더 높은 것은 급가속/짐 적재 대응을 위함)

        # 5. 성능 데이터 (Performance) - 사용자 확인 데이터(0-60mph)로 변경
        # [가속] 0-60 mph (0-96.56 km/h) : 4.5초
        # *시뮬레이터가 0-60mph 데이터를 우선 사용하도록 키 이름 변경
        "accel_0_60mph_sec": 4.5, 
        
        # [제동] 60-0 mph (96.56-0 km/h)
        # https://fastestlaps.com/models/jaguar-i-pace
        # 이건 자료가 없어서 구글에서 나온 결과값으로 
        "braking_dist_at_60mph_m": 34
    }
}

TESLA_M3 = {
    # 📌 메인 차량: 2024 Tesla Model 3 RWD (Highland)
    "tesla_m3_std_2024": {
        "brand": "Tesla",
        "model": "Model 3 Rear-Wheel Drive (2024 Highland)",
        "year": 2024,
        
        # 1. 중량 (Weight)
        "mass_kg": 1760,        # 공차중량 (3,880 lbs)

        # 2. 치수 (Dimensions) - mm -> m 변환
        "length_m": 4.720,      
        "width_m": 2.089,       
        "width_folded_m": 1.933,
        "width_body_m": 1.850,  
        "height_m": 1.440,      
        "wheelbase_m": 2.875,   
        "ground_clearance_m": 0.138, 

        # 3. 섀시 (Chassis)
        "track_front_m": 1.582, 
        "track_rear_m": 1.560,  
        "turning_circle_m": 11.7, 
        "drag_coeff": 0.219,    

        # 4. 타이어 (Tires)
        "tire_spec_18in": "235/45R18", 
        "tire_spec_19in": "235/40R19", 
        "tire_pressure_psi": 42,       

        # 5. 성능 데이터 (User Provided Data) https://www.motortrend.com/reviews/2024-tesla-model-3-highland-0-60-mph-and-quarter-mile-times-tested
        # [사용자 입력] 0-60 mph: 5.6초
        "accel_0_60mph_sec": 5.6,
        
        # [사용자 입력] 60-0 mph Braking: 115 ft
        # 변환: 115 feet * 0.3048 = 35.05 meters
        "braking_dist_at_60mph_m": 35.05
    }
}

def get_car_specs(car_key):
    """차량 키를 입력하면 스펙 딕셔너리를 반환"""
    return CAR_DB.get(car_key, None)