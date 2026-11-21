import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="IRON FIST REALTIME", page_icon="🥊", layout="centered")

# ---------------------------------------------------------
# 1. 데이터 구조 (리스트): 캐릭터 목록 및 전적 기록
# ---------------------------------------------------------
characters = [
    "🥋 진 (밸런스형)",
    "⚡ 카즈야 (파워형)",
    "🦊 화랑 (스피드형)",
    "🐆 킹 (탱커형)",
]

if "battle_history" not in st.session_state:
    st.session_state.battle_history = []


# ---------------------------------------------------------
# 2. 함수 (def) & 3. 조건문 (if-elif-else): 캐릭터 능력치 계산
# ---------------------------------------------------------
def calculate_fighter_stats(char_name, rage_boost):
    if "밸런스형" in char_name:
        hp, atk, spd, color = 100, 12, 5.5, "#3B82F6"
    elif "파워형" in char_name:
        hp, atk, spd, color = 95, 16, 4.8, "#EF4444"
    elif "스피드형" in char_name:
        hp, atk, spd, color = 90, 11, 7.2, "#F59E0B"
    else:  # 탱커형
        hp, atk, spd, color = 125, 13, 4.2, "#10B981"

    # 조건문으로 각성 보너스(공격력 강화) 적용
    if rage_boost >= 3:
        atk += 4
    elif rage_boost == 2:
        atk += 2

    return hp, atk, spd, color


st.title("🥊 IRON FIST : 실시간 2D 격투 아레나")
st.write("캐릭터와 능력치를 세팅한 뒤, 아래 **게임 화면을 마우스로 한 번 클릭**하고 키보드로 직접 싸우세요!")

# 대전 모드 및 캐릭터 선택 UI
mode = st.radio(
    "대전 모드 선택",
    ["🤖 1P vs AI 대전", "👥 2P 친구와 키보드 대전 (한 컴퓨터)"],
    horizontal=True,
)
is_ai_mode = "true" if "AI" in mode else "false"

col1, col2 = st.columns(2)
with col1:
    p1_char = st.selectbox("1P 캐릭터 선택", characters, index=0)
    p1_boost = st.slider("1P 투지 레벨 (공격력 보너스)", 1, 3, 1)
with col2:
    p2_char = st.selectbox("2P 캐릭터 선택", characters, index=1)
    p2_boost = st.slider("2P 투지 레벨 (공격력 보너스)", 1, 3, 1)

p1_hp, p1_atk, p1_spd, p1_color = calculate_fighter_stats(p1_char, p1_boost)
p2_hp, p2_atk, p2_spd, p2_color = calculate_fighter_stats(p2_char, p2_boost)

# 강조 수치(Metric)로 양쪽 전투력 표시
m1, m2 = st.columns(2)
m1.metric(f"1P {p1_char.split(' ')[1]}", f"HP {p1_hp} / 공격력 {p1_atk}", f"스피드 {p1_spd}")
m2.metric(f"2P {p2_char.split(' ')[1]}", f"HP {p2_hp} / 공격력 {p2_atk}", f"스피드 {p2_spd}")

# 조작법 안내
if is_ai_mode == "true":
    st.info("🎮 **1P 조작법:** 이동 `A / D` | 점프 `W` | 펀치 `J` | 발차기 `K` | 가드 `L` | 재시작 `R`")
else:
    st.info(
        "🎮 **1P:** 이동 `A/D`, 점프 `W`, 펀치 `F`, 킥 `G`, 가드 `H`  |  "
        "**2P:** 이동 `←/→`, 점프 `↑`, 펀치 `J`, 킥 `K`, 가드 `L`  |  재시작 `R`"
    )

