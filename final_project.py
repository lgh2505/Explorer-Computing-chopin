
import streamlit as st
import pandas as pd

"# Ray Casting 기반 1인칭 FPS 게임의 Python 구현 - 시점 제어와 전투·스킬 시스템을 포함한 게임플레이 설계 "

"## 1. 연구배경 및 필요성"
"평소 FPS 게임에 대한 높은 관심을 바탕으로, 본 프로젝트를 통해 1인칭 슈팅 게임을 직접 구현해보고자 하였습니다."
"레이캐스팅(Ray Casting) 기법을 활용하여 2차원 맵을 기반으로 3차원 시점의 화면을 구현함으로써, 시점 표현과 공간 투영의 원리를 탐구하였고,"
"Pygame을 활용한 구현 과정을 통해 게임이 동작하는 구조와 핵심 메커니즘을 이해할 수 있었습니다."
"이러한 과정은 게임을 플레이하는 것을 넘어, 게임 시스템과 프로그램의 실행 원리에 대한 이해를 심화하는 데 의의가 있다고 생각합니다."

"## 2. 프로젝트 진행과정"
"본 프로젝트는 레이캐스팅 기법을 적용하여 2차원 맵 상에 1인칭 시점의 플레이어를 배치하는 단계부터 시작하였습니다."
"이후 시야각(FOV) 및 시점 조정, 점프와 줌 기능을 구현하여 플레이어의 시점 제어를 확장하였고,"
"다음으로 투사체 발사, 배경음악, 이동하는 오브젝트와 스킬 시스템을 추가하여 기본적인 게임플레이 구조를 완성하였습니다."
"오브젝트 디자인을 위해서는 Selenium 기반 웹 크롤링을 통해 공개 게임 에셋을 수집하였으며, 해당 과정은 이후 항목에서 자세히 서술합니다."

"## 3. 프로젝트 성과"

"### **(1) 기능**"
"**1. 기본 기능**"
"- w,a,s,d 키로 전후좌우 이동이 가능하며, 스페이스 바로 점프가 가능하다."
"- 마우스를 이동하여 상하좌우로 시야를 조정할 수 있다."
"- 마우스 좌클릭으로 투사체를 발사할 수 있으며, 사운드 효과가 동반된다. 투사체는 직진하여 벽에 부딪히면 소멸한다."
"- p 키를 누르면 배경음악이 꺼지고, 다시 p키를 누르면 배경음악이 재생된다."

"**2. 오브젝트 설명**"
"- 우주선 오브제는 플레이어처럼 투사체를 발사하며, 폭탄에 닿으면 HP가 감소한다."
st.image("./images/start_screen.png", caption="Object Image")

"**3. zoom 기능**"
"- 마우스 우클릭으로 확대가 가능하다."
st.image("./images/zoom_in.png", caption="Zoom_in Image")

"**4. 1인칭-3인칭 시점 전환 기능**"
"- 마우스 휠을 내리면 3인칭으로 시점이 전환되며, 휠을 올리면 1인칭으로 시점이 전환된다."
st.image("./images/Third_Person_View.png", caption="Third-Person View Image")

"**5. 미니맵 기능**"
"- 미니맵을 통해 플레이어의 위치와 과녁의 위치를 확인할 수 있다."
st.image("./images/minimap.png", caption="minimap Image")

"**6. HP바**"
"- 내 HP와 적의 HP를 확인할 수 있다."
st.image("./images/TARGET_HP.png", caption="HP bar Image")

"**7. 스킬**"
"- R키를 누르면 보고 있는 방향으로 5칸 앞으로 순간이동하며,"
"T키를 누르면 오브젝트와 투사체의 이동 속도를 5초 동안 절반으로 낮춘다."

"**8. 무기 전환**"
"- 1을 누르면 pistol로 전환하여, 더 빠른 속도로 투사체를 발사할 수 있다."
"20발을 모두 쏜 후에는 장전이 필요하며, 다시 1키를 누르면 기본 무기로 전환된다."

"**9. 자동/수동 종료 기능**"
"- 플레이어가 모든 적을 처치하거나, HP가 0이 된다면, 게임이 자동으로 종료된다. ESC키를 눌러 수동으로 종료할 수도 있다."
st.image("./images/GAME_CLEAR.png", caption="Game Clear Image")
st.image("./images/GAME_OVER.png", caption="Game Over Image")

