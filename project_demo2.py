import pygame, sys, math

# ----- 기본 설정 -----
W, H = 960, 540
HALF_H = H // 2
FPS = 60

# ▶ FOV를 가변으로 (줌)
FOV_BASE_DEG = 66
FOV_ZOOM_DEG = 38              # 줌 시 FOV(좁을수록 확대)
FOV_LERP_SPEED = 10.0          # FOV 보간 속도 (값↑ = 더 빠른 전환)

# 레이 수/기둥 폭(고정)
NUM_RAYS = 320
MAX_DEPTH = 20.0

MOVE_SPEED = 3.2
ROT_SPEED = math.radians(120)
MOUSE_SENS_BASE = 0.0028       # 기본 좌우 감도
PITCH_SENS_BASE = 0.0022       # 기본 상하 감도
SENS_ZOOM_SCALE = 0.4          # 줌 시 감도 배율(40%)

PITCH_MIN  = -0.6
PITCH_MAX  =  0.6

# 점프/중력
GRAVITY = 2800.0
JUMP_VELOCITY = 900.0
CAM_Z_FLOOR = 0.0
CAM_Z_MAX = 160.0

# 3인칭 카메라
CAMERA_BACK = 0.8
CAMERA_SAFETY_STEPS = 10
PLAYER_RENDER_SCALE = 0.55

# 점프 패럴랙스
PARALLAX_STRENGTH = 0.85
NEAR_CLAMP = 0.15

# 투사체
PROJ_SPEED = 6.0
PROJ_RADIUS_WORLD = 0.18
PROJ_LIFETIME = 3.0
FIRE_COOLDOWN = 0.25
MUZZLE_OFFSET = 0.35

# ── 과녁 정의 (문자 -> 색상/점수) ─────────────────────────
TARGET_DEF = {
    'R': {'color': (220, 60, 60),  'points': 10},  # Red
    'G': {'color': (60, 200, 90),  'points': 15},  # Green
    'B': {'color': (80, 120, 255), 'points': 20},  # Blue
}
TARGET_CHARS = ''.join(TARGET_DEF.keys())

# 테스트용 맵 (R/G/B 과녁 포함)
MAP = [
    "111111111111",
    "1..RGGGBBBB1",
    "1..........1",
    "1.R........1",
    "1..........1",
    "1..........1",
    "1.G........1",
    "1..........1",
    "1..........1",
    "1..........1",
    "1.B........1",
    "111111111111",
]

def is_wall(x, y):
    if x < 0 or y < 0: return True
    j, i = int(x), int(y)
    if i < 0 or i >= len(MAP) or j < 0 or j >= len(MAP[0]): return True
    ch = MAP[i][j]
    # 과녁도 벽처럼 충돌 대상으로 취급
    return ch == '1' or (ch in TARGET_CHARS)
# 과녁 원 충돌 반지름(월드 단위, 타일 1칸=1.0)
TARGET_RADIUS = 0.6

def segment_circle_hit(x0, y0, x1, y1, cx, cy, r):
    """선분 (x0,y0)-(x1,y1)이 원 (cx,cy,r)과 교차하면 True"""
    vx, vy = x1 - x0, y1 - y0
    wx, wy = cx - x0, cy - y0
    vv = vx*vx + vy*vy
    if vv == 0:
        # 정지한 경우: 시작점이 원 안인가
        return (wx*wx + wy*wy) <= r*r
    t = (wx*vx + wy*vy) / vv
    t = 0.0 if t < 0.0 else (1.0 if t > 1.0 else t)
    px, py = x0 + t*vx, y0 + t*vy
    dx, dy = px - cx, py - cy
    return (dx*dx + dy*dy) <= r*r


def cast_rays(cam_x, cam_y, angle, fov):
    """현재 fov에 맞춰 레이를 쏘고, 왜곡 보정 거리 리스트 반환"""
    rays = []
    delta_angle = fov / NUM_RAYS
    start_angle = angle - fov / 2
    for r in range(NUM_RAYS):
        ray_angle = start_angle + r * delta_angle
        sin_a = math.sin(ray_angle); cos_a = math.cos(ray_angle)
        depth = 0.01; hit = False
        while depth < MAX_DEPTH:
            x = cam_x + cos_a * depth
            y = cam_y + sin_a * depth
            if is_wall(x, y):
                hit = True; break
            depth += 0.01
        if not hit: depth = MAX_DEPTH
        depth_corrected = depth * math.cos(ray_angle - angle)
        rays.append(depth_corrected)
    return rays