# ---------------------------------------------------------
# 실시간 HTML5 캔버스 격투 게임 엔진
# ---------------------------------------------------------
game_html = """
<!DOCTYPE html>
<html>
<head>
<style>
  body { margin: 0; background: #111827; display: flex; flex-direction: column; align-items: center; font-family: sans-serif; }
  canvas { border: 3px solid #374151; border-radius: 10px; background: linear-gradient(180deg, #1E293B 0%, #0F172A 78%, #334155 78%, #1E293B 100%); outline: none; cursor: pointer; }
  .hint { color: #9CA3AF; font-size: 13px; margin-top: 6px; }
</style>
</head>
<body>
<canvas id="arena" width="680" height="330" tabindex="0"></canvas>
<div class="hint">※ 키보드가 안 먹히면 위 게임 화면 안쪽을 마우스로 한 번 클릭해 주세요!</div>

<script>
const canvas = document.getElementById("arena");
const ctx = canvas.getContext("2d");
canvas.focus();

const isAI = __IS_AI__;
const keys = {};

window.addEventListener("keydown", (e) => {
  if (["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", "Space"].includes(e.code)) {
    e.preventDefault();
  }
  keys[e.code] = true;
  if (e.code === "KeyR" && gameOver) resetMatch();
});
window.addEventListener("keyup", (e) => { keys[e.code] = false; });
canvas.addEventListener("click", () => canvas.focus());

const GROUND_Y = 260;
const GRAVITY = 0.65;

function createFighter(x, name, maxHp, atk, spd, color, facing) {
  return {
    x, y: GROUND_Y, vx: 0, vy: 0,
    name, maxHp, hp: maxHp, atk, spd, color, facing,
    state: "idle", timer: 0, hasHit: false, onGround: true
  };
}

let p1, p2, gameOver, winnerText, sparks;

function resetMatch() {
  p1 = createFighter(150, "__P1_NAME__", __P1_HP__, __P1_ATK__, __P1_SPD__, "__P1_COLOR__", 1);
  p2 = createFighter(530, "__P2_NAME__", __P2_HP__, __P2_ATK__, __P2_SPD__, "__P2_COLOR__", -1);
  gameOver = false;
  winnerText = "";
  sparks = [];
}

resetMatch();

function startAttack(fighter, type) {
  if (fighter.state === "idle" || fighter.state === "block") {
    fighter.state = type;
    fighter.timer = type === "punch" ? 14 : 20;
    fighter.hasHit = false;
  }
}

function updateFighter(f, controls, target) {
  if (f.timer > 0) {
    f.timer--;
    if (f.timer === 0) f.state = "idle";
  }

  // 바라보는 방향 자동 전환
  if (f.state === "idle" || f.state === "block") {
    f.facing = target.x >= f.x ? 1 : -1;
  }

  // 이동 및 방어 입력 (공격/피격 경직 중이 아닐 때)
  if (f.state === "idle" || f.state === "block") {
    if (controls.block) {
      f.state = "block";
      f.vx *= 0.7;
    } else {
      f.state = "idle";
      if (controls.left) f.vx = -f.spd;
      else if (controls.right) f.vx = f.spd;
      else f.vx *= 0.7;

      if (controls.jump && f.onGround) {
        f.vy = -13;
        f.onGround = false;
      }
      if (controls.punch) startAttack(f, "punch");
      else if (controls.kick) startAttack(f, "kick");
    }
  } else {
    f.vx *= 0.85;
  }

  // 물리 이동 적용
  f.x += f.vx;
  f.y += f.vy;
  if (!f.onGround) f.vy += GRAVITY;

  if (f.y >= GROUND_Y) {
    f.y = GROUND_Y;
    f.vy = 0;
    f.onGround = true;
  }
  f.x = Math.max(40, Math.min(canvas.width - 40, f.x));

  // 공격 타격 판정
  if ((f.state === "punch" || f.state === "kick") && !f.hasHit) {
    const activeFrame = (f.state === "punch" && f.timer <= 9 && f.timer >= 5) ||
                        (f.state === "kick" && f.timer <= 13 && f.timer >= 7);
    if (activeFrame) {
      const reach = f.state === "punch" ? 68 : 85;
      const inFront = (f.facing === 1 && target.x >= f.x && target.x - f.x <= reach) ||
                      (f.facing === -1 && target.x <= f.x && f.x - target.x <= reach);
      const sameHeight = Math.abs(f.y - target.y) < 55;

      if (inFront && sameHeight) {
        f.hasHit = true;
        let dmg = f.state === "punch" ? f.atk : Math.round(f.atk * 1.35);
        if (target.state === "block") {
          dmg = Math.max(2, Math.round(dmg * 0.25));
          target.vx = f.facing * 5;
          sparks.push({ x: target.x, y: target.y - 45, color: "#60A5FA", life: 12 });
        } else {
          target.state = "hit";
          target.timer = 12;
          target.vx = f.facing * 9;
          target.vy = -4;
          target.onGround = false;
          sparks.push({ x: target.x, y: target.y - 45, color: "#FBBF24", life: 15 });
        }
        target.hp = Math.max(0, target.hp - dmg);
      }
    }
  }
}

function getAIControls(ai, player) {
  const dist = Math.abs(ai.x - player.x);
  const c = { left: false, right: false, jump: false, punch: false, kick: false, block: false };

  if ((player.state === "punch" || player.state === "kick") && dist < 95 && Math.random() < 0.45) {
    c.block = true;
    return c;
  }
  if (dist > 65) {
    if (player.x < ai.x) c.left = true;
    else c.right = true;
    if (Math.random() < 0.015) c.jump = true;
  } else {
    const r = Math.random();
    if (r < 0.07) c.punch = true;
    else if (r < 0.12) c.kick = true;
    else if (r < 0.15) c.block = true;
  }
  return c;
}

function drawFighter(f) {
  ctx.save();
  ctx.translate(f.x, f.y);

  // 바닥 그림자
  ctx.fillStyle = "rgba(0,0,0,0.35)";
  ctx.beginPath();
  ctx.ellipse(0, 4, 24, 7, 0, 0, Math.PI * 2);
  ctx.fill();

  // 피격 시 깜빡임
  ctx.fillStyle = f.state === "hit" ? "#FFFFFF" : f.color;

  // 다리
  ctx.fillRect(-14, -28, 10, 28);
  if (f.state === "kick") {
    ctx.fillStyle = "#FDE047";
    ctx.fillRect(f.facing === 1 ? 4 : -54, -36, 50, 11);
    ctx.fillStyle = f.color;
  } else {
    ctx.fillRect(4, -28, 10, 28);
  }

  // 몸통
  ctx.fillRect(-16, -64, 32, 38);

  // 머리 & 머리띠
  ctx.beginPath();
  ctx.arc(0, -78, 15, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = "#F8FAFC";
  ctx.fillRect(-15, -83, 30, 5);

  // 팔 (펀치 / 가드)
  if (f.state === "punch") {
    ctx.fillStyle = "#F87171";
    ctx.fillRect(f.facing === 1 ? 10 : -52, -56, 42, 11);
  } else if (f.state === "block") {
    ctx.strokeStyle = "#38BDF8";
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.arc(f.facing * 12, -50, 32, -Math.PI / 2, Math.PI / 2, f.facing === -1);
    ctx.stroke();
  }

  // 머리 위 이름표
  ctx.fillStyle = "#E2E8F0";
  ctx.font = "bold 12px sans-serif";
  ctx.textAlign = "center";
  ctx.fillText(f.name, 0, -102);

  ctx.restore();
}

function drawHUD() {
  // 1P 체력바
  ctx.fillStyle = "#374151";
  ctx.fillRect(25, 20, 260, 22);
  ctx.fillStyle = p1.hp > 30 ? "#3B82F6" : "#EF4444";
  ctx.fillRect(25, 20, 260 * (p1.hp / p1.maxHp), 22);
  ctx.strokeStyle = "#F9FAFB";
  ctx.strokeRect(25, 20, 260, 22);

  // 2P 체력바
  ctx.fillStyle = "#374151";
  ctx.fillRect(395, 20, 260, 22);
  const p2Width = 260 * (p2.hp / p2.maxHp);
  ctx.fillStyle = p2.hp > 30 ? "#10B981" : "#EF4444";
  ctx.fillRect(395 + (260 - p2Width), 20, p2Width, 22);
  ctx.strokeStyle = "#F9FAFB";
  ctx.strokeRect(395, 20, 260, 22);

  // VS 텍스트 및 수치
  ctx.fillStyle = "#FBBF24";
  ctx.font = "900 20px sans-serif";
  ctx.textAlign = "center";
  ctx.fillText("VS", 340, 38);

  ctx.fillStyle = "#FFFFFF";
  ctx.font = "bold 13px sans-serif";
  ctx.textAlign = "left";
  ctx.fillText(`${p1.name} (${p1.hp}/${p1.maxHp})`, 28, 58);
  ctx.textAlign = "right";
  ctx.fillText(`${p2.name} (${p2.hp}/${p2.maxHp})`, 652, 58);
}

function loop() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  if (!gameOver) {
    const p1Controls = isAI ? {
      left: keys["KeyA"], right: keys["KeyD"], jump: keys["KeyW"],
      punch: keys["KeyJ"], kick: keys["KeyK"], block: keys["KeyL"]
    } : {
      left: keys["KeyA"], right: keys["KeyD"], jump: keys["KeyW"],
      punch: keys["KeyF"], kick: keys["KeyG"], block: keys["KeyH"]
    };

    const p2Controls = isAI ? getAIControls(p2, p1) : {
      left: keys["ArrowLeft"], right: keys["ArrowRight"], jump: keys["ArrowUp"],
      punch: keys["KeyJ"], kick: keys["KeyK"], block: keys["KeyL"]
    };

    updateFighter(p1, p1Controls, p2);
    updateFighter(p2, p2Controls, p1);

    if (p1.hp <= 0 || p2.hp <= 0) {
      gameOver = true;
      winnerText = p1.hp > 0 ? `🏆 ${p1.name} K.O. 승리!` : `🏆 ${p2.name} K.O. 승리!`;
    }
  }

  drawHUD();
  drawFighter(p1);
  drawFighter(p2);

  // 타격 이펙트
  for (let i = sparks.length - 1; i >= 0; i--) {
    const s = sparks[i];
    ctx.fillStyle = s.color;
    ctx.beginPath();
    ctx.arc(s.x, s.y, (16 - s.life) * 2.2, 0, Math.PI * 2);
    ctx.fill();
    s.life--;
    if (s.life <= 0) sparks.splice(i, 1);
  }

  // K.O. 종료 오버레이
  if (gameOver) {
    ctx.fillStyle = "rgba(0, 0, 0, 0.65)";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "#FACC15";
    ctx.font = "900 36px sans-serif";
    ctx.textAlign = "center";
    ctx.fillText(winnerText, canvas.width / 2, 155);
    ctx.fillStyle = "#E5E7EB";
    ctx.font = "bold 16px sans-serif";
    ctx.fillText("다시 싸우려면 키보드 [ R ] 키를 누르세요!", canvas.width / 2, 195);
  }

  requestAnimationFrame(loop);
}

loop();
</script>
</body>
</html>
"""

