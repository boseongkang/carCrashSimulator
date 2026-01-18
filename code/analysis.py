import pandas as pd
import matplotlib.pyplot as plt

# 1. 아까 받은 CSV 파일 불러오기
df = pd.read_csv('../data/waymo_physics_data.csv') # 파일 경로 맞춰주세요!

# 2. 가장 속도가 빨랐던 순간 찾기
max_speed = df['Speed_MPH'].max()
print(f"🏎️ 데이터셋에서 가장 빨랐던 속도: {max_speed:.2f} MPH")

# 3. '급감속(브레이크)'한 차량 찾기
# (가속도가 음수이면서 크기가 큰 경우)
# 간단하게 속도 차이(diff)로 가속도 근사 계산
df['Accel'] = df.groupby('Vehicle_ID')['Speed_MPH'].diff() / 0.1 # 0.1초 간격

# 급브레이크(-10 mph/s 이하) 밟은 데이터만 필터링
braking_events = df[df['Accel'] < -10]

print(f"🚨 급브레이크 감지된 횟수: {len(braking_events)}번")

if not braking_events.empty:
    # 첫 번째 급브레이크 차량의 속도 그래프 그리기
    target_id = braking_events.iloc[0]['Vehicle_ID']
    target_data = df[df['Vehicle_ID'] == target_id]
    
    plt.figure(figsize=(10, 5))
    plt.plot(target_data['Time_Sec'], target_data['Speed_MPH'], label='Speed (MPH)')
    plt.title(f"Braking Scenario (Vehicle ID: {target_id})")
    plt.xlabel("Time (sec)")
    plt.ylabel("Speed (MPH)")
    plt.grid(True)
    plt.legend()
    plt.show()