# ----- 과녁 오브젝트 -----
class Target:
    def __init__(self, col, row, ch):
        self.cx = col + 0.5  # 월드 좌표(타일 중앙)
        self.cy = row + 0.5
        self.ch = ch
        self.color = TARGET_DEF[ch]['color']
        self.points = TARGET_DEF[ch]['points']
        self.alive = True

def parse_targets_from_map():
    targets = []
    for r, line in enumerate(MAP):
        for c, ch in enumerate(line):
            if ch in TARGET_CHARS:
                targets.append(Target(c, r, ch))
    return targets

def render_targets(surface, targets, cam_x, cam_y, yaw, horizon_y, fov, depths):
    """과녁을 벽에 가려지게 그리기"""
    for t in targets:
        if not t.alive:
            continue
        dx, dy = t.cx - cam_x, t.cy - cam_y
        dist = math.hypot(dx, dy)

        if dist < 0.001:
            continue
        ang = math.atan2(dy, dx)
        da = (ang - yaw + math.pi) % (2*math.pi) - math.pi
        half_fov = fov * 0.5
        if abs(da) > half_fov + math.radians(6):
            continue

        screen_x = int((da + half_fov) / (2*half_fov) * W)
        size_px = max(12, min(80, int((0.35 / max(dist, 0.01)) * H)))
        parallax = int((-cam_z) * 0.25 / max(dist, 0.15))
        screen_y = horizon_y + parallax

        # 벽 깊이와 비교 (가려짐 처리)
        ray_idx = int(screen_x * NUM_RAYS / W)
        ray_idx = max(0, min(NUM_RAYS - 1, ray_idx))

        # 중심까지의 '레이 방향 깊이' (벽 깊이와 동일 기준으로 비교)
        center_d = dist * math.cos(da)
        wall_d   = depths[ray_idx]

        # 같은 벽면에 붙은 과녁은 '벽보다 약간 뒤'에 있는 값이 나오므로,
        # 마진(+0.7 타일) 안쪽은 보이도록 허용
        if center_d > wall_d + 0.7:
            continue

        # 그릴 때는 너무 파고들지 않게 벽면 근처 깊이를 사용
        #draw_d = max(NEAR_CLAMP, wall_d - 0.02)
        draw_d = wall_d - 0.02

        outer_r = size_px // 2
        inner_r = max(2, int(outer_r * 0.6))
        bull_r  = max(1, int(outer_r * 0.28))
        pygame.draw.circle(surface, (240, 240, 240), (screen_x, screen_y), outer_r)
        pygame.draw.circle(surface, t.color,         (screen_x, screen_y), inner_r)
        pygame.draw.circle(surface, (255, 255, 255), (screen_x, screen_y), bull_r)


# ----- 투사체 -----
class Projectile:
    def __init__(self, x, y, yaw, color=(120, 200, 255)):
        self.x = x; self.y = y
        self.vx = math.cos(yaw) * PROJ_SPEED
        self.vy = math.sin(yaw) * PROJ_SPEED
        self.life = PROJ_LIFETIME
        self.color = color

    def update(self, dt, targets):
        gained = 0
        steps = max(1, int(max(abs(self.vx), abs(self.vy)) * dt * 4))
        sx = (self.vx * dt) / steps
        sy = (self.vy * dt) / steps
        for _ in range(steps):
            prevx, prevy = self.x, self.y
            nx = self.x + sx; ny = self.y + sy

            # --- 과녁 세그먼트-원 충돌 검사 ---
            for t in targets:
                if not t.alive:
                    continue
                if segment_circle_hit(prevx, prevy, nx, ny, t.cx, t.cy, TARGET_RADIUS):
                    t.alive = False
                    row = MAP[int(t.cy)]
                    MAP[int(t.cy)] = row[:int(t.cx)] + '1' + row[int(t.cx)+1:]
                    gained += t.points
                    self.life = 0.0
                    return gained

            # --- 벽 충돌 ---
            if is_wall(nx, ny):
                self.life = 0.0
                return gained

            # 이동 확정
            self.x, self.y = nx, ny

        self.life -= dt
        return gained

    def is_dead(self):
        return self.life <= 0.0

    def render(self, surface, cam_x, cam_y, yaw, horizon_y, fov):
        # 카메라 기준
        dx = self.x - cam_x; dy = self.y - cam_y
        dist = math.hypot(dx, dy)
        if dist < 0.001: return
        ang = math.atan2(dy, dx)
        da = (ang - yaw + math.pi) % (2*math.pi) - math.pi
        half_fov = fov * 0.5
        if abs(da) > half_fov + math.radians(5):  # 시야 밖
            return
        # 화면 x
        screen_x = int((da + half_fov) / (2*half_fov) * W)
        # 거리 역수로 화면 반지름
        radius_px = max(6, int((PROJ_RADIUS_WORLD / max(dist, 0.01)) * H * 1.2))
        # 점프 패럴랙스(약하게)
        parallax = int((-cam_z) * 0.25 / max(dist, 0.15))
        screen_y = horizon_y + parallax
        pygame.draw.circle(surface, self.color, (screen_x, screen_y), radius_px)