# 파이썬에서 계산된 능력치를 게임 화면에 주입
game_html = (
    game_html.replace("__IS_AI__", is_ai_mode)
    .replace("__P1_NAME__", p1_char.split(" ")[1])
    .replace("__P1_HP__", str(p1_hp))
    .replace("__P1_ATK__", str(p1_atk))
    .replace("__P1_SPD__", str(p1_spd))
    .replace("__P1_COLOR__", p1_color)
    .replace("__P2_NAME__", p2_char.split(" ")[1])
    .replace("__P2_HP__", str(p2_hp))
    .replace("__P2_ATK__", str(p2_atk))
    .replace("__P2_SPD__", str(p2_spd))
    .replace("__P2_COLOR__", p2_color)
)

components.html(game_html, height=365)

# ---------------------------------------------------------
# 4. 반복문 (for): 전체 캐릭터 능력치 비교표(Table) 출력
# ---------------------------------------------------------
st.subheader("📊 전체 캐릭터 기본 능력치 도감")
roster_table = []
for char in characters:
    hp, atk, spd, _ = calculate_fighter_stats(char, 1)
    roster_table.append(
        {"캐릭터": char, "기본 체력(HP)": hp, "기본 공격력": atk, "이동 속도": spd}
    )
st.table(roster_table)