"### (2) 주요 기능 구현 방법"
"**1. 3D**"
"Ray Casting 기법을 통해 2D맵을 3D처럼 보이도록 구현하였다."
"핵심 함수: cast_rays(cam_x, cam_y, angle, fov)"

"**2. 상하 시선**"
"pitch를 마우스 y이동으로 바꾸고 PITCH_MIN~PITCH_MAX로 제한하였으며,"
"수평선의 위치를 바꿔 상하 시선을 구현하였다."

"**3. 점프 및 착지**"
"cam_z는 카메라의 높이를 의미하는 변수로,"
"점프 시 vz = -JUMP_VELOCITY, 이후 GRAVITY로 낙하하도록 하였고,"
"벽/스프라이트 렌더링에서 parallax = int(-cam_z * PARALLAX_STRENGTH / d)를 적용해"
"가까운 물체일수록 더 크게 흔들려 점프 시 시점 변화가 강조되도록 하였다."

"**4. zoom 기능**"
"zoom 기능은 FOV 보간과 투영면 계산을 적용하여 구현하였다"

"**5. 미니맵**"
"미니맵은 수정 가능한 2차원 리스트 형태로 구성하였다."
"핵심 함수: MAP = [list(row) for row in MAP]"

"**6. 스킬**"
"대쉬 스킬은 벽을 관통하지 않도록 하기 위해,"
"BLINK_STEP 간격으로 조금식 앞을 검사하며 벽이 나오면 멈추는 방식으로 설계하였다."

"시간 스킬은 오브젝트와 투사체에만 적용되는 dt를 따로 만들어, 속도가 느려지도록 조정하였다."
"핵심 함수: dt_entities = dt * (TIME_SLOW_FACTOR if slow_active else 1.0)"

"7. **무기 전환**"
"pistol 기능은 상태 머신(State Machine) 형태로,"
"입력(발사, 무기 전환)과 조건(탄창 잔량, 장전 시간)에 따라"
"발사 가능 여부와 발사 속도가 달라지도록 설계하였다."

"### (3) 데이터 수집 과정"

st.markdown("""
Selenium을 이용해 OpenGameArt와 Game-icons의 동적 웹 페이지를 스크롤 방식으로 로딩한 뒤,
이미지 URL을 추출·필터링하여 게임 오브젝트에 활용할 에셋을 자동 수집하였다.
""")

st.markdown("[OpenGameArt: 공개 게임 에셋 제공 사이트, OpenGameArt](https://opengameart.org/)")
st.markdown("[Game-icons: 무료 아이콘 제공 사이트](https://game-icons.net/)")

"다음은 크롤링 후 실제 게임에 적용한 사진들입니다."
st.image("./images/player.jpg", caption="player Image(3인칭)", width=150)
st.image("./images/target_red.png", caption="target_red Image")
st.image("./images/target_blue.png", caption="target_blue(bomb) Image")
st.image("./images/target_green.png", caption="target_green(spaceship) Image")
st.image("./images/slow_icon.png", caption="slow_icon Image", width=150)
st.image("./images/pistol_icon.png", caption="pistol_icon Image", width=150)

"### (4) 게임에 사용된 소리"

"1. 게임 배경음악 (출처: Garage Band로 직접 작곡)"
st.audio("./sound/bgm.ogg", format="audio/ogg")
"2. 투사체 발사 효과음 (출처: https://artlist.io)"
st.audio("./sound/projectile.mp3", format="audio/mp3")

"## 4. 프로젝트 기대효과"
"본 프로젝트를 통해 Python과 Pygame에 대한 이해를 심화하고, 게임 구현 전반에 필요한 기본적인 구조와 원리를 학습할 수 있었습니다."
"또한 레이캐스팅, 시점 제어, 상태 머신 등 게임 프로그래밍의 핵심 개념을 실제 구현을 통해 체득하였습니다."
"복합적인 기능을 단계적으로 설계·확장하는 과정을 통해 시스템적 사고와 문제 해결 능력을 향상시킬 수 있었으며,"
"이러한 경험은 향후 다양한 프로그래밍 언어와 게임 구현 방식을 탐구하는 데 있어 중요한 기초이자 디딤돌이 될 것으로 기대됩니다."