def lerp(a, b, t):
    return a + (b - a) * t

def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    clock = pygame.time.Clock()

    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)

    # 플레이어 상태
    px, py = 2.5, 2.5
    yaw = 0.0
    pitch = 0.0
    third_person = False
    
    # 점프
    global cam_z
    cam_z = CAM_Z_FLOOR
    vz = 0.0
    on_ground = True

    # 과녁/점수
    targets = parse_targets_from_map()
    score = 0

    # 투사체
    projectiles = []
    fire_cd = 0.0

    # ▶ 줌 상태
    fov_cur = math.radians(FOV_BASE_DEG)   # 현재 FOV(라디안)
    zooming = False

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        # ----- 이벤트 -----
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False
                elif e.key == pygame.K_SPACE and on_ground:
                    vz = -JUMP_VELOCITY; on_ground = False
            elif e.type == pygame.MOUSEMOTION:
                dx, dy = e.rel
                # 줌에 따라 감도 축소
                sens_scale = SENS_ZOOM_SCALE if zooming else 1.0
                yaw   +=  dx * (MOUSE_SENS_BASE * sens_scale)
                pitch -=  dy * (PITCH_SENS_BASE * sens_scale)
                pitch = max(PITCH_MIN, min(PITCH_MAX, pitch))
            elif e.type == pygame.MOUSEWHEEL:
                if e.y < 0: third_person = True
                elif e.y > 0: third_person = False
            elif e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 3:   # 우클릭 눌렀을 때
                    zooming = True
            elif e.type == pygame.MOUSEBUTTONUP:
                if e.button == 3:   # 우클릭 뗐을 때
                    zooming = False

        keys = pygame.key.get_pressed()

        # 좌클릭 발사(쿨다운)
        fire_cd = max(0.0, fire_cd - dt)
        if pygame.mouse.get_pressed(3)[0] and fire_cd <= 0.0:
            muzzle_x = px + math.cos(yaw) * MUZZLE_OFFSET
            muzzle_y = py + math.sin(yaw) * MUZZLE_OFFSET
            if not is_wall(muzzle_x, muzzle_y):
                projectiles.append(Projectile(muzzle_x, muzzle_y, yaw, color=(120,200,255)))
                fire_cd = FIRE_COOLDOWN

        # 보조 회전(옵션)
        if keys[pygame.K_LEFT]:  yaw -= ROT_SPEED * dt
        if keys[pygame.K_RIGHT]: yaw += ROT_SPEED * dt

        # ----- 이동 -----
        dir_x = math.cos(yaw); dir_y = math.sin(yaw)
        right_x = math.cos(yaw + math.pi/2); right_y = math.sin(yaw + math.pi/2)
        nx, ny = px, py
        speed = MOVE_SPEED * dt * (0.50 if zooming else 1.0)
        if keys[pygame.K_w]: nx += dir_x * speed; ny += dir_y * speed
        if keys[pygame.K_s]: nx -= dir_x * speed; ny -= dir_y * speed
        if keys[pygame.K_d]: nx += right_x * speed; ny += right_y * speed
        if keys[pygame.K_a]: nx -= right_x * speed; ny -= right_y * speed
        if not is_wall(nx, py): px = nx
        if not is_wall(px, ny): py = ny

        # ----- 점프/중력 -----
        if not on_ground:
            vz += GRAVITY * dt
            cam_z += vz * dt
            if cam_z >= CAM_Z_FLOOR:
                cam_z = CAM_Z_FLOOR; vz = 0.0; on_ground = True
        cam_z = max(-CAM_Z_MAX, min(CAM_Z_FLOOR, cam_z))

        # ----- 카메라 -----
        cam_x, cam_y = px, py
        if third_person:
            back_target_x = px - dir_x * CAMERA_BACK
            back_target_y = py - dir_y * CAMERA_BACK
            cx, cy = back_target_x, back_target_y
            if is_wall(cx, cy):
                for s in range(1, CAMERA_SAFETY_STEPS+1):
                    t = s / CAMERA_SAFETY_STEPS
                    cx = px - dir_x * (CAMERA_BACK * (1 - t))
                    cy = py - dir_y * (CAMERA_BACK * (1 - t))
                    if not is_wall(cx, cy): break
                else:
                    cx, cy = px, py
            cam_x, cam_y = cx, cy

        # ▶ 목표 FOV로 부드럽게 보간
        fov_target = math.radians(FOV_ZOOM_DEG if zooming else FOV_BASE_DEG)
        fov_cur = lerp(fov_cur, fov_target, min(1.0, FOV_LERP_SPEED * dt))

        # ----- 레이캐스팅 -----
        depths = cast_rays(cam_x, cam_y, yaw, fov_cur)

        # ----- 투사체 업데이트 (+ 점수) -----
        gained_total = 0
        for p in projectiles:
            gained_total += p.update(dt, targets)
        if gained_total:
            score += gained_total
        projectiles = [p for p in projectiles if not p.is_dead()]

        # ----- 렌더 -----
        # 피치 → 지평선
        pitch_off = int(math.tan(pitch) * H * 0.45)
        horizon_y = HALF_H + pitch_off

        # 하늘/바닥
        SKY_COLOR   = (0, 0, 0)
        FLOOR_COLOR = (200, 200, 200)
        screen.fill(SKY_COLOR)
        pygame.draw.rect(screen, FLOOR_COLOR, (0, horizon_y, W, H - horizon_y))

        # 벽(항상 밝게)
        SCALE = W // NUM_RAYS
        WALL_COLOR = (100, 100, 100)
        for i, depth in enumerate(depths):
            d = max(depth, NEAR_CLAMP)
            proj_h = min(int((1.0 / d) * H * 0.9), H)
            parallax = int(-cam_z * PARALLAX_STRENGTH / d)
            x = i * SCALE
            y = horizon_y - proj_h // 2 + parallax
            pygame.draw.rect(screen, WALL_COLOR, (x, y, SCALE + 1, proj_h))

        # 과녁
        render_targets(screen, targets, cam_x, cam_y, yaw, horizon_y, fov_cur, depths)

        # 투사체
        for p in projectiles:
            p.render(screen, cam_x, cam_y, yaw, horizon_y, fov_cur)
            
        # 3인칭 플레이어
        if third_person:
            d_cam = max(0.001, math.hypot(px - cam_x, py - cam_y))
            player_h = int((1.0 / d_cam) * H * PLAYER_RENDER_SCALE)
            player_h = max(24, min(player_h, int(H * 0.8)))
            player_w = int(player_h * 0.45)
            cx, cy = W // 2, horizon_y + (player_h // 2) - 6
            rect = pygame.Rect(cx - player_w // 2, cy - player_h, player_w, player_h)
            pygame.draw.rect(screen, (60,180,255), rect, border_radius=6)
            pygame.draw.rect(screen, (20,60,90), rect, width=2, border_radius=6)

        # 미니맵(원래 방식 유지)
        mm = 6
        map_h = len(MAP)
        map_w = len(MAP[0])
        for row, line in enumerate(MAP):
            for col, ch in enumerate(line):
                if ch == '1':
                    c = (70,70,70)
                elif ch in TARGET_CHARS:
                    c = (150,110,110)
                else:
                    c = (35,35,35)
                draw_x = 10 + row * mm
                draw_y = 10 + (map_w - 1 - col) * mm
                pygame.draw.rect(screen, c, (draw_x, draw_y, mm - 1, mm - 1))
        px_rot = py
        py_rot = map_w - 1 - px
        pygame.draw.circle(screen, (0, 200, 255),
                        (10 + int(px_rot * mm), 10 + int(py_rot * mm)), 2)

        # 크로스헤어
        if not third_person:
            cx, cy = W // 2, H // 2
            thickness = 2 if zooming else 3
            length = 7 if zooming else 6
            color = (230, 230, 230)
            pygame.draw.line(screen, color, (cx - length, cy), (cx + length, cy), thickness)
            pygame.draw.line(screen, color, (cx, cy - length), (cx, cy + length), thickness)

        # HUD
        small = pygame.font.SysFont(None, 20)
        info = f"{'3rd' if third_person else '1st'} | FOV={math.degrees(fov_cur):.1f} | zoom={'ON' if zooming else 'OFF'} | score={score}"
        screen.blit(small.render(info, True, (210,220,230)), (12, 12))

        pygame.display.flip()

    pygame.quit(); sys.exit()

if __name__ == "__main__":
    main()